# Order exceptions — Mon 19 Oct 2026, 08:00

**29 exceptions across 29 orders** (14.4% of 201 platform orders). High: 15 · Medium: 11 · Low: 3

| Exception | Count | Severity | Owner |
|---|---|---|---|
| MISSING_IN_WMS | 4 | HIGH | Platform/Tech |
| CARRIER_EXCEPTION | 3 | HIGH | Carrier |
| QTY_MISMATCH | 3 | HIGH | Warehouse |
| SKU_MISMATCH | 2 | HIGH | Warehouse |
| ORPHAN_IN_WMS | 2 | HIGH | Warehouse |
| DUPLICATE_IN_WMS | 1 | HIGH | Warehouse |
| STUCK_IN_TRANSIT | 4 | MEDIUM | Carrier |
| STUCK_IN_WAREHOUSE | 4 | MEDIUM | Warehouse |
| MISSING_TRACKING | 3 | MEDIUM | Carrier |
| STATUS_MISMATCH | 3 | LOW | Platform/Tech |

## Queue (work top to bottom)

| # | Order | Exception | Sev | Detail |
|---|---|---|---|---|
| 1 | ORD-100185 | CARRIER_EXCEPTION | HIGH | DPD status EXCEPTION_ADDRESS (tracking TRK1312606333) |
| 2 | ORD-100075 | QTY_MISMATCH | HIGH | Platform qty 4 vs WMS qty 5 |
| 3 | ORD-100158 | QTY_MISMATCH | HIGH | Platform qty 3 vs WMS qty 4 |
| 4 | ORD-100063 | SKU_MISMATCH | HIGH | Platform SKU SKU-1038 vs WMS SKU SKU-1010 |
| 5 | ORD-100099 | DUPLICATE_IN_WMS | HIGH | 2 WMS records for one order |
| 6 | ORD-100177 | CARRIER_EXCEPTION | HIGH | DPD status RETURNED_TO_SENDER (tracking TRK5203589186) |
| 7 | ORD-100018 | SKU_MISMATCH | HIGH | Platform SKU SKU-1028 vs WMS SKU SKU-1024 |
| 8 | ORD-100198 | CARRIER_EXCEPTION | HIGH | DHL status EXCEPTION_ADDRESS (tracking TRK9926778957) |
| 9 | ORD-100021 | QTY_MISMATCH | HIGH | Platform qty 1 vs WMS qty 2 |
| 10 | ORD-100069 | MISSING_IN_WMS | HIGH | Placed 25.0h ago on eBay, not in WMS |
| 11 | ORD-100115 | MISSING_IN_WMS | HIGH | Placed 25.0h ago on eBay, not in WMS |
| 12 | ORD-100162 | MISSING_IN_WMS | HIGH | Placed 22.0h ago on Shopify, not in WMS |
| 13 | ORD-100007 | MISSING_IN_WMS | HIGH | Placed 21.0h ago on eBay, not in WMS |
| 14 | ORD-900000 | ORPHAN_IN_WMS | HIGH | WMS status PICKING with no platform order |
| 15 | ORD-900001 | ORPHAN_IN_WMS | HIGH | WMS status PICKING with no platform order |
| 16 | ORD-100097 | STUCK_IN_TRANSIT | MEDIUM | Last DPD scan 113.0h ago (tracking TRK8353640266) |
| 17 | ORD-100096 | STUCK_IN_WAREHOUSE | MEDIUM | WMS status RECEIVED, order is 95.0h old (SLA 48h) |
| 18 | ORD-100047 | STUCK_IN_WAREHOUSE | MEDIUM | WMS status PICKING, order is 86.0h old (SLA 48h) |
| 19 | ORD-100110 | STUCK_IN_WAREHOUSE | MEDIUM | WMS status RECEIVED, order is 84.0h old (SLA 48h) |
| 20 | ORD-100149 | STUCK_IN_TRANSIT | MEDIUM | Last PostNL scan 95.0h ago (tracking TRK5751023835) |
| 21 | ORD-100174 | STUCK_IN_TRANSIT | MEDIUM | Last Royal Mail scan 115.0h ago (tracking TRK7079202254) |
| 22 | ORD-100058 | MISSING_TRACKING | MEDIUM | Dispatched 43.0h ago, no carrier record |
| 23 | ORD-100141 | STUCK_IN_WAREHOUSE | MEDIUM | WMS status RECEIVED, order is 61.0h old (SLA 48h) |
| 24 | ORD-100125 | MISSING_TRACKING | MEDIUM | Dispatched 46.0h ago, no carrier record |
| 25 | ORD-100091 | MISSING_TRACKING | MEDIUM | Dispatched 33.0h ago, no carrier record |
| 26 | ORD-100169 | STUCK_IN_TRANSIT | MEDIUM | Last Royal Mail scan 116.0h ago (tracking TRK3874432021) |
| 27 | ORD-100039 | STATUS_MISMATCH | LOW | Royal Mail shows DELIVERED, platform shows Processing |
| 28 | ORD-100068 | STATUS_MISMATCH | LOW | DPD shows DELIVERED, platform shows Processing |
| 29 | ORD-100184 | STATUS_MISMATCH | LOW | Royal Mail shows DELIVERED, platform shows Processing |

## Draft escalations (review before sending — nothing is sent automatically)

### To DHL (carrier)

Subject: 1 order(s) needing action — 19 Oct

Hi DHL team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100198 — carrier exception: DHL status EXCEPTION_ADDRESS (tracking TRK9926778957)

Thanks,
Gonini Ops

### To DPD (carrier)

Subject: 3 order(s) needing action — 19 Oct

Hi DPD team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100185 — carrier exception: DPD status EXCEPTION_ADDRESS (tracking TRK1312606333)
- ORD-100177 — carrier exception: DPD status RETURNED_TO_SENDER (tracking TRK5203589186)
- ORD-100097 — stuck in transit: Last DPD scan 113.0h ago (tracking TRK8353640266)

Thanks,
Gonini Ops

### To PostNL (carrier)

Subject: 1 order(s) needing action — 19 Oct

Hi PostNL team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100149 — stuck in transit: Last PostNL scan 95.0h ago (tracking TRK5751023835)

Thanks,
Gonini Ops

### To Royal Mail (carrier)

Subject: 2 order(s) needing action — 19 Oct

Hi Royal Mail team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100174 — stuck in transit: Last Royal Mail scan 115.0h ago (tracking TRK7079202254)
- ORD-100169 — stuck in transit: Last Royal Mail scan 116.0h ago (tracking TRK3874432021)

Thanks,
Gonini Ops

### To DE-BER-01 (warehouse)

Subject: 2 order(s) needing action — 19 Oct

Hi DE-BER-01 team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100125 — missing tracking: Dispatched 46.0h ago, no carrier record
- ORD-100091 — missing tracking: Dispatched 33.0h ago, no carrier record

Thanks,
Gonini Ops

### To NL-AMS-01 (warehouse)

Subject: 3 order(s) needing action — 19 Oct

Hi NL-AMS-01 team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100063 — sku mismatch: Platform SKU SKU-1038 vs WMS SKU SKU-1010
- ORD-100099 — duplicate in wms: 2 WMS records for one order
- ORD-100058 — missing tracking: Dispatched 43.0h ago, no carrier record

Thanks,
Gonini Ops

### To UK-CDF-02 (warehouse)

Subject: 5 order(s) needing action — 19 Oct

Hi UK-CDF-02 team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100075 — qty mismatch: Platform qty 4 vs WMS qty 5
- ORD-100158 — qty mismatch: Platform qty 3 vs WMS qty 4
- ORD-100021 — qty mismatch: Platform qty 1 vs WMS qty 2
- ORD-100047 — stuck in warehouse: WMS status PICKING, order is 86.0h old (SLA 48h)
- ORD-100141 — stuck in warehouse: WMS status RECEIVED, order is 61.0h old (SLA 48h)

Thanks,
Gonini Ops

### To UK-NOT-01 (warehouse)

Subject: 5 order(s) needing action — 19 Oct

Hi UK-NOT-01 team,

Today's reconciliation flagged the orders below. Could you confirm status and next steps by end of day?

- ORD-100018 — sku mismatch: Platform SKU SKU-1028 vs WMS SKU SKU-1024
- ORD-900000 — orphan in wms: WMS status PICKING with no platform order
- ORD-900001 — orphan in wms: WMS status PICKING with no platform order
- ORD-100096 — stuck in warehouse: WMS status RECEIVED, order is 95.0h old (SLA 48h)
- ORD-100110 — stuck in warehouse: WMS status RECEIVED, order is 84.0h old (SLA 48h)

Thanks,
Gonini Ops
