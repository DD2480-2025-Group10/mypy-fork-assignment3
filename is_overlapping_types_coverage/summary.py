from __future__ import annotations

import os
from collections import defaultdict


def summarize() -> None:
    totals: dict[int, int] = defaultdict(int)

    here = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(here, "logs")
    if not os.path.isdir(logs_dir):
        print("No logs directory found; nothing to summarize.")
        return

    for fname in os.listdir(logs_dir):
        if not (fname.startswith("coverage_") and fname.endswith(".txt")):
            continue
        path = os.path.join(logs_dir, fname)
        try:
            with open(path, encoding="utf8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 2:
                        continue
                    try:
                        bid = int(parts[0])
                        cnt = int(parts[1])
                    except ValueError:
                        continue
                    totals[bid] += cnt
        except OSError:
            continue

    hit_ids = {bid for bid, cnt in totals.items() if cnt > 0}

    print(f"Total unique branch ids hit: {len(hit_ids)}")
    if hit_ids:
        print("Hit ids:", ", ".join(str(bid) for bid in sorted(hit_ids)))


if __name__ == "__main__":
    summarize()
