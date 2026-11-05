"""Public display labels: no real trade-partner name beside a Cinderhaven dollar figure.

Rule decided 2026-11-05 (lailara-website DECISIONS); labels come from the
vendored reference/retailer_display_labels.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from app.labels import display_label

ROOT = Path(__file__).resolve().parent.parent
_MAP = json.loads((ROOT / "reference" / "retailer_display_labels.json").read_text(encoding="utf-8"))
_REAL = [v["name"] for g in ("retailers", "distributors") for v in _MAP[g].values()
         if v["name"] != v["label"]]
_REAL_RE = re.compile(r"\b(" + "|".join(re.escape(n) for n in _REAL) + r"|DPI)\b")

_NET = pd.DataFrame({
    "retailer": ["Walmart", "Costco", "Kroger", "Whole Foods", "Sprouts", "Regional Group"],
    "gross_revenue": [7.4e6, 7.0e6, 6.6e6, 5.6e6, 3.9e6, 1.7e6],
    "trade_spend": [0.9e6, 0.7e6, 0.7e6, 0.5e6, 0.4e6, 0.1e6],
    "net_revenue": [6.5e6, 6.3e6, 5.9e6, 5.1e6, 3.5e6, 1.6e6],
    "net_to_gross_ratio": [0.87, 0.9, 0.89, 0.91, 0.9, 0.94],
})


def test_display_label_by_name_and_id():
    assert display_label("Walmart") == "National mass retailer"
    assert display_label("RET-WALMART", capitalize=False) == "national mass retailer"
    assert display_label("DIST-KEHE") == "Distributor B"
    assert display_label("Regional Group", capitalize=False) == "Regional Group"
    assert display_label("Unknown Co") == "Unknown Co"


def test_compression_lead_uses_labels():
    from app.layout import _compression_lead
    text = _compression_lead(_NET)
    assert not _REAL_RE.search(text), text
    assert "The national mass retailer, the club retailer, and the conventional grocer are" in text


def test_bump_chart_text_uses_labels():
    from app.charts import bump_chart
    fig = bump_chart(_NET)
    rendered = [a.text for a in fig.layout.annotations]
    rendered += [t.name for t in fig.data] + [t.hovertemplate for t in fig.data]
    for s in rendered:
        assert not _REAL_RE.search(s), s


def test_leakage_grid_rows_carry_label_not_id():
    from app.charts import leakage_instances_grid
    df = pd.DataFrame({
        "leakage_type": ["ghost_promo"], "deduction_id": ["RD-1"], "retailer_id": ["RET-COSTCO"],
        "promo_id": [None], "period": ["2024-01-01"], "agreed_amount": [None],
        "actual_amount": [100.0], "variance": [None], "classification": ["Recoverable"],
    })
    grid = leakage_instances_grid(df)
    assert grid.rowData[0]["retailer_label"] == "Club retailer"
    assert "retailer_id" not in grid.rowData[0]
