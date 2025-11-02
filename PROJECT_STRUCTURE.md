# ODIBI CORE Project Structure

**Last Updated**: November 2, 2025  
**Version**: 1.0 (Production-Clean)

---

## 📁 Directory Layout

```
odibi_core/                              # PROJECT ROOT
│
├── odibi_core/                          # 🔵 SOURCE CODE
│   ├── core/                            #    Core abstractions
│   │   ├── node.py                      #    NodeBase, Step, NodeState
│   │   ├── orchestrator.py              #    Pipeline orchestration
│   │   ├── config_loader.py             #    Config loading (JSON/SQL)
│   │   ├── tracker.py                   #    Execution tracking
│   │   └── events.py                    #    Event system
│   │
│   ├── engine/                          #    Engine implementations
│   │   ├── base_context.py              #    EngineContext ABC
│   │   ├── pandas_context.py            #    Pandas + DuckDB
│   │   ├── spark_context.py             #    Spark implementation
│   │   └── spark_local_config.py        #    Local Spark config
│   │
│   ├── nodes/                           #    Pipeline nodes
│   │   ├── connect_node.py              #    Connection node
│   │   ├── ingest_node.py               #    Ingestion node
│   │   ├── store_node.py                #    Storage node
│   │   ├── transform_node.py            #    Transformation node
│   │   └── publish_node.py              #    Publishing node
│   │
│   ├── functions/                       #    Engineering functions
│   │   ├── thermo/                      #    Thermodynamics
│   │   ├── psychro/                     #    Psychrometrics
│   │   ├── physics/                     #    Physical calculations
│   │   └── math/                        #    Mathematical utilities
│   │
│   ├── learnodibi_ui/                   #    Teaching platform UI
│   │   ├── app.py                       #    Main Streamlit app
│   │   ├── pages/                       #    UI pages
│   │   ├── walkthrough_parser.py        #    Markdown parser
│   │   ├── code_executor.py             #    Safe code execution
│   │   └── project_scaffolder.py        #    Project templates
│   │
│   ├── observability/                   #    Logging & metrics
│   ├── metrics/                         #    Metrics collection
│   ├── connectors/                      #    Cloud connectors
│   └── sdk/                             #    Python SDK
│
├── tests/                               # 🧪 TEST SUITE
│   ├── unit/                            #    Unit tests
│   ├── integration/                     #    Integration tests
│   └── conftest.py                      #    Pytest fixtures
│
├── docs/                                # 📚 DOCUMENTATION
│   ├── walkthroughs/                    #    11 teaching walkthroughs
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_1.md  # Scaffolding (4h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_2.md  # Dual-Engine (4h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_3.md  # Orchestration (4h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_4.md  # Documentation (4h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_5.md  # Parallelism (4h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_6.md  # Streaming (4h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_7.md  # Cloud (3.5h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_8.md  # Observability (3h)
│   │   ├── DEVELOPER_WALKTHROUGH_PHASE_9.md  # SDK/CLI (3h)
│   │   ├── DEVELOPER_WALKTHROUGH_FUNCTIONS.md  # Functions (5h)
│   │   └── DEVELOPER_WALKTHROUGH_LEARNODIBI.md  # Studio (2h)
│   │
│   ├── guides/                          #    User guides
│   │   ├── LAUNCH_LEARNODIBI_NOW.md     #    Quick start guide
│   │   ├── STUDIO_LAUNCH_GUIDE.md       #    Studio setup
│   │   ├── UI_USER_GUIDE.md             #    UI features
│   │   ├── DOCKER_QUICKSTART.md         #    Docker quick start
│   │   └── DOCKER_GUIDE.md              #    Docker detailed guide
│   │
│   ├── reports/                         #    Validation reports (53 files)
│   │   ├── LEARNODIBI_TEACHING_OVERHAUL_FINAL.md
│   │   ├── PHASE_10_LEARNODIBI_COMPLETE.md
│   │   ├── WALKTHROUGH_CODE_VALIDATION_COMPLETE.md
│   │   └── ... (all validation/audit reports)
│   │
│   ├── archive/                         #    Archived documentation
│   ├── reference/                       #    API reference
│   └── changelogs/                      #    Version history
│
├── deploy/                              # 🚀 DEPLOYMENT
│   ├── docker/                          #    Docker configuration
│   │   ├── Dockerfile                   #    Container definition
│   │   ├── docker-compose.yml           #    Multi-container setup
│   │   ├── .dockerignore                #    Docker ignore rules
│   │   └── setup_spark_windows.ps1      #    Windows Spark setup
│   │
│   └── scripts/                         #    Launch scripts
│       ├── launch_studio.py             #    Python launcher
│       ├── launch_studio.bat            #    Windows launcher
│       ├── run_studio.bat               #    Windows runner
│       └── run_studio.sh                #    Unix/Mac runner
│
├── scripts/                             # 🛠️ UTILITY SCRIPTS
│   ├── test_all.py                      #    Main test runner
│   ├── freeze_manifest.py               #    Freeze walkthrough manifest
│   ├── verify_*.py                      #    Verification scripts (7 files)
│   ├── validate_*.py                    #    Validation scripts (2 files)
│   ├── walkthrough_compiler.py          #    Compile walkthroughs
│   ├── walkthrough_code_fixer.py        #    Fix walkthrough code
│   └── ... (diagnostic & fix scripts)
│
├── examples/                            # 📝 EXAMPLE PIPELINES
│   └── run_energy_efficiency_demo.py    #    Energy efficiency demo
│
├── artifacts/                           # 📦 BUILD OUTPUTS (git-ignored)
│   ├── logs/                            #    All log files
│   │   ├── logs/                        #    Application logs
│   │   ├── tracker_logs/                #    Pipeline tracking logs
│   │   └── *.txt                        #    Build/test logs
│   │
│   ├── test_results/                    #    Test runner scripts
│   │   ├── test_all_ui_features.py
│   │   ├── test_full_studio.py
│   │   └── ... (11 UI test scripts)
│   │
│   ├── metrics/                         #    Metrics data
│   ├── grafana_templates/               #    Grafana dashboards
│   ├── stories/                         #    HTML execution reports
│   └── .pytest_cache/                   #    Pytest cache
│
├── .gitignore                           # Git ignore rules
├── .dockerignore                        # Docker ignore rules (in deploy/docker/)
│
├── pyproject.toml                       # 📦 Package configuration
├── setup.py                             # Setup script
├── pytest.ini                           # Pytest configuration
├── requirements.txt                     # Runtime dependencies
├── requirements-dev.txt                 # Development dependencies
│
├── README.md                            # 📖 Main documentation
├── INSTALL.md                           # Installation guide
├── PROJECT_STRUCTURE.md                 # This file
├── REORGANIZATION_COMPLETE.md           # Reorganization report
│
├── walkthrough_manifest.json            # Original manifest
└── walkthrough_manifest_v2.json         # Teaching-mode manifest
```

---

## 🎯 Key Directories

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `odibi_core/` | Framework source code | 5 modules, 40+ files |
| `tests/` | Test suite | Unit, integration tests |
| `docs/` | Documentation | Walkthroughs, guides, reports |
| `deploy/` | Deployment configs | Docker, launch scripts |
| `scripts/` | Utility scripts | Validators, verifiers, fixers |
| `examples/` | Example pipelines | Demo scripts |
| `artifacts/` | Build outputs | Logs, test results, metrics |

---

## 📊 File Counts

- **Source Code**: ~60 Python files
- **Tests**: ~30 test files
- **Walkthroughs**: 11 teaching guides (39.5 hours)
- **User Guides**: 6 guides
- **Validation Reports**: 53 reports
- **Utility Scripts**: 18 scripts
- **Root Files**: 14 (production-clean)

---

## 🔍 Finding What You Need

### "I want to..."

**Learn the framework**  
→ Start with [`docs/walkthroughs/`](docs/walkthroughs/)  
→ Begin with Phase 1 (4 hours)

**Launch LearnODIBI Studio**  
→ Read [`docs/guides/LAUNCH_LEARNODIBI_NOW.md`](docs/guides/LAUNCH_LEARNODIBI_NOW.md)  
→ Run `python deploy/scripts/launch_studio.py`

**Deploy with Docker**  
→ Read [`docs/guides/DOCKER_QUICKSTART.md`](docs/guides/DOCKER_QUICKSTART.md)  
→ Use files in [`deploy/docker/`](deploy/docker/)

**Run tests**  
→ Use `pytest tests/` from root  
→ Or `python scripts/test_all.py`

**See validation reports**  
→ Browse [`docs/reports/`](docs/reports/)  
→ Key report: [`LEARNODIBI_TEACHING_OVERHAUL_FINAL.md`](docs/reports/LEARNODIBI_TEACHING_OVERHAUL_FINAL.md)

**Understand the architecture**  
→ Read [`README.md`](README.md)  
→ See [`docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md`](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md)

**Extend the framework**  
→ See custom node registration in [`README.md`](README.md)  
→ Review [`odibi_core/nodes/`](odibi_core/nodes/) for examples

---

## 🚀 Quick Commands

```bash
# Install the package
pip install -e .

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/unit/test_node_base.py -v

# Launch LearnODIBI Studio
python deploy/scripts/launch_studio.py

# Validate walkthroughs
python scripts/verify_walkthrough_parser.py

# Build Docker image
cd deploy/docker
docker-compose up --build

# Run test suite
python scripts/test_all.py

# Freeze walkthrough manifest
python scripts/freeze_manifest.py
```

---

## 📝 Naming Conventions

### Source Files
- `*_context.py` — Engine context implementations
- `*_node.py` — Node type implementations
- `*_loader.py` — Data/config loaders

### Test Files
- `test_*.py` — Pytest test files
- `conftest.py` — Pytest fixtures

### Documentation
- `DEVELOPER_WALKTHROUGH_*.md` — Teaching walkthroughs
- `*_GUIDE.md` — User guides
- `*_COMPLETE.md` — Completion reports
- `*_VALIDATION*.md` — Validation reports

### Scripts
- `verify_*.py` — Verification scripts
- `validate_*.py` — Validation scripts
- `test_*.py` — Test runners

---

## 🎓 Learning Path

For new developers joining the project:

1. **Start Here**: [`README.md`](README.md)
2. **Install**: [`INSTALL.md`](INSTALL.md)
3. **Learn**: [`docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md`](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md)
4. **Practice**: [`examples/`](examples/)
5. **Contribute**: See node registration in README

---

## 🔧 Maintenance

### Regenerating Build Artifacts

```bash
# Regenerate egg-info
pip install -e .

# Regenerate walkthrough manifest
python scripts/freeze_manifest.py

# Regenerate pytest cache
pytest --cache-clear
```

### Cleaning Build Artifacts

```bash
# Remove all build artifacts
rm -rf artifacts/
rm -rf odibi_core.egg-info/
rm -rf dist/ build/
rm -rf .pytest_cache/

# Then reinstall
pip install -e .
```

---

## 📦 What's Git-Ignored

The following directories/files are git-ignored (see [`.gitignore`](.gitignore)):

- `artifacts/` — Build outputs, logs, test results
- `odibi_core.egg-info/` — Package metadata (regenerated)
- `dist/`, `build/` — Distribution builds
- `.pytest_cache/` — Pytest cache
- `__pycache__/` — Python bytecode
- `*.log` — Log files
- `*.db`, `*.parquet`, `*.csv` — Data files

---

## ✅ Quality Checks

Run these to verify the project structure:

```bash
# Verify reorganization
python verify_reorganization.py

# Verify imports
python -c "import odibi_core; print('OK')"

# Count files
ls -R | wc -l

# Check root cleanliness
ls -1 | wc -l  # Should be <25
```

---

## 🎯 Project Status

**Reorganization**: ✅ Complete (Nov 2, 2025)  
**Structure**: Production-clean  
**Root Files**: 14 (target: <25)  
**Documentation**: Organized into `/docs`  
**Deployment**: Organized into `/deploy`  
**Build Artifacts**: Isolated in `/artifacts`  

**Next**: Ready for UI revamp, packaging, and collaboration

---

**Maintained by**: ODIBI CORE Team  
**Last Verified**: November 2, 2025
