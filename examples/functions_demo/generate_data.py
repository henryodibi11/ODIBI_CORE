"""
Generate synthetic data for functions demo.

Creates clean, realistic datasets for demonstrating ODIBI CORE functions
across both Pandas and Spark engines.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def generate_users_data(n_rows=100):
    """Generate synthetic user data."""
    np.random.seed(42)
    
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
    statuses = ["active", "inactive", "pending", "suspended"]
    
    data = {
        "user_id": range(1, n_rows + 1),
        "first_name": np.random.choice(first_names, n_rows),
        "last_name": np.random.choice(last_names, n_rows),
        "email": [f"user{i}@example.com" for i in range(1, n_rows + 1)],
        "signup_date": pd.date_range("2023-01-01", periods=n_rows, freq="D"),
        "status": np.random.choice(statuses, n_rows, p=[0.7, 0.15, 0.1, 0.05]),
        "age": np.random.randint(18, 70, n_rows),
        "score": np.random.normal(75, 15, n_rows).round(2)
    }
    
    return pd.DataFrame(data)


def generate_orders_data(n_rows=200):
    """Generate synthetic order data."""
    np.random.seed(43)
    
    products = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse"]
    
    data = {
        "order_id": range(1, n_rows + 1),
        "user_id": np.random.randint(1, 101, n_rows),
        "product": np.random.choice(products, n_rows),
        "quantity": np.random.randint(1, 5, n_rows),
        "price": np.random.choice([299.99, 599.99, 899.99, 1299.99, 49.99, 29.99], n_rows),
        "order_date": pd.date_range("2023-01-01", periods=n_rows, freq="12h"),
        "shipped": np.random.choice([True, False], n_rows, p=[0.8, 0.2])
    }
    
    df = pd.DataFrame(data)
    df["total"] = df["quantity"] * df["price"]
    
    return df


def generate_messy_data(n_rows=50):
    """Generate messy data for cleaning demo."""
    np.random.seed(44)
    
    # Intentionally messy data
    data = {
        "ID": range(1, n_rows + 1),
        "  ProductName  ": [
            "  Widget A  ", "WIDGET b", "widget_C", "  Product X", "product y  "
        ] * 10,
        "StatusFlag": ["yes", "no", "Y", "N", "1", "0", "true", "false", "Yes", "No"] * 5,
        "CreatedDate": [
            "2023-01-15", "2023/02/20", "15-03-2023", "2023-04-01", "05/05/2023"
        ] * 10,
        "Value": ["100", "200.5", "invalid", "300", "N/A"] * 10,
        "Notes": [None, "some text", "", "N/A", "null"] * 10
    }
    
    return pd.DataFrame(data)


def generate_timeseries_data(n_rows=100):
    """Generate time series data for datetime and math demos."""
    np.random.seed(45)
    
    dates = pd.date_range("2023-01-01", periods=n_rows, freq="D")
    
    # Trend + seasonality + noise
    trend = np.linspace(100, 150, n_rows)
    seasonality = 10 * np.sin(np.linspace(0, 4*np.pi, n_rows))
    noise = np.random.normal(0, 5, n_rows)
    
    data = {
        "date": dates,
        "value": trend + seasonality + noise,
        "category": np.random.choice(["A", "B", "C"], n_rows),
        "temperature": np.random.normal(20, 5, n_rows).round(1),
        "humidity": np.random.uniform(30, 80, n_rows).round(1)
    }
    
    return pd.DataFrame(data)


def main():
    """Generate all datasets and save to CSV."""
    output_dir = Path(__file__).parent
    
    print("Generating synthetic data...")
    
    # Generate datasets
    users = generate_users_data(100)
    orders = generate_orders_data(200)
    messy = generate_messy_data(50)
    timeseries = generate_timeseries_data(100)
    
    # Save to CSV
    users.to_csv(output_dir / "users.csv", index=False)
    orders.to_csv(output_dir / "orders.csv", index=False)
    messy.to_csv(output_dir / "messy_data.csv", index=False)
    timeseries.to_csv(output_dir / "timeseries.csv", index=False)
    
    print(f"Generated 4 datasets:")
    print(f"   - users.csv ({len(users)} rows)")
    print(f"   - orders.csv ({len(orders)} rows)")
    print(f"   - messy_data.csv ({len(messy)} rows)")
    print(f"   - timeseries.csv ({len(timeseries)} rows)")
    print(f"\nSaved to: {output_dir}")


if __name__ == "__main__":
    main()
