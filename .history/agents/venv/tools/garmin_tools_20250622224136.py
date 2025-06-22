
# agents/fitness_ai_single.py - Everything in One File
import json
import sys
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from typing import Any, Dict, List
import statistics

# ============================================================================
# TOOLS - All fitness calculation tools in one place
# ============================================================================

class GarminDataTool(BaseTool):
    name: str = "Garmin Data Tool"
    description: str = "Access and analyze Garmin fitness data including activities, metrics, and trends"
    
    def _run(self, data_type: str = "all") -> str:
        """Access Garmin data for analysis"""
        return f"Garmin data accessed for: {data_type}"
