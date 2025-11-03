-- ============================================================
-- ODIBI_CORE Dual-Mode Showcase Database Initialization
-- ============================================================
-- Creates tables for storing SQL-based configurations

CREATE TABLE IF NOT EXISTS showcase_config (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    showcase_id INTEGER NOT NULL,
    showcase_name TEXT NOT NULL,
    layer TEXT NOT NULL,  -- bronze, silver, gold
    step_name TEXT NOT NULL,
    step_type TEXT NOT NULL,  -- read, transform, write, aggregate, join, pivot
    engine TEXT DEFAULT 'pandas',  -- pandas or spark
    value TEXT,  -- JSON string for step configuration
    params TEXT,  -- JSON string for parameters
    inputs TEXT,  -- JSON array of input table names
    outputs TEXT,  -- JSON array of output table names
    metadata TEXT,  -- JSON string for additional metadata
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS showcase_metadata (
    showcase_id INTEGER PRIMARY KEY,
    showcase_name TEXT NOT NULL,
    theme TEXT NOT NULL,
    description TEXT,
    data_sources TEXT,  -- JSON array
    expected_outputs TEXT,  -- JSON array
    learning_objectives TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for faster lookups
CREATE INDEX IF NOT EXISTS idx_showcase_config_showcase_id ON showcase_config(showcase_id);
CREATE INDEX IF NOT EXISTS idx_showcase_config_layer ON showcase_config(layer);
CREATE INDEX IF NOT EXISTS idx_showcase_config_enabled ON showcase_config(enabled);
