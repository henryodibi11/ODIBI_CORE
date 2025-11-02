"""
Demo Project Page - Interactive medallion architecture pipeline
"""

import streamlit as st
import sys
from pathlib import Path
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box, info_box
from odibi_core.learnodibi_ui.components import data_preview, metrics_display
from odibi_core.learnodibi_ui.utils import (
    create_sample_data, add_to_history, format_execution_time
)

apply_theme()

# Initialize session state
if "demo_data" not in st.session_state:
    st.session_state.demo_data = {
        "bronze": None,
        "silver": None,
        "gold": None
    }

if "demo_metrics" not in st.session_state:
    st.session_state.demo_metrics = {
        "bronze": {},
        "silver": {},
        "gold": {}
    }

# Header
st.title("⚡ Interactive Demo Project")
st.markdown("Experience a complete data pipeline with Bronze → Silver → Gold layers")

st.markdown("---")

# Pipeline overview
st.markdown("### 📊 Pipeline Architecture")

col1, col2, col3 = st.columns(3)

with col1:
    bronze_status = "✅" if st.session_state.demo_data["bronze"] is not None else "⏸️"
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; text-align: center;'>
        <h2 style='color: #CD7F32; margin: 0;'>{bronze_status} Bronze</h2>
        <p style='color: {COLORS['text_secondary']};'>Raw Data Ingestion</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    silver_status = "✅" if st.session_state.demo_data["silver"] is not None else "⏸️"
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; text-align: center;'>
        <h2 style='color: #C0C0C0; margin: 0;'>{silver_status} Silver</h2>
        <p style='color: {COLORS['text_secondary']};'>Cleaned & Validated</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    gold_status = "✅" if st.session_state.demo_data["gold"] is not None else "⏸️"
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; text-align: center;'>
        <h2 style='color: #FFD700; margin: 0;'>{gold_status} Gold</h2>
        <p style='color: {COLORS['text_secondary']};'>Analytics Ready</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Layer tabs
tabs = st.tabs(["🥉 Bronze Layer", "🥈 Silver Layer", "🥇 Gold Layer", "📈 Analytics"])

# BRONZE LAYER
with tabs[0]:
    st.markdown("### 🥉 Bronze Layer - Raw Data Ingestion")
    
    info_box("The Bronze layer ingests raw data from various sources without transformation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Configuration")
        
        # Source configuration
        n_rows = st.slider("Number of rows to ingest", 100, 10000, 1000, step=100)
        
        source_config = {
            "source_type": "sensor_data",
            "n_rows": n_rows,
            "include_nulls": st.checkbox("Include some null values", value=True),
            "include_outliers": st.checkbox("Include outliers", value=True)
        }
        
        st.json(source_config)
    
    with col2:
        st.markdown("#### Actions")
        
        if st.button("📥 Ingest Data", type="primary", use_container_width=True, key="ingest_bronze"):
            with st.spinner("Ingesting data..."):
                start_time = time.time()
                
                # Create sample data
                df = create_sample_data(n_rows)
                
                # Add some nulls if requested
                if source_config["include_nulls"]:
                    null_indices = np.random.choice(len(df), size=int(len(df) * 0.05), replace=False)
                    df.loc[null_indices, 'temperature'] = None
                
                # Add outliers if requested
                if source_config["include_outliers"]:
                    outlier_indices = np.random.choice(len(df), size=int(len(df) * 0.02), replace=False)
                    df.loc[outlier_indices, 'temperature'] = df['temperature'].mean() + 3 * df['temperature'].std()
                
                execution_time = time.time() - start_time
                
                # Store in session state
                st.session_state.demo_data["bronze"] = df
                st.session_state.demo_metrics["bronze"] = {
                    "execution_time": execution_time,
                    "rows_processed": len(df),
                    "success": True,
                    "errors": 0
                }
                
                add_to_history("bronze_ingestion", st.session_state.demo_metrics["bronze"])
                
                success_box(f"Ingested {len(df):,} rows in {format_execution_time(execution_time)}")
        
        if st.button("🔄 Reset Bronze", use_container_width=True, key="reset_bronze"):
            st.session_state.demo_data["bronze"] = None
            st.session_state.demo_metrics["bronze"] = {}
            st.rerun()
    
    # Display data and metrics
    if st.session_state.demo_data["bronze"] is not None:
        st.markdown("---")
        
        # Metrics
        if st.session_state.demo_metrics["bronze"]:
            metrics_display(st.session_state.demo_metrics["bronze"], title="Bronze Layer Metrics", key="bronze_metrics")
        
        # Data preview
        data_preview(st.session_state.demo_data["bronze"], title="Bronze Layer Data", key="bronze_data")
    else:
        st.info("👆 Click 'Ingest Data' to load the Bronze layer")

# SILVER LAYER
with tabs[1]:
    st.markdown("### 🥈 Silver Layer - Data Cleaning & Validation")
    
    info_box("The Silver layer cleans and validates data from Bronze")
    
    if st.session_state.demo_data["bronze"] is None:
        st.warning("⚠️ Please run the Bronze layer first")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Transformation Configuration")
            
            transformations = {
                "fill_nulls": st.checkbox("Fill null values", value=True),
                "remove_outliers": st.checkbox("Remove outliers (3σ)", value=True),
                "validate_ranges": st.checkbox("Validate value ranges", value=True),
                "add_derived_columns": st.checkbox("Add derived columns", value=True)
            }
            
            st.json(transformations)
        
        with col2:
            st.markdown("#### Actions")
            
            if st.button("⚙️ Transform Data", type="primary", use_container_width=True, key="transform_silver"):
                with st.spinner("Transforming data..."):
                    start_time = time.time()
                    
                    df = st.session_state.demo_data["bronze"].copy()
                    
                    # Apply transformations
                    if transformations["fill_nulls"]:
                        # Fill numeric columns with their median
                        for col in df.select_dtypes(include=[np.number]).columns:
                            df[col] = df[col].fillna(df[col].median())
                    
                    if transformations["remove_outliers"]:
                        for col in ['temperature', 'humidity', 'pressure']:
                            mean = df[col].mean()
                            std = df[col].std()
                            df = df[(df[col] >= mean - 3*std) & (df[col] <= mean + 3*std)]
                    
                    if transformations["validate_ranges"]:
                        df = df[
                            (df['temperature'] >= -50) & (df['temperature'] <= 60) &
                            (df['humidity'] >= 0) & (df['humidity'] <= 100) &
                            (df['pressure'] >= 900) & (df['pressure'] <= 1100)
                        ]
                    
                    if transformations["add_derived_columns"]:
                        df['date'] = df['timestamp'].dt.date
                        df['hour'] = df['timestamp'].dt.hour
                        df['temp_category'] = pd.cut(
                            df['temperature'], 
                            bins=[-np.inf, 15, 25, np.inf],
                            labels=['Cold', 'Moderate', 'Hot']
                        )
                    
                    execution_time = time.time() - start_time
                    
                    # Store in session state
                    st.session_state.demo_data["silver"] = df
                    st.session_state.demo_metrics["silver"] = {
                        "execution_time": execution_time,
                        "rows_processed": len(df),
                        "success": True,
                        "errors": 0,
                        "rows_removed": len(st.session_state.demo_data["bronze"]) - len(df)
                    }
                    
                    add_to_history("silver_transformation", st.session_state.demo_metrics["silver"])
                    
                    success_box(f"Transformed {len(df):,} rows in {format_execution_time(execution_time)}")
            
            if st.button("🔄 Reset Silver", use_container_width=True, key="reset_silver"):
                st.session_state.demo_data["silver"] = None
                st.session_state.demo_metrics["silver"] = {}
                st.rerun()
        
        # Display data and metrics
        if st.session_state.demo_data["silver"] is not None:
            st.markdown("---")
            
            # Metrics
            if st.session_state.demo_metrics["silver"]:
                metrics_display(st.session_state.demo_metrics["silver"], title="Silver Layer Metrics", key="silver_metrics")
            
            # Data preview
            data_preview(st.session_state.demo_data["silver"], title="Silver Layer Data", key="silver_data")
        else:
            st.info("👆 Click 'Transform Data' to create the Silver layer")

# GOLD LAYER
with tabs[2]:
    st.markdown("### 🥇 Gold Layer - Analytics Aggregation")
    
    info_box("The Gold layer creates business-ready aggregated views")
    
    if st.session_state.demo_data["silver"] is None:
        st.warning("⚠️ Please run the Silver layer first")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Aggregation Configuration")
            
            agg_config = {
                "group_by": st.multiselect(
                    "Group by",
                    ["sensor_id", "date", "hour", "temp_category"],
                    default=["sensor_id", "date"]
                ),
                "aggregations": st.multiselect(
                    "Aggregations",
                    ["mean", "sum", "min", "max", "count"],
                    default=["mean", "count"]
                )
            }
            
            st.json(agg_config)
        
        with col2:
            st.markdown("#### Actions")
            
            if st.button("📊 Aggregate Data", type="primary", use_container_width=True, key="aggregate_gold"):
                if not agg_config["group_by"]:
                    st.error("Please select at least one group by column")
                else:
                    with st.spinner("Aggregating data..."):
                        start_time = time.time()
                        
                        df = st.session_state.demo_data["silver"]
                        
                        # Perform aggregation
                        agg_dict = {}
                        for col in ['temperature', 'humidity', 'pressure', 'energy_kwh']:
                            agg_dict[col] = agg_config["aggregations"]
                        
                        gold_df = df.groupby(agg_config["group_by"]).agg(agg_dict).round(2)
                        gold_df = gold_df.reset_index()
                        
                        # Flatten column names
                        gold_df.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                          for col in gold_df.columns.values]
                        
                        execution_time = time.time() - start_time
                        
                        # Store in session state
                        st.session_state.demo_data["gold"] = gold_df
                        st.session_state.demo_metrics["gold"] = {
                            "execution_time": execution_time,
                            "rows_processed": len(gold_df),
                            "success": True,
                            "errors": 0,
                            "aggregation_ratio": len(df) / len(gold_df) if len(gold_df) > 0 else 0
                        }
                        
                        add_to_history("gold_aggregation", st.session_state.demo_metrics["gold"])
                        
                        success_box(f"Aggregated to {len(gold_df):,} rows in {format_execution_time(execution_time)}")
            
            if st.button("🔄 Reset Gold", use_container_width=True, key="reset_gold"):
                st.session_state.demo_data["gold"] = None
                st.session_state.demo_metrics["gold"] = {}
                st.rerun()
        
        # Display data and metrics
        if st.session_state.demo_data["gold"] is not None:
            st.markdown("---")
            
            # Metrics
            if st.session_state.demo_metrics["gold"]:
                metrics_display(st.session_state.demo_metrics["gold"], title="Gold Layer Metrics", key="gold_metrics")
            
            # Data preview
            data_preview(st.session_state.demo_data["gold"], title="Gold Layer Data", key="gold_data")
        else:
            st.info("👆 Click 'Aggregate Data' to create the Gold layer")

# ANALYTICS
with tabs[3]:
    st.markdown("### 📈 Analytics Dashboard")
    
    if st.session_state.demo_data["gold"] is None:
        st.warning("⚠️ Please complete the Gold layer to view analytics")
    else:
        silver_df = st.session_state.demo_data["silver"]
        gold_df = st.session_state.demo_data["gold"]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records (Silver)", f"{len(silver_df):,}")
        with col2:
            st.metric("Aggregated Groups (Gold)", f"{len(gold_df):,}")
        with col3:
            avg_temp = silver_df['temperature'].mean()
            st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
        with col4:
            total_energy = silver_df['energy_kwh'].sum()
            st.metric("Total Energy", f"{total_energy:.1f} kWh")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature distribution
            fig = px.histogram(
                silver_df,
                x='temperature',
                nbins=30,
                title="Temperature Distribution",
                color_discrete_sequence=[COLORS['primary']]
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Energy by sensor
            if 'sensor_id' in silver_df.columns:
                energy_by_sensor = silver_df.groupby('sensor_id')['energy_kwh'].sum()
                fig = px.bar(
                    x=energy_by_sensor.index,
                    y=energy_by_sensor.values,
                    title="Energy Consumption by Sensor",
                    labels={'x': 'Sensor ID', 'y': 'Energy (kWh)'},
                    color_discrete_sequence=[COLORS['secondary']]
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Temperature over time
            fig = px.line(
                silver_df.head(200),
                x='timestamp',
                y='temperature',
                title="Temperature Over Time",
                color_discrete_sequence=[COLORS['info']]
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation matrix
            corr_cols = ['temperature', 'humidity', 'pressure', 'energy_kwh']
            corr = silver_df[corr_cols].corr()
            
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix",
                color_continuous_scale="RdBu_r"
            )
            st.plotly_chart(fig, use_container_width=True)

# Pipeline summary
st.markdown("---")
st.markdown("### 📋 Pipeline Summary")

# Check if all demo data exists (not None)
if all(v is not None for v in st.session_state.demo_data.values()):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px;'>
            <h4 style='color: #CD7F32;'>🥉 Bronze</h4>
            <p>Rows: {len(st.session_state.demo_data['bronze']):,}</p>
            <p>Time: {format_execution_time(st.session_state.demo_metrics['bronze'].get('execution_time', 0))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px;'>
            <h4 style='color: #C0C0C0;'>🥈 Silver</h4>
            <p>Rows: {len(st.session_state.demo_data['silver']):,}</p>
            <p>Time: {format_execution_time(st.session_state.demo_metrics['silver'].get('execution_time', 0))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px;'>
            <h4 style='color: #FFD700;'>🥇 Gold</h4>
            <p>Rows: {len(st.session_state.demo_data['gold']):,}</p>
            <p>Time: {format_execution_time(st.session_state.demo_metrics['gold'].get('execution_time', 0))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Total pipeline time
    total_time = sum(
        metrics.get('execution_time', 0) 
        for metrics in st.session_state.demo_metrics.values()
    )
    
    st.success(f"✅ Complete pipeline executed in {format_execution_time(total_time)}")
else:
    st.info("Complete all layers to see the full pipeline summary")
