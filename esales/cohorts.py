import pandas as pd
import numpy as np


def build(df: pd.DataFrame) -> pd.DataFrame:
    c = df[df["completed"]].copy()
    c["month"] = c["order_date"].dt.to_period("M")

    first_purchase = (
        c.groupby("customer_id")["month"]
        .min()
        .rename("cohort_month")
        .reset_index()
    )
    c = c.merge(first_purchase, on="customer_id")
    c["period_number"] = (c["month"] - c["cohort_month"]).apply(lambda x: x.n)

    cohort_data = (
        c.groupby(["cohort_month", "period_number"])["customer_id"]
        .nunique()
        .reset_index()
    )

    cohort_size = cohort_data[cohort_data["period_number"] == 0].set_index("cohort_month")["customer_id"]
    cohort_data["cohort_size"] = cohort_data["cohort_month"].map(cohort_size)
    cohort_data["retention"]   = (cohort_data["customer_id"] / cohort_data["cohort_size"] * 100).round(1)

    pivot = cohort_data.pivot(index="cohort_month", columns="period_number", values="retention")
    pivot.index = pivot.index.astype(str)
    pivot.columns = [f"M+{c}" for c in pivot.columns]
    return pivot


def retention_color(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "dim"
    if val >= 40:
        return "bold green"
    if val >= 20:
        return "green"
    if val >= 10:
        return "yellow"
    return "red"
