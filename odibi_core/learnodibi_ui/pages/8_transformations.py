"""
Transformations Explorer - Interactive DAG visualization and data flow analysis
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any

ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box, error_box, info_box
from odibi_core.learnodibi_ui.utils import initialize_session_state, create_sample_data

st.set_page_config(
    page_title="Transformations Explorer - ODIBI CORE Studio",
    page_icon="🔄",
    layout="wide"
)

apply_theme()
initialize_session_state()

if 'selected_pipeline' not in st.session_state:
    st.session_state.selected_pipeline = None


def get_example_pipelines() -> Dict[str, Dict]:
    """Define example transformation pipelines"""
    return {
        "Energy Efficiency Pipeline": {
            "description": "Process raw energy meter data through Bronze → Silver → Gold layers",
            "layers": {
                "bronze": {
                    "name": "Raw Ingestion",
                    "description": "Ingest raw energy meter readings",
                    "type": "ingest",
                    "code": """# Bronze Layer - Raw Ingestion
df_bronze = pd.read_csv('energy_meters.csv')
# Store as-is, no transformations""",
                    "transformation": lambda df: df.copy()
                },
                "silver": {
                    "name": "Data Cleansing",
                    "description": "Clean data, handle nulls, add timestamps",
                    "type": "sql",
                    "code": """# Silver Layer - Clean & Standardize
SELECT 
    timestamp,
    sensor_id,
    COALESCE(temperature, 25.0) as temperature,
    COALESCE(humidity, 60.0) as humidity,
    COALESCE(pressure, 1013.0) as pressure,
    energy_kwh,
    current_timestamp() as processed_at
FROM bronze
WHERE energy_kwh > 0""",
                    "transformation": lambda df: df.assign(
                        temperature=df['temperature'].fillna(25.0),
                        humidity=df['humidity'].fillna(60.0),
                        pressure=df['pressure'].fillna(1013.0),
                        processed_at=pd.Timestamp.now()
                    ).query('energy_kwh > 0')
                },
                "gold": {
                    "name": "Business Aggregation",
                    "description": "Calculate daily efficiency metrics",
                    "type": "sql",
                    "code": """# Gold Layer - Aggregate for Analytics
SELECT 
    sensor_id,
    DATE(timestamp) as date,
    AVG(temperature) as avg_temperature,
    AVG(humidity) as avg_humidity,
    SUM(energy_kwh) as total_energy,
    COUNT(*) as reading_count
FROM silver
GROUP BY sensor_id, DATE(timestamp)""",
                    "transformation": lambda df: df.groupby([
                        'sensor_id',
                        df['timestamp'].dt.date
                    ]).agg({
                        'temperature': 'mean',
                        'humidity': 'mean',
                        'energy_kwh': 'sum',
                        'sensor_id': 'count'
                    }).rename(columns={'sensor_id': 'reading_count'}).reset_index()
                }
            }
        },
        "Data Quality Pipeline": {
            "description": "Validate and enrich sensor data with quality scores",
            "layers": {
                "bronze": {
                    "name": "Raw Collection",
                    "description": "Collect raw sensor readings",
                    "type": "ingest",
                    "code": """# Bronze - Raw sensor data
df_bronze = ingest_from_source('sensors')""",
                    "transformation": lambda df: df.copy()
                },
                "silver": {
                    "name": "Quality Scoring",
                    "description": "Calculate data quality scores",
                    "type": "function",
                    "code": """# Silver - Add quality metrics
def calculate_quality_score(row):
    score = 100
    if pd.isna(row['temperature']): score -= 20
    if pd.isna(row['humidity']): score -= 20
    if row['energy_kwh'] <= 0: score -= 30
    return score

df['quality_score'] = df.apply(calculate_quality_score, axis=1)
df['quality_tier'] = pd.cut(
    df['quality_score'], 
    bins=[0, 50, 80, 100],
    labels=['Low', 'Medium', 'High']
)""",
                    "transformation": lambda df: df.assign(
                        quality_score=lambda x: 100 - 
                            (x['temperature'].isna() * 20) - 
                            (x['humidity'].isna() * 20) - 
                            ((x['energy_kwh'] <= 0) * 30),
                        quality_tier=lambda x: pd.cut(
                            x['quality_score'],
                            bins=[0, 50, 80, 100],
                            labels=['Low', 'Medium', 'High']
                        )
                    )
                },
                "gold": {
                    "name": "Quality Analytics",
                    "description": "Aggregate quality metrics by sensor",
                    "type": "sql",
                    "code": """# Gold - Quality summary
SELECT 
    sensor_id,
    AVG(quality_score) as avg_quality,
    COUNT(CASE WHEN quality_tier='High' THEN 1 END) as high_quality_count,
    COUNT(*) as total_readings
FROM silver
GROUP BY sensor_id""",
                    "transformation": lambda df: df.groupby('sensor_id').agg({
                        'quality_score': 'mean',
                        'sensor_id': 'count'
                    }).rename(columns={'sensor_id': 'total_readings'}).assign(
                        high_quality_count=lambda x: 0
                    ).reset_index()
                }
            }
        },
        "Time Series Analysis": {
            "description": "Transform time-series data with rolling calculations",
            "layers": {
                "bronze": {
                    "name": "Raw Time Series",
                    "description": "Ingest time-ordered sensor data",
                    "type": "ingest",
                    "code": """# Bronze - Time series data
df_bronze = read_time_series('sensors.parquet')""",
                    "transformation": lambda df: df.copy()
                },
                "silver": {
                    "name": "Rolling Metrics",
                    "description": "Calculate moving averages and trends",
                    "type": "function",
                    "code": """# Silver - Rolling calculations
df_sorted = df.sort_values('timestamp')
df_sorted['temp_ma_24h'] = (
    df_sorted.groupby('sensor_id')['temperature']
    .transform(lambda x: x.rolling(24, min_periods=1).mean())
)
df_sorted['energy_trend'] = (
    df_sorted.groupby('sensor_id')['energy_kwh']
    .transform(lambda x: x.diff())
)""",
                    "transformation": lambda df: df.sort_values('timestamp').assign(
                        temp_ma_24h=lambda x: x.groupby('sensor_id')['temperature']
                            .transform(lambda g: g.rolling(24, min_periods=1).mean()),
                        energy_trend=lambda x: x.groupby('sensor_id')['energy_kwh']
                            .transform(lambda g: g.diff())
                    )
                },
                "gold": {
                    "name": "Anomaly Detection",
                    "description": "Flag anomalies based on rolling stats",
                    "type": "function",
                    "code": """# Gold - Detect anomalies
threshold = 2.0
df['is_anomaly'] = (
    abs(df['temperature'] - df['temp_ma_24h']) > threshold
)
anomaly_summary = df.groupby('sensor_id').agg({
    'is_anomaly': 'sum',
    'sensor_id': 'count'
})""",
                    "transformation": lambda df: df.assign(
                        is_anomaly=lambda x: abs(x['temperature'] - x['temp_ma_24h']) > 2.0
                    ).groupby('sensor_id').agg({
                        'is_anomaly': 'sum',
                        'sensor_id': 'count'
                    }).rename(columns={'sensor_id': 'total_readings', 'is_anomaly': 'anomaly_count'})
                    .reset_index()
                }
            }
        }
    }


def generate_pipeline_dag(pipeline_name: str, pipeline_config: Dict) -> str:
    """Generate Mermaid DAG for a pipeline"""
    layers = pipeline_config['layers']
    
    mermaid = """```mermaid
graph LR
    %% Node definitions
    SOURCE[("📁 Data Source")]
    """
    
    layer_nodes = {
        'bronze': ('BRONZE["🥉 Bronze Layer<br/>Raw Ingestion"]', '#FFE5B4'),
        'silver': ('SILVER["🥈 Silver Layer<br/>Transformation"]', '#C0C0C0'),
        'gold': ('GOLD["🥇 Gold Layer<br/>Aggregation"]', '#FFD700')
    }
    
    for layer, (node_def, color) in layer_nodes.items():
        if layer in layers:
            mermaid += f"    {node_def}\n"
            mermaid += f"    style {layer.upper()} fill:{color},stroke:#333,stroke-width:2px\n"
    
    mermaid += """    TARGET[("💾 Storage")]
    
    %% Connections
    SOURCE --> BRONZE
"""
    
    if 'silver' in layers:
        mermaid += "    BRONZE --> SILVER\n"
    if 'gold' in layers:
        mermaid += "    SILVER --> GOLD\n"
    
    last_layer = list(layers.keys())[-1].upper()
    mermaid += f"    {last_layer} --> TARGET\n"
    
    mermaid += "    style SOURCE fill:#E3F2FD,stroke:#1976D2,stroke-width:2px\n"
    mermaid += "    style TARGET fill:#E8F5E9,stroke:#388E3C,stroke-width:2px\n"
    mermaid += "```"
    
    return mermaid


def render_transformation_step(
    layer_name: str, 
    layer_config: Dict, 
    input_df: pd.DataFrame,
    layer_color: str
) -> pd.DataFrame:
    """Render a transformation step with input/output preview"""
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {layer_color}22, {layer_color}11); 
                padding: 1.5rem; border-radius: 12px; border-left: 4px solid {layer_color};
                margin: 1rem 0;'>
        <h3 style='color: {layer_color}; margin: 0;'>
            {layer_name.upper()} Layer: {layer_config['name']}
        </h3>
        <p style='color: {COLORS['text_secondary']}; margin-top: 0.5rem;'>
            {layer_config['description']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_code, col_preview = st.columns([1, 1])
    
    with col_code:
        st.markdown(f"**📝 Transformation Code** (`{layer_config['type']}` type)")
        st.code(layer_config['code'], language="python" if layer_config['type'] == "function" else "sql")
    
    with col_preview:
        st.markdown("**📊 Input Data Sample**")
        st.dataframe(input_df.head(5), use_container_width=True, hide_index=True)
    
    try:
        output_df = layer_config['transformation'](input_df)
        
        st.markdown("##")
        
        col_output, col_metrics = st.columns([2, 1])
        
        with col_output:
            st.markdown("**✅ Output Data Sample**")
            st.dataframe(output_df.head(5), use_container_width=True, hide_index=True)
        
        with col_metrics:
            st.markdown("**📈 Transformation Metrics**")
            
            input_rows = len(input_df)
            output_rows = len(output_df)
            input_cols = len(input_df.columns)
            output_cols = len(output_df.columns)
            
            st.metric("Rows", output_rows, delta=output_rows - input_rows)
            st.metric("Columns", output_cols, delta=output_cols - input_cols)
            
            if input_rows > 0:
                retention_pct = (output_rows / input_rows) * 100
                st.metric("Data Retention", f"{retention_pct:.1f}%")
        
        return output_df
        
    except Exception as e:
        error_box(f"Transformation failed: {str(e)}")
        return input_df


def create_sample_bronze_data() -> pd.DataFrame:
    """Create sample Bronze layer data"""
    np.random.seed(42)
    n_rows = 100
    
    return pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='H'),
        'sensor_id': np.random.choice(['S001', 'S002', 'S003'], n_rows),
        'temperature': np.random.normal(25, 5, n_rows),
        'humidity': np.random.normal(60, 10, n_rows),
        'pressure': np.random.normal(1013, 5, n_rows),
        'energy_kwh': np.random.uniform(10, 100, n_rows)
    })


def main():
    st.title("🔄 Transformations Explorer")
    st.markdown(
        f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>"
        "Visualize data transformations through Bronze → Silver → Gold layers</p>",
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Pipeline Explorer",
        "📊 DAG Visualization", 
        "🧪 Step-by-Step Flow",
        "📚 Transform Patterns"
    ])
    
    with tab1:
        st.markdown("### 🔍 Select a Transformation Pipeline")
        
        pipelines = get_example_pipelines()
        
        col_select, col_info = st.columns([1, 2])
        
        with col_select:
            selected_name = st.selectbox(
                "Choose Pipeline:",
                options=list(pipelines.keys()),
                key="pipeline_selector"
            )
            
            st.session_state.selected_pipeline = selected_name
            
            st.markdown("##")
            
            selected_pipeline = pipelines[selected_name]
            
            st.markdown(f"**Description:**")
            st.info(selected_pipeline['description'])
            
            st.markdown(f"**Layers:**")
            for layer_name in selected_pipeline['layers'].keys():
                layer_icon = "🥉" if layer_name == "bronze" else "🥈" if layer_name == "silver" else "🥇"
                st.markdown(f"- {layer_icon} {layer_name.upper()}")
        
        with col_info:
            st.markdown("### 📋 Pipeline Overview")
            
            selected_pipeline = pipelines[selected_name]
            
            for layer_name, layer_config in selected_pipeline['layers'].items():
                color_map = {
                    'bronze': '#CD7F32',
                    'silver': '#C0C0C0',
                    'gold': COLORS['primary']
                }
                
                st.markdown(f"""
                <div style='background: {color_map[layer_name]}22; padding: 1rem; 
                            border-radius: 8px; margin: 0.5rem 0; 
                            border-left: 3px solid {color_map[layer_name]};'>
                    <h4 style='color: {color_map[layer_name]}; margin: 0;'>
                        {layer_name.upper()}: {layer_config['name']}
                    </h4>
                    <p style='margin: 0.5rem 0 0 0; color: {COLORS['text_secondary']};'>
                        {layer_config['description']}
                    </p>
                    <p style='margin: 0.3rem 0 0 0; font-size: 0.9em;'>
                        <strong>Type:</strong> {layer_config['type']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Pipeline DAG Visualization")
        
        if st.session_state.selected_pipeline:
            selected_pipeline = pipelines[st.session_state.selected_pipeline]
            
            info_box("""
            **Understanding the DAG:**
            - 📁 **Data Source**: Raw input data
            - 🥉 **Bronze Layer**: Raw data ingestion (no transformations)
            - 🥈 **Silver Layer**: Cleaned and standardized data
            - 🥇 **Gold Layer**: Business-ready aggregated data
            - 💾 **Storage**: Persisted output
            """)
            
            st.markdown("##")
            
            dag_diagram = generate_pipeline_dag(
                st.session_state.selected_pipeline,
                selected_pipeline
            )
            
            st.markdown(dag_diagram)
            
            st.markdown("##")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='background: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
                    <h3 style='color: {COLORS['primary']};'>3</h3>
                    <p style='color: {COLORS['text_secondary']}; margin: 0;'>Transformation Layers</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
                    <h3 style='color: {COLORS['secondary']};'>{len(selected_pipeline['layers'])}</h3>
                    <p style='color: {COLORS['text_secondary']}; margin: 0;'>Processing Steps</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                transform_types = set(layer['type'] for layer in selected_pipeline['layers'].values())
                st.markdown(f"""
                <div style='background: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
                    <h3 style='color: {COLORS['info']};'>{len(transform_types)}</h3>
                    <p style='color: {COLORS['text_secondary']}; margin: 0;'>Transform Types</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            info_box("Select a pipeline from the Pipeline Explorer tab to view its DAG")
    
    with tab3:
        st.markdown("### 🧪 Step-by-Step Data Flow")
        
        if st.session_state.selected_pipeline:
            selected_pipeline = pipelines[st.session_state.selected_pipeline]
            
            st.markdown("**Run the pipeline and see data transformation at each layer:**")
            
            if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
                bronze_data = create_sample_bronze_data()
                
                st.markdown("##")
                st.markdown("### 📊 Transformation Flow")
                
                current_data = bronze_data
                
                color_map = {
                    'bronze': '#CD7F32',
                    'silver': '#C0C0C0',
                    'gold': COLORS['primary']
                }
                
                for i, (layer_name, layer_config) in enumerate(selected_pipeline['layers'].items()):
                    st.markdown(f"## ")
                    current_data = render_transformation_step(
                        layer_name,
                        layer_config,
                        current_data,
                        color_map[layer_name]
                    )
                    
                    if i < len(selected_pipeline['layers']) - 1:
                        st.markdown(f"""
                        <div style='text-align: center; margin: 2rem 0;'>
                            <div style='font-size: 2em; color: {COLORS['primary']};'>⬇️</div>
                            <p style='color: {COLORS['text_secondary']};'>Data flows to next layer</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("##")
                success_box(f"✅ Pipeline completed successfully! Final output has {len(current_data)} rows.")
        else:
            info_box("Select a pipeline from the Pipeline Explorer tab to run it")
    
    with tab4:
        st.markdown("### 📚 Common Transformation Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px;'>
                <h4 style='color: {COLORS['primary']};'>🔄 SQL Transformations</h4>
                
                <p><strong>Best for:</strong></p>
                <ul>
                    <li>Filtering and aggregation</li>
                    <li>Joins and unions</li>
                    <li>Window functions</li>
                    <li>Declarative transformations</li>
                </ul>
                
                <p><strong>Example Use Cases:</strong></p>
                <ul>
                    <li>Clean and standardize data</li>
                    <li>Calculate business metrics</li>
                    <li>Combine multiple sources</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##")
            
            st.markdown("**Example SQL Transform:**")
            st.code("""SELECT 
    sensor_id,
    DATE(timestamp) as date,
    AVG(temperature) as avg_temp,
    MAX(energy_kwh) as peak_energy
FROM bronze
WHERE temperature > 0
GROUP BY sensor_id, DATE(timestamp)""", language="sql")
        
        with col2:
            st.markdown(f"""
            <div style='background: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px;'>
                <h4 style='color: {COLORS['secondary']};'>🐍 Function Transformations</h4>
                
                <p><strong>Best for:</strong></p>
                <ul>
                    <li>Complex business logic</li>
                    <li>Custom calculations</li>
                    <li>ML feature engineering</li>
                    <li>External API calls</li>
                </ul>
                
                <p><strong>Example Use Cases:</strong></p>
                <ul>
                    <li>Domain-specific calculations</li>
                    <li>Data enrichment</li>
                    <li>Custom validation rules</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##")
            
            st.markdown("**Example Function Transform:**")
            st.code("""def calculate_efficiency(df):
    df['efficiency'] = (
        df['output_energy'] / df['input_energy']
    ) * 100
    df['efficiency_tier'] = pd.cut(
        df['efficiency'],
        bins=[0, 50, 75, 100],
        labels=['Low', 'Medium', 'High']
    )
    return df""", language="python")
        
        st.markdown("##")
        
        st.markdown("### 💡 Transformation Best Practices")
        
        best_practices = [
            ("📏 **Keep transforms focused**", "Each layer should have a single, clear purpose"),
            ("🔍 **Filter early**", "Remove unnecessary data at Bronze layer to improve performance"),
            ("✅ **Validate at each step**", "Add data quality checks between layers"),
            ("📊 **Log transformations**", "Track row counts and metrics at each stage"),
            ("🔄 **Make them idempotent**", "Running the same transform twice should produce the same result"),
            ("⚡ **Optimize for your engine**", "Use SQL for Spark, vectorized operations for Pandas"),
        ]
        
        cols = st.columns(2)
        for i, (title, description) in enumerate(best_practices):
            with cols[i % 2]:
                st.markdown(f"""
                <div style='background: {COLORS['surface']}; padding: 1rem; 
                            border-radius: 8px; margin: 0.5rem 0;'>
                    <p style='margin: 0; font-weight: bold;'>{title}</p>
                    <p style='margin: 0.3rem 0 0 0; color: {COLORS['text_secondary']}; 
                              font-size: 0.9em;'>{description}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("##")
        
        success_box("""
        **ODIBI CORE TransformNode supports both SQL and Function transforms!**
        
        Switch between them seamlessly in your pipeline configuration:
        ```python
        # SQL Transform
        Step(layer="silver", type="sql", value="SELECT * FROM bronze WHERE...")
        
        # Function Transform  
        Step(layer="silver", type="function", value="my_module.transform_func")
        ```
        """)


if __name__ == "__main__":
    main()
