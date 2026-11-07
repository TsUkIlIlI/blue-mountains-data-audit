"""Check grid-day joins and detection labels in a prepared data handoff."""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


EXAMPLES = Path(__file__).resolve().parent / "examples"
FEATURE_KEY = ["grid_id", "feature_date"]
LABEL_KEY = ["grid_id", "target_date"]
COUNT_COLUMNS = [
    "fire_detection_count_raw",
    "prescribed_burn_detection_count",
    "eligible_fire_detection_count",
]
PANEL_COLUMNS = [*FEATURE_KEY, "target_date", "fire_today", "fire_positive"]
LABEL_COLUMNS = [*LABEL_KEY, *COUNT_COLUMNS, "fire_positive"]
ONE_DAY = pd.Timedelta(days=1)


def read_table(path, columns, dates, key):
    table = pd.read_csv(path, usecols=columns, dtype={"grid_id": "string"})
    if table.empty or table[columns].isna().any().any():
        raise ValueError(f"{path.name}: expected rows with all required fields populated")
    table["grid_id"] = table["grid_id"].str.strip()
    if table["grid_id"].eq("").any():
        raise ValueError(f"{path.name}: blank grid identifier")
    for column in dates:
        table[column] = pd.to_datetime(table[column], format="%Y-%m-%d", errors="raise")
    if table[dates].isna().any().any():
        raise ValueError(f"{path.name}: missing calendar date")
    numeric = [column for column in columns if column not in ["grid_id", *dates]]
    table[numeric] = table[numeric].apply(pd.to_numeric, errors="raise")
    if table.duplicated(key).any():
        raise ValueError(f"{path.name}: duplicate key ({', '.join(key)})")
    return table


def audit(panel, labels):
    dates = panel["feature_date"]
    first_day, last_day = dates.min(), dates.max()
    feature_days = (last_day - first_day).days + 1
    cells = set(panel["grid_id"])
    label_dates = labels["target_date"]
    counts = labels[COUNT_COLUMNS]
    raw, prescribed, eligible = (counts[column] for column in COUNT_COLUMNS)

    # A left join keeps every panel row visible when a reference label is missing.
    target = panel.merge(
        labels[[*LABEL_KEY, "fire_positive"]],
        on=LABEL_KEY,
        how="left",
        validate="one_to_one",
        indicator=True,
        suffixes=("_panel", "_label"),
    )
    feature_labels = labels[[*LABEL_KEY, "fire_positive"]].rename(
        columns={"target_date": "feature_date", "fire_positive": "expected_fire_today"}
    )
    current = panel.merge(
        feature_labels, on=FEATURE_KEY, how="left", validate="one_to_one", indicator=True
    )

    checks = {
        "complete_feature_grid_days": len(panel) == len(cells) * feature_days,
        "complete_reference_grid_days": (
            set(labels["grid_id"]) == cells
            and label_dates.min() == first_day
            and label_dates.max() == last_day + ONE_DAY
            and len(labels) == len(cells) * (feature_days + 1)
        ),
        "target_is_next_utc_day": (panel["target_date"] == dates + ONE_DAY).all(),
        "counts_are_nonnegative_integers": (counts.ge(0) & counts.mod(1).eq(0)).all().all(),
        "eligible_equals_raw_minus_prescribed": eligible.eq(raw - prescribed).all(),
        "positive_label_matches_eligible_count": labels["fire_positive"].eq(eligible.gt(0)).all(),
        "target_labels_present": target["_merge"].eq("both").all(),
        "target_labels_match": target["fire_positive_panel"].eq(target["fire_positive_label"]).all(),
        "feature_day_labels_present": current["_merge"].eq("both").all(),
        "feature_day_labels_match": current["fire_today"].eq(current["expected_fire_today"]).all(),
    }
    monthly = (
        labels.assign(month=label_dates.dt.to_period("M").astype(str))
        .groupby("month", as_index=False)
        .agg(
            calendar_days=("target_date", "nunique"),
            label_rows=("grid_id", "size"),
            eligible_detections=("eligible_fire_detection_count", "sum"),
            positive_cell_days=("fire_positive", "sum"),
        )
    )
    checks = {name: bool(result) for name, result in checks.items()}
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "model_rows": len(panel),
        "label_rows": len(labels),
        "grid_cells": len(cells),
        "checks": checks,
        "monthly_label_coverage": monthly.to_dict(orient="records"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=EXAMPLES / "model_panel.csv")
    parser.add_argument("--labels", type=Path, default=EXAMPLES / "daily_labels.csv")
    args = parser.parse_args()
    try:
        panel = read_table(args.panel, PANEL_COLUMNS, ["feature_date", "target_date"], FEATURE_KEY)
        labels = read_table(args.labels, LABEL_COLUMNS, ["target_date"], LABEL_KEY)
        report = audit(panel, labels)
    except (OSError, ValueError) as exc:
        print(f"Audit input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
