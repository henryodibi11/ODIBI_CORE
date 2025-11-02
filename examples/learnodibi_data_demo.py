"""
Demo script for ODIBI CORE learnodibi_data module.

This script demonstrates how to use the synthetic dataset generators
for teaching and demonstration purposes.
"""

from odibi_core.learnodibi_data import (
    get_dataset,
    list_datasets,
    generate_all_datasets,
    get_dataset_info
)


def main():
    print("=" * 70)
    print("ODIBI CORE - LearnODIBI Data Demo")
    print("=" * 70)
    print()
    
    # List available datasets
    print("1. Available Datasets")
    print("-" * 70)
    datasets = list_datasets()
    for i, name in enumerate(datasets, 1):
        print(f"   {i}. {name}")
    print()
    
    # Load and inspect each dataset
    print("2. Dataset Overview")
    print("-" * 70)
    
    for dataset_name in datasets:
        print(f"\n[{dataset_name.upper()}]")
        print("   " + "-" * 65)
        
        # Get dataset info
        info = get_dataset_info(dataset_name)
        print(f"   File exists: {info['file_exists']}")
        if info['file_exists']:
            size_kb = info['file_size_bytes'] / 1024
            print(f"   File size: {size_kb:.1f} KB")
        
        # Load dataset
        df = get_dataset(dataset_name)
        print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        
        # Show sample
        print(f"\n   Sample (first 3 rows):")
        print("   " + str(df.head(3).to_string(index=False)).replace('\n', '\n   '))
        print()
    
    # Energy dataset deep dive
    print("\n3. Energy Dataset Quality Analysis")
    print("-" * 70)
    energy_df = get_dataset("energy_demo")
    
    print(f"Total rows: {len(energy_df)}")
    print(f"\nFacilities: {', '.join(energy_df['facility_id'].unique())}")
    print(f"Date range: {energy_df['timestamp'].min()} to {energy_df['timestamp'].max()}")
    
    # Check for nulls (intentional quality issues)
    print("\nData Quality Issues (intentional for teaching):")
    numeric_cols = ['temperature_f', 'pressure_psi', 'flow_rate_gpm', 'power_kw', 'efficiency_pct']
    for col in numeric_cols:
        null_count = energy_df[col].isnull().sum()
        null_pct = (null_count / len(energy_df)) * 100
        if null_count > 0:
            print(f"   - {col}: {null_count} nulls ({null_pct:.1f}%)")
    
    # Summary statistics
    print("\nSummary Statistics:")
    print(energy_df[numeric_cols].describe().to_string())
    
    # Weather dataset analysis
    print("\n\n4. Weather Dataset Seasonal Patterns")
    print("-" * 70)
    weather_df = get_dataset("weather_demo")
    
    print(f"Total days: {weather_df['date'].nunique()}")
    print(f"Locations: {weather_df['location'].nunique()}")
    
    # Temperature by location
    print("\nAverage Temperature by Location:")
    for location in weather_df['location'].unique():
        loc_data = weather_df[weather_df['location'] == location]
        avg_temp = loc_data['temp_celsius'].mean()
        min_temp = loc_data['temp_celsius'].min()
        max_temp = loc_data['temp_celsius'].max()
        print(f"   {location}: {avg_temp:.1f}C (range: {min_temp:.1f}C to {max_temp:.1f}C)")
    
    # Maintenance dataset analysis
    print("\n\n5. Maintenance Dataset Analysis")
    print("-" * 70)
    maint_df = get_dataset("maintenance_demo")
    
    print(f"Total maintenance records: {len(maint_df)}")
    print(f"Unique equipment: {maint_df['equipment_id'].nunique()}")
    
    print("\nMaintenance Status Distribution:")
    status_counts = maint_df['status'].value_counts()
    for status, count in status_counts.items():
        pct = (count / len(maint_df)) * 100
        print(f"   {status}: {count} ({pct:.1f}%)")
    
    print("\nCost Summary:")
    print(f"   Total: ${maint_df['cost'].sum():,.2f}")
    print(f"   Average: ${maint_df['cost'].mean():,.2f}")
    print(f"   Min: ${maint_df['cost'].min():,.2f}")
    print(f"   Max: ${maint_df['cost'].max():,.2f}")
    
    print("\nDowntime Summary:")
    print(f"   Total: {maint_df['downtime_hours'].sum():.1f} hours")
    print(f"   Average: {maint_df['downtime_hours'].mean():.1f} hours")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  - Use these datasets in ODIBI CORE pipelines")
    print("  - Practice data validation and cleaning")
    print("  - Build transformation and aggregation nodes")
    print("  - Create visualizations and reports")
    print()


if __name__ == "__main__":
    main()
