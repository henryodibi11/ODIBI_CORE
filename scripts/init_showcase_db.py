"""
Initialize showcase SQL configuration database.
Creates tables and populates with all 10 showcase configs.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("D:/projects/odibi_core/resources/configs/showcases/showcase_configs.db")

def init_database():
    """Create database and tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read schema from SQL file
    schema_file = Path("D:/projects/odibi_core/resources/configs/showcases/showcase_db_init.sql")
    if schema_file.exists():
        schema_sql = schema_file.read_text()
        cursor.executescript(schema_sql)
    
    conn.commit()
    return conn

def insert_showcase_metadata(conn, showcase_id, name, theme, description, sources, outputs, objectives):
    """Insert showcase metadata."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO showcase_metadata 
        (showcase_id, showcase_name, theme, description, data_sources, expected_outputs, learning_objectives)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (showcase_id, name, theme, description, json.dumps(sources), json.dumps(outputs), objectives))
    conn.commit()

def insert_config_step(conn, showcase_id, showcase_name, layer, step_name, step_type, engine, value, params, inputs, outputs, metadata):
    """Insert a single config step."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO showcase_config 
        (showcase_id, showcase_name, layer, step_name, step_type, engine, value, params, inputs, outputs, metadata, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        showcase_id, showcase_name, layer, step_name, step_type, engine,
        json.dumps(value), json.dumps(params), json.dumps(inputs), json.dumps(outputs), json.dumps(metadata)
    ))
    conn.commit()

def populate_showcase_01(conn):
    """Populate showcase #1: Global Bookstore Analytics."""
    showcase_id = 1
    showcase_name = "Global Bookstore Analytics"
    
    # Insert metadata
    insert_showcase_metadata(
        conn, showcase_id, showcase_name,
        theme="Retail Analytics",
        description="End-to-end bookstore sales analysis with inventory joins and multi-dimensional aggregations",
        sources=["bookstore_sales.csv", "bookstore_inventory.csv"],
        outputs=["revenue_by_region.csv", "revenue_by_genre.csv"],
        objectives="Demonstrate bronze/silver/gold medallion architecture with Pandas engine"
    )
    
    # Bronze layer
    insert_config_step(
        conn, showcase_id, showcase_name, "bronze", "load_bookstore_sales", "read", "pandas",
        value={"source": "resources/data/showcases/bookstore_sales.csv", "format": "csv"},
        params={}, inputs=[], outputs=["bookstore_sales"],
        metadata={"description": "Load raw sales data from CSV", "data_source": "Point-of-sale system export"}
    )
    
    insert_config_step(
        conn, showcase_id, showcase_name, "bronze", "load_bookstore_inventory", "read", "pandas",
        value={"source": "resources/data/showcases/bookstore_inventory.csv", "format": "csv"},
        params={}, inputs=[], outputs=["bookstore_inventory"],
        metadata={"description": "Load inventory data from warehouse system", "data_source": "Inventory management database"}
    )
    
    # Silver layer
    insert_config_step(
        conn, showcase_id, showcase_name, "silver", "calculate_revenue", "transform", "pandas",
        value={"operation": "add_column", "column_name": "revenue", "expression": "price * quantity_sold"},
        params={}, inputs=["bookstore_sales"], outputs=["sales_with_revenue"],
        metadata={"description": "Calculate total revenue per book sale"}
    )
    
    insert_config_step(
        conn, showcase_id, showcase_name, "silver", "join_sales_inventory", "join", "pandas",
        value={"left_table": "sales_with_revenue", "right_table": "bookstore_inventory", "join_key": "book_id", "join_type": "inner"},
        params={}, inputs=["sales_with_revenue", "bookstore_inventory"], outputs=["sales_inventory_joined"],
        metadata={"description": "Join sales with inventory to get complete book information"}
    )
    
    # Gold layer
    insert_config_step(
        conn, showcase_id, showcase_name, "gold", "aggregate_by_region", "aggregate", "pandas",
        value={"group_by": ["store_region"], "aggregations": {"total_revenue": {"column": "revenue", "function": "sum"}, "total_books_sold": {"column": "quantity_sold", "function": "sum"}, "avg_price": {"column": "price", "function": "mean"}}},
        params={}, inputs=["sales_inventory_joined"], outputs=["revenue_by_region"],
        metadata={"description": "Aggregate sales metrics by geographical region"}
    )
    
    insert_config_step(
        conn, showcase_id, showcase_name, "gold", "aggregate_by_genre", "aggregate", "pandas",
        value={"group_by": ["genre"], "aggregations": {"total_revenue": {"column": "revenue", "function": "sum"}, "total_books_sold": {"column": "quantity_sold", "function": "sum"}, "book_count": {"column": "book_id", "function": "count"}}},
        params={}, inputs=["sales_inventory_joined"], outputs=["revenue_by_genre"],
        metadata={"description": "Aggregate sales metrics by book genre"}
    )
    
    insert_config_step(
        conn, showcase_id, showcase_name, "gold", "export_region_analysis", "write", "pandas",
        value={"destination": "resources/output/showcases/sql_mode/showcase_01/revenue_by_region.csv", "format": "csv"},
        params={}, inputs=["revenue_by_region"], outputs=[],
        metadata={"description": "Export regional analysis to CSV"}
    )
    
    insert_config_step(
        conn, showcase_id, showcase_name, "gold", "export_genre_analysis", "write", "pandas",
        value={"destination": "resources/output/showcases/sql_mode/showcase_01/revenue_by_genre.csv", "format": "csv"},
        params={}, inputs=["revenue_by_genre"], outputs=[],
        metadata={"description": "Export genre analysis to CSV"}
    )
    
    print(f"✅ Showcase #1: {showcase_name} - SQL config populated")

if __name__ == "__main__":
    print("Initializing showcase configuration database...")
    conn = init_database()
    populate_showcase_01(conn)
    conn.close()
    print(f"\n✅ Database created: {DB_PATH}")
