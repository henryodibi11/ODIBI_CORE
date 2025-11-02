"""
SDK Examples Page - Real code patterns and best practices
"""

import streamlit as st
import sys
from pathlib import Path
import time

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, info_box, success_box
from odibi_core.learnodibi_ui.utils import execute_with_metrics, format_execution_time

apply_theme()

# Header
st.title("💻 SDK Examples")
st.markdown("Learn ODIBI CORE through practical code examples")

st.markdown("---")

# Example categories
examples = {
    "Getting Started": {
        "Basic Pipeline": {
            "description": "Create a simple data pipeline with all five nodes",
            "difficulty": "Beginner",
            "code": """
from odibi_core.nodes import ConnectNode, IngestNode, TransformNode, StoreNode
import pandas as pd

# Sample data
data = pd.DataFrame({
    'id': [1, 2, 3],
    'value': [10, 20, 30]
})

# Create simple pipeline
# 1. Transform
transformed = data.copy()
transformed['doubled'] = transformed['value'] * 2

# 2. Display results
print(f"Processed {len(transformed)} rows")
print(transformed)

result = transformed
"""
        },
        "Configuration Management": {
            "description": "Manage pipeline configuration using dictionaries",
            "difficulty": "Beginner",
            "code": """
# Define pipeline configuration
config = {
    'pipeline_name': 'my_first_pipeline',
    'source': {
        'type': 'csv',
        'path': 'data/input.csv'
    },
    'transformations': [
        {'type': 'filter', 'column': 'status', 'value': 'active'},
        {'type': 'sort', 'column': 'date', 'ascending': False}
    ],
    'target': {
        'type': 'parquet',
        'path': 'data/output.parquet'
    }
}

# Use configuration
print(f"Pipeline: {config['pipeline_name']}")
print(f"Source: {config['source']['type']}")
print(f"Transformations: {len(config['transformations'])}")

result = config
"""
        }
    },
    "Data Transformation": {
        "Data Cleaning": {
            "description": "Clean and prepare data for analysis",
            "difficulty": "Intermediate",
            "code": """
import pandas as pd
import numpy as np

# Create messy data
data = pd.DataFrame({
    'name': ['  John  ', 'Jane', None, '  Bob'],
    'age': [25, None, 30, 35],
    'salary': [50000, 60000, None, 75000]
})

print("Before cleaning:")
print(data)

# Clean data
cleaned = data.copy()

# 1. Clean strings
cleaned['name'] = cleaned['name'].str.strip()

# 2. Handle nulls
cleaned['name'] = cleaned['name'].fillna('Unknown')
cleaned['age'] = cleaned['age'].fillna(cleaned['age'].median())
cleaned['salary'] = cleaned['salary'].fillna(cleaned['salary'].mean())

print("\\nAfter cleaning:")
print(cleaned)

result = cleaned
"""
        },
        "Aggregations": {
            "description": "Perform group-by aggregations",
            "difficulty": "Intermediate",
            "code": """
import pandas as pd

# Sample sales data
data = pd.DataFrame({
    'region': ['North', 'North', 'South', 'South', 'East'],
    'product': ['A', 'B', 'A', 'B', 'A'],
    'sales': [100, 150, 200, 175, 125],
    'quantity': [10, 15, 20, 17, 12]
})

print("Original data:")
print(data)

# Aggregate by region
agg_result = data.groupby('region').agg({
    'sales': ['sum', 'mean'],
    'quantity': 'sum'
}).round(2)

print("\\nAggregated by region:")
print(agg_result)

result = agg_result
"""
        }
    },
    "Advanced Patterns": {
        "Error Handling": {
            "description": "Implement robust error handling",
            "difficulty": "Advanced",
            "code": """
import pandas as pd

def safe_transform(df, column, operation):
    \"\"\"Safely transform data with error handling\"\"\"
    try:
        if operation == 'normalize':
            min_val = df[column].min()
            max_val = df[column].max()
            if max_val == min_val:
                raise ValueError("Cannot normalize constant values")
            df[column] = (df[column] - min_val) / (max_val - min_val)
        
        return {'success': True, 'data': df, 'error': None}
    
    except Exception as e:
        return {'success': False, 'data': df, 'error': str(e)}

# Test data
data = pd.DataFrame({'values': [1, 2, 3, 4, 5]})

# Apply safe transformation
result_obj = safe_transform(data.copy(), 'values', 'normalize')

if result_obj['success']:
    print("✅ Transformation successful")
    print(result_obj['data'])
else:
    print(f"❌ Error: {result_obj['error']}")

result = result_obj['data']
"""
        },
        "Parallel Processing": {
            "description": "Process data in parallel for better performance",
            "difficulty": "Advanced",
            "code": """
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def process_chunk(chunk_data):
    \"\"\"Process a chunk of data\"\"\"
    # Simulate processing
    chunk_data['processed'] = chunk_data['value'] * 2
    return chunk_data

# Create sample data
data = pd.DataFrame({
    'id': range(100),
    'value': np.random.rand(100)
})

# Split into chunks
n_chunks = 4
chunks = np.array_split(data, n_chunks)

print(f"Processing {len(data)} rows in {n_chunks} chunks...")

# Process in parallel
with ThreadPoolExecutor(max_workers=n_chunks) as executor:
    processed_chunks = list(executor.map(process_chunk, chunks))

# Combine results
result = pd.concat(processed_chunks, ignore_index=True)

print(f"✅ Processed {len(result)} rows")
print(result.head())
"""
        }
    },
    "Real-World Use Cases": {
        "ETL Pipeline": {
            "description": "Complete ETL pipeline with bronze-silver-gold layers",
            "difficulty": "Advanced",
            "code": """
import pandas as pd
import numpy as np

# Simulate ETL Pipeline

# BRONZE: Raw ingestion
print("=== BRONZE LAYER ===")
bronze_data = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=10, freq='h'),
    'sensor_id': np.random.choice(['S1', 'S2'], 10),
    'temperature': np.random.normal(25, 5, 10),
    'humidity': np.random.normal(60, 10, 10)
})
print(f"Ingested {len(bronze_data)} raw records")

# SILVER: Cleaned and validated
print("\\n=== SILVER LAYER ===")
silver_data = bronze_data.copy()
silver_data['temperature'] = silver_data['temperature'].clip(0, 50)
silver_data['humidity'] = silver_data['humidity'].clip(0, 100)
silver_data['date'] = silver_data['timestamp'].dt.date
print(f"Cleaned {len(silver_data)} records")

# GOLD: Aggregated analytics
print("\\n=== GOLD LAYER ===")
gold_data = silver_data.groupby(['sensor_id', 'date']).agg({
    'temperature': ['mean', 'min', 'max'],
    'humidity': ['mean']
}).round(2)
print("Aggregated data by sensor and date:")
print(gold_data)

result = gold_data
"""
        },
        "Data Quality Checks": {
            "description": "Implement comprehensive data quality validation",
            "difficulty": "Intermediate",
            "code": """
import pandas as pd

def data_quality_report(df):
    \"\"\"Generate data quality report\"\"\"
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    # Column-level checks
    report['columns'] = {}
    for col in df.columns:
        report['columns'][col] = {
            'dtype': str(df[col].dtype),
            'missing': df[col].isnull().sum(),
            'unique': df[col].nunique()
        }
    
    return report

# Sample data with quality issues
data = pd.DataFrame({
    'id': [1, 2, 2, 4, 5],
    'value': [10, None, 30, 40, 50],
    'category': ['A', 'B', 'A', None, 'C']
})

# Generate report
report = data_quality_report(data)

print("📊 Data Quality Report")
print(f"Total Rows: {report['total_rows']}")
print(f"Total Columns: {report['total_columns']}")
print(f"Missing Values: {report['missing_values']}")
print(f"Duplicate Rows: {report['duplicate_rows']}")
print(f"Memory Usage: {report['memory_usage_mb']:.2f} MB")

result = data
"""
        }
    }
}

# Sidebar navigation
with st.sidebar:
    st.markdown("### 📚 Example Categories")
    selected_category = st.radio(
        "Category",
        list(examples.keys()),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Difficulty filter
    difficulty_filter = st.multiselect(
        "Filter by Difficulty",
        ["Beginner", "Intermediate", "Advanced"],
        default=["Beginner", "Intermediate", "Advanced"]
    )

# Main content
st.markdown(f"### {selected_category}")

category_examples = examples[selected_category]

for example_name, example_data in category_examples.items():
    difficulty = example_data['difficulty']
    
    # Apply difficulty filter
    if difficulty not in difficulty_filter:
        continue
    
    with st.expander(f"{'🟢' if difficulty == 'Beginner' else '🟡' if difficulty == 'Intermediate' else '🔴'} {example_name}", expanded=False):
        # Description
        st.markdown(f"**Description:** {example_data['description']}")
        st.markdown(f"**Difficulty:** {difficulty}")
        
        st.markdown("---")
        
        # Code
        st.markdown("**Code:**")
        st.code(example_data['code'], language="python")
        
        # Run button
        col1, col2 = st.columns([1, 4])
        
        with col1:
            run_button = st.button(
                "▶️ Run Example",
                key=f"run_{selected_category}_{example_name}",
                use_container_width=True
            )
        
        if run_button:
            with st.spinner("Executing..."):
                # Execute code
                start_time = time.time()
                
                try:
                    # Create namespace with imports
                    import numpy as np
                    import pandas as pd
                    
                    namespace = {
                        'pd': pd,
                        'np': np,
                        '__builtins__': __builtins__
                    }
                    
                    # Execute code
                    exec(example_data['code'], namespace)
                    
                    execution_time = time.time() - start_time
                    
                    # Show success
                    success_box(f"Execution completed in {format_execution_time(execution_time)}")
                    
                    # Show output
                    if 'result' in namespace:
                        st.markdown("**Output:**")
                        
                        result = namespace['result']
                        
                        if isinstance(result, pd.DataFrame):
                            st.dataframe(result, use_container_width=True)
                            
                            # Download button
                            csv = result.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name=f"{example_name.replace(' ', '_').lower()}_results.csv",
                                mime="text/csv",
                                key=f"download_{selected_category}_{example_name}"
                            )
                        elif isinstance(result, dict):
                            st.json(result)
                        else:
                            st.write(result)
                    
                    # Show metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Execution Time", format_execution_time(execution_time))
                    with col2:
                        st.metric("Status", "✅ Success")
                    with col3:
                        if 'result' in namespace and isinstance(namespace['result'], pd.DataFrame):
                            st.metric("Rows", len(namespace['result']))
                
                except Exception as e:
                    execution_time = time.time() - start_time
                    st.error(f"❌ Error: {str(e)}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Execution Time", format_execution_time(execution_time))
                    with col2:
                        st.metric("Status", "❌ Failed")

# Bottom tips
st.markdown("---")
st.markdown("### 💡 Pro Tips")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px;'>
        <h4 style='color: {COLORS['primary']}; margin-top: 0;'>Best Practices</h4>
        <ul>
            <li>Always validate input data</li>
            <li>Use type hints for clarity</li>
            <li>Implement error handling</li>
            <li>Add logging for debugging</li>
            <li>Write unit tests</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px;'>
        <h4 style='color: {COLORS['primary']}; margin-top: 0;'>Performance Tips</h4>
        <ul>
            <li>Use vectorized operations</li>
            <li>Avoid loops when possible</li>
            <li>Process data in chunks</li>
            <li>Leverage parallel processing</li>
            <li>Monitor memory usage</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
