import pandas as pd


def summary(df: pd.DataFrame) -> dict:
    c = df[df["completed"]]
    total_rev = c["revenue"].sum()
    total_orders = len(c)
    unique_customers = c["customer_id"].nunique()

    monthly = c.groupby("month_str")["revenue"].sum().sort_index()
    months = list(monthly.index)
    revenues = list(monthly.values)

    # MoM growth: last full month vs prior
    mom_growth = None
    if len(revenues) >= 2:
        mom_growth = round((revenues[-1] - revenues[-2]) / revenues[-2] * 100, 1)

    # YoY growth
    yoy_growth = None
    yearly = c.groupby("year")["revenue"].sum()
    if len(yearly) >= 2:
        years = sorted(yearly.index)
        yoy_growth = round((yearly[years[-1]] - yearly[years[-2]]) / yearly[years[-2]] * 100, 1)

    top_cat = c.groupby("category")["revenue"].sum().idxmax() if not c.empty else "—"
    refund_rate = round((1 - df["completed"].mean()) * 100, 1)

    return {
        "total_revenue":     round(total_rev, 2),
        "total_orders":      total_orders,
        "unique_customers":  unique_customers,
        "avg_order_value":   round(total_rev / total_orders, 2) if total_orders else 0,
        "avg_items_order":   round(c["quantity"].mean(), 1) if not c.empty else 0,
        "refund_rate":       refund_rate,
        "top_category":      top_cat,
        "mom_growth":        mom_growth,
        "yoy_growth":        yoy_growth,
        "monthly_labels":    months,
        "monthly_revenue":   revenues,
    }


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    c = df[df["completed"]]
    return (
        c.groupby("category")
        .agg(
            orders=("order_id", "count"),
            revenue=("revenue", "sum"),
            customers=("customer_id", "nunique"),
            avg_order=("revenue", "mean"),
        )
        .round(2)
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
