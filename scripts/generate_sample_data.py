"""Generate realistic mock exports from three systems (seller platform, WMS, carrier)
with a known set of injected exceptions, so the reconciler can be tested against
ground truth.

Usage: python generate_sample_data.py [out_dir]
"""
import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
AS_OF = datetime(2026, 10, 19, 8, 0)
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "sample_data")
OUT.mkdir(parents=True, exist_ok=True)

SELLERS = ["Northwind Skincare", "Brightpeak Outdoor", "Lumen Home", "Kettle & Co", "Vela Activewear"]
CHANNELS = ["Shopify", "Amazon", "eBay"]
WAREHOUSES = ["UK-NOT-01", "UK-CDF-02", "NL-AMS-01", "DE-BER-01"]
CARRIERS = ["DPD", "Royal Mail", "PostNL", "DHL"]
COUNTRIES = ["GB", "GB", "GB", "NL", "DE", "FR", "IE"]
SKUS = [f"SKU-{n:04d}" for n in range(1000, 1040)]

def ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M")

platform, wms, carrier, truth = [], [], [], []

def healthy_order(i):
    oid = f"ORD-{100000 + i}"
    created = AS_OF - timedelta(hours=random.randint(30, 140))
    sku, qty = random.choice(SKUS), random.randint(1, 4)
    wh, car = random.choice(WAREHOUSES), random.choice(CARRIERS)
    dispatched = created + timedelta(hours=random.randint(4, 20))
    delivered = random.random() < 0.6
    if delivered:
        last_scan = min(dispatched + timedelta(hours=random.randint(10, 40)), AS_OF - timedelta(hours=1))
    else:  # healthy in-transit parcels have a recent scan
        last_scan = max(AS_OF - timedelta(hours=random.randint(2, 48)), dispatched + timedelta(hours=1))
    platform.append(dict(order_id=oid, seller=random.choice(SELLERS), channel=random.choice(CHANNELS),
                         sku=sku, qty=qty, order_created_at=ts(created),
                         destination_country=random.choice(COUNTRIES),
                         platform_status="Delivered" if delivered else "Shipped"))
    wms.append(dict(order_id=oid, warehouse=wh, sku=sku, qty=qty, wms_status="DISPATCHED",
                    status_updated_at=ts(dispatched)))
    carrier.append(dict(order_id=oid, tracking_number=f"TRK{random.randint(10**9, 10**10-1)}",
                        carrier=car, carrier_status="DELIVERED" if delivered else "IN_TRANSIT",
                        last_scan_at=ts(last_scan)))
    return oid

# 200 orders, all healthy to start
ids = [healthy_order(i) for i in range(200)]
P = {r["order_id"]: r for r in platform}
W = {r["order_id"]: r for r in wms}
C = {r["order_id"]: r for r in carrier}
targets = iter(random.sample(ids, 40))

def inject(kind, n, fn):
    for _ in range(n):
        oid = next(targets)
        fn(oid)
        truth.append(dict(order_id=oid, injected_exception=kind))

def missing_in_wms(oid):
    P[oid]["platform_status"] = "Processing"
    P[oid]["order_created_at"] = ts(AS_OF - timedelta(hours=random.randint(8, 30)))
    del W[oid]; del C[oid]

def missing_tracking(oid):
    P[oid]["platform_status"] = "Shipped"
    W[oid]["status_updated_at"] = ts(AS_OF - timedelta(hours=random.randint(30, 60)))
    del C[oid]

def stuck_in_warehouse(oid):
    P[oid]["platform_status"] = "Processing"
    P[oid]["order_created_at"] = ts(AS_OF - timedelta(hours=random.randint(60, 96)))
    W[oid]["wms_status"] = random.choice(["RECEIVED", "PICKING"])
    W[oid]["status_updated_at"] = ts(AS_OF - timedelta(hours=random.randint(55, 90)))
    del C[oid]

def stuck_in_transit(oid):
    P[oid]["platform_status"] = "Shipped"
    C[oid]["carrier_status"] = "IN_TRANSIT"
    C[oid]["last_scan_at"] = ts(AS_OF - timedelta(hours=random.randint(80, 120)))

def qty_mismatch(oid):
    W[oid]["qty"] = int(P[oid]["qty"]) + 1

def sku_mismatch(oid):
    W[oid]["sku"] = random.choice([s for s in SKUS if s != P[oid]["sku"]])

def status_mismatch(oid):
    C[oid]["carrier_status"] = "DELIVERED"
    P[oid]["platform_status"] = "Processing"

def carrier_exception(oid):
    P[oid]["platform_status"] = "Shipped"
    C[oid]["carrier_status"] = random.choice(["EXCEPTION_ADDRESS", "RETURNED_TO_SENDER", "DAMAGED"])

inject("MISSING_IN_WMS", 4, missing_in_wms)
inject("MISSING_TRACKING", 3, missing_tracking)
inject("STUCK_IN_WAREHOUSE", 4, stuck_in_warehouse)
inject("STUCK_IN_TRANSIT", 4, stuck_in_transit)
inject("QTY_MISMATCH", 3, qty_mismatch)
inject("SKU_MISMATCH", 2, sku_mismatch)
inject("STATUS_MISMATCH", 3, status_mismatch)
inject("CARRIER_EXCEPTION", 3, carrier_exception)

wms_rows = list(W.values())
# duplicate WMS record (double-picked risk)
dup = next(targets)
wms_rows.append(dict(W[dup])); truth.append(dict(order_id=dup, injected_exception="DUPLICATE_IN_WMS"))
# orphan WMS records (in warehouse, no platform order)
for k in range(2):
    oid = f"ORD-{900000 + k}"
    wms_rows.append(dict(order_id=oid, warehouse="UK-NOT-01", sku=random.choice(SKUS), qty=1,
                         wms_status="PICKING", status_updated_at=ts(AS_OF - timedelta(hours=5))))
    truth.append(dict(order_id=oid, injected_exception="ORPHAN_IN_WMS"))

# a fresh order that is NOT yet late - should not be flagged (tests false positives)
fresh = "ORD-100999"
platform.append(dict(order_id=fresh, seller="Lumen Home", channel="Shopify", sku="SKU-1001", qty=1,
                     order_created_at=ts(AS_OF - timedelta(hours=1)), destination_country="GB",
                     platform_status="Processing"))

random.shuffle(wms_rows)
def write(name, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

write("platform_orders.csv", platform)
write("wms_records.csv", wms_rows)
write("carrier_tracking.csv", list(C.values()))
write("_ground_truth.csv", truth)
print(f"Wrote {len(platform)} platform, {len(wms_rows)} WMS, {len(C)} carrier rows; "
      f"{len(truth)} injected exceptions -> {OUT}")
