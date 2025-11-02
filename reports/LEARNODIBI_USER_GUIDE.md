# LearnODIBI Studio — User Guide 🎓

**Welcome to LearnODIBI Studio** — your self-guided platform for mastering the ODIBI CORE data engineering framework!

---

## 🚀 Getting Started

### Launch the Platform

```bash
# Navigate to the ODIBI CORE directory
cd /d:/projects/odibi_core

# Start the Streamlit app
streamlit run learnodibi_ui.py
```

The platform will open in your default web browser at `http://localhost:8501`

---

## 🏠 Home Screen

When you first launch LearnODIBI Studio, you'll see the **Home Screen** with three main paths:

### 1. 🛤️ Start Guided Course
- Follow a structured learning path from beginner to advanced
- Lessons presented in sequential order
- Automatic progression through phases
- **Best for**: First-time learners

### 2. 🔍 Explore Lessons
- Jump to any lesson freely
- Search by keyword (e.g., "streaming", "config", "SDK")
- Browse by phase or difficulty
- **Best for**: Experienced users or targeted learning

### 3. 📊 My Progress
- View your learning journey
- See completed lessons and steps
- Track earned badges
- Resume where you left off
- **Best for**: Checking achievements

---

## 🛤️ Guided Learning Mode

### How It Works

1. **Click "Start Guided Course"** on the home screen
2. You'll begin with **Phase 1, Lesson 1**
3. Read the lesson overview
4. Navigate through steps using **Previous/Next** buttons
5. Mark steps complete to track progress
6. When you finish a lesson, you'll see **"🎓 Lesson Complete!"**
7. Use **"Next Lesson"** to continue to the next topic

### Navigation Controls

- **⏮️ First** — Jump to Step 1
- **⬅️ Previous** — Go back one step
- **Progress Bar** — Shows current position (e.g., "Step 5 of 32")
- **Next ➡️** — Advance one step
- **Last ⏭️** — Jump to final step

### Learning Features

#### 📖 Step Explanation
Every step includes:
- **Clear explanation** of the concept
- **Code examples** (when applicable)
- **Context panel** with key concepts and tips

#### 💻 Code Blocks
- Each code block has a **📋 Copy** button
- Click to copy code to your clipboard
- Paste into your local Python environment to try it

#### 🧪 Try It Yourself
Instead of running code in the browser, you'll see:
> "Copy this code and run it in your own Python environment to see the results. Experiment with different values and parameters to deepen your understanding!"

This encourages **hands-on practice** in your own development setup.

#### ✅ Mark Complete
- Click **"✅ Mark Step Complete"** when you finish a step
- Progress is saved automatically
- You'll auto-advance to the next step

---

## 🔍 Explore Mode

### How It Works

1. **Click "Explore Lessons"** on the home screen
2. **Search** for specific topics using the search bar
3. **Browse** all lessons grouped by phase
4. **Click any lesson** to jump directly to it

### Search Tips

Enter keywords like:
- `streaming` — Find lessons about streaming data
- `config` — Learn about configuration systems
- `SDK` — Explore SDK and CLI development
- `functions` — Discover the functions library

### Lesson Cards

Each lesson card shows:
- **Title** — Full lesson name
- **Description** — What you'll learn
- **Difficulty Badge** — Beginner / Intermediate / Advanced
- **Steps** — Number of steps (e.g., 📊 32 steps)
- **Duration** — Estimated time (e.g., ⏱️ ~4 hours)

Click **"Start Lesson"** to begin.

---

## 📚 Lesson View

### Layout

The lesson view has **three panels**:

#### Left Panel: Navigation Tree
- Shows all phases and lessons
- Expand a phase to see its lessons
- Click any lesson to jump to it
- Difficulty badges (B/I/A) for quick reference

#### Center Panel: Lesson Content
- **Lesson Header** — Title, author, duration
- **Lesson Overview** — Summary of what you'll learn (expandable)
- **Current Step** — Step number, title, explanation
- **Code Examples** — Syntax-highlighted with copy button
- **Navigation Controls** — Move between steps
- **Mark Complete Button** — Track your progress

#### Right Panel: Context Area
- **Step Status** — ✅ Completed or ⏳ In Progress
- **Key Concepts** — Tags for this step
- **Quick Tips** — Helpful reminders

### Step-by-Step Navigation

1. Read the **step header** (e.g., "Step 5: Understanding ConnectNode")
2. Read the **explanation** carefully
3. Review the **code example** (if present)
4. **Copy the code** using the 📋 button
5. **Try it yourself** in your local environment
6. Click **"✅ Mark Step Complete"**
7. Move to the **next step**

### Expandable Sections

- **💡 Why It Matters** — Context on why this concept is important
- **⚠️ Common Mistakes** — Pitfalls to avoid
- **📋 Lesson Overview** — High-level summary

---

## 📊 Progress Tracking

### View Your Progress

Click **"My Progress"** from the home screen or sidebar.

### What You'll See

#### Overall Stats
- **Lessons Completed** — Progress badge (e.g., 3/11)
- **Steps Completed** — Total steps finished (e.g., 45/205)
- **Badges Earned** — Achievements unlocked (e.g., 🏆 5 badges)

#### Lesson Breakdown
- Expandable list of all lessons
- Progress bar for each lesson
- **Resume** button to continue where you left off

### Progress Persistence

Your progress is saved automatically in `progress.json`:
- Lessons completed
- Steps completed
- Badges earned
- Last position (lesson + step)

**Note**: Progress is stored locally. If you reset the app or clear session data, progress will be lost.

---

## 🛠️ Project Scaffolder

### Create a New ODIBI CORE Project

1. Click **"🛠️ New Project"** in the sidebar
2. Enter **Project Name** (e.g., "my_odibi_pipeline")
3. Enter **Project Path** — absolute path (e.g., `D:/projects/my_odibi_pipeline`)
4. Select **Template**:
   - **Basic Pipeline** — Simple Bronze → Silver → Gold
   - **Transformation Focus** — Data transformation playground
   - **Functions Playground** — Explore ODIBI functions
5. Click **"🚀 Create Project"**

### What Gets Created

```
my_odibi_project/
├── configs/               # Configuration files
│   └── pipeline_config.json
├── data/
│   ├── bronze/           # Raw data
│   ├── silver/           # Transformed data
│   └── gold/             # Aggregated data
├── notebooks/            # Jupyter notebooks
├── logs/                 # Log files
├── run_project.py        # Main pipeline script
└── README.md             # Project documentation
```

### Run Your New Project

```bash
cd D:/projects/my_odibi_project
python run_project.py
```

---

## 🎨 Customization

### Sidebar Options

#### 🎯 Learning Mode
- **🛤️ Guided Course** — Linear progression
- **🔍 Free Explore** — Jump to any lesson

#### 🎨 Theme
- **☀️ Light Mode** — Coming soon!
- **🌙 Dark Mode** — Current default (Afro-futurist theme)

#### 📊 Progress Summary
- Shows completed lessons / total lessons
- Displays earned badges
- Quick stats at a glance

#### ⚙️ Quick Actions
- **🏠 Home** — Return to home screen
- **🛠️ New Project** — Open scaffolder
- **🔄 Reset Progress** — Clear all progress (use with caution!)

---

## 💡 Learning Tips

### For Beginners

1. **Start with Guided Mode** — Don't skip ahead
2. **Take your time** — Read explanations carefully
3. **Try every code example** — Copy and run locally
4. **Mark steps complete** — Track your journey
5. **Use the context panel** — Check key concepts
6. **Don't rush** — Understanding beats speed

### For Intermediate Learners

1. **Use Explore Mode** — Jump to relevant topics
2. **Search by keyword** — Find what you need quickly
3. **Review "Why It Matters"** — Deepen understanding
4. **Experiment with code** — Modify examples
5. **Check "Common Mistakes"** — Avoid pitfalls

### For Advanced Users

1. **Skim familiar topics** — Focus on new concepts
2. **Cross-reference phases** — Connect the dots
3. **Build projects** — Use the scaffolder
4. **Read function source** — Understand internals
5. **Contribute back** — Share insights with the community

---

## ❓ Frequently Asked Questions

### How do I run code examples?

**Copy the code** using the 📋 button, then **paste into your local Python environment**. LearnODIBI Studio is designed for **guided reading**, not live code execution.

### Can I reset my progress?

Yes! Click **"🔄 Reset Progress"** in the sidebar. **Warning**: This cannot be undone.

### Where is my progress saved?

Progress is stored in `odibi_core/progress.json`. It persists across sessions unless you reset or delete the file.

### How do I jump to a specific lesson?

Use **Explore Mode** → Search or browse → Click **"Start Lesson"**.

### What if I don't see a lesson in the tree?

Make sure the lesson exists in `walkthrough_manifest.json` and is in the `docs/walkthroughs/` directory.

### Can I view lessons offline?

Yes! The walkthroughs are Markdown files in `docs/walkthroughs/`. You can read them directly without the UI.

### How do I suggest improvements?

Contact the ODIBI CORE team or open an issue in the project repository.

---

## 🎓 Learning Path Recommendation

### Week 1: Foundations
- **Phase 1** — Core Architecture (ConnectNode, IngestNode, etc.)
- **Phase 2** — Dual-Engine Support (Pandas + Spark)

### Week 2: Configuration & Docs
- **Phase 3** — Configuration System
- **Phase 4** — Documentation & Self-Description

### Week 3: Advanced Topics
- **Phase 5** — Parallel Execution
- **Phase 6** — Streaming Data

### Week 4: Production & SDK
- **Phase 7** — Cloud Integration
- **Phase 8** — Observability
- **Phase 9** — SDK & CLI

### Anytime: Deep Dives
- **Functions** — Explore 100+ utility functions
- **LearnODIBI** — Understand the platform itself

---

## 🏆 Achievements & Badges

### How to Earn Badges

- **First Lesson** — Complete your first lesson
- **Phase Master** — Complete all lessons in a phase
- **Function Explorer** — Complete the Functions walkthrough
- **SDK Developer** — Complete the SDK/CLI walkthrough
- **Fast Learner** — Complete 3 lessons in one session
- **Completionist** — Finish all 11 lessons

Badges are displayed in **My Progress** screen.

---

## 🛡️ Troubleshooting

### The UI won't start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`  
**Solution**: Install Streamlit: `pip install streamlit`

**Error**: `FileNotFoundError: walkthrough_manifest.json`  
**Solution**: Make sure you're in the `odibi_core` directory

### Lesson content doesn't render

**Issue**: Blank lesson screen  
**Solution**: Check that the walkthrough file exists in `docs/walkthroughs/`

### Progress not saving

**Issue**: Progress resets every session  
**Solution**: Check file permissions for `progress.json`

### Navigation buttons not working

**Issue**: Clicking buttons doesn't change steps  
**Solution**: Refresh the page (`R` key in Streamlit)

---

## 📞 Support

For help, questions, or feedback:

- **Documentation**: `docs/` folder in ODIBI CORE
- **Repository**: Contact repository maintainers
- **Community**: Join the ODIBI CORE community (if available)

---

## 🎉 You're Ready!

You now have everything you need to master ODIBI CORE using LearnODIBI Studio.

**Happy Learning!** 🚀

---

**LearnODIBI Studio**  
**by Henry Odibi**  
**Powered by ODIBI CORE Framework**
