# ODIBI Core Documentation Index

**Version**: 1.1.0  
**Last Updated**: 2025-11-02  
**Framework**: Node-centric, Engine-agnostic, Config-driven Data Engineering

---

## 📚 Documentation Structure

### Getting Started
- [Main README](../README.md) - Project overview and quick start
- [Installation Guide](../INSTALL.md) - Detailed setup instructions
- [Quick Start](../QUICK_START.md) - Get running in 5 minutes
- [Project Structure](../PROJECT_STRUCTURE.md) - Architecture overview

### Core Modules

#### LearnODIBI - Teaching Platform
- [LearnODIBI Module](modules/learnodibi.md) - Interactive teaching interface
- [LearnODIBI UI](modules/learnodibi_ui.md) - Streamlit application details
- **Quick Launch**: `learnodibi` or `from odibi_core.learnodibi import launch_ui`

#### Developer Tools
- [Scripts Documentation](modules/scripts.md) - Utility scripts and helpers

### Framework Documentation

#### Walkthroughs (11 Comprehensive Guides - 39.5 hours)

**Beginner Track** (12 hours)
- [Phase 1: Scaffolding](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md) - Foundation (2h)
- [Phase 2: Dual-Engine](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_2.md) - Pandas/Spark parity (5h)
- [Phase 3: Orchestration](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_3.md) - DAG execution (5h)

**Intermediate Track** (18 hours)
- [Phase 4: Documentation](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_4.md) - Writing docs (1h)
- [Phase 5: Parallelism](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_5.md) - Concurrent execution (3h)
- [Phase 6: Streaming](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_6.md) - Real-time processing (6h)
- [Phase 7: Functions](walkthroughs/DEVELOPER_WALKTHROUGH_FUNCTIONS.md) - Pure functions (8h)

**Advanced Track** (9.5 hours)
- [Phase 8: Cloud](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_7.md) - Distributed systems (4h)
- [Phase 9: Observability](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_8.md) - Monitoring (1.5h)
- [Phase 10: SDK/CLI](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_9.md) - Developer interface (4h)

#### Technical Reference
- [Format Support](reference/FORMAT_SUPPORT.md) - Supported file formats
- [SQL Database Support](reference/SQL_DATABASE_SUPPORT.md) - Database connectors
- [Engine Contexts](reference/ENGINE_CONTEXTS.md) - Pandas vs Spark
- [Node Types](reference/NODE_TYPES.md) - 5 canonical nodes

#### Reports & Validation
- [Phase Completion Reports](reports/) - Development milestone documentation
- [Validation Reports](reports/) - Testing and quality assurance
- [Audit Reports](reports/) - Code and content audits

### Guides

#### User Guides
- [LearnODIBI User Guide](guides/LEARNODIBI_USER_GUIDE.md) - End-user documentation
- [UI User Guide](guides/UI_USER_GUIDE.md) - LearnODIBI UI features
- [Launch Instructions](guides/LAUNCH_LEARNODIBI_NOW.md) - Quick start for LearnODIBI

#### Developer Guides
- [Docker Quickstart](guides/DOCKER_QUICKSTART.md) - Container deployment
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute (Phase 5)

### Changelogs
- [Roadmap v1.1](changelogs/ROADMAP_V1.1_REASSESSMENT.md) - Revised development roadmap
- [Version History](changelogs/) - Release notes and changes

---

## 🎯 Quick Navigation

### I want to...

#### Learn ODIBI Core
→ Launch [LearnODIBI](modules/learnodibi.md): `learnodibi`  
→ Start with [Phase 1 Walkthrough](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md)  
→ Browse [All Walkthroughs](walkthroughs/)

#### Build a Pipeline
→ Read [Quick Start](../QUICK_START.md)  
→ Check [Format Support](reference/FORMAT_SUPPORT.md)  
→ Review [Node Types](reference/NODE_TYPES.md)

#### Deploy to Production
→ Follow [Installation Guide](../INSTALL.md)  
→ Configure [Engine Contexts](reference/ENGINE_CONTEXTS.md)  
→ Read [Docker Quickstart](guides/DOCKER_QUICKSTART.md)

#### Contribute
→ Read [Contributing Guide](../CONTRIBUTING.md)  
→ Check [Scripts Documentation](modules/scripts.md)  
→ Review [Code Style](../AGENTS.md)

#### Debug an Issue
→ Check [Validation Reports](reports/)  
→ Review [Audit Reports](reports/)  
→ Search [GitHub Issues](https://github.com/yourorg/odibi_core/issues)

---

## 📊 Documentation Coverage

### Module Documentation: 100%
- ✅ Core Framework
- ✅ LearnODIBI Platform
- ✅ Streamlit UI
- ✅ Developer Scripts

### API Documentation: In Progress
- ✅ High-level SDK (Phase 9)
- ✅ CLI Commands (Phase 9)
- ⏳ Auto-generated API docs (Phase 10)

### Walkthroughs: 11/11 Complete
- ✅ All 10 framework phases documented
- ✅ Functions module walkthrough
- ✅ LearnODIBI integration complete

---

## 🔍 Search & Index

### By Topic

**Architecture**
- Node Model, Engine Contexts, DAG Orchestration
- [Main README](../README.md) | [Walkthroughs](walkthroughs/)

**Data Processing**
- Ingestion, Transformation, Storage, Publishing
- [Format Support](reference/FORMAT_SUPPORT.md) | [Node Types](reference/NODE_TYPES.md)

**Cloud & Distributed**
- Azure, S3, Spark, Streaming, Checkpointing
- [Phase 7 Walkthrough](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_7.md)

**Observability**
- Logging, Metrics, Monitoring, Alerting
- [Phase 8 Walkthrough](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_8.md)

**Teaching & Learning**
- LearnODIBI, Interactive Walkthroughs, Quizzes
- [LearnODIBI Module](modules/learnodibi.md) | [User Guide](guides/LEARNODIBI_USER_GUIDE.md)

### By Audience

**Data Engineers**
→ [Quick Start](../QUICK_START.md), [Format Support](reference/FORMAT_SUPPORT.md), [Engine Contexts](reference/ENGINE_CONTEXTS.md)

**Framework Developers**
→ [Walkthroughs](walkthroughs/), [Scripts](modules/scripts.md), [Reports](reports/)

**Students & Learners**
→ [LearnODIBI](modules/learnodibi.md), [Beginner Walkthroughs](walkthroughs/)

**DevOps & Operators**
→ [Installation](../INSTALL.md), [Docker](guides/DOCKER_QUICKSTART.md), [Observability](walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_8.md)

---

## 📦 Documentation Artifacts

### Source Locations
- **Root Documentation**: `/README.md`, `/INSTALL.md`, `/QUICK_START.md`
- **Module READMEs**: `/odibi_core/*/README.md`
- **Walkthroughs**: `/docs/walkthroughs/*.md`
- **Reference**: `/docs/reference/*.md`
- **Reports**: `/docs/reports/*.md` (public), `/resources/reports/*.md` (development)

### Build & Generation
- **Manual**: Root files, module READMEs
- **Generated**: Phase completion reports, validation summaries
- **Auto-generated (Phase 10)**: API documentation from docstrings

---

## 🚀 What's Next?

### Upcoming Documentation (Phase 10)
- [ ] Auto-generated API reference (from docstrings)
- [ ] Migration guide (v2 → v1)
- [ ] Sample project templates
- [ ] Video tutorials
- [ ] Community cookbook

### How to Contribute
1. Fork the repository
2. Add/update documentation
3. Submit pull request
4. See [Contributing Guide](../CONTRIBUTING.md) for details

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourorg/odibi_core/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/odibi_core/discussions)
- **Email**: henry@odibi.com

---

**Documentation Version**: 1.1.0  
**Framework Version**: 1.1.0  
**LearnODIBI**: Integrated ✅  
**Last Build**: 2025-11-02
