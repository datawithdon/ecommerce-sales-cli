# esales — E-commerce Sales Intelligence CLI

A terminal-native analytics tool that turns a orders CSV into actionable sales intelligence — no browser, no dashboards, just your shell.

Built with [Typer](https://typer.tiangolo.com), [Rich](https://rich.readthedocs.io), [Plotext](https://github.com/piccolomo/plotext), and pandas.

## Commands

| Command | What it does |
|---------|-------------|
| `esales summary` | Revenue KPIs + monthly trend + category breakdown |
| `esales rfm` | RFM segmentation — Champions, Loyal, At Risk, Lost… |
| `esales cohorts` | Monthly customer retention cohort table |
| `esales top-products` | Best and worst SKUs by revenue & volume |
| `esales clv` | Customer lifetime value distribution + top spenders |

Every command accepts `--file / -f` to point at your own CSV (defaults to the included sample).

## Quick Start

```bash
git clone https://github.com/datawithdon/ecommerce-sales-cli.git
cd ecommerce-sales-cli
pip install -r requirements.txt
pip install -e .

# Run with sample data (included)
esales summary
esales rfm
esales cohorts
esales top-products
esales clv

# Use your own data
esales summary --file path/to/orders.csv
esales rfm --file path/to/orders.csv --segment "At Risk"
esales top-products --file path/to/orders.csv --top 15
```

Alternatively without installing:

```bash
python -m esales summary
```

## CSV Format

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | string | Unique order ID |
| `customer_id` | string | Customer identifier |
| `product` | string | Product name |
| `category` | string | Product category |
| `order_date` | date | Order date (YYYY-MM-DD) |
| `quantity` | int | Units ordered |
| `unit_price` | float | Price per unit |
| `discount_pct` | float | Discount as decimal (0.10 = 10%) |
| `revenue` | float | Actual revenue collected |
| `status` | string | `completed` or `refunded` |

## Regenerate Sample Data

```bash
python generate_sample_data.py
# → data/sample_sales.csv  (2,000+ orders, 320 customers, 25 products, 2 years)
```

## RFM Segments

| Segment | Description |
|---------|-------------|
| Champions | High recency, frequency, and monetary value |
| Loyal | Regular buyers with strong spend |
| Potential Loyalists | Recent shoppers, not yet frequent |
| New Customers | Very recent, first-time buyers |
| At Risk | Used to buy often — going quiet |
| Hibernating | Low across all three dimensions |
| Lost | Haven't bought in a long time |

## Tech Stack

- [Typer](https://typer.tiangolo.com) — CLI framework
- [Rich](https://rich.readthedocs.io) — terminal formatting, tables, panels
- [Plotext](https://github.com/piccolomo/plotext) — ASCII charts in the terminal
- [pandas](https://pandas.pydata.org) — data wrangling

## License

MIT
