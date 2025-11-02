"""
Engines - Pandas-focused data processing (Spark support available)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import time

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box, error_box, info_box
from odibi_core.learnodibi_ui.utils import initialize_session_state

# Page config
st.set_page_config(
    page_title="Engines - ODIBI CORE Studio",
    page_icon="⚙️",
    layout="wide"
)

apply_theme()
initialize_session_state()


def create_sample_data(size: str) -> pd.DataFrame:
    """Create sample dataset for comparison"""
    sizes = {
        "Small (100 rows)": 100,
        "Medium (1,000 rows)": 1000,
        "Large (10,000 rows)": 10000
    }
    
    n = sizes.get(size, 100)
    
    return pd.DataFrame({
        'id': range(n),
        'value': [i * 2 for i in range(n)],
        'category': [f'Cat_{i % 5}' for i in range(n)],
        'score': [50 + (i % 50) for i in range(n)]
    })


def run_pandas_operation(df: pd.DataFrame, operation: str) -> dict:
    """Run operation using Pandas"""
    start = time.time()
    
    try:
        if operation == "Filter":
            result = df[df['value'] > 50]
        elif operation == "Aggregate":
            result = df.groupby('category')['score'].mean()
        elif operation == "Transform":
            result = df.copy()
            result['value_squared'] = result['value'] ** 2
        elif operation == "Join":
            df2 = df.copy()
            df2['extra'] = df2['id'] * 10
            result = df.merge(df2[['id', 'extra']], on='id')
        else:
            result = df
        
        duration = time.time() - start
        
        return {
            'success': True,
            'result': result,
            'duration': duration,
            'rows': len(result),
            'engine': 'Pandas'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'duration': time.time() - start,
            'engine': 'Pandas'
        }


def run_spark_operation(df: pd.DataFrame, operation: str) -> dict:
    """Run operation using Spark (simulated for now)"""
    start = time.time()
    
    try:
        # Try to use PySpark if available
        try:
            from pyspark.sql import SparkSession
            from odibi_core.engine import SparkEngineContext
            
            # Note: This is simplified - real implementation would use SparkEngineContext
            spark = SparkSession.builder.master("local[1]").appName("LearnODIBI").getOrCreate()
            spark_df = spark.createDataFrame(df)
            
            if operation == "Filter":
                result_spark = spark_df.filter(spark_df.value > 50)
            elif operation == "Aggregate":
                result_spark = spark_df.groupBy('category').mean('score')
            elif operation == "Transform":
                from pyspark.sql.functions import col
                result_spark = spark_df.withColumn('value_squared', col('value') ** 2)
            elif operation == "Join":
                df2_spark = spark_df.select('id').withColumn('extra', col('id') * 10)
                result_spark = spark_df.join(df2_spark, on='id')
            else:
                result_spark = spark_df
            
            result = result_spark.toPandas()
            duration = time.time() - start
            
            return {
                'success': True,
                'result': result,
                'duration': duration,
                'rows': len(result),
                'engine': 'Spark'
            }
        
        except ImportError:
            # Fallback: simulate Spark behavior
            duration = time.time() - start + 0.1  # Add overhead
            result = run_pandas_operation(df, operation)
            result['duration'] = duration
            result['engine'] = 'Spark (simulated)'
            return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'duration': time.time() - start,
            'engine': 'Spark'
        }


def main():
    st.title("🐼 Pandas-Focused Processing")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>ODIBI CORE runs on Pandas by default • Spark support available for advanced use cases</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🐼 Pandas Examples", "📊 Engine Comparison", "⚡ Advanced: Spark"])
    
    with tab1:
        st.markdown("### 🐼 Interactive Pandas Examples")
        
        info_box("""
        **ODIBI CORE is built for Pandas!** All examples in this platform use Pandas by default.
        This makes it perfect for:
        - Local development and testing
        - Small to medium datasets (up to several GB)
        - Interactive data analysis
        - Quick prototyping
        """)
        
        st.markdown("##")
        st.markdown("#### Try Common Pandas Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_size = st.selectbox(
                "Dataset Size:",
                options=["Small (100 rows)", "Medium (1,000 rows)", "Large (10,000 rows)"],
                index=0
            )
        
        with col2:
            operation = st.selectbox(
                "Operation:",
                options=["Filter", "Aggregate", "Transform", "Join"],
                index=0
            )
        
        if st.button("▶️ Run with Pandas", type="primary", use_container_width=True):
            # Create dataset
            df = create_sample_data(dataset_size)
            
            st.markdown("##")
            st.markdown("### 📊 Results")
            
            # Run on Pandas
            with st.spinner("Running with Pandas..."):
                pandas_result = run_pandas_operation(df, operation)
            
            if pandas_result['success']:
                col_metrics, col_preview = st.columns([1, 2])
                
                with col_metrics:
                    st.metric("⏱️ Duration", f"{pandas_result['duration']:.4f}s")
                    st.metric("📊 Rows Output", pandas_result['rows'])
                    st.metric("🐼 Engine", "Pandas")
                
                with col_preview:
                    st.markdown("**Data Preview:**")
                    st.dataframe(pandas_result['result'].head(10), use_container_width=True)
                
                success_box(f"✅ Successfully processed {pandas_result['rows']:,} rows using Pandas!")
                
                # Show the code that was executed
                st.markdown("##")
                st.markdown("**📝 Pandas Code Used:**")
                
                if operation == "Filter":
                    code = """df_filtered = df[df['value'] > 50]"""
                elif operation == "Aggregate":
                    code = """df_agg = df.groupby('category')['score'].mean()"""
                elif operation == "Transform":
                    code = """df['value_squared'] = df['value'] ** 2"""
                elif operation == "Join":
                    code = """df_joined = df.merge(df2[['id', 'extra']], on='id')"""
                else:
                    code = "# No operation selected"
                
                st.code(code, language="python")
            else:
                error_box(f"Error: {pandas_result['error']}")
    
    with tab2:
        st.markdown("### 📊 Engine Differences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background: {COLORS['primary']}22; padding: 1.5rem; border-radius: 8px;'>
                <h3 style='color: {COLORS['primary']};'>🐼 Pandas Engine</h3>
                
                <h4>✅ Best For:</h4>
                <ul>
                    <li>Small to medium datasets (< 1GB)</li>
                    <li>Single-machine processing</li>
                    <li>Interactive analysis</li>
                    <li>Quick prototyping</li>
                </ul>
                
                <h4>⚡ Characteristics:</h4>
                <ul>
                    <li>In-memory processing</li>
                    <li>Eager execution</li>
                    <li>Simple API</li>
                    <li>Fast for small data</li>
                </ul>
                
                <h4>⚠️ Limitations:</h4>
                <ul>
                    <li>Limited by RAM</li>
                    <li>Single-threaded (mostly)</li>
                    <li>Not distributed</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: {COLORS['secondary']}22; padding: 1.5rem; border-radius: 8px;'>
                <h3 style='color: {COLORS['secondary']};'>⚡ Spark Engine</h3>
                
                <h4>✅ Best For:</h4>
                <ul>
                    <li>Large datasets (> 1GB)</li>
                    <li>Distributed processing</li>
                    <li>Production pipelines</li>
                    <li>Batch processing</li>
                </ul>
                
                <h4>⚡ Characteristics:</h4>
                <ul>
                    <li>Lazy evaluation</li>
                    <li>Distributed computing</li>
                    <li>Fault-tolerant</li>
                    <li>Scales horizontally</li>
                </ul>
                
                <h4>⚠️ Limitations:</h4>
                <ul>
                    <li>Setup overhead</li>
                    <li>Slower for small data</li>
                    <li>More complex</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("##")
        
        # Code comparison
        st.markdown("### 💻 Code Comparison")
        
        col_code1, col_code2 = st.columns(2)
        
        with col_code1:
            st.markdown("**Pandas Code:**")
            st.code("""
import pandas as pd
from odibi_core.engine import PandasEngineContext

# Initialize engine
engine = PandasEngineContext()

# Load data
df = pd.read_csv('data.csv')

# Transform
df_filtered = df[df['value'] > 50]
df_agg = df_filtered.groupby('category').mean()

# Save
df_agg.to_csv('output.csv')
""", language="python")
        
        with col_code2:
            st.markdown("**Spark Code:**")
            st.code("""
from pyspark.sql import SparkSession
from odibi_core.engine import SparkEngineContext

# Initialize Spark
spark = SparkSession.builder.getOrCreate()
engine = SparkEngineContext(spark)

# Load data
df = spark.read.csv('data.csv', header=True)

# Transform (lazy)
df_filtered = df.filter(df.value > 50)
df_agg = df_filtered.groupBy('category').mean()

# Save (triggers execution)
df_agg.write.csv('output.csv')
""", language="python")
    
    with tab3:
        st.markdown("### ⚡ Advanced: Spark Support")
        
        warning_box("""
        **Note:** Spark support is available but requires additional setup.
        Most users should stick with Pandas for local development and testing.
        """)
        
        st.markdown("##")
        
        st.markdown("#### 🎯 When to Consider Spark")
        
        info_box("""
        **Consider Spark when:**
        
        - Data size exceeds 10GB
        - You have a Spark cluster available
        - You need distributed processing
        - You require fault tolerance for production pipelines
        - Working with very large-scale data (100GB+)
        
        **Stick with Pandas when:**
        
        - Data fits in memory (< several GB)
        - Doing local development
        - Need quick interactive results
        - Prototyping and testing
        - Working on a single machine
        """)
        
        st.markdown("##")
        
        st.markdown("#### 🔧 Spark Setup (Optional)")
        
        st.markdown("""
        To use Spark with ODIBI CORE:
        
        1. **Install PySpark:**
        ```bash
        pip install pyspark
        ```
        
        2. **Configure Spark Session:**
        ```python
        from pyspark.sql import SparkSession
        from odibi_core.engine import SparkEngineContext
        
        # Create Spark session
        spark = SparkSession.builder \\
            .master("local[*]") \\
            .appName("ODIBI_CORE") \\
            .getOrCreate()
        
        # Use with ODIBI CORE
        engine = SparkEngineContext(spark)
        ```
        
        3. **Use in your pipeline** - Same node code works with both engines!
        """)
        
        st.markdown("##")
        
        st.markdown("#### 💡 Pandas Optimization Tips")
        
        st.markdown("""
        **For 99% of use cases, optimized Pandas is sufficient:**
        
        - ✅ Use vectorized operations (avoid loops)
        - ✅ Filter data early to reduce memory usage
        - ✅ Use appropriate dtypes (e.g., category for repeated strings)
        - ✅ Process data in chunks for very large files
        - ✅ Use `inplace=True` to save memory
        - ✅ Consider Dask for larger-than-memory data (easier than Spark!)
        
        **Example:**
        ```python
        # Good: Vectorized
        df['new_col'] = df['value'] * 2
        
        # Bad: Loop
        for idx, row in df.iterrows():
            df.at[idx, 'new_col'] = row['value'] * 2
        ```
        """)


if __name__ == "__main__":
    main()
