from pathlib import Path
import pandas as pd
import sys
from rich.console import Console

_console = Console(stderr=True)

REQUIRED = {
    "order_id", "customer_id", "product", "category",
    "order_date", "quantity", "unit_price", "discount_pct", "revenue", "status",
}


def load(path: Path) -> pd.DataFrame:
    if not path.exists():
        _console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)

    df = pd.read_csv(path, parse_dates=["order_date"])
    missing = REQUIRED - set(df.columns)
    if missing:
        _console.print(f"[red]Missing columns:[/red] {', '.join(sorted(missing))}")
        sys.exit(1)

    df["month"]        = df["order_date"].dt.to_period("M")
    df["month_str"]    = df["month"].astype(str)
    df["year"]         = df["order_date"].dt.year
    df["completed"]    = df["status"] == "completed"
    df["order_value"]  = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])
    return df


def completed(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["completed"]].copy()
