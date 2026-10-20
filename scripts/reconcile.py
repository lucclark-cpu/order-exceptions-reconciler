"""Daily cross-system order reconciliation.

Compares three exports — seller platform orders, warehouse (WMS) records and carrier
tracking — and produces a prioritised exception queue plus draft escalations.

Usage:
  python reconcile.py --platform platform_orders.csv --wms wms_records.csv \
      --carrier carrier_tracking.csv --out output/ [--as-of "2026-10-19 08:00"] [--config config.json]

Only the standard library is used, so it runs anywhere Python 3.9+ does.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DEFAULT_CONFIG = {
    "wms_ingest_sla_hours": 4,       # order should reach the WMS within this
    "dispatch_sla_hours": 48,        # order should leave the warehouse within this
    "tracking_sla_hours": 24,        # dispatched order should have a carrier scan within this
    "transit_stall_hours": 72,       # no carrier scan for this long = stalled
    "pre_dispatch_statuses": ["RECEIVED", "PICKING", "PACKED", "ON_HOLD"],
    "carrier_problem_statuses": ["EXCEPTION_ADDRESS", "RETURNED_TO_SENDER", "DAMAGED", "LOST"],
}

# type -> (severity, owner, recommended action)
RULES = {
    "MISSING_IN_WMS":     ("HIGH", "Platform/Tech", "Order never reached the warehouse. Check the integration log, re-push the order to the WMS, tell the seller if dispatch SLA is at risk."),
    "DUPLICATE_IN_WMS":   ("HIGH", "Warehouse",     "Same order exists twice in the WMS — risk of double shipment. Ask the warehouse to cancel the duplicate before it is picked."),
    "ORPHAN_IN_WMS":      ("HIGH", "Warehouse",     "Warehouse is processing an order with no matching platform order. Hold it and confirm the order ID/source before it ships."),
    "QTY_MISMATCH":       ("HIGH", "Warehouse",     "Quantity in WMS differs from the seller's order. Correct the WMS line (or confirm with the seller) before/after dispatch."),
    "SKU_MISMATCH":       ("HIGH", "Warehouse",     "Wrong SKU in the WMS. Customer may receive the wrong item — intercept if not delivered, raise with the warehouse."),
    "CARRIER_EXCEPTION":  ("HIGH", "Carrier",       "Carrier has flagged a problem (address/damage/return). Contact the carrier, confirm the address with the seller, arrange redelivery or replacement."),
    "STUCK_IN_WAREHOUSE": ("MEDIUM", "Warehouse",   "Order past dispatch SLA and not shipped. Chase the warehouse for a dispatch time and reason (stock, hold, capacity)."),
    "MISSING_TRACKING":   ("MEDIUM", "Carrier",     "Warehouse says dispatched but the carrier has no record. Ask the warehouse for the manifest/collection proof and chase the carrier."),
    "STUCK_IN_TRANSIT":   ("MEDIUM", "Carrier",     "No carrier scan within the stall window. Open a trace with the carrier; if no movement in 24h, consider a reship."),
    "STATUS_MISMATCH":    ("LOW", "Platform/Tech",  "Seller-facing status disagrees with the warehouse/carrier. Resync the status so the seller's view is correct."),
}
SEV_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def parse_ts(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M") if s and s.strip() else None


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def hours(a, b):
    return round((a - b).total_seconds() / 3600, 1)


def reconcile(platform, wms, carrier, as_of, cfg):
    exceptions = []

    def flag(oid, kind, detail, age_h, seller="", warehouse="", carrier_name=""):
        sev, owner, action = RULES[kind]
        exceptions.append(dict(order_id=oid, exception=kind, severity=sev, owner=owner,
                               age_hours=age_h, seller=seller, warehouse=warehouse,
                               carrier=carrier_name, detail=detail, recommended_action=action))

    wms_count = Counter(r["order_id"] for r in wms)
    W = {r["order_id"]: r for r in wms}
    C = {r["order_id"]: r for r in carrier}
    P = {r["order_id"]: r for r in platform}

    for oid, p in P.items():
        created = parse_ts(p["order_created_at"])
        age = hours(as_of, created)
        seller = p.get("seller", "")
        w, c = W.get(oid), C.get(oid)

        if w is None:
            if age > cfg["wms_ingest_sla_hours"]:
                flag(oid, "MISSING_IN_WMS", f"Placed {age}h ago on {p.get('channel','')}, not in WMS", age, seller)
            continue

        wh = w.get("warehouse", "")
        if wms_count[oid] > 1:
            flag(oid, "DUPLICATE_IN_WMS", f"{wms_count[oid]} WMS records for one order", age, seller, wh)
        if str(p["qty"]) != str(w["qty"]):
            flag(oid, "QTY_MISMATCH", f"Platform qty {p['qty']} vs WMS qty {w['qty']}", age, seller, wh)
        if p["sku"] != w["sku"]:
            flag(oid, "SKU_MISMATCH", f"Platform SKU {p['sku']} vs WMS SKU {w['sku']}", age, seller, wh)

        status = w["wms_status"].upper()
        if status in cfg["pre_dispatch_statuses"]:
            if age > cfg["dispatch_sla_hours"]:
                flag(oid, "STUCK_IN_WAREHOUSE", f"WMS status {status}, order is {age}h old (SLA {cfg['dispatch_sla_hours']}h)", age, seller, wh)
            if p.get("platform_status", "").lower() in ("shipped", "delivered"):
                flag(oid, "STATUS_MISMATCH", f"Platform shows {p['platform_status']} but WMS is {status}", age, seller, wh)
            continue

        if status == "DISPATCHED" and c is None:
            since = hours(as_of, parse_ts(w["status_updated_at"]))
            if since > cfg["tracking_sla_hours"]:
                flag(oid, "MISSING_TRACKING", f"Dispatched {since}h ago, no carrier record", age, seller, wh)
            continue

        if c:
            cs, car = c["carrier_status"].upper(), c.get("carrier", "")
            since_scan = hours(as_of, parse_ts(c["last_scan_at"]))
            if cs in cfg["carrier_problem_statuses"]:
                flag(oid, "CARRIER_EXCEPTION", f"{car} status {cs} (tracking {c.get('tracking_number','')})", age, seller, wh, car)
            elif cs == "IN_TRANSIT" and since_scan > cfg["transit_stall_hours"]:
                flag(oid, "STUCK_IN_TRANSIT", f"Last {car} scan {since_scan}h ago (tracking {c.get('tracking_number','')})", age, seller, wh, car)
            if cs == "DELIVERED" and p.get("platform_status", "").lower() != "delivered":
                flag(oid, "STATUS_MISMATCH", f"{car} shows DELIVERED, platform shows {p.get('platform_status')}", age, seller, wh, car)

    for oid in wms_count:
        if oid not in P:
            w = W[oid]
            flag(oid, "ORPHAN_IN_WMS", f"WMS status {w['wms_status']} with no platform order", "", "", w.get("warehouse", ""))

    exceptions.sort(key=lambda e: (SEV_RANK[e["severity"]], -(e["age_hours"] or 0)))
    return exceptions


def write_outputs(exceptions, n_orders, out_dir, as_of):
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = ["order_id", "exception", "severity", "owner", "age_hours", "seller",
              "warehouse", "carrier", "detail", "recommended_action"]
    with open(out_dir / "exceptions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(exceptions)

    by_type = Counter(e["exception"] for e in exceptions)
    by_sev = Counter(e["severity"] for e in exceptions)
    affected = len({e["order_id"] for e in exceptions})
    L = [f"# Order exceptions — {as_of:%a %d %b %Y, %H:%M}", "",
         f"**{len(exceptions)} exceptions across {affected} orders** "
         f"({affected / max(n_orders, 1):.1%} of {n_orders} platform orders). "
         f"High: {by_sev['HIGH']} · Medium: {by_sev['MEDIUM']} · Low: {by_sev['LOW']}", "",
         "| Exception | Count | Severity | Owner |", "|---|---|---|---|"]
    for kind, n in sorted(by_type.items(), key=lambda kv: (SEV_RANK[RULES[kv[0]][0]], -kv[1])):
        L.append(f"| {kind} | {n} | {RULES[kind][0]} | {RULES[kind][1]} |")
    L += ["", "## Queue (work top to bottom)", "",
          "| # | Order | Exception | Sev | Detail |", "|---|---|---|---|---|"]
    for i, e in enumerate(exceptions, 1):
        L.append(f"| {i} | {e['order_id']} | {e['exception']} | {e['severity']} | {e['detail']} |")

    groups = defaultdict(list)
    for e in exceptions:
        if e["owner"] == "Warehouse" and e["warehouse"]:
            groups[("Warehouse", e["warehouse"])].append(e)
        elif e["owner"] == "Carrier" and e["carrier"]:
            groups[("Carrier", e["carrier"])].append(e)
        elif e["owner"] == "Carrier":  # missing tracking: carrier unknown, go via warehouse
            groups[("Warehouse", e["warehouse"])].append(e)
    L += ["", "## Draft escalations (review before sending — nothing is sent automatically)", ""]
    for (kind, name), items in sorted(groups.items()):
        L += [f"### To {name} ({kind.lower()})", "",
              f"Subject: {len(items)} order(s) needing action — {as_of:%d %b}", "",
              f"Hi {name} team,", "",
              "Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?", ""]
        for e in items:
            L.append(f"- {e['order_id']} — {e['exception'].replace('_', ' ').lower()}: {e['detail']}")
        L += ["", "Thanks,", "Gonini Ops", ""]
    (out_dir / "exceptions_report.md").write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", required=True)
    ap.add_argument("--wms", required=True)
    ap.add_argument("--carrier", required=True)
    ap.add_argument("--out", default="output")
    ap.add_argument("--as-of", help="'YYYY-MM-DD HH:MM'; defaults to now")
    ap.add_argument("--config", help="JSON file overriding SLA thresholds")
    a = ap.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    if a.config:
        cfg.update(json.loads(Path(a.config).read_text()))
    as_of = parse_ts(a.as_of) if a.as_of else datetime.now().replace(second=0, microsecond=0)

    platform, wms, carrier = read_csv(a.platform), read_csv(a.wms), read_csv(a.carrier)
    exc = reconcile(platform, wms, carrier, as_of, cfg)
    write_outputs(exc, len(platform), Path(a.out), as_of)
    print(f"{len(exc)} exceptions -> {Path(a.out) / 'exceptions_report.md'}")


if __name__ == "__main__":
    main()
