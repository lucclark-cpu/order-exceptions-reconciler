# Order exceptions reconciler — a Claude skill

Built by Lucien Clark as a working example for Gonini's Graduate Business Operations Associate role.

**The problem:** every day, someone has to cross-check three systems — the seller platform, the
warehouse (WMS) and carrier tracking — to find orders that went missing, got stuck, or don't match.
Done by hand it's slow and easy to miss things.

**What this does:** Claude takes the three exports, runs a deterministic checker, sanity-checks the
result, and hands back a prioritised exception queue plus draft emails to each warehouse and
carrier (drafted, never sent without approval).

**Design choices**
- *Rules in code, judgement in Claude.* Thresholds and matching logic are in `scripts/reconcile.py`
  so results are repeatable and auditable. Claude does what code is bad at: spotting a bad export,
  noticing a systemic pattern, writing the escalation.
- *SLAs are config, not hard-coded* (`--config`), because every warehouse contract differs. The
  defaults (4h / 48h / 24h / 72h) are my assumptions, not Gonini's real numbers.
- *Tested against ground truth.* Mock data with 29 injected exceptions and decoys; current run
  catches 29/29 with 0 false positives.

**Try it**
```
python scripts/generate_sample_data.py
python scripts/reconcile.py --platform sample_data/platform_orders.csv --wms sample_data/wms_records.csv \
    --carrier sample_data/carrier_tracking.csv --out output --as-of "2026-10-19 08:00"
python scripts/check_against_ground_truth.py sample_data/_ground_truth.csv output/exceptions.csv
```

**What I'd do next with real access:** map the real Bezos Platform / WMS / Ops Dashboard export
columns; add the invoice-vs-rate-card check; schedule it to run each morning and post the HIGH items
to the ops channel.

Why I built this: at Finnegan Marshall I reconciled monthly draw reports — developer budgets,
change orders and cost-to-complete — across 20+ live lender-side schemes, flagging variances before
they reached the lender. Same job, different nouns.
