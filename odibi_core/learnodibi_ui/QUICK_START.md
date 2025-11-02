# ODIBI CORE Studio - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install streamlit plotly pandas numpy
```

### Step 2: Run the App
```bash
# From project root
streamlit run odibi_core/learnodibi_ui/app.py

# Or use launcher
run_studio.bat    # Windows
./run_studio.sh   # Linux/Mac
```

### Step 3: Open Browser
Navigate to: **http://localhost:8501**

---

## 📚 Page Guide

| Page | Icon | Purpose | Time to Complete |
|------|------|---------|------------------|
| **Home** | 🏠 | Overview & getting started | 5 min |
| **Core Concepts** | 🎓 | Learn 5 canonical nodes | 15 min |
| **Functions Explorer** | 🔍 | Browse & test 100+ functions | 20 min |
| **SDK Examples** | 💻 | See real code patterns | 25 min |
| **Demo Project** | ⚡ | Run complete pipeline | 30 min |
| **Documentation** | 📖 | Deep dive into details | As needed |

---

## ⚡ Quick Actions

### Run Your First Pipeline
1. Go to **Core Concepts** page
2. Scroll to "Putting It All Together"
3. Click "▶️ Run Complete Pipeline"
4. Watch the magic happen!

### Test a Function
1. Go to **Functions Explorer** page
2. Click on any function (e.g., "safe_divide")
3. Adjust parameters
4. Click "▶️ Run"

### Try the Demo
1. Go to **Demo Project** page
2. Click "📥 Ingest Data" in Bronze tab
3. Move to Silver tab, click "⚙️ Transform Data"
4. Move to Gold tab, click "📊 Aggregate Data"
5. Check Analytics tab for visualizations

---

## 💡 Pro Tips

- **Use Search** - Each page has filtering/search
- **Download Results** - Most outputs can be exported
- **Explore Examples** - Click all "Try It" buttons
- **Check Metrics** - Monitor execution performance
- **Read Tooltips** - Hover for additional info

---

## 🎯 Learning Path

### For Beginners
1. Home → Core Concepts → Functions Explorer → Demo Project

### For Developers
1. SDK Examples → Demo Project → Documentation

### For Instructors
1. Core Concepts → SDK Examples → Demo Project

---

## 📱 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `R` | Rerun app |
| `C` | Clear cache |
| `Ctrl+K` | Focus search |
| `Esc` | Close sidebar |

---

## 🔧 Troubleshooting

### Issue: Port 8501 busy
```bash
streamlit run odibi_core/learnodibi_ui/app.py --server.port 8502
```

### Issue: Import errors
```bash
# Reinstall odibi_core
pip install -e /d:/projects/odibi_core
```

### Issue: Cache problems
Press **'C'** in the app or:
```bash
streamlit cache clear
```

---

## 📞 Need Help?

- **FAQ**: Check Documentation page
- **Examples**: Browse SDK Examples page
- **Docs**: Read the Documentation section

---

## ✅ Checklist

Before you start, ensure:
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`streamlit`, `plotly`, `pandas`, `numpy`)
- [ ] ODIBI CORE installed (`pip install -e .`)
- [ ] Port 8501 available

Run verification:
```bash
python verify_learnodibi_ui.py
```

---

## 🎉 You're Ready!

Start exploring **ODIBI CORE Studio** and master the ODIBI CORE framework through interactive learning!

**Enjoy the journey!** 🚀

---

*Created by Henry Odibi | Part of ODIBI CORE Framework*
