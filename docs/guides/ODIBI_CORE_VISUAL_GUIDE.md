# ODIBI CORE - Complete Visual Framework Guide

> **Your visual companion for mastering ODIBI CORE** - Maps, decision trees, and patterns to help you build data pipelines with confidence.

---

## 📖 Table of Contents

### Part 1: Framework Overview
1. [Big Picture: Complete Framework Architecture](#1-big-picture-complete-framework-architecture)
2. [Core Concepts Summary](#2-core-concepts-summary)

### Part 2: Visual Maps & Diagrams  
3. [Pipeline Execution Flow](#3-pipeline-execution-flow)
4. [Component Connection Map](#4-component-connection-map)
5. [Data Flow Through Nodes](#5-data-flow-through-nodes)
6. [Node Lifecycle](#6-node-lifecycle)

### Part 3: Decision Trees
7. [Which Node Should I Use?](#7-decision-tree-which-node-should-i-use)
8. [Pandas or Spark?](#8-decision-tree-pandas-or-spark)
9. [Which Format for My Data?](#9-decision-tree-which-format-for-my-data)
10. [How Do I Connect to X?](#10-decision-tree-how-do-i-connect-to-x)

### Part 4: System Maps
11. [Checkpoint & Resume System](#11-checkpoint--resume-system)
12. [Caching System](#12-caching-system)
13. [Event & Hook System](#13-event--hook-system)
14. [Observability Stack](#14-observability-stack)

### Part 5: Advanced Patterns
15. [Streaming & Scheduling](#15-streaming--scheduling)
16. [Distributed Execution](#16-distributed-execution)
17. [Story Generation](#17-story-generation)

### Part 6: Quick Reference
18. [Contract Implementation Cheatsheet](#18-contract-implementation-cheatsheet)
19. [Complete Pipeline Examples](#19-complete-pipeline-examples)

---

## Part 1: Framework Overview

### 1. Big Picture: Complete Framework Architecture

```mermaid
graph TB
    subgraph "USER CODE"
        Config[Step Configurations]
        UserPipeline[User Pipeline Definition]
    end

    subgraph "ORCHESTRATION LAYER"
        DAGBuilder[DAGBuilder<br/>Converts Steps → DAG]
        Orchestrator[Orchestrator<br/>Pipeline Manager]
        DAGExecutor[DAGExecutor<br/>Parallel Execution Engine]
        DistributedExecutor[DistributedExecutor<br/>Multi-Worker Execution]
    end

    subgraph "EXECUTION LAYER - Core Contracts"
        NodeBase[NodeBase Contract<br/>run data_map]
        EngineContext[EngineContext Contract<br/>read/write/sql/temp]
        
        subgraph "Node Implementations"
            ConnectNode[ConnectNode]
            IngestNode[IngestNode]
            TransformNode[TransformNode]
            StoreNode[StoreNode]
            PublishNode[PublishNode]
        end
        
        subgraph "Engine Implementations"
            PandasContext[PandasEngineContext<br/>DuckDB SQL]
            SparkContext[SparkEngineContext<br/>Spark SQL]
        end
    end

    subgraph "I/O LAYER"
        Readers[Readers<br/>CSV/Parquet/SQL/Delta]
        Writers[Writers<br/>CSV/Parquet/Delta]
        CloudAdapter[CloudAdapter<br/>Azure/S3/HDFS/Kafka]
    end

    subgraph "STATE MANAGEMENT"
        DataMap[data_map<br/>logical_name → DataFrame]
        Tracker[Tracker<br/>Snapshots & Lineage]
        CheckpointMgr[CheckpointManager<br/>Save/Resume State]
        CacheMgr[CacheManager<br/>Output Caching]
    end

    subgraph "OBSERVABILITY"
        EventBus[EventBus<br/>Lifecycle Events]
        Metrics[MetricsManager<br/>Performance Tracking]
        StoryGen[StoryGenerator<br/>HTML Reports]
        Logger[StructuredLogger]
    end

    subgraph "ADVANCED FEATURES"
        Scheduler[ScheduleManager<br/>Cron & Events]
        StreamMgr[StreamManager<br/>Continuous Processing]
        FuncRegistry[Function Registry<br/>Transform Functions]
        SDK[SDK Tools<br/>Validator, Docs]
    end

    Config --> DAGBuilder
    UserPipeline --> Orchestrator
    DAGBuilder --> Orchestrator
    Orchestrator --> DAGExecutor
    DAGExecutor --> DistributedExecutor
    
    DAGExecutor --> NodeBase
    NodeBase --> ConnectNode
    NodeBase --> IngestNode
    NodeBase --> TransformNode
    NodeBase --> StoreNode
    NodeBase --> PublishNode
    
    ConnectNode --> EngineContext
    IngestNode --> EngineContext
    TransformNode --> EngineContext
    StoreNode --> EngineContext
    PublishNode --> EngineContext
    
    EngineContext --> PandasContext
    EngineContext --> SparkContext
    
    PandasContext --> Readers
    SparkContext --> Readers
    PandasContext --> Writers
    SparkContext --> Writers
    PandasContext --> CloudAdapter
    SparkContext --> CloudAdapter
    
    NodeBase --> DataMap
    DAGExecutor --> DataMap
    NodeBase --> Tracker
    DAGExecutor --> CheckpointMgr
    DAGExecutor --> CacheMgr
    
    DAGExecutor --> EventBus
    EventBus --> Metrics
    EventBus --> StoryGen
    EventBus --> Logger
    
    Orchestrator --> Scheduler
    Orchestrator --> StreamMgr
    TransformNode --> FuncRegistry
    
    classDef userCode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef orchestration fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef execution fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef io fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef state fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef observability fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef advanced fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    
    class Config,UserPipeline userCode
    class DAGBuilder,Orchestrator,DAGExecutor,DistributedExecutor orchestration
    class NodeBase,EngineContext,ConnectNode,IngestNode,TransformNode,StoreNode,PublishNode,PandasContext,SparkContext execution
    class Readers,Writers,CloudAdapter io
    class DataMap,Tracker,CheckpointMgr,CacheMgr state
    class EventBus,Metrics,StoryGen,Logger observability
    class Scheduler,StreamMgr,FuncRegistry,SDK advanced
```

### 2. Core Concepts Summary

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **User Code** | Define pipeline steps and configuration | Step configurations (JSON/SQLite/CSV) |
| **Orchestration** | Convert steps to DAG and manage execution | DAGBuilder, Orchestrator, DAGExecutor |
| **Execution** | Run individual operations | 5 Node types, 2 Engine contexts |
| **I/O** | Read/write data | Readers, Writers, CloudAdapter |
| **State** | Track data and execution state | data_map, Tracker, Checkpoints, Cache |
| **Observability** | Monitor and report | Events, Metrics, Stories, Logs |
| **Advanced** | Automation and scaling | Scheduler, Streaming, Functions, SDK |

---

## Part 2: Visual Maps & Diagrams

### 3. Pipeline Execution Flow

```mermaid
flowchart TD
    Start([User Defines Steps]) --> LoadConfig[Load Configuration<br/>JSON/SQLite/CSV]
    LoadConfig --> Validate{Valid Config?}
    Validate -->|No| Error1[❌ Show Validation Errors]
    Validate -->|Yes| BuildDAG[DAGBuilder<br/>Build Dependency Graph]
    
    BuildDAG --> CheckCycles{Circular<br/>Dependencies?}
    CheckCycles -->|Yes| Error2[❌ Circular Dependency Error]
    CheckCycles -->|No| CreateOrch[Create Orchestrator<br/>+ Context + Tracker + Events]
    
    CreateOrch --> InitExec[Initialize DAGExecutor<br/>with Checkpoint & Cache]
    
    InitExec --> CheckResume{Resume from<br/>Checkpoint?}
    CheckResume -->|Yes| LoadCP[Load Checkpoint State]
    CheckResume -->|No| FreshStart[Fresh Execution]
    
    LoadCP --> StartExec
    FreshStart --> StartExec[Start Execution]
    
    StartExec --> EventStart[Emit: pipeline_start]
    EventStart --> InitDataMap[Initialize data_map = empty]
    
    InitDataMap --> GetReady[Get Ready Nodes<br/>no dependencies]
    
    GetReady --> HasReady{Ready nodes<br/>available?}
    HasReady -->|No| AllDone{All nodes<br/>completed?}
    AllDone -->|No| Deadlock[❌ Execution Deadlock]
    AllDone -->|Yes| Success
    
    HasReady -->|Yes| CheckCache{Cache<br/>available?}
    CheckCache -->|Hit| UseCache[Use Cached Output]
    CheckCache -->|Miss| RunNode[Execute Node.run data_map]
    
    RunNode --> EventNodeStart[Emit: node_start]
    EventNodeStart --> TrackerStart[Tracker: start_step]
    TrackerStart --> NodeExec[Node Execution Logic]
    
    NodeExec --> NodeSuccess{Success?}
    NodeSuccess -->|No| Retry{Retry?}
    Retry -->|Yes, under limit| RunNode
    Retry -->|No, max retries| NodeFailed[Mark FAILED<br/>Emit: node_error]
    NodeSuccess -->|Yes| NodeDone
    
    NodeDone[Mark SUCCESS] --> TrackerEnd[Tracker: end_step]
    TrackerEnd --> SaveCache[Save to Cache]
    SaveCache --> EventNodeEnd[Emit: node_complete]
    
    UseCache --> EventNodeEnd
    NodeFailed --> EventNodeEnd
    
    EventNodeEnd --> SaveCP{Auto<br/>Checkpoint?}
    SaveCP -->|Yes| CreateCP[Save Checkpoint]
    SaveCP -->|No| UpdateDeps
    CreateCP --> UpdateDeps[Update Dependencies]
    
    UpdateDeps --> GetReady
    
    Success[✅ Pipeline Complete] --> EventEnd[Emit: pipeline_complete]
    EventEnd --> ExportMetrics[Export Metrics]
    ExportMetrics --> GenStory[Generate HTML Story]
    GenStory --> ReturnResult[Return OrchestrationResult]
    
    Deadlock --> ReturnResult
    Error1 --> ReturnResult
    Error2 --> ReturnResult
    
    classDef successNode fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    classDef errorNode fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    classDef processNode fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    classDef decisionNode fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    
    class Success,NodeDone,UseCache successNode
    class Error1,Error2,Deadlock,NodeFailed errorNode
    class RunNode,BuildDAG,CreateOrch,InitExec,TrackerStart,TrackerEnd,SaveCache,SaveCP,ExportMetrics,GenStory processNode
    class Validate,CheckCycles,CheckResume,HasReady,AllDone,CheckCache,NodeSuccess,Retry,SaveCP decisionNode
```

### 4. Component Connection Map

```mermaid
graph LR
    subgraph "Node Execution Context"
        Node[Any Node<br/>ConnectNode, IngestNode, etc.]
        Step[Step Config<br/>layer, name, type, value, params, inputs, outputs]
        Context[EngineContext<br/>PandasEngineContext or SparkEngineContext]
        Tracker[Tracker<br/>Execution snapshots]
        Events[EventEmitter<br/>Lifecycle hooks]
        DataMap[data_map<br/>Dictionary of DataFrames]
    end
    
    subgraph "Engine Operations"
        Read[context.read source]
        Write[context.write df, target]
        SQL[context.execute_sql query]
        RegTemp[context.register_temp name, df]
        Secret[context.get_secret key]
    end
    
    subgraph "External Systems"
        Files[(File System<br/>CSV, Parquet, JSON)]
        Cloud[(Cloud Storage<br/>Azure, S3)]
        DB[(Databases<br/>SQL, SQLite)]
        Secrets[(Secret Store<br/>Dict or Callable)]
    end
    
    Node -->|configured with| Step
    Node -->|uses| Context
    Node -->|logs to| Tracker
    Node -->|emits to| Events
    Node -->|reads from & writes to| DataMap
    
    Context -->|implements| Read
    Context -->|implements| Write
    Context -->|implements| SQL
    Context -->|implements| RegTemp
    Context -->|implements| Secret
    
    Read -->|accesses| Files
    Read -->|accesses| Cloud
    Read -->|accesses| DB
    Write -->|accesses| Files
    Write -->|accesses| Cloud
    Write -->|accesses| DB
    Secret -->|accesses| Secrets
    
    classDef coreNode fill:#e1bee7,stroke:#4a148c,stroke-width:2px
    classDef operationNode fill:#c5e1a5,stroke:#33691e,stroke-width:2px
    classDef externalNode fill:#ffccbc,stroke:#bf360c,stroke-width:2px
    
    class Node,Step,Context,Tracker,Events,DataMap coreNode
    class Read,Write,SQL,RegTemp,Secret operationNode
    class Files,Cloud,DB,Secrets externalNode
```

### 5. Data Flow Through Nodes

```mermaid
sequenceDiagram
    participant DM as data_map
    participant IN as IngestNode
    participant TN as TransformNode
    participant SN as StoreNode
    participant CTX as EngineContext
    participant FS as File System

    Note over DM: Initial: data_map = {}
    
    rect rgb(230, 247, 255)
    Note over IN: INGEST PHASE
    IN->>CTX: context.read("data.csv")
    CTX->>FS: Read CSV file
    FS-->>CTX: Return DataFrame
    CTX-->>IN: df
    IN->>DM: data_map["raw_data"] = df
    Note over DM: data_map = {"raw_data": df}
    end
    
    rect rgb(255, 243, 224)
    Note over TN: TRANSFORM PHASE
    TN->>DM: Read data_map["raw_data"]
    DM-->>TN: df (bronze)
    TN->>CTX: context.register_temp("bronze", df)
    TN->>CTX: context.execute_sql("SELECT * FROM bronze WHERE value > 80")
    CTX-->>TN: filtered_df
    TN->>DM: data_map["filtered_data"] = filtered_df
    Note over DM: data_map = {"raw_data": df, "filtered_data": filtered_df}
    end
    
    rect rgb(232, 245, 233)
    Note over SN: STORE PHASE
    SN->>DM: Read data_map["filtered_data"]
    DM-->>SN: filtered_df
    SN->>CTX: context.write(filtered_df, "output.parquet")
    CTX->>FS: Write Parquet file
    Note over DM: data_map unchanged (store is side effect)
    end
```

**Key Points:**
- `data_map` is a shared dictionary: `Dict[str, DataFrame]`
- Keys are **dataset keys** (e.g., "raw_data", "filtered_data")
- Step `inputs`/`outputs` use **logical names** that map to dataset keys
- IngestNode adds to `data_map`
- TransformNode reads from and writes to `data_map`
- StoreNode/PublishNode read from `data_map` but don't modify it

### 6. Node Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PENDING: Node Created
    
    PENDING --> RUNNING: DAGExecutor selects node
    
    RUNNING --> CheckCache: Check if cached
    CheckCache --> CACHED: Cache Hit
    CheckCache --> Executing: Cache Miss
    
    Executing --> TrackerStart: tracker.start_step()
    TrackerStart --> SnapshotBefore: tracker.snapshot("before")
    SnapshotBefore --> NodeRun: node.run(data_map)
    
    NodeRun --> NodeSuccess: Execution succeeds
    NodeRun --> NodeError: Execution fails
    
    NodeSuccess --> SnapshotAfter: tracker.snapshot("after")
    SnapshotAfter --> TrackerEnd: tracker.end_step("success")
    TrackerEnd --> SaveCache: cache_manager.save()
    SaveCache --> EmitSuccess: events.emit("node_complete")
    
    NodeError --> CheckRetry: Retry available?
    CheckRetry --> TrackerStart: Yes, retry
    CheckRetry --> TrackerFail: No, max retries reached
    TrackerFail --> EmitError: events.emit("node_error")
    
    EmitSuccess --> SUCCESS
    EmitError --> FAILED
    CACHED --> SUCCESS
    
    SUCCESS --> Checkpoint: Auto checkpoint?
    Checkpoint --> [*]
    FAILED --> Checkpoint
```

**Node States:**
- **PENDING**: Node created, waiting for dependencies
- **RUNNING**: Node selected for execution
- **CACHED**: Output retrieved from cache (skip execution)
- **SUCCESS**: Execution completed successfully
- **FAILED**: Execution failed after max retries

---

## Part 3: Decision Trees

### 7. Decision Tree: Which Node Should I Use?

```mermaid
flowchart TD
    Start{What do you<br/>want to do?} --> Connect{Establish a<br/>connection?}
    Start --> ReadData{Read data from<br/>a source?}
    Start --> Transform{Transform or<br/>modify data?}
    Start --> SaveData{Save data to<br/>storage layer?}
    Start --> Export{Export to external<br/>system?}
    
    Connect -->|Yes| ConnectNode[✅ ConnectNode<br/>Establishes database/API/storage connections<br/>No data outputs, only side effects]
    
    ReadData -->|Yes| IngestNode[✅ IngestNode<br/>Reads from CSV, Parquet, SQL, APIs<br/>Writes to data_map]
    
    Transform -->|Yes| TransformType{SQL or<br/>Function?}
    TransformType -->|SQL| TransformSQL[✅ TransformNode type=sql<br/>Register temp tables, execute SQL]
    TransformType -->|Function| TransformFunc[✅ TransformNode type=function<br/>Call custom Python function]
    
    SaveData -->|Yes| StoreLoc{Save where?}
    StoreLoc -->|Bronze/Silver/Gold<br/>local storage| StoreNode[✅ StoreNode<br/>Persist to Parquet/Delta/CSV locally]
    StoreLoc -->|External system<br/>database/API| PublishNode1[✅ PublishNode<br/>Alternative for external writes]
    
    Export -->|Yes| PublishNode[✅ PublishNode<br/>Export to Delta Lake, databases, APIs<br/>Similar to StoreNode but for downstream systems]
    
    classDef nodeClass fill:#b2dfdb,stroke:#00695c,stroke-width:2px
    class ConnectNode,IngestNode,TransformSQL,TransformFunc,StoreNode,PublishNode,PublishNode1 nodeClass
```

**Quick Reference:**

| I want to... | Use This Node | Example |
|--------------|---------------|---------|
| Connect to PostgreSQL | ConnectNode | `value="postgresql://host:5432/db"` |
| Read a CSV file | IngestNode | `value="data/input.csv"` |
| Filter data with SQL | TransformNode (SQL) | `value="SELECT * FROM bronze WHERE x > 10"` |
| Apply custom calculation | TransformNode (Function) | `value="thermo.steam.calc_enthalpy"` |
| Save to Bronze layer | StoreNode | `value="bronze/data.parquet"` |
| Export to Delta Lake | PublishNode | `value="delta_table_name"` |

### 8. Decision Tree: Pandas or Spark?

```mermaid
flowchart TD
    Start{Which engine<br/>should I use?} --> DataSize{How much<br/>data?}
    
    DataSize -->|< 1 GB| SmallData
    DataSize -->|1-10 GB| MediumData
    DataSize -->|> 10 GB| LargeData
    
    SmallData{Local dev<br/>or production?} -->|Local dev| Pandas1[✅ Pandas<br/>Fast, simple, DuckDB SQL]
    SmallData -->|Production| Pandas2[✅ Pandas<br/>Unless distributed needed]
    
    MediumData{Need distributed<br/>processing?} -->|No| Pandas3[✅ Pandas<br/>Still fast enough]
    MediumData -->|Yes| Spark1[✅ Spark<br/>Scale horizontally]
    
    LargeData{Running on<br/>cluster?} -->|Yes| Spark2[✅ Spark<br/>Distributed, partitioned]
    LargeData -->|No, local| Spark3[✅ Spark Local<br/>master=local[*]]
    
    Start --> Features{Need specific<br/>features?}
    Features -->|Delta Lake| SparkDelta[✅ Spark<br/>Native Delta support]
    Features -->|DuckDB SQL| PandasDuck[✅ Pandas<br/>Fast in-memory SQL]
    Features -->|Databricks| SparkDB[✅ Spark<br/>Native integration]
    Features -->|Simple transforms| PandasSimple[✅ Pandas<br/>Easier API]
    
    classDef pandasNode fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef sparkNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class Pandas1,Pandas2,Pandas3,PandasDuck,PandasSimple pandasNode
    class Spark1,Spark2,Spark3,SparkDelta,SparkDB sparkNode
```

**Comparison Matrix:**

| Factor | Pandas | Spark |
|--------|--------|-------|
| **Data Size** | < 1-10 GB | > 10 GB or distributed |
| **SQL Engine** | DuckDB (in-memory) | Spark SQL (distributed) |
| **Development** | Faster, simpler API | More complex, cluster setup |
| **Production** | Single-node workloads | Multi-node clusters |
| **Delta Lake** | Read as Parquet | Native support with ACID |
| **Databricks** | Limited | Fully integrated |
| **Memory** | Limited to RAM | Distributed across workers |

### 9. Decision Tree: Which Format for My Data?

```mermaid
flowchart TD
    Start{What format<br/>should I use?} --> Use{What's your<br/>use case?}
    
    Use -->|Development/Testing| DevFormat{Human<br/>readable?}
    DevFormat -->|Yes| CSV1[✅ CSV<br/>Easy to inspect, edit]
    DevFormat -->|No, performance| Parquet1[✅ Parquet<br/>Fast, columnar]
    
    Use -->|Production Bronze| BronzeFormat{Source<br/>format?}
    BronzeFormat -->|CSV source| CSV2[✅ CSV<br/>Keep original format]
    BronzeFormat -->|Any source| Parquet2[✅ Parquet<br/>Standardize to Parquet]
    
    Use -->|Production Silver/Gold| ProdFormat{Need ACID<br/>transactions?}
    ProdFormat -->|Yes| Delta[✅ Delta Lake<br/>ACID, time travel, Spark]
    ProdFormat -->|No| ParquetProd[✅ Parquet<br/>Fast, columnar, efficient]
    
    Use -->|Analytics/ML| Analytics{Query<br/>patterns?}
    Analytics -->|Column-heavy| ParquetAnal[✅ Parquet<br/>Columnar format]
    Analytics -->|Nested data| ParquetNest[✅ Parquet<br/>Supports nested schemas]
    
    Use -->|Streaming| Streaming{Real-time?}
    Streaming -->|Yes| JSON1[✅ JSON<br/>Line-delimited, streaming]
    Streaming -->|No, micro-batch| Parquet3[✅ Parquet<br/>Efficient batches]
    
    Use -->|External Exchange| Exchange{Recipient<br/>requirements?}
    Exchange -->|Excel-compatible| CSV3[✅ CSV<br/>Universal compatibility]
    Exchange -->|Big data tools| Parquet4[✅ Parquet or Delta<br/>Industry standard]
    
    classDef csvNode fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef parquetNode fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    classDef deltaNode fill:#b2ebf2,stroke:#00695c,stroke-width:2px
    classDef jsonNode fill:#f8bbd0,stroke:#c2185b,stroke-width:2px
    
    class CSV1,CSV2,CSV3 csvNode
    class Parquet1,Parquet2,ParquetProd,ParquetAnal,ParquetNest,Parquet3,Parquet4 parquetNode
    class Delta deltaNode
    class JSON1 jsonNode
```

**Format Comparison:**

| Format | Best For | Pros | Cons |
|--------|----------|------|------|
| **CSV** | Human-readable, simple data | Universal, editable, Excel-compatible | Large files, no schema, text-based |
| **JSON** | Nested data, APIs, streaming | Flexible schema, nested structures | Larger than binary formats |
| **Parquet** | Analytics, large datasets | Columnar, compressed, fast queries | Not human-readable |
| **Delta** | Production pipelines, ACID | Versioning, time travel, ACID | Spark-specific (limited Pandas) |
| **AVRO** | Schema evolution, Kafka | Schema registry, compact | Less common than Parquet |

### 10. Decision Tree: How Do I Connect to X?

```mermaid
flowchart TD
    Start{What do you<br/>need to connect to?} --> CloudStorage{Cloud<br/>Storage?}
    Start --> Database{Database?}
    Start --> API{API/External<br/>System?}
    
    CloudStorage -->|Azure Blob/ADLS| Azure[✅ CloudAdapter.create "azure"<br/>account_name, account_key or<br/>service principal]
    CloudStorage -->|AWS S3| S3[✅ CloudAdapter.create "s3"<br/>bucket, region, access_key<br/>⚠️ Simulation stub in Phase 7]
    CloudStorage -->|HDFS| HDFS[✅ CloudAdapter.create "hdfs"<br/>namenode_host, port<br/>⚠️ Simulation stub]
    
    Database -->|Engine?| EngineChoice{Pandas or<br/>Spark?}
    EngineChoice -->|Pandas| PandasDB{Database<br/>type?}
    EngineChoice -->|Spark| SparkDB{Database<br/>type?}
    
    PandasDB -->|SQLite| SQLite[✅ pandas_ctx.read source.db<br/>source_type="sqlite", table="..."]
    PandasDB -->|PostgreSQL/MySQL/etc| SQLAlchemy[✅ pandas_ctx.read ...<br/>source_type="sql"<br/>connection_string="...", query="..."]
    
    SparkDB -->|Any JDBC| JDBC[✅ spark_ctx.read ...<br/>source_type="jdbc"<br/>jdbc_url, table, driver, user, password]
    
    API -->|REST API| REST[✅ IngestNode<br/>Custom reader or use requests library<br/>Store credentials in secrets]
    API -->|Kafka| Kafka[✅ CloudAdapter.create "kafka"<br/>bootstrap_servers, topic<br/>⚠️ Simulation stub]
    
    classDef cloudNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef dbNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef apiNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class Azure,S3,HDFS cloudNode
    class SQLite,SQLAlchemy,JDBC dbNode
    class REST,Kafka apiNode
```

**Connection Examples:**

```python
# Azure ADLS
azure = CloudAdapter.create(
    "azure",
    account_name="mystorageaccount",
    account_key="...",  # or use service principal
    simulate=False
)
df = azure.read("container/path/data.parquet")

# PostgreSQL (Pandas)
pandas_ctx = PandasEngineContext(secrets={"db_pass": "secret"})
df = pandas_ctx.read(
    "db_connection",
    source_type="sql",
    connection_string="postgresql://user:pass@host:5432/db",
    query="SELECT * FROM table"
)

# PostgreSQL (Spark)
spark_ctx = SparkEngineContext()
df = spark_ctx.read(
    "table_name",
    source_type="jdbc",
    jdbc_url="jdbc:postgresql://host:5432/db",
    table="users",
    driver="org.postgresql.Driver",
    user="admin",
    password=spark_ctx.get_secret("db_pass")
)
```

---

## Part 4: System Maps

### 11. Checkpoint & Resume System

```mermaid
flowchart LR
    subgraph "During Execution"
        Exec[DAGExecutor Running] --> NodeComplete{Node<br/>Complete?}
        NodeComplete -->|Yes| AutoCP{Auto<br/>Checkpoint?}
        AutoCP -->|Yes, mode=AUTO| SaveCP[CheckpointManager.save]
        AutoCP -->|Yes, mode=LAYER| CheckLayer{Layer<br/>complete?}
        CheckLayer -->|Yes| SaveCP
        AutoCP -->|No| Continue
        CheckLayer -->|No| Continue
        SaveCP --> SaveState[Save to checkpoint_id.json]
    end
    
    subgraph "Checkpoint Data"
        SaveState --> CPData[Checkpoint<br/>completed_nodes<br/>pending_nodes<br/>failed_nodes<br/>iteration<br/>metadata]
    end
    
    subgraph "Resume Execution"
        Resume[Resume Request] --> LoadCP[CheckpointManager.load latest]
        LoadCP --> RestoreState[Restore completed/pending/failed]
        RestoreState --> SkipDone[Skip completed nodes]
        SkipDone --> RetryFailed{Retry<br/>failed?}
        RetryFailed -->|Yes| RerunFailed[Rerun failed nodes]
        RetryFailed -->|No| ContinuePending[Continue with pending]
        RerunFailed --> ContinuePending
        ContinuePending --> Exec
    end
    
    classDef execNode fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    classDef cpNode fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef resumeNode fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    
    class Exec,NodeComplete,Continue execNode
    class SaveCP,SaveState,CPData,AutoCP,CheckLayer cpNode
    class Resume,LoadCP,RestoreState,SkipDone,RetryFailed,RerunFailed,ContinuePending resumeNode
```

**Checkpoint Modes:**

| Mode | When to Checkpoint | Use Case |
|------|-------------------|----------|
| **MANUAL** | User-triggered | Full control over checkpoint timing |
| **AUTO** | After each successful node | Maximum fault tolerance, more overhead |
| **INTERVAL** | At regular intervals | Balance between safety and performance |
| **LAYER** | After completing each DAG layer | Natural checkpoints at medallion boundaries |

**Resume Workflow:**

```python
# Initial run (fails at node 5)
executor = DAGExecutor(dag, context, tracker, events, checkpoint_manager=cp_mgr)
result = executor.execute()  # Fails, checkpoint saved

# Resume from checkpoint
cp_mgr = CheckpointManager()
checkpoint = cp_mgr.load_latest("pipeline_name")
executor = DAGExecutor(
    dag, context, tracker, events,
    checkpoint_manager=cp_mgr,
    resume_from=checkpoint  # Resume from saved state
)
result = executor.execute()  # Skips completed, retries failed, continues pending
```

### 12. Caching System

```mermaid
flowchart TD
    NodeStart[Node Selected for Execution] --> CheckCache{Cache<br/>Enabled?}
    CheckCache -->|No| Execute[Execute Node]
    CheckCache -->|Yes| CalcKey[Calculate Cache Key<br/>step_name + params + input_hash]
    
    CalcKey --> LookupCache{Cache<br/>Exists?}
    LookupCache -->|No, Cache Miss| Execute
    LookupCache -->|Yes, Cache Hit| ValidCache{Cache<br/>Valid?}
    
    ValidCache -->|No, Expired/Invalid| Execute
    ValidCache -->|Yes| LoadCache[Load Cached Output]
    LoadCache --> RestoreDataMap[Restore to data_map]
    RestoreDataMap --> IncrHit[Metrics: cache_hit++]
    IncrHit --> SkipExec[✅ Skip Execution]
    
    Execute --> RunNode[node.run data_map]
    RunNode --> Success{Success?}
    Success -->|No| IncrMiss[Metrics: cache_miss++]
    Success -->|Yes| SaveOutput[Save Output to Cache]
    SaveOutput --> IncrMiss
    IncrMiss --> Continue[Continue Execution]
    
    SkipExec --> Continue
    
    classDef cacheHit fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    classDef cacheMiss fill:#ffccbc,stroke:#d84315,stroke-width:2px
    classDef processNode fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    
    class LoadCache,RestoreDataMap,IncrHit,SkipExec cacheHit
    class Execute,RunNode,SaveOutput,IncrMiss cacheMiss
    class NodeStart,CheckCache,CalcKey,LookupCache,ValidCache,Success,Continue processNode
```

**Cache Types:**

| Cache Type | Storage | Use Case | Pros | Cons |
|------------|---------|----------|------|------|
| **Local Cache** | Disk (checkpoint_dir/) | Development, single-node | Fast, simple | Not shared across runs |
| **Cloud Cache** | Azure Blob/S3 | Distributed, multi-run | Shared, persistent | Network overhead |
| **Memory Cache** | In-memory dict | Streaming, within-run | Fastest | Lost on process exit |

**Cache Configuration:**

```python
# Local disk cache
cache_mgr = CacheManager(cache_dir="cache/")
executor = DAGExecutor(dag, context, tracker, events, cache_manager=cache_mgr, use_cache=True)

# Cloud cache (Azure)
cloud_cache = CloudCacheManager(
    cloud_adapter=azure_adapter,
    cache_prefix="pipeline_cache/"
)
executor = DAGExecutor(dag, context, tracker, events, cache_manager=cloud_cache, use_cache=True)
```

### 13. Event & Hook System

```mermaid
sequenceDiagram
    participant Exec as DAGExecutor
    participant Bus as EventBus
    participant Hook1 as LogRotationHook
    participant Hook2 as MetricsExportHook
    participant Hook3 as Custom Alert Hook
    
    Note over Bus: Hooks registered at startup
    Bus->>Hook1: register("pipeline_complete", priority=HIGH)
    Bus->>Hook2: register("pipeline_complete", priority=MEDIUM)
    Bus->>Hook3: register("pipeline_complete", priority=LOW)
    
    rect rgb(230, 247, 255)
    Note over Exec: Pipeline Execution Start
    Exec->>Bus: emit("pipeline_start", {pipeline_name, start_time})
    Bus->>Hook1: Execute (if registered for pipeline_start)
    end
    
    rect rgb(255, 243, 224)
    Note over Exec: Node Execution
    Exec->>Bus: emit("node_start", {step_name, layer})
    Exec->>Bus: emit("node_complete", {step_name, duration, state})
    end
    
    rect rgb(232, 245, 233)
    Note over Exec: Pipeline Complete
    Exec->>Bus: emit("pipeline_complete", {success_count, failed_count, ...})
    Bus->>Hook1: Execute (priority=HIGH)
    Hook1-->>Bus: Done
    Bus->>Hook2: Execute (priority=MEDIUM)
    Hook2-->>Bus: Done
    Bus->>Hook3: Execute (priority=LOW)
    Hook3-->>Bus: Done (custom alert sent)
    end
```

**Event Types:**

| Event | When Emitted | Event Data |
|-------|-------------|------------|
| `pipeline_start` | Pipeline execution begins | `pipeline_name`, `start_time` |
| `pipeline_complete` | Pipeline finishes (success or partial) | `pipeline_name`, `success_count`, `failed_count`, `duration_ms` |
| `pipeline_error` | Pipeline encounters fatal error | `pipeline_name`, `error_message` |
| `node_start` | Node execution begins | `step_name`, `layer` |
| `node_complete` | Node completes successfully | `step_name`, `layer`, `duration_ms`, `state` |
| `node_error` | Node fails | `step_name`, `error_message` |

**Hook Registration:**

```python
from odibi_core.observability import EventBus, EventPriority

bus = EventBus()

# Built-in hook: Summary
bus.register_hook("pipeline_complete", bus.create_summary_hook())

# Built-in hook: Metrics export
bus.register_hook("pipeline_complete", bus.create_metrics_export_hook("metrics/"))

# Custom hook: Alerts
def send_alert(event_data):
    if event_data.get("failed_count", 0) > 0:
        print(f"🚨 ALERT: {event_data['failed_count']} nodes failed!")
        # Send email, Slack, PagerDuty, etc.

bus.register_hook("pipeline_complete", send_alert, priority=EventPriority.HIGH)
```

### 14. Observability Stack

```mermaid
graph TB
    subgraph "Data Collection"
        Node[Node Execution] --> Tracker[Tracker<br/>Snapshots & Lineage]
        Node --> Metrics[MetricsManager<br/>Performance Metrics]
        Node --> Events[EventBus<br/>Lifecycle Events]
        Node --> Logger[StructuredLogger<br/>Logs]
    end
    
    subgraph "Data Storage"
        Tracker --> TrackerJSON[tracker_logs/<br/>run_001.json]
        Metrics --> MetricsJSON[metrics/<br/>metrics.json]
        Metrics --> Prometheus[metrics/<br/>prometheus.txt]
        Events --> EventLog[events/<br/>events.log]
        Logger --> LogFile[logs/<br/>pipeline.log]
    end
    
    subgraph "Visualization & Reporting"
        TrackerJSON --> StoryGen[StoryGenerator]
        MetricsJSON --> Dashboard[Metrics Dashboard]
        Prometheus --> PromServer[Prometheus Server]
        StoryGen --> HTMLStory[stories/<br/>pipeline_story.html]
    end
    
    subgraph "Analysis"
        HTMLStory --> User[👤 User Analysis]
        Dashboard --> User
        PromServer --> Grafana[Grafana Dashboards]
        Grafana --> User
    end
    
    classDef collectNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef storageNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef vizNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class Tracker,Metrics,Events,Logger collectNode
    class TrackerJSON,MetricsJSON,Prometheus,EventLog,LogFile storageNode
    class StoryGen,Dashboard,PromServer,HTMLStory,Grafana vizNode
```

**Observability Layers:**

1. **Tracker** - Captures execution details:
   - Before/after snapshots of DataFrames
   - Schema changes and row count deltas
   - Execution timing per step
   - Lineage: what data came from where

2. **MetricsManager** - Collects performance metrics:
   - Node execution duration
   - Data throughput (rows/sec)
   - Cache hit/miss rates
   - Memory usage
   - Success/failure counts

3. **EventBus** - Emits lifecycle events:
   - Pipeline and node lifecycle events
   - Triggers automation hooks
   - Integration with external monitoring

4. **StoryGenerator** - Creates visual reports:
   - HTML execution stories with timing
   - Schema diffs and sample data
   - DAG visualization
   - Interactive collapsible sections

**Usage Example:**

```python
# Setup observability stack
tracker = Tracker(log_dir="tracker_logs/")
metrics = MetricsManager()
events = EventBus()
story_gen = StoryGenerator(output_dir="stories/")

# Register metrics hook
events.register_hook("pipeline_complete", metrics.create_export_hook("metrics/"))

# Execute pipeline
executor = DAGExecutor(dag, context, tracker, events)
result = executor.execute()

# Generate story
lineage = tracker.export_lineage()
html = story_gen.generate_story(lineage)
with open("stories/pipeline_run.html", "w") as f:
    f.write(html)

# Export metrics
metrics.save_to_file("metrics/metrics.json")
metrics.save_prometheus("metrics/prometheus.txt")
```

---

## Part 5: Advanced Patterns

### 15. Streaming & Scheduling

#### Streaming Architecture

```mermaid
flowchart LR
    subgraph "Stream Sources"
        FileWatch[File Watch<br/>Monitor directory]
        IntervalPoll[Interval Poll<br/>Query database every N sec]
        Incremental[Incremental Read<br/>Watermark-based]
    end
    
    subgraph "Stream Manager"
        StreamMgr[StreamManager] --> CheckNew{New data<br/>available?}
        CheckNew -->|No| Wait[Wait for interval]
        CheckNew -->|Yes| ReadBatch[Read Batch]
        Wait --> CheckNew
    end
    
    subgraph "Pipeline Execution"
        ReadBatch --> UpdateDataMap[Update data_map with new batch]
        UpdateDataMap --> DAGExec[DAGExecutor.run_continuous]
        DAGExec --> ProcessBatch[Process Batch]
        ProcessBatch --> UpdateWatermark[Update Watermark]
        UpdateWatermark --> Checkpoint[Save Checkpoint iteration++]
    end
    
    Checkpoint --> CheckNew
    
    FileWatch --> StreamMgr
    IntervalPoll --> StreamMgr
    Incremental --> StreamMgr
    
    classDef sourceNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef streamNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef pipelineNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class FileWatch,IntervalPoll,Incremental sourceNode
    class StreamMgr,CheckNew,Wait,ReadBatch streamNode
    class UpdateDataMap,DAGExec,ProcessBatch,UpdateWatermark,Checkpoint pipelineNode
```

**Streaming Modes:**

| Mode | How It Works | Use Case |
|------|--------------|----------|
| **FILE_WATCH** | Monitors directory for new files | Landing zone ingestion |
| **INTERVAL** | Polls source at fixed intervals | Database incremental loads |
| **INCREMENTAL** | Reads data > last watermark | CDC (Change Data Capture) |
| **EVENT** | Triggered by external events | Kafka, webhooks |

**Example: File Watch Streaming**

```python
from odibi_core.streaming import StreamManager, StreamMode, StreamConfig

# Configure stream source
config = StreamConfig(
    mode=StreamMode.FILE_WATCH,
    source_path="data/incoming/",
    file_pattern="*.csv",
    interval_seconds=10,
    batch_size=1000
)

# Create stream manager
stream_mgr = StreamManager(checkpoint_dir="checkpoints/")
stream_mgr.add_source("csv_stream", config)

# Run continuous pipeline
executor = DAGExecutor(dag, context, tracker, events)
for iteration, batch_df in stream_mgr.stream("csv_stream"):
    data_map = {"new_data": batch_df}
    executor.run_continuous(data_map, iteration=iteration)
```

#### Scheduling Architecture

```mermaid
flowchart TD
    subgraph "Schedule Definition"
        Cron[Cron Expression<br/>"0 * * * *" = hourly]
        Interval[Interval<br/>300 seconds = 5 min]
        FileWatch[File Watch<br/>path + pattern]
        Hybrid[Hybrid<br/>Time + Event]
    end
    
    subgraph "Schedule Manager"
        Mgr[ScheduleManager] --> CheckTime{Check<br/>Schedules}
        CheckTime --> CronCheck{Cron<br/>due?}
        CheckTime --> IntervalCheck{Interval<br/>elapsed?}
        CheckTime --> FileCheck{New<br/>files?}
        
        CronCheck -->|Yes| Execute
        IntervalCheck -->|Yes| Execute
        FileCheck -->|Yes| Execute
        
        CronCheck -->|No| Sleep
        IntervalCheck -->|No| Sleep
        FileCheck -->|No| Sleep
        
        Execute[Execute Function<br/>run_pipeline] --> UpdateSchedule[Update last_run, next_run]
        UpdateSchedule --> Sleep[Sleep check_interval]
        Sleep --> CheckTime
    end
    
    Cron --> Mgr
    Interval --> Mgr
    FileWatch --> Mgr
    Hybrid --> Mgr
    
    classDef schedNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef mgrNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class Cron,Interval,FileWatch,Hybrid schedNode
    class Mgr,CheckTime,CronCheck,IntervalCheck,FileCheck,Execute,UpdateSchedule,Sleep mgrNode
```

**Example: Cron Scheduling**

```python
from odibi_core.scheduler import ScheduleManager

def run_pipeline():
    executor = DAGExecutor(dag, context, tracker, events)
    executor.execute()

# Create schedule manager
scheduler = ScheduleManager(check_interval=10)

# Schedule hourly execution
scheduler.schedule("0 * * * *", run_pipeline, name="hourly_pipeline")

# Schedule every 5 minutes
scheduler.schedule_interval(300, run_pipeline, name="frequent_pipeline")

# File watch trigger
scheduler.schedule_file_watch(
    "data/incoming/",
    run_pipeline,
    pattern="*.csv",
    name="file_trigger_pipeline"
)

# Start scheduler (runs in background thread)
scheduler.start()
```

### 16. Distributed Execution

```mermaid
flowchart TB
    subgraph "Sequential Execution (Base DAGExecutor)"
        SeqDAG[DAG with 10 nodes] --> SeqLayer1[Layer 1: 3 nodes]
        SeqLayer1 --> Node1[Execute Node 1]
        Node1 --> Node2[Execute Node 2]
        Node2 --> Node3[Execute Node 3]
        Node3 --> SeqLayer2[Layer 2: 4 nodes...]
        Note1[⏱️ Total Time = Sum of all nodes]
    end
    
    subgraph "Parallel Execution (DistributedExecutor)"
        ParDAG[DAG with 10 nodes] --> ParLayer1[Layer 1: 3 nodes]
        ParLayer1 --> Worker1[Worker 1: Node 1]
        ParLayer1 --> Worker2[Worker 2: Node 2]
        ParLayer1 --> Worker3[Worker 3: Node 3]
        Worker1 --> Sync1[Sync Point]
        Worker2 --> Sync1
        Worker3 --> Sync1
        Sync1 --> ParLayer2[Layer 2: 4 nodes...]
        Note2[⏱️ Total Time = Max time per layer]
    end
    
    classDef seqNode fill:#ffccbc,stroke:#d84315,stroke-width:2px
    classDef parNode fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    
    class SeqDAG,SeqLayer1,Node1,Node2,Node3,SeqLayer2,Note1 seqNode
    class ParDAG,ParLayer1,Worker1,Worker2,Worker3,Sync1,ParLayer2,Note2 parNode
```

**Execution Backends:**

| Backend | How It Works | Best For | Setup |
|---------|--------------|----------|-------|
| **THREAD_POOL** | Multi-threading (Python threads) | I/O-bound tasks (read/write) | Built-in, no setup |
| **PROCESS_POOL** | Multi-processing (separate processes) | CPU-bound tasks (computations) | Built-in, pickable objects required |
| **RAY** | Distributed cluster execution | Large-scale, multi-machine | Ray cluster required |

**Example: Distributed Execution**

```python
from odibi_core.distributed import DistributedExecutor, ExecutionBackend

# Thread pool for I/O-bound pipeline
executor = DistributedExecutor(
    dag=dag,
    context=context,
    tracker=tracker,
    events=events,
    backend=ExecutionBackend.THREAD_POOL,
    distributed_max_workers=4,  # 4 parallel threads
    retry_failed=True,
    distributed_max_retries=3
)
result = executor.execute()

# Process pool for CPU-bound pipeline
executor = DistributedExecutor(
    dag=dag,
    context=context,
    tracker=tracker,
    events=events,
    backend=ExecutionBackend.PROCESS_POOL,
    distributed_max_workers=8,  # 8 parallel processes
)
result = executor.execute()
```

### 17. Story Generation

```mermaid
flowchart LR
    subgraph "Execution"
        Pipeline[Pipeline Execution] --> Tracker[Tracker Captures<br/>Snapshots & Timing]
    end
    
    subgraph "Data Export"
        Tracker --> Export[tracker.export_lineage]
        Export --> Lineage[Lineage JSON<br/>steps, snapshots, summary]
    end
    
    subgraph "Story Generation"
        Lineage --> StoryGen[StoryGenerator]
        StoryGen --> Header[Render Header<br/>pipeline_id, start_time]
        Header --> Summary[Render Summary<br/>success/failed counts, duration]
        Summary --> DAGViz[Render DAG Visualization<br/>if dag_builder provided]
        DAGViz --> Steps[For each step:]
        Steps --> StepCard[Render Step Card<br/>- Inputs/outputs<br/>- Before/after snapshots<br/>- Schema diff<br/>- Sample data<br/>- Timing]
        StepCard --> Footer[Render Footer<br/>execution stats]
    end
    
    subgraph "Output"
        Footer --> HTML[Interactive HTML Story]
        HTML --> User[👤 User Opens in Browser]
    end
    
    classDef execNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef dataNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storyNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef outputNode fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    
    class Pipeline,Tracker execNode
    class Export,Lineage dataNode
    class StoryGen,Header,Summary,DAGViz,Steps,StepCard,Footer storyNode
    class HTML,User outputNode
```

**Story Features:**

- **Step Cards**: Collapsible sections for each step showing:
  - Input/output datasets
  - Before/after snapshots with row counts
  - Schema changes highlighted
  - Sample data tables (configurable rows)
  - Execution timing and status
  
- **Summary Stats**: Pipeline-level metrics:
  - Total duration
  - Success/failed step counts
  - Row count changes
  
- **DAG Visualization** (if DAGBuilder provided):
  - Graphviz-rendered dependency graph
  - Color-coded node states

**Example: Generate Story**

```python
from odibi_core.story import StoryGenerator
from odibi_core.core import Tracker

# Execute pipeline with tracker
tracker = Tracker(log_dir="tracker_logs/")
executor = DAGExecutor(dag, context, tracker, events)
result = executor.execute()

# Export lineage
lineage = tracker.export_lineage()

# Generate HTML story
story_gen = StoryGenerator(
    output_dir="stories/",
    explanations={
        "ingest_csv": "Reads customer transaction data from CSV files.",
        "filter_high_value": "Filters transactions above $1000 for fraud analysis."
    }
)
html = story_gen.generate_story(lineage, max_rows=20)

# Save to file
with open("stories/pipeline_run.html", "w") as f:
    f.write(html)

print("Story saved to stories/pipeline_run.html")
```

---

## Part 6: Quick Reference

### 18. Contract Implementation Cheatsheet

#### NodeBase Contract Implementations

| Node | Purpose | Inputs | Outputs | Key Config |
|------|---------|--------|---------|------------|
| **ConnectNode** | Establish connections | None | None (side effect) | `value` = connection string<br>`params` = connection params |
| **IngestNode** | Read data | None | `outputs` → data_map | `value` = source path<br>`params` = read options |
| **TransformNode** | Transform data | `inputs` ← data_map | `outputs` → data_map | `type` = "sql" or "function"<br>`value` = query or function path |
| **StoreNode** | Save data | `inputs` ← data_map | None (side effect) | `value` = target path<br>`params` = write options |
| **PublishNode** | Export data | `inputs` ← data_map | None (side effect) | `value` = target endpoint<br>`params` = export options |

#### EngineContext Contract Implementations

| Method | PandasEngineContext | SparkEngineContext |
|--------|---------------------|-------------------|
| **connect()** | Initializes DuckDB in-memory | Creates SparkSession |
| **read()** | `pd.read_*()` | `spark.read.*()` |
| **write()** | `df.to_*()` | `df.write.*()` |
| **execute_sql()** | DuckDB SQL execution | Spark SQL execution |
| **register_temp()** | Stores in dict, registers with DuckDB | `df.createOrReplaceTempView()` |
| **collect_sample()** | `df.head(n)` | `df.limit(n).toPandas()` |
| **get_secret()** | Dict or callable lookup | Dict or callable lookup |

#### CloudAdapter Contract Implementations

| Adapter | Status | Authentication | Key Methods |
|---------|--------|----------------|-------------|
| **AzureAdapter** | ✅ Full | Account key, Service principal, Managed identity | `read()`, `write()`, `exists()`, `list()`, `delete()`, `get_secret()` from Key Vault |
| **S3Adapter** | ⚠️ Stub | Planned: Access key/secret | Simulation only |
| **HDFSAdapter** | ⚠️ Stub | Planned: Kerberos | Simulation only |
| **KafkaAdapter** | ⚠️ Stub | Planned: SASL/SSL | Simulation only |

### 19. Complete Pipeline Examples

#### Example 1: Simple CSV → Transform → Parquet (Pandas)

```python
from odibi_core.core import Step, DAGBuilder, Orchestrator, PandasEngineContext, Tracker, EventEmitter

# Define steps
steps = [
    Step(
        layer="ingest",
        name="read_csv",
        type="config_op",
        engine="pandas",
        value="data/input.csv",
        outputs={"data": "raw_data"}
    ),
    Step(
        layer="transform",
        name="filter_records",
        type="sql",
        engine="pandas",
        value="SELECT * FROM raw WHERE value > 100",
        inputs={"raw": "raw_data"},
        outputs={"data": "filtered_data"}
    ),
    Step(
        layer="store",
        name="save_parquet",
        type="config_op",
        engine="pandas",
        value="output/filtered.parquet",
        inputs={"data": "filtered_data"}
    )
]

# Build DAG
builder = DAGBuilder(steps)
dag = builder.build()

# Setup execution
context = PandasEngineContext()
tracker = Tracker()
events = EventEmitter()

# Execute
orchestrator = Orchestrator(steps, context, tracker, events)
result = orchestrator.execute()

print(f"Success: {result.success}")
print(f"Data map keys: {result.data_map.keys()}")
```

#### Example 2: Medallion Pipeline (Bronze → Silver → Gold)

```python
steps = [
    # Bronze: Ingest raw data
    Step(
        layer="ingest",
        name="ingest_transactions",
        type="config_op",
        engine="spark",
        value="data/raw/transactions.csv",
        outputs={"data": "bronze_transactions"}
    ),
    Step(
        layer="store",
        name="save_bronze",
        type="config_op",
        engine="spark",
        value="delta/bronze/transactions",
        inputs={"data": "bronze_transactions"},
        params={"mode": "overwrite", "source_type": "delta"}
    ),
    
    # Silver: Clean and validate
    Step(
        layer="transform",
        name="clean_transactions",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                transaction_id,
                CAST(amount AS DOUBLE) as amount,
                to_date(transaction_date, 'yyyy-MM-dd') as transaction_date,
                customer_id
            FROM bronze
            WHERE amount IS NOT NULL AND amount > 0
        """,
        inputs={"bronze": "bronze_transactions"},
        outputs={"data": "silver_transactions"}
    ),
    Step(
        layer="store",
        name="save_silver",
        type="config_op",
        engine="spark",
        value="delta/silver/transactions",
        inputs={"data": "silver_transactions"},
        params={"mode": "overwrite", "source_type": "delta"}
    ),
    
    # Gold: Aggregate for analytics
    Step(
        layer="transform",
        name="aggregate_daily",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                transaction_date,
                customer_id,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM silver
            GROUP BY transaction_date, customer_id
        """,
        inputs={"silver": "silver_transactions"},
        outputs={"data": "gold_daily_summary"}
    ),
    Step(
        layer="publish",
        name="publish_gold",
        type="config_op",
        engine="spark",
        value="delta/gold/daily_summary",
        inputs={"data": "gold_daily_summary"},
        params={"mode": "append", "source_type": "delta"}
    )
]

# Execute with Spark
from odibi_core.core import SparkEngineContext

spark_context = SparkEngineContext()
orchestrator = Orchestrator(steps, spark_context, tracker, events)
result = orchestrator.execute()
```

#### Example 3: Cloud Pipeline (Azure ADLS → Spark → Delta)

```python
from odibi_core.cloud import CloudAdapter

# Setup Azure connection
azure = CloudAdapter.create(
    "azure",
    account_name="mystorageaccount",
    account_key="...",
    simulate=False
)
azure.connect()

steps = [
    # Read from Azure ADLS
    Step(
        layer="ingest",
        name="read_from_adls",
        type="config_op",
        engine="spark",
        value="abfss://container@account.dfs.core.windows.net/data/input.parquet",
        outputs={"data": "cloud_data"}
    ),
    
    # Transform
    Step(
        layer="transform",
        name="enrich_data",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                *,
                CURRENT_TIMESTAMP() as processed_at,
                'ADLS_PIPELINE' as source_system
            FROM cloud_data
        """,
        inputs={"cloud_data": "cloud_data"},
        outputs={"data": "enriched_data"}
    ),
    
    # Publish to Delta Lake on ADLS
    Step(
        layer="publish",
        name="publish_to_delta",
        type="config_op",
        engine="spark",
        value="abfss://container@account.dfs.core.windows.net/delta/enriched_data",
        inputs={"data": "enriched_data"},
        params={"mode": "append", "source_type": "delta"}
    )
]

# Execute
spark_context = SparkEngineContext()
orchestrator = Orchestrator(steps, spark_context, tracker, events)
result = orchestrator.execute()

# Alternative: Use CloudAdapter directly
df = azure.read("container/data/input.parquet", format="parquet")
# ... process df ...
azure.write(df, "container/delta/output", format="parquet")
```

---

## 🎯 Key Takeaways

### Framework Philosophy

1. **Everything is a Node** - All operations (connect, ingest, transform, store, publish) follow the same NodeBase contract
2. **Engine-Agnostic** - Switch between Pandas and Spark without changing pipeline logic
3. **Contract-Driven** - All components implement well-defined contracts (ABC classes)
4. **Observable by Default** - Tracker, Events, Metrics built into every execution
5. **Fault-Tolerant** - Checkpoints, retries, caching for production resilience

### When to Use What

| Scenario | Use This |
|----------|----------|
| Local development, < 1 GB data | Pandas + CSV/Parquet |
| Production, > 10 GB data | Spark + Delta Lake |
| Need to resume after failure | DAGExecutor + CheckpointManager (mode=AUTO) |
| Speed up repeated runs | DAGExecutor + CacheManager |
| Monitor pipeline health | Tracker + MetricsManager + StoryGenerator |
| Schedule periodic runs | ScheduleManager (cron or interval) |
| Process continuous streams | StreamManager + DAGExecutor.run_continuous() |
| Parallel execution | DistributedExecutor (THREAD_POOL or PROCESS_POOL) |
| Cloud storage integration | CloudAdapter (Azure, S3, HDFS) |

### Common Patterns

#### Pattern 1: Standard Batch Pipeline
```
Steps → DAGBuilder → Orchestrator → DAGExecutor → Result
```

#### Pattern 2: Fault-Tolerant Production Pipeline
```
Steps + CheckpointManager + CacheManager → Orchestrator → DistributedExecutor → Result
```

#### Pattern 3: Streaming Pipeline
```
StreamManager → DAGExecutor.run_continuous(iteration) → Checkpoint per iteration
```

#### Pattern 4: Scheduled Pipeline
```
ScheduleManager.schedule(cron, run_pipeline) → Periodic Execution
```

---

**Version:** ODIBI CORE Phase 8  
**Last Updated:** 2024  
**Companion to:** [ODIBI_CORE_CONTRACT_CHEATSHEET.md](file:///d:/ODIBI_CORE_CONTRACT_CHEATSHEET.md)  
**Walkthrough:** See `odibi_core/docs/walkthroughs/`

---

## 📚 Next Steps

1. **Start with the walkthroughs** - Follow Phase 1-8 developer walkthroughs
2. **Build simple pipelines** - Use Example 1 (CSV → Transform → Parquet)
3. **Add observability** - Enable Tracker and StoryGenerator
4. **Scale up** - Try Medallion pipeline (Example 2)
5. **Go distributed** - Experiment with DistributedExecutor
6. **Add automation** - Schedule pipelines, enable streaming

**Happy building! 🚀**
