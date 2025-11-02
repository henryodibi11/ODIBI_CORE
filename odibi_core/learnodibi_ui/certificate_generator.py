"""
Certificate Generator - Create completion certificates for learners
"""

from datetime import datetime
from pathlib import Path


def generate_certificate(learner_name: str, completion_data: dict) -> str:
    """
    Generate a completion certificate in markdown format
    
    Args:
        learner_name: Name of the learner
        completion_data: Dict with lessons_completed, steps_completed, badges, etc.
        
    Returns:
        Certificate content as markdown string
    """
    total_lessons = completion_data.get("total_lessons", 11)
    completed_lessons = len(completion_data.get("lessons_completed", []))
    total_steps = sum(len(steps) for steps in completion_data.get("steps_completed", {}).values())
    badges = len(completion_data.get("badges_earned", []))
    quizzes = len(completion_data.get("quizzes_passed", []))
    
    completion_date = datetime.now().strftime("%B %d, %Y")
    
    certificate = f"""
---
# 🎓 CERTIFICATE OF COMPLETION 🎓

---

## This certifies that

# **{learner_name}**

## Has successfully completed the

# ODIBI CORE Development Course

---

### 📊 Achievement Summary

**Lessons Completed:** {completed_lessons} / {total_lessons}  
**Steps Completed:** {total_steps}  
**Quizzes Passed:** {quizzes}  
**Badges Earned:** {badges} 🏆

---

### ✅ Competencies Demonstrated

- ✅ **Core Architecture** - Mastered the 5 Canonical Nodes
- ✅ **Dual-Engine Development** - Built code for Pandas and Spark
- ✅ **Configuration Systems** - Created config-driven pipelines
- ✅ **Functions Library** - Utilized 100+ engineering utilities
- ✅ **Production Deployment** - Applied SDK and CLI tools
- ✅ **Best Practices** - Followed medallion architecture patterns

---

### 🌟 Skills Acquired

**Data Engineering:**
- Bronze → Silver → Gold pipeline design
- ETL/ELT pattern implementation
- Data quality validation
- Error handling and logging

**Software Engineering:**
- Engine-agnostic code design
- Configuration management
- Testing and validation
- SDK and CLI development

**Production Readiness:**
- Cloud deployment (Azure, Databricks)
- Streaming data processing
- Observability and monitoring
- Performance optimization

---

### 🏆 Certification Level

"""
    
    # Determine certification level
    if completed_lessons == total_lessons and quizzes >= 10 and badges >= 5:
        certificate += """
**🌟 MASTER LEVEL 🌟**

*Completed all lessons, passed all quizzes, earned multiple badges.*  
*Ready for production data engineering with ODIBI CORE.*
"""
    elif completed_lessons >= 8:
        certificate += """
**⭐ ADVANCED LEVEL ⭐**

*Completed majority of lessons and demonstrated strong understanding.*  
*Capable of building complex ODIBI CORE pipelines.*
"""
    elif completed_lessons >= 5:
        certificate += """
**📚 INTERMEDIATE LEVEL 📚**

*Completed core lessons and essential competencies.*  
*Ready to build basic ODIBI CORE pipelines.*
"""
    else:
        certificate += """
**📖 FOUNDATION LEVEL 📖**

*Completed initial lessons and gained foundational knowledge.*  
*Continue learning to unlock advanced capabilities.*
"""
    
    certificate += f"""

---

**Issued:** {completion_date}  
**Powered by:** ODIBI CORE Framework  
**Created by:** Henry Odibi  

---

*This certificate demonstrates successful completion of the LearnODIBI Studio course.*  
*Share your achievement with #ODIBICoreGraduate*

---
"""
    
    return certificate


def generate_certificate_html(learner_name: str, completion_data: dict) -> str:
    """Generate HTML version of certificate for better printing"""
    md_cert = generate_certificate(learner_name, completion_data)
    
    # Simple HTML wrapper with styling
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ODIBI CORE Certificate - {learner_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', 'Georgia', serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 3rem;
            background: linear-gradient(135deg, #FFF7ED, #FFFFFF);
            border: 10px solid #F5B400;
        }}
        h1 {{
            color: #F5B400;
            text-align: center;
            font-size: 2.5rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        h2 {{
            color: #00A86B;
            text-align: center;
        }}
        h3 {{
            color: #D97706;
            border-bottom: 2px solid #F5B400;
            padding-bottom: 0.5rem;
        }}
        .learner-name {{
            font-size: 3rem;
            color: #D97706;
            text-align: center;
            margin: 2rem 0;
            font-weight: bold;
        }}
        .date {{
            text-align: center;
            color: #6B7280;
            font-style: italic;
        }}
        ul {{
            line-height: 2;
        }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: 'Segoe UI';">
{md_cert}
    </pre>
</body>
</html>
"""
    return html
