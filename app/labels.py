"""Public display labels for Cinderhaven trade partners.

Reads the vendored reference/retailer_display_labels.json (synced from the
cinderhaven-data-platform by scripts/refresh_canonical.py). The data keeps the
real names; every rendered surface that puts a name beside a Cinderhaven dollar
figure shows the label instead. Display layer only: IDs, data keys, and
computations are untouched.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_LABELS_JSON = Path(__file__).resolve().parent.parent / "reference" / "retailer_display_labels.json"


@lru_cache(maxsize=1)
def _lookup() -> dict[str, str]:
    """Map both partner IDs (RET-*, DIST-*) and real names to their labels."""
    data = json.loads(_LABELS_JSON.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for group in ("retailers", "distributors"):
        for pid, entry in data[group].items():
            out[pid] = entry["label"]
            out[entry["name"]] = entry["label"]
    return out


def display_label(name_or_id, capitalize: bool = True) -> str:
    """Return the public label for a retailer/distributor name or ID.

    capitalize=True for table cells, legend/chart entries, and sentence starts;
    False for mid-sentence use. Unknown values pass through unchanged.
    """
    key = str(name_or_id)
    label = _lookup().get(key, key)
    if capitalize and label:
        return label[0].upper() + label[1:]
    return label
