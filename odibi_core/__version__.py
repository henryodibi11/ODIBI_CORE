"""Version information for ODIBI CORE."""

from datetime import datetime

__version__ = "1.1.0"
__phase__ = "learning-ecosystem"
__author__ = "Henry Odibi"
__build_date__ = datetime.now().isoformat()
__supported_engines__ = ["pandas", "spark"]
__python_requires__ = ">=3.8"
