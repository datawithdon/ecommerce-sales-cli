import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(7)
np.random.seed(7)

PRODUCTS = [
    ("Wireless Headphones",  "Electronics",   89.99),
    ("USB-C Hub",            "Electronics",   34.99),
    ("Mechanical Keyboard",  "Electronics",  119.99),
    ("Webcam 1080p",         "Electronics",   59.99),
    ("Monitor Stand",        "Electronics",   44.99),
    ("Running Shoes",        "Apparel",        79.99),
    ("Yoga Mat",             "Apparel",        29.99),
    ("Winter Jacket",        "Apparel",       149.99),
    ("Compression Socks",    "Apparel",        14.99),
    ("Baseball Cap",         "Apparel",        24.99),
    ("Coffee Maker",         "Home & Kitchen", 69.99),
    ("Air Purifier",         "Home & Kitchen",129.99),
    ("Blender",              "Home & Kitchen", 54.99),
    ("Cutting Board Set",    "Home & Kitchen", 39.99),
    ("Knife Sharpener",      "Home & Kitchen", 24.99),
    ("Protein Powder",       "Health",         49.99),
    ("Resistance Bands",     "Health",         19.99),
    ("Foam Roller",          "Health",         34.99),
    ("Multivitamin 90ct",    "Health",         22.99),
    ("Sleep Mask",           "Health",          9.99),
    ("Notebook A5",          "Stationery",      8.99),
    ("Ballpoint Pens 12pk",  "Stationery",     11.99),
    ("Desk Organizer",       "Stationery",     27.99),
    ("Sticky Notes 400ct",   "Stationery",      6.99),
    ("Whiteboard Markers",   "Stationery",     13.99),
]

COUNTRIES = ["US", "US", "US", "US", "UK", "UK", "CA", "CA", "AU", "DE"]

START = datetime(2023, 1, 1)
END   = datetime(2024, 12, 31)

def rand_date(start=START, end=END):
    delta = (end - start).days
    # Q4 seasonal boost
    d = start + timedelta(days=random.randint(0, delta))
    if d.month in (10, 11, 12) and random.random() < 0.3:
        d = start + timedelta(days=random.randint(0, delta))  # resample → more Q4
    return d

def build_customers(n=320):
    tiers = (
        [("champion", 20, 30)] * int(n * 0.15) +
        [("loyal",     8, 18)] * int(n * 0.30) +
        [("occasional",2,  5)] * int(n * 0.35) +
        [("one_time",  1,  2)] * int(n * 0.20)
    )
    return [{"id": f"CUST-{1000+i}", "country": random.choice(COUNTRIES),
             "tier": t, "min_orders": mn, "max_orders": mx}
            for i, (t, mn, mx) in enumerate(tiers)]


def generate():
    customers = build_customers()
    rows = []
    order_num = 10000

    for cust in customers:
        n_orders = random.randint(cust["min_orders"], cust["max_orders"])
        dates = sorted(rand_date() for _ in range(n_orders))
        favorite_cat = random.choice([p[1] for p in PRODUCTS])

        for d in dates:
            # bias toward favourite category
            pool = [p for p in PRODUCTS if p[1] == favorite_cat] * 3 + PRODUCTS
            product, category, base_price = random.choice(pool)
            qty = random.randint(1, 4)
            discount = round(random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20]), 2)
            revenue = round(qty * base_price * (1 - discount), 2)
            status = "refunded" if random.random() < 0.09 else "completed"

            rows.append({
                "order_id":    f"ORD-{order_num}",
                "customer_id": cust["id"],
                "country":     cust["country"],
                "product":     product,
                "category":    category,
                "order_date":  d.date(),
                "quantity":    qty,
                "unit_price":  base_price,
                "discount_pct":discount,
                "revenue":     revenue if status == "completed" else 0.0,
                "status":      status,
            })
            order_num += 1

    df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate()
    df.to_csv("data/sample_sales.csv", index=False)
    print(f"Generated {len(df)} orders across {df['customer_id'].nunique()} customers → data/sample_sales.csv")
