"""
Core Concepts Page - Learn about the 5 canonical node types
"""

import streamlit as st
import sys
from pathlib import Path

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, info_box, success_box
from odibi_core.learnodibi_ui.utils import get_node_types, display_code_with_run
from odibi_core.learnodibi_ui.utils import initialize_session_state

apply_theme()
initialize_session_state()

# Header
st.title("🎓 Core Concepts")
st.markdown("Learn about the fundamental building blocks of ODIBI CORE")

st.markdown("---")

# Introduction
st.markdown(f"""
<div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;'>
    <h3 style='color: {COLORS['primary']}; margin-top: 0;'>The Node-Based Architecture</h3>
    <p style='font-size: 1.05em; line-height: 1.6;'>
        ODIBI CORE is built around <strong>five canonical node types</strong> that represent the fundamental 
        operations in any data engineering pipeline. Each node has a specific responsibility and can be 
        composed with others to build complex data workflows.
    </p>
</div>
""", unsafe_allow_html=True)

# Interactive Node Diagram
st.markdown("### 🔄 Data Flow Architecture")

info_box("Click on each node type below to learn more and see examples")

# Create tabs for each node type
node_types = get_node_types()

tabs = st.tabs([f"{node['icon']} {node['name']}" for node in node_types])

for i, (tab, node) in enumerate(zip(tabs, node_types)):
    with tab:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {node['icon']} {node['name']}")
            st.markdown(f"**{node['description']}**")
            st.markdown(f"*Example use case:* {node['example']}")
            
            st.markdown("---")
            
            # Show code example based on node type
            if node['name'] == "ConnectNode":
                st.markdown("#### Code Example")
                code = """
from odibi_core.nodes import ConnectNode

# Create a connection to Azure Blob Storage
connect = ConnectNode(
    name="azure_connection",
    connection_type="azure_blob",
    config={
        "account_name": "myaccount",
        "container": "data"
    }
)

# Execute connection
connection = connect.execute()
print(f"Connected: {connection.is_connected}")
"""
                st.code(code, language="python")
                
                if st.button("💡 Try It", key=f"try_{node['name']}", use_container_width=True):
                    with st.spinner("Running..."):
                        st.code("""
# Simulated output:
Connected: True
Connection established to Azure Blob Storage
Container: data
""", language="text")
                        success_box("Connection node executed successfully!")
            
            elif node['name'] == "IngestNode":
                st.markdown("#### Code Example")
                code = """
from odibi_core.nodes import IngestNode

# Ingest data from a source
ingest = IngestNode(
    name="read_sensor_data",
    source_connection=connection,
    source_path="sensors/data.parquet",
    read_options={"columns": ["timestamp", "temperature"]}
)

# Execute ingestion
df = ingest.execute()
print(f"Loaded {len(df)} rows")
"""
                st.code(code, language="python")
                
                if st.button("💡 Try It", key=f"try_{node['name']}", use_container_width=True):
                    import pandas as pd
                    import numpy as np
                    
                    with st.spinner("Ingesting data..."):
                        # Create sample data
                        df = pd.DataFrame({
                            "timestamp": pd.date_range("2024-01-01", periods=100, freq="h"),
                            "temperature": np.random.normal(25, 5, 100)
                        })
                        
                        st.dataframe(df.head(10), use_container_width=True)
                        success_box(f"Loaded {len(df)} rows successfully!")
            
            elif node['name'] == "TransformNode":
                st.markdown("#### Code Example")
                code = """
from odibi_core.nodes import TransformNode
from odibi_core.functions import conversion_utils, data_ops
import pandas as pd

# Sample data
df = pd.DataFrame({
    'temperature': [20.5, 22.1, None, 19.8, 21.3],
    'humidity': [45, 52, 48, None, 50]
})

# Fill null values
df_clean = conversion_utils.fill_null(df, 'temperature', fill_value=20.0)
df_clean = conversion_utils.fill_null(df_clean, 'humidity', fill_value=50)

# Deduplicate
df_final = data_ops.deduplicate(df_clean)

print(f"Cleaned {len(df_final)} rows")
"""
                st.code(code, language="python")
                
                if st.button("💡 Try It", key=f"try_{node['name']}", use_container_width=True):
                    import pandas as pd
                    import numpy as np
                    
                    with st.spinner("Transforming data..."):
                        # Create and transform sample data
                        df = pd.DataFrame({
                            "temperature": [20, 22, None, 25, 23]
                        })
                        
                        # Apply transformation
                        df_transformed = df.ffill()  # Forward fill nulls
                        df_transformed["temp_fahrenheit"] = df_transformed["temperature"] * 9/5 + 32
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("**Before:**")
                            st.dataframe(df, use_container_width=True)
                        with col_b:
                            st.markdown("**After:**")
                            st.dataframe(df_transformed, use_container_width=True)
                        
                        success_box("Transformation completed!")
            
            elif node['name'] == "StoreNode":
                st.markdown("#### Code Example")
                code = """
from odibi_core.nodes import StoreNode

# Store transformed data
store = StoreNode(
    name="save_to_delta",
    target_connection=connection,
    target_path="processed/sensor_data",
    format="delta",
    write_mode="append",
    partition_by=["date"]
)

# Execute storage
result = store.execute(transformed_df)
print(f"Stored {result['rows_written']} rows")
"""
                st.code(code, language="python")
                
                if st.button("💡 Try It", key=f"try_{node['name']}", use_container_width=True):
                    with st.spinner("Storing data..."):
                        st.code("""
# Simulated output:
Stored 100 rows
Format: delta
Location: processed/sensor_data
Partitions: ['2024-01-01', '2024-01-02', '2024-01-03']
""", language="text")
                        success_box("Data stored successfully!")
            
            elif node['name'] == "PublishNode":
                st.markdown("#### Code Example")
                code = """
from odibi_core.nodes import PublishNode

# Publish data
publish = PublishNode(
    name="expose_api",
    source_data=stored_df,
    publish_type="rest_api",
    config={
        "endpoint": "/api/sensors",
        "methods": ["GET"],
        "cache_ttl": 300
    }
)

# Execute publication
api_url = publish.execute()
print(f"API available at: {api_url}")
"""
                st.code(code, language="python")
                
                if st.button("💡 Try It", key=f"try_{node['name']}", use_container_width=True):
                    with st.spinner("Publishing..."):
                        st.code("""
# Simulated output:
API available at: http://localhost:8000/api/sensors
Methods: GET
Cache TTL: 300 seconds
Documentation: http://localhost:8000/docs
""", language="text")
                        success_box("API endpoint published successfully!")
        
        with col2:
            st.markdown(f"""
            <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; position: sticky; top: 1rem;'>
                <h4 style='color: {COLORS['secondary']}; margin-top: 0;'>Key Features</h4>
                <ul>
                    <li>✅ Declarative configuration</li>
                    <li>✅ Built-in error handling</li>
                    <li>✅ Automatic metrics tracking</li>
                    <li>✅ Full observability</li>
                    <li>✅ Easy composition</li>
                </ul>
                
                <h4 style='color: {COLORS['secondary']}; margin-top: 1.5rem;'>Best Practices</h4>
                <ul>
                    <li>🎯 Single responsibility</li>
                    <li>🔄 Reusable components</li>
                    <li>📊 Monitor metrics</li>
                    <li>🛡️ Validate inputs/outputs</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Complete Pipeline Example
st.markdown("---")
st.markdown("### 🔗 Putting It All Together")

st.markdown("""
Here's how all five nodes work together in a complete pipeline:
""")

complete_example = """
from odibi_core.nodes import (
    ConnectNode, IngestNode, TransformNode, StoreNode, PublishNode
)

# 1. Connect to source
source_conn = ConnectNode(name="azure_source", 
                          connection_type="azure_blob").execute()

# 2. Ingest raw data (Bronze layer)
raw_data = IngestNode(name="ingest_sensors",
                      source_connection=source_conn,
                      source_path="raw/sensors/*.parquet").execute()

# 3. Transform data (Silver layer)
clean_data = TransformNode(name="clean_data",
                           transformations=[...]).execute(raw_data)

# 4. Store processed data (Gold layer)
StoreNode(name="save_gold",
          target_path="gold/sensors",
          format="delta").execute(clean_data)

# 5. Publish via API
PublishNode(name="sensor_api",
            publish_type="rest_api").execute(clean_data)
"""

st.code(complete_example, language="python")

if st.button("▶️ Run Complete Pipeline", type="primary", use_container_width=True):
    import time
    import pandas as pd
    import numpy as np
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate pipeline execution
    stages = [
        ("Connecting to source...", 0.2),
        ("Ingesting raw data...", 0.4),
        ("Transforming data...", 0.6),
        ("Storing to Delta Lake...", 0.8),
        ("Publishing API...", 1.0)
    ]
    
    for stage, progress in stages:
        status_text.text(stage)
        progress_bar.progress(progress)
        time.sleep(0.5)
    
    status_text.empty()
    progress_bar.empty()
    
    # Show results
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows Processed", "10,542")
    with col2:
        st.metric("Execution Time", "2.3s")
    with col3:
        st.metric("API Endpoint", "✅ Active")
    
    success_box("Pipeline executed successfully! All layers processed.")

# Next Steps
st.markdown("---")
st.markdown("### 🚀 Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
        <h4>📚 Explore Functions</h4>
        <p>Discover the rich library of transformation functions</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
        <h4>💻 Try SDK Examples</h4>
        <p>See real code patterns and best practices</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
        <h4>⚡ Run Demo Project</h4>
        <p>Experience a complete data pipeline</p>
    </div>
    """, unsafe_allow_html=True)
