"""
Quiz Database - Knowledge check questions for each phase
"""

QUIZZES = {
    "DEVELOPER_WALKTHROUGH_PHASE_1.md": [
        {
            "step": 5,
            "question": "What is the primary purpose of a ConnectNode?",
            "options": [
                "Transform data between formats",
                "Establish connections to data sources",
                "Store processed data",
                "Publish results to consumers"
            ],
            "correct": 1,
            "explanation": "ConnectNode is the foundational node that establishes and manages connections to data sources like databases, APIs, and file systems."
        },
        {
            "step": 10,
            "question": "In the 5 canonical nodes, which node is responsible for reading data into DataFrames?",
            "options": [
                "ConnectNode",
                "IngestNode",
                "TransformNode",
                "StoreNode"
            ],
            "correct": 1,
            "explanation": "IngestNode reads data from connected sources into Pandas or Spark DataFrames, making it available for transformation."
        },
        {
            "step": 15,
            "question": "What does the Medallion Architecture pattern consist of?",
            "options": [
                "Gold → Silver → Bronze",
                "Bronze → Silver → Gold",
                "Raw → Processed → Published",
                "Input → Transform → Output"
            ],
            "correct": 1,
            "explanation": "Medallion Architecture follows Bronze (raw) → Silver (validated/cleaned) → Gold (aggregated/business-ready) pattern."
        },
        {
            "step": 25,
            "question": "Why is composability important in ODIBI CORE?",
            "options": [
                "Makes code run faster",
                "Allows nodes to be reused and combined flexibly",
                "Reduces file size",
                "Simplifies debugging"
            ],
            "correct": 1,
            "explanation": "Composability allows nodes to be mixed, matched, and reused across different pipelines, making the framework flexible and maintainable."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_2.md": [
        {
            "step": 5,
            "question": "What are the two execution engines supported by ODIBI CORE?",
            "options": [
                "NumPy and Dask",
                "Pandas and Spark",
                "SQL and NoSQL",
                "Python and R"
            ],
            "correct": 1,
            "explanation": "ODIBI CORE supports both Pandas (for smaller datasets) and Spark (for distributed processing) as execution engines."
        },
        {
            "step": 10,
            "question": "What is the key benefit of dual-engine support?",
            "options": [
                "Faster execution speed",
                "Write once, run on both small and large datasets",
                "Better error messages",
                "Automatic optimization"
            ],
            "correct": 1,
            "explanation": "Dual-engine support means you write your logic once, and it works on both Pandas (local) and Spark (distributed) without code changes."
        },
        {
            "step": 15,
            "question": "How does ODIBI detect which engine to use?",
            "options": [
                "User manually specifies in config",
                "Automatically detects DataFrame type",
                "Random selection",
                "Always uses Pandas first"
            ],
            "correct": 1,
            "explanation": "ODIBI uses the detect_engine() function which inspects the DataFrame's module to determine if it's Pandas or Spark."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_3.md": [
        {
            "step": 3,
            "question": "What format does ODIBI use for configuration?",
            "options": [
                "YAML files",
                "JSON files and database tables",
                "XML files",
                "Python dictionaries only"
            ],
            "correct": 1,
            "explanation": "ODIBI uses JSON files for local configs and database tables for centralized configuration management."
        },
        {
            "step": 8,
            "question": "What is the benefit of config-driven development?",
            "options": [
                "Faster code execution",
                "Change pipeline behavior without code changes",
                "Smaller file sizes",
                "Automatic testing"
            ],
            "correct": 1,
            "explanation": "Config-driven means you can modify pipeline behavior, sources, transformations by changing config files instead of rewriting code."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_FUNCTIONS.md": [
        {
            "step": 3,
            "question": "What pattern does safe_divide() use to handle division by zero?",
            "options": [
                "Try-except blocks",
                "Conditional logic with fill_value fallback",
                "Ignoring the error",
                "Converting to strings"
            ],
            "correct": 1,
            "explanation": "safe_divide() uses conditional logic (np.where or F.when) to check for zero denominators and returns a fill_value instead."
        },
        {
            "step": 8,
            "question": "How does the detect_engine() function work?",
            "options": [
                "Reads a config file",
                "Inspects the DataFrame's module name",
                "Asks the user",
                "Checks system resources"
            ],
            "correct": 1,
            "explanation": "detect_engine() checks type(df).__module__ to see if it contains 'pandas' or 'pyspark' to determine the engine."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_9.md": [
        {
            "step": 5,
            "question": "What does the ODIBI SDK provide?",
            "options": [
                "Only CLI commands",
                "Programmatic API and CLI tools",
                "Just documentation",
                "Web interface"
            ],
            "correct": 1,
            "explanation": "The SDK provides both a Python API for programmatic use and CLI commands for terminal-based pipeline management."
        },
        {
            "step": 15,
            "question": "What command runs an ODIBI pipeline?",
            "options": [
                "python pipeline.py",
                "odibi run <config>",
                "spark-submit",
                "execute-pipeline"
            ],
            "correct": 1,
            "explanation": "The CLI command 'odibi run <config>' executes a pipeline based on the specified configuration file."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_6.md": [
        {
            "step": 3,
            "question": "What are the three main streaming modes in StreamManager?",
            "options": [
                "BATCH, REALTIME, SCHEDULED",
                "FILE_WATCH, INTERVAL, INCREMENTAL",
                "POLL, PUSH, HYBRID",
                "SYNC, ASYNC, PARALLEL"
            ],
            "correct": 1,
            "explanation": "StreamManager supports FILE_WATCH (monitor directories), INTERVAL (poll at fixed intervals), and INCREMENTAL (read new data since last watermark)."
        },
        {
            "step": 7,
            "question": "What is the purpose of a watermark in streaming?",
            "options": [
                "To prevent data duplication",
                "To track the last processed record for incremental reads",
                "To compress data",
                "To encrypt streaming data"
            ],
            "correct": 1,
            "explanation": "A watermark is a timestamp or value tracking the 'high water mark' of processed data, enabling incremental reads by only processing new data since the last watermark."
        },
        {
            "step": 10,
            "question": "What does CheckpointManager enable?",
            "options": [
                "Faster execution speed",
                "Resume pipeline execution from failure points",
                "Automatic debugging",
                "Schema validation"
            ],
            "correct": 1,
            "explanation": "CheckpointManager saves DAG state to disk, allowing pipelines to resume from failure points instead of restarting from scratch."
        },
        {
            "step": 14,
            "question": "How does ScheduleManager differ from external cron?",
            "options": [
                "It runs inside the pipeline process with integrated state management",
                "It's faster than cron",
                "It doesn't support intervals",
                "It only works on Windows"
            ],
            "correct": 0,
            "explanation": "ScheduleManager runs within the pipeline process, integrating with checkpoints and events, unlike external cron which is process-external."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_7.md": [
        {
            "step": 2,
            "question": "What is the primary benefit of CloudAdapter's factory pattern?",
            "options": [
                "It makes code run faster",
                "It provides a unified API for multiple cloud backends (Azure, S3, HDFS)",
                "It reduces memory usage",
                "It automatically encrypts data"
            ],
            "correct": 1,
            "explanation": "CloudAdapter uses the factory pattern to provide a single, consistent API across different cloud backends, making it easy to switch between Azure, S3, HDFS without changing client code."
        },
        {
            "step": 5,
            "question": "What are the three authentication methods supported by AzureAdapter?",
            "options": [
                "Username/Password, OAuth, API Key",
                "Account Key, Service Principal, Managed Identity",
                "SSH Key, Bearer Token, Basic Auth",
                "Certificate, SAML, Kerberos"
            ],
            "correct": 1,
            "explanation": "AzureAdapter supports: (1) Account Key authentication, (2) Service Principal with client credentials, and (3) Managed Identity/DefaultAzureCredential for Azure resources."
        },
        {
            "step": 8,
            "question": "How does CloudCacheManager determine cache keys?",
            "options": [
                "Using random UUIDs",
                "Based on file timestamps",
                "Using SHA256 hash of namespace, inputs, and version (content-addressed)",
                "Sequential integer IDs"
            ],
            "correct": 2,
            "explanation": "CloudCacheManager uses SHA256 hashing of the namespace, inputs, and version to create deterministic, content-addressed cache keys. Identical inputs always produce the same key."
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_8.md": [
        {
            "step": 2,
            "question": "What format does StructuredLogger use for log storage?",
            "options": [
                "JSON Array",
                "CSV",
                "JSON Lines (JSONL)",
                "Binary protocol buffers"
            ],
            "correct": 2,
            "explanation": "JSON Lines (JSONL) allows streaming reads and append-only writes without loading entire files into memory."
        },
        {
            "step": 4,
            "question": "What metric formats can MetricsExporter export to?",
            "options": [
                "Only JSON",
                "Prometheus, JSON, and Parquet",
                "Only Prometheus",
                "CSV and XML"
            ],
            "correct": 1,
            "explanation": "MetricsExporter supports Prometheus (for Grafana), JSON (for dashboards), and Parquet (for analysis)."
        },
        {
            "step": 6,
            "question": "What is the purpose of the EventBus pattern?",
            "options": [
                "Faster execution",
                "Decoupling components and separation of concerns",
                "Reduced memory usage",
                "Better error messages"
            ],
            "correct": 1,
            "explanation": "EventBus decouples components, allowing hooks to be added/removed without modifying core pipeline logic."
        },
        {
            "step": 12,
            "question": "What advantage does JSON Lines have over JSON Array for logging?",
            "options": [
                "Smaller file size",
                "Better encryption",
                "Streaming reads without loading entire file",
                "Faster parsing"
            ],
            "correct": 2,
            "explanation": "JSON Lines allows line-by-line streaming reads, while JSON Arrays require loading the entire file into memory."
        },
        {
            "step": 8,
            "question": "How do EventBus hook priorities work?",
            "options": [
                "Higher numbers execute first",
                "Lower numbers execute first (HIGH=0, NORMAL=1, LOW=2)",
                "Priorities are ignored",
                "Random execution order"
            ],
            "correct": 1,
            "explanation": "EventPriority uses IntEnum where lower numbers = higher priority. Hooks are sorted by priority and executed in ascending order (HIGH=0 runs before NORMAL=1)."
        },
        {
            "step": 10,
            "question": "What is the purpose of log rotation in StructuredLogger?",
            "options": [
                "To compress logs automatically",
                "To prevent log files from growing indefinitely",
                "To encrypt old logs",
                "To delete logs older than 30 days"
            ],
            "correct": 1,
            "explanation": "Log rotation creates new log files when the current file reaches max_size_mb, preventing unbounded file growth while preserving historical logs."
        }
    ]
}


def get_quizzes_for_lesson(lesson_id: str):
    """Get all quizzes for a specific lesson"""
    return QUIZZES.get(lesson_id, [])


def get_quiz_for_step(lesson_id: str, step_number: int):
    """Get quiz for a specific step if it exists"""
    quizzes = QUIZZES.get(lesson_id, [])
    for quiz in quizzes:
        if quiz["step"] == step_number:
            return quiz
    return None
