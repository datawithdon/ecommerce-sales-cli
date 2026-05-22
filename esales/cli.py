from pathlib import Path
from typing import Optional
import math

import typer
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich import box
from rich.text import Text

from esales import loader, kpis, rfm as rfm_mod, cohorts as cohorts_mod, charts

app = typer.Typer(
    name="esales",
    help="[bold cyan]E-commerce Sales Intelligence CLI[/bold cyan] — analyze orders CSVs in your terminal.",
    rich_markup_mode="rich",
    add_completion=False,
)

console = Console()

DEFAULT_DATA = Path(__file__).parent.parent / "data" / "sample_sales.csv"
FILE_OPTION  = typer.Option(DEFAULT_DATA, "--file", "-f", help="Path to orders CSV", show_default=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt_money(v: float) -> str:
    return f"${v:,.2f}"

def _trend(v) -> str:
    if v is None:
        return "—"
    arrow = "▲" if v >= 0 else "▼"
    color = "green" if v >= 0 else "red"
    return f"[{color}]{arrow} {abs(v):.1f}%[/{color}]"

def _kpi_card(label: str, value: str, sub: str = ""):
    body = Text(value, style="bold white", justify="center")
    if sub:
        body.append(f"\n{sub}", style="dim")
    from rich.panel import Panel
    return Panel(body, title=f"[dim]{label}[/dim]", border_style="cyan", padding=(0, 2))


# ── Commands ───────────────────────────────────────────────────────────────────

@app.command()
def summary(file: Path = FILE_OPTION):
    """Revenue KPIs at a glance + monthly trend chart."""
    df  = loader.load(file)
    kpi = kpis.summary(df)

    console.print()
    console.rule("[bold cyan]Sales Summary[/bold cyan]")
    console.print()

    cards = [
        _kpi_card("Total Revenue",      _fmt_money(kpi["total_revenue"]),    f"MoM {_trend(kpi['mom_growth'])}"),
        _kpi_card("Orders",             f"{kpi['total_orders']:,}",           f"YoY {_trend(kpi['yoy_growth'])}"),
        _kpi_card("Unique Customers",   f"{kpi['unique_customers']:,}"),
        _kpi_card("Avg Order Value",    _fmt_money(kpi["avg_order_value"])),
        _kpi_card("Avg Items / Order",  str(kpi["avg_items_order"])),
        _kpi_card("Refund Rate",        f"{kpi['refund_rate']}%"),
        _kpi_card("Top Category",       kpi["top_category"]),
    ]
    console.print(Columns(cards, equal=True, expand=True))
    console.print()

    if kpi["monthly_labels"]:
        charts.revenue_trend(kpi["monthly_labels"], kpi["monthly_revenue"])

    cat_df = kpis.by_category(df)
    if not cat_df.empty:
        console.print()
        charts.category_bar(cat_df["category"].tolist(), cat_df["revenue"].tolist())


@app.command()
def rfm(
    file:    Path         = FILE_OPTION,
    top:     int          = typer.Option(20,  "--top",     "-n", help="Show top N customers"),
    segment: Optional[str]= typer.Option(None,"--segment", "-s", help="Filter to a specific segment"),
):
    """RFM customer segmentation — Champions, Loyal, At Risk, and more."""
    df     = loader.load(file)
    scored = rfm_mod.score(df)
    summ   = rfm_mod.segment_summary(scored)

    console.print()
    console.rule("[bold cyan]RFM Segmentation[/bold cyan]")
    console.print()

    # Segment overview table
    seg_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    seg_table.add_column("Segment",       style="bold")
    seg_table.add_column("Customers",     justify="right")
    seg_table.add_column("% of Base",     justify="right")
    seg_table.add_column("Avg Revenue",   justify="right")
    seg_table.add_column("Avg Orders",    justify="right")
    seg_table.add_column("Avg Days Since",justify="right")

    for _, row in summ.iterrows():
        color = rfm_mod.SEGMENT_COLORS.get(row["segment"], "white")
        seg_table.add_row(
            f"[{color}]{row['segment']}[/{color}]",
            str(int(row["customers"])),
            f"{row['pct']}%",
            _fmt_money(row["avg_monetary"]),
            str(row["avg_frequency"]),
            f"{int(row['avg_recency'])}d",
        )

    console.print(seg_table)
    console.print()

    # Customer-level table
    display = scored.copy()
    if segment:
        seg_lower = segment.lower()
        display = display[display["segment"].str.lower().str.contains(seg_lower)]
        if display.empty:
            console.print(f"[yellow]No customers in segment matching '{segment}'[/yellow]")
            return

    display = display.head(top)
    cust_table = Table(
        title=f"Top {len(display)} Customers" + (f" — {segment}" if segment else ""),
        box=box.SIMPLE_HEAVY, header_style="bold cyan",
    )
    cust_table.add_column("Customer ID",  style="dim")
    cust_table.add_column("Segment",      style="bold")
    cust_table.add_column("R",  justify="center")
    cust_table.add_column("F",  justify="center")
    cust_table.add_column("M",  justify="center")
    cust_table.add_column("Score", justify="center")
    cust_table.add_column("Revenue", justify="right")
    cust_table.add_column("Orders",  justify="right")
    cust_table.add_column("Last Order", justify="right")

    for _, row in display.iterrows():
        color = rfm_mod.SEGMENT_COLORS.get(row["segment"], "white")
        cust_table.add_row(
            row["customer_id"],
            f"[{color}]{row['segment']}[/{color}]",
            str(int(row["R"])),
            str(int(row["F"])),
            str(int(row["M"])),
            str(int(row["rfm_score"])),
            _fmt_money(row["monetary"]),
            str(int(row["frequency"])),
            str(row["last_order"].date()),
        )

    console.print(cust_table)


@app.command()
def cohorts(file: Path = FILE_OPTION):
    """Monthly customer retention cohort table."""
    df    = loader.load(file)
    pivot = cohorts_mod.build(df)

    # Keep only M+0 to M+11 to keep the table readable
    cols = [c for c in pivot.columns if int(c.split("+")[1]) <= 11]
    pivot = pivot[cols]

    console.print()
    console.rule("[bold cyan]Customer Retention Cohorts[/bold cyan]")
    console.print()
    console.print("[dim]Cells show % of cohort who purchased again in that month. M+0 = 100% by definition.[/dim]")
    console.print()

    table = Table(box=box.SIMPLE, header_style="bold cyan", show_lines=False)
    table.add_column("Cohort", style="bold")
    for col in pivot.columns:
        table.add_column(col, justify="right")

    for cohort, row in pivot.iterrows():
        cells = []
        for col in pivot.columns:
            val = row[col]
            if col == "M+0":
                cells.append("[bold]100%[/bold]")
            elif pd.isna(val):
                cells.append("[dim]·[/dim]")
            else:
                color = cohorts_mod.retention_color(val)
                cells.append(f"[{color}]{val:.0f}%[/{color}]")
        table.add_row(str(cohort), *cells)

    console.print(table)
    console.print()
    console.print("[dim]Color guide: [green]≥20%[/green]  [yellow]≥10%[/yellow]  [red]<10%[/red][/dim]")

import pandas as pd  # noqa: E402 — needed for cohorts NaN check


@app.command("top-products")
def top_products(
    file: Path = FILE_OPTION,
    n:    int  = typer.Option(10, "--top", "-n", help="Number of products to show"),
):
    """Best and worst performing products by revenue and volume."""
    df = loader.load(file)
    c  = loader.completed(df)

    prod = (
        c.groupby(["product", "category"])
        .agg(
            orders=("order_id",   "count"),
            revenue=("revenue",   "sum"),
            units=("quantity",    "sum"),
            avg_price=("unit_price", "mean"),
            avg_discount=("discount_pct", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    console.print()
    console.rule("[bold cyan]Product Performance[/bold cyan]")
    console.print()

    # Chart: top N by revenue
    top_n = prod.head(n)
    charts.product_bar(top_n["product"].tolist(), top_n["revenue"].tolist())
    console.print()

    def _make_table(title: str, data: pd.DataFrame, title_color: str) -> Table:
        t = Table(title=f"[{title_color}]{title}[/{title_color}]",
                  box=box.ROUNDED, header_style="bold cyan")
        t.add_column("Product")
        t.add_column("Category",    style="dim")
        t.add_column("Revenue",     justify="right")
        t.add_column("Orders",      justify="right")
        t.add_column("Units",       justify="right")
        t.add_column("Avg Price",   justify="right")
        t.add_column("Avg Disc",    justify="right")
        for _, row in data.iterrows():
            t.add_row(
                row["product"], row["category"],
                _fmt_money(row["revenue"]),
                str(int(row["orders"])),
                str(int(row["units"])),
                _fmt_money(row["avg_price"]),
                f"{row['avg_discount']*100:.0f}%",
            )
        return t

    console.print(Columns([
        _make_table(f"Top {n} Products",    prod.head(n),         "green"),
        _make_table(f"Bottom {n} Products", prod.tail(n)[::-1],   "red"),
    ], equal=True, expand=True))


@app.command()
def clv(file: Path = FILE_OPTION):
    """Customer lifetime value — distribution, percentiles, and top spenders."""
    df     = loader.load(file)
    scored = rfm_mod.score(df)

    total_days = (df["order_date"].max() - df["order_date"].min()).days or 1
    years      = total_days / 365.25

    # Simple CLV: monetary already = total spend over the dataset window
    scored["clv"] = scored["monetary"]

    console.print()
    console.rule("[bold cyan]Customer Lifetime Value[/bold cyan]")
    console.print()

    values = scored["clv"].tolist()
    charts.clv_histogram(values)
    console.print()

    # Percentile table
    import numpy as np
    pcts   = [10, 25, 50, 75, 90, 95, 99]
    ptable = Table(title="CLV Percentiles", box=box.ROUNDED, header_style="bold cyan")
    ptable.add_column("Percentile", justify="center")
    ptable.add_column("CLV",        justify="right")
    for p in pcts:
        ptable.add_row(f"P{p}", _fmt_money(float(np.percentile(values, p))))

    # Top spenders
    stop = Table(title="Top 10 Spenders", box=box.ROUNDED, header_style="bold cyan")
    stop.add_column("Customer",  style="dim")
    stop.add_column("Segment",   style="bold")
    stop.add_column("CLV",       justify="right")
    stop.add_column("Orders",    justify="right")

    for _, row in scored.nlargest(10, "clv").iterrows():
        color = rfm_mod.SEGMENT_COLORS.get(row["segment"], "white")
        stop.add_row(
            row["customer_id"],
            f"[{color}]{row['segment']}[/{color}]",
            _fmt_money(row["clv"]),
            str(int(row["frequency"])),
        )

    console.print(Columns([ptable, stop], equal=True, expand=True))
    console.print()

    avg  = float(scored["clv"].mean())
    med  = float(scored["clv"].median())
    best = float(scored["clv"].max())
    from rich.panel import Panel
    console.print(
        Panel(
            f"Mean CLV [bold]{_fmt_money(avg)}[/bold]  ·  "
            f"Median [bold]{_fmt_money(med)}[/bold]  ·  "
            f"Highest [bold]{_fmt_money(best)}[/bold]  ·  "
            f"Dataset window [bold]{years:.1f} yrs[/bold]",
            border_style="cyan",
        )
    )
