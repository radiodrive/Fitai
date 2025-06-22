import json
import sys
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from typing import Any, Dict, List
import statistics


class FitnessCalculatorTool(BaseTool):
    name: str = "Fitness Calculator"
    description: str = "Calculate fitness metrics, training zones, and performance indicators"
    
    def _run(self, calculation_type: str, **kwargs) -> str:
        """Perform fitness calculations"""
        if calculation_type == "heart_rate_zones":
            max_hr = kwargs.get('max_hr', 185)
            zones = self.calculate_hr_zones(max_hr)
            return f"Heart Rate Zones: {zones}"
        elif calculation_type == "training_load":
            activities = kwargs.get('activities', [])
            load = self.calculate_training_load(activities)
            return f"Training Load: {load}"
        else:
            return f"Calculation completed for: {calculation_type}"
    
    def calculate_hr_zones(self, max_hr: int) -> Dict:
        """Calculate heart rate training zones"""
        return {
            'Zone 1 (Recovery)': f"{int(max_hr * 0.5)}-{int(max_hr * 0.6)} bpm",
            'Zone 2 (Aerobic)': f"{int(max_hr * 0.6)}-{int(max_hr * 0.7)} bpm",
            'Zone 3 (Tempo)': f"{int(max_hr * 0.7)}-{int(max_hr * 0.8)} bpm",
            'Zone 4 (Threshold)': f"{int(max_hr * 0.8)}-{int(max_hr * 0.9)} bpm",
            'Zone 5 (VO2 Max)': f"{int(max_hr * 0.9)}-{max_hr} bpm"
        }
    
    def calculate_training_load(self, activities: List[Dict]) -> float:
        """Calculate training load from activities"""
        if not activities:
            return 0.0
        
        total_load = 0
        for activity in activities:
            duration = activity.get('duration', 0) / 60  # Convert to minutes
            intensity = activity.get('averageHeartRate', 120) / 180  # Normalize
            load = duration * intensity
            total_load += load
        
        return round(total_load, 2)

class RecoveryAnalyzer(BaseTool):
    name: str = "Recovery Analyzer"
    description: str = "Analyze recovery status and provide recommendations"
    
    def _run(self, recovery_data: Dict = None) -> str:
        """Analyze recovery metrics and provide insights"""
        if not recovery_data:
            return "No recovery data provided"
        
        sleep_score = recovery_data.get('sleepScore', 70)
        stress_level = recovery_data.get('stressLevel', 50)
        hrv = recovery_data.get('heartRateVariability', 30)
        resting_hr = recovery_data.get('restingHeartRate', 60)
        
        # Calculate recovery score
        recovery_score = self.calculate_recovery_score(sleep_score, stress_level, hrv, resting_hr)
        recommendations = self.get_recovery_recommendations(recovery_score)
        
        return f"Recovery Score: {recovery_score}/100. {recommendations}"
    
    def calculate_recovery_score(self, sleep: int, stress: int, hrv: int, rhr: int) -> int:
        """Calculate overall recovery score"""
        sleep_weight = 0.4
        stress_weight = 0.3
        hrv_weight = 0.2
        rhr_weight = 0.1
        
        stress_normalized = max(0, 100 - stress)
        
        score = (
            sleep * sleep_weight +
            stress_normalized * stress_weight +
            min(hrv * 2, 100) * hrv_weight +
            max(0, 100 - (rhr - 40)) * rhr_weight
        )
        
        return int(min(100, max(0, score)))
    
    def get_recovery_recommendations(self, score: int) -> str:
        """Provide recovery recommendations based on score"""
        if score >= 80:
            return "Excellent recovery! Perfect day for high-intensity training."
        elif score >= 65:
            return "Good recovery. Moderate to high intensity training recommended."
        elif score >= 50:
            return "Fair recovery. Consider light to moderate training."
        else:
            return "Poor recovery. Rest day or very light activity recommended."

class TrainingLoadCalculator(BaseTool):
    name: str = "Training Load Calculator"
    description: str = "Calculate and analyze training load and provide workout recommendations"
    
    def _run(self, training_data: Dict = None) -> str:
        """Calculate training load and provide recommendations"""
        if not training_data:
            return "No training data provided"
        
        recent_activities = training_data.get('recentActivities', [])
        current_load = self.calculate_current_load(recent_activities)
        recommendations = self.get_training_recommendations(current_load)
        
        return f"Current Training Load: {current_load}. {recommendations}"
    
    def calculate_current_load(self, activities: List[Dict]) -> float:
        """Calculate current training load from recent activities"""
        if not activities:
            return 0.0
        
        total_load = 0
        for activity in activities[-7:]:  # Last 7 days
            duration = activity.get('duration', 0) / 3600  # Convert to hours
            intensity = self.get_intensity_factor(activity.get('activityType', 'unknown'))
            avg_hr = activity.get('averageHeartRate', 120)
            hr_factor = avg_hr / 180  # Normalize heart rate
            
            load = duration * intensity * hr_factor * 100
            total_load += load
        
        return round(total_load, 1)
    
    def get_intensity_factor(self, activity_type: str) -> float:
        """Get intensity factor for different activity types"""
        intensity_map = {
            'running': 1.2,
            'cycling': 1.0,
            'swimming': 1.1,
            'strength_training': 0.8,
            'walking': 0.3,
            'yoga': 0.4,
            'unknown': 0.7
        }
        return intensity_map.get(activity_type.lower(), 0.7)
    
    def get_training_recommendations(self, load: float) -> str:
        """Provide training recommendations based on current load"""
        if load > 300:
            return "High training load detected. Consider reducing intensity or taking a rest day."
        elif load > 200:
            return "Moderate training load. Maintain current routine with adequate recovery."
        elif load > 100:
            return "Light training load. Good opportunity to increase intensity or volume."
        else:
            return "Low training load. Consider increasing activity level if feeling well."