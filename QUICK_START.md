# ODIBI CORE Quick Start Guide

**Welcome to ODIBI CORE!** This guide gets you up and running in 5 minutes.

---

## ⚡ Installation (2 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd odibi_core

# Install with all dependencies (recommended)
pip install -e ".[dev]"

# Verify installation
python -c "import odibi_core; print('✓ ODIBI CORE installed')"
```

---

## 🎓 Launch LearnODIBI Studio (1 minute)

The **fastest way to learn** ODIBI CORE is through the interactive teaching platform:

```bash
# Launch the studio
python deploy/scripts/launch_studio.py
```

Then open your browser to **http://localhost:8501**

**What you'll see**:
- 11 interactive walkthroughs (39.5 hours of content)
- Live code execution
- Checkpoints and quizzes
- Try-it-yourself experiments

**Start with**: Phase 1 — Building the Foundation (4 hours)

---

## 🚀 Run Your First Pipeline (2 minutes)

### Option 1: Use the SDK

```python
from odibi_core.sdk import ODIBI

# Create a pipeline
pipeline = ODIBI.from_config("examples/energy_efficiency.json")

# Execute with Pandas
result = pipeline.run(engine="pandas")

# View execution summary
print(result.summary())
```

### Option 2: Use the CLI

```bash
# Run a pipeline
odibi run --config examples/energy_efficiency.json --engine pandas

# Validate configuration
odibi validate --config examples/energy_efficiency.json

# Check version
odibi version
```

---

## 📚 What to Explore Next

### 1. Learn the Framework (Recommended)

**Interactive Platform**: [Launch LearnODIBI Studio](#-launch-learnodibi-studio-1-minute)

**Walkthroughs** (choose your track):

**Beginner Track** (12 hours):
- [Phase 1: Scaffolding](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md) (4h)
- [Phase 2: Dual-Engine System](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_2.md) (4h)
- [Phase 3: Orchestration](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_3.md) (4h)

**Intermediate Track** (18 hours):
- Phase 4-6: Documentation, Parallelism, Streaming
- Functions Library: Engineering Calculations
- LearnODIBI Studio: Platform Mechanics

**Advanced Track** (9.5 hours):
- Phase 7-9: Cloud, Observability, SDK/CLI

### 2. Run the Demo Project

```bash
# Run Energy Efficiency demo
python examples/run_energy_efficiency_demo.py
```

### 3. Read the Documentation

- **[README.md](README.md)** — Project overview
- **[INSTALL.md](INSTALL.md)** — Detailed installation
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** — Directory layout
- **[User Guide](docs/guides/UI_USER_GUIDE.md)** — LearnODIBI features

---

## 🐳 Docker Quick Start

```bash
# Build and run with Docker Compose
cd deploy/docker
docker-compose up --build

# Access at http://localhost:8501
```

See [Docker Quick Start Guide](docs/guides/DOCKER_QUICKSTART.md) for details.

---

## 🔧 Verify Installation

```bash
# Run verification script
python verify_reorganization.py

# Should output:
# [SUCCESS] REORGANIZATION VERIFICATION COMPLETE
```

---

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/unit/test_node_base.py -v

# Run with coverage
pytest tests/ --cov=odibi_core --cov-report=html
```

---

## ❓ Common Questions

**Q: Which Python version do I need?**  
A: Python 3.8+ (3.10+ recommended)

**Q: Does Spark work on Windows?**  
A: Spark has Windows issues. Use PandasEngineContext for local development. Spark works perfectly on Linux, Mac, and cloud (Databricks, EMR).

**Q: How do I add a custom Node?**  
A: See the [Contributing section in README.md](README.md#-contributing)

**Q: Where are the walkthroughs?**  
A: Two ways:
1. Interactive: Launch LearnODIBI Studio
2. Markdown: Browse `docs/walkthroughs/`

**Q: Can I skip the walkthroughs?**  
A: You can, but we recommend Phase 1 (4h) to understand the architecture. The framework is designed to be learned progressively.

---

## 🆘 Need Help?

- **Installation Issues**: See [INSTALL.md](INSTALL.md)
- **Learning Path**: Start with [Phase 1 Walkthrough](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md)
- **UI Features**: Read [UI User Guide](docs/guides/UI_USER_GUIDE.md)
- **Project Structure**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Reports & Validation**: Browse [docs/reports/](docs/reports/)

---

## 📁 Key Files & Directories

```
odibi_core/
├── odibi_core/              # Source code
├── docs/walkthroughs/       # 11 teaching walkthroughs
├── docs/guides/             # User guides
├── deploy/scripts/          # Launch scripts
├── examples/                # Example pipelines
└── README.md                # Full documentation
```

---

## 🎯 Your Next Steps

1. ✅ Install: `pip install -e ".[dev]"`
2. ✅ Launch Studio: `python deploy/scripts/launch_studio.py`
3. ✅ Start Phase 1 walkthrough
4. ✅ Run demo: `python examples/run_energy_efficiency_demo.py`
5. ✅ Read [README.md](README.md) for deep dive

---

**Welcome to ODIBI CORE!** You're now ready to build production-grade, engine-agnostic data pipelines. 🚀

---

**Quick Links**:
- [README](README.md) | [Installation](INSTALL.md) | [Project Structure](PROJECT_STRUCTURE.md)
- [Walkthroughs](docs/walkthroughs/) | [Guides](docs/guides/) | [Reports](docs/reports/)
