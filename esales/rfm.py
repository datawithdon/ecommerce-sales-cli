import pandas as pd
import numpy as np


SEGMENTS = {
    "Champions":          (lambda r, f, m: (r >= 4) & (f >= 4) & (m >= 4)),
    "Loyal":              (lambda r, f, m: (f >= 3) & (m >= 3) & ~((r >= 4) & (f >= 4) & (m >= 4))),
    "Potential Loyalists":(lambda r, f, m: (r >= 3) & (f <= 2)),
    "New Customers":      (lambda r, f, m: (r >= 4) & (f == 1)),
    "At Risk":            (lambda r, f, m: (r <= 2) & (f >= 3)),
    "Hibernating":        (lambda r, f, m: (r <= 2) & (f <= 2) & (m >= 2)),
    "Lost":               (lambda r, f, m: (r == 1) & (f <= 2) & (m == 1)),
}

SEGMENT_COLORS = {
    "Champions":           "bold green",
    "Loyal":               "green",
    "Potential Loyalists": "cyan",
    "New Customers":       "blue",
    "At Risk":             "yellow",
    "Hibernating":         "dark_orange",
    "Lost":                "red",
}


def score(df: pd.DataFrame) -> pd.DataFrame:
    c = df[df["completed"]].copy()
    snapshot = c["order_date"].max() + pd.Timedelta(days=1)

    cust = (
        c.groupby("customer_id")
        .agg(
            last_order=("order_date", "max"),
            frequency=("order_id", "count"),
            monetary=("revenue", "sum"),
        )
        .reset_index()
    )
    cust["recency_days"] = (snapshot - cust["last_order"]).dt.days

    # Quintile scoring (1=worst, 5=best)
    cust["R"] = pd.qcut(cust["recency_days"].rank(method="first"), 5,
                         labels=[5, 4, 3, 2, 1]).astype(int)
    cust["F"] = pd.qcut(cust["frequency"].rank(method="first"),    5,
                         labels=[1, 2, 3, 4, 5]).astype(int)
    cust["M"] = pd.qcut(cust["monetary"].rank(method="first"),     5,
                         labels=[1, 2, 3, 4, 5]).astype(int)
    cust["rfm_score"] = cust["R"] + cust["F"] + cust["M"]

    # Assign segment (first match wins)
    cust["segment"] = "Other"
    for seg, fn in SEGMENTS.items():
        mask = fn(cust["R"], cust["F"], cust["M"]) & (cust["segment"] == "Other")
        cust.loc[mask, "segment"] = seg

    return cust.sort_values("rfm_score", ascending=False)


def segment_summary(scored: pd.DataFrame) -> pd.DataFrame:
    total = len(scored)
    return (
        scored.groupby("segment")
        .agg(
            customers=("customer_id", "count"),
            avg_monetary=("monetary", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_recency=("recency_days", "mean"),
        )
        .round(1)
        .reset_index()
        .assign(pct=lambda x: (x["customers"] / total * 100).round(1))
        .sort_values("avg_monetary", ascending=False)
    )
