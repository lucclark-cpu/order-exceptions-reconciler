"""Score the reconciler against the injected exceptions in the sample data.

Usage: python check_against_ground_truth.py sample_data/_ground_truth.csv output/exceptions.csv
"""
import csv
import sys

truth = {(r["order_id"], r["injected_exception"]) for r in csv.DictReader(open(sys.argv[1]))}
found = {(r["order_id"], r["exception"]) for r in csv.DictReader(open(sys.argv[2]))}

missed = truth - found
extra = found - truth
caught = truth & found
print(f"Injected: {len(truth)}  Caught: {len(caught)}  Missed: {len(missed)}  Extra flags: {len(extra)}")
for m in sorted(missed):
    print("  MISSED", m)
for e in sorted(extra):
    print("  EXTRA ", e)
sys.exit(0 if not missed else 1)
