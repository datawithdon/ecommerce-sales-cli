"""Plotext chart helpers — each function calls plt.show() directly."""
import plotext as plt
import shutil


def _width() -> int:
    return shutil.get_terminal_size((100, 24)).columns - 4


def _reset(height=16):
    plt.clf()
    plt.plotsize(_width(), height)
    plt.theme("dark")


def revenue_trend(labels: list, values: list):
    _reset(14)
    x = list(range(len(values)))
    plt.plot(x, values, marker="braille")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")
    step = max(1, len(labels) // 8)
    plt.xticks(x[::step], labels[::step])
    plt.show()


def category_bar(categories: list, revenues: list):
    _reset(14)
    plt.bar(categories, revenues, orientation="horizontal")
    plt.title("Revenue by Category")
    plt.show()


def clv_histogram(values: list):
    _reset(14)
    plt.hist(values, bins=20)
    plt.title("Customer Lifetime Value Distribution")
    plt.xlabel("CLV ($)")
    plt.ylabel("Customers")
    plt.show()


def product_bar(products: list, revenues: list):
    _reset(18)
    plt.bar(products, revenues, orientation="horizontal")
    plt.title("Revenue by Product")
    plt.show()
