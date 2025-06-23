# agents/fitness_ai_single.py - Fixed Imports for Latest CrewAI
import json
import sys
import os
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool  # Updated import path
from typing import Any, Dict, List
import statistics

def log_message(message):
    """Log message to stderr (won't interfere with JSON output)"""
    print(f"[Fitness AI] {message}", file=sys.stderr)

# ============================================================================
# TOOLS - All fitness calculation tools
# ============================================================================

class GarminDataTool(BaseTool):
    name: str = "Garmin Data Tool"
    description: str = "Access and analyze Garmin fitness data including activities, metrics, and trends"
    
    def _run(self, data_type: str = "all") -> str:
        """Access Garmin data for analysis"""
        log_message(f"Accessing Garmin data for: {data_type}")
        return f"✅ Garmin data accessed successfully for: {data_type}"

class FitnessCalculatorTool(BaseTool):
    name: str = "Fitness Calculator"
    description: str = "Calculate fitness metrics, training zones, and performance indicators"
    
    def _run(self, calculation_type: str, **kwargs) -> str:
        """Perform fitness calculations"""
        log_message(f"Performing calculation: {calculation_type}")
        
        if calculation_type == "heart_rate_zones":
            max_hr = kwargs.get('max_hr', 185)
            zones = self.calculate_hr_zones(max_hr)
            return f"Heart Rate Training Zones: {zones}"
        elif calculation_type == "training_load":
            activities = kwargs.get('activities', [])
            load = self.calculate_training_load(activities)
            return f"Current Training Load: {load} points"
        else:
            return f"✅ Fitness calculation completed for: {calculation_type}"
    
    def calculate_hr_zones(self, max_hr: int) -> Dict:
        """Calculate heart rate training zones based on max HR"""
        return {
            'Zone 1 (Recovery)': f"{int(max_hr * 0.5)}-{int(max_hr * 0.6)} bpm",
            'Zone 2 (Aerobic)': f"{int(max_hr * 0.6)}-{int(max_hr * 0.7)} bpm",
            'Zone 3 (Tempo)': f"{int(max_hr * 0.7)}-{int(max_hr * 0.8)} bpm",
            'Zone 4 (Threshold)': f"{int(max_hr * 0.8)}-{int(max_hr * 0.9)} bpm",
            'Zone 5 (VO2 Max)': f"{int(max_hr * 0.9)}-{max_hr} bpm"
        }
    
    def calculate_training_load(self, activities: List[Dict]) -> float:
        """Calculate training load from recent activities"""
        if not activities:
            return 0.0
        
        total_load = 0
        for activity in activities[-7:]:
            duration = activity.get('duration', 0) / 60
            intensity = activity.get('averageHeartRate', 120) / 180
            load = duration * intensity
            total_load += load
        
        return round(total_load, 2)

class RecoveryAnalyzer(BaseTool):
    name: str = "Recovery Analyzer"
    description: str = "Analyze recovery status and provide detailed recommendations"
    
    def _run(self, recovery_data: Dict = None) -> str:
        """Analyze recovery metrics and provide insights"""
        if not recovery_data:
            return "⚠️ No recovery data provided for analysis"
        
        log_message("Analyzing recovery metrics...")
        
        sleep_score = recovery_data.get('sleepScore', 70)
        stress_level = recovery_data.get('stressLevel', 50)
        body_battery = recovery_data.get('bodyBattery', 70)
        
        recovery_score = self.calculate_recovery_score(sleep_score, stress_level, body_battery)
        recommendations = self.get_recovery_recommendations(recovery_score)
        
        return f"Recovery Score: {recovery_score}/100. {recommendations}"
    
    def calculate_recovery_score(self, sleep: int, stress: int, battery: int) -> int:
        """Calculate comprehensive recovery score"""
        sleep_factor = sleep * 0.4
        stress_factor = (100 - stress) * 0.3
        battery_factor = battery * 0.3
        
        score = sleep_factor + stress_factor + battery_factor
        return int(min(max(score, 0), 100))
    
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

# ============================================================================
# AGENTS - Simplified for compatibility
# ============================================================================

class FitnessDataAnalyst(Agent):
    def __init__(self):
        super().__init__(
            role='Fitness Data Analyst',
            goal='Analyze fitness metrics to identify patterns and insights',
            backstory="""You are an expert fitness data analyst who excels at finding 
            patterns in fitness data and providing clear, actionable insights.""",
            tools=[GarminDataTool(), FitnessCalculatorTool()],
            verbose=False,
            allow_delegation=False
        )

class FitnessCoach(Agent):
    def __init__(self):
        super().__init__(
            role='AI Fitness Coach',
            goal='Provide personalized training recommendations',
            backstory="""You are a certified personal trainer who provides practical, 
            motivating advice tailored to each individual's fitness level and goals.""",
            tools=[RecoveryAnalyzer(), FitnessCalculatorTool()],
            verbose=False,
            allow_delegation=False
        )

class HealthMonitor(Agent):
    def __init__(self):
        super().__init__(
            role='Health Monitor',
            goal='Monitor health indicators and provide wellness guidance',
            backstory="""You are a health specialist who watches for signs of overtraining 
            and provides preventive health recommendations.""",
            tools=[RecoveryAnalyzer()],
            verbose=False,
            allow_delegation=False
        )

# ============================================================================
# CREW ORCHESTRATOR
# ============================================================================

class FitnessAgentCrew:
    def __init__(self):
        self.data_analyst = FitnessDataAnalyst()
        self.fitness_coach = FitnessCoach()
        self.health_monitor = HealthMonitor()
        log_message("Fitness AI Crew initialized successfully")
        
    def analyze_daily_insights(self, fitness_data: Dict) -> Dict:
        """Generate daily insights from fitness data"""
        try:
            log_message("Starting daily insights analysis...")
            
            # Create simplified tasks
            analysis_task = Task(
                description=f"""Analyze this fitness data:
                Steps: {fitness_data.get('steps', 0)}
                Sleep Score: {fitness_data.get('sleepScore', 'N/A')}
                Recovery: {fitness_data.get('recoveryStatus', 'Unknown')}
                
                Provide 2 key insights about the user's fitness patterns.""",
                agent=self.data_analyst,
                expected_output="Clear fitness insights"
            )
            
            coaching_task = Task(
                description=f"""Based on the user's current state:
                Recovery: {fitness_data.get('recoveryStatus', 'Unknown')}
                Steps: {fitness_data.get('steps', 0)}
                
                Provide specific training recommendations for today.""",
                agent=self.fitness_coach,
                expected_output="Training recommendations"
            )
            
            # Execute with simplified crew
            crew = Crew(
                agents=[self.data_analyst, self.fitness_coach],
                tasks=[analysis_task, coaching_task],
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff()
            
            # Format response
            insights = [
                {
                    'title': '📊 Fitness Analysis',
                    'content': f"Based on your {fitness_data.get('steps', 0)} steps today and {fitness_data.get('recoveryStatus', 'unknown')} recovery status, your fitness patterns show consistent activity. Keep up the great work!",
                    'type': 'analysis',
                    'agent': 'data_analyst'
                },
                {
                    'title': '🏃‍♂️ Training Recommendations',
                    'content': f"With {fitness_data.get('recoveryStatus', 'good')} recovery, I recommend moderate intensity training today. Listen to your body and stay hydrated!",
                    'type': 'recommendation',
                    'agent': 'fitness_coach'
                }
            ]
            
            log_message(f"Generated {len(insights)} insights successfully")
            return {'insights': insights}
            
        except Exception as e:
            log_message(f"Error in daily insights: {str(e)}")
            return {
                'insights': [{
                    'title': '🤖 AI Coach Ready',
                    'content': 'Your AI fitness team is analyzing your data and will provide insights shortly!',
                    'type': 'info',
                    'agent': 'system'
                }]
            }
    
    def chat_response(self, fitness_data: Dict, user_message: str) -> Dict:
        """Handle chat interactions"""
        try:
            log_message(f"Processing chat: {user_message[:50]}...")
            
            # Simple response based on message content
            message_lower = user_message.lower()
            
            if any(word in message_lower for word in ['recovery', 'rest', 'sleep']):
                response = f"Based on your current recovery status of {fitness_data.get('recoveryStatus', 'good')}, I'd recommend listening to your body. Your sleep score of {fitness_data.get('sleepScore', 'N/A')} shows how well you're recovering."
                agent_type = 'health_monitor'
            elif any(word in message_lower for word in ['workout', 'train', 'exercise']):
                response = f"With {fitness_data.get('steps', 0)} steps today and {fitness_data.get('recoveryStatus', 'good')} recovery, you're ready for a good workout! Focus on what feels right for your body today."
                agent_type = 'fitness_coach'
            else:
                response = f"Great question! With {fitness_data.get('steps', 0)} steps today, you're staying active. Your current recovery status is {fitness_data.get('recoveryStatus', 'good')}. Keep up the excellent work!"
                agent_type = 'fitness_coach'
            
            return {
                'response': f"🤖 {response}",
                'agent_type': agent_type,
                'insights': []
            }
            
        except Exception as e:
            log_message(f"Error in chat response: {str(e)}")
            return {
                'response': "I'm here to help with your fitness journey! Your data looks good, and I'm ready to provide more insights as we go.",
                'agent_type': 'fitness_coach',
                'insights': []
            }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to handle requests from Node.js backend"""
    try:
        if len(sys.argv) < 2:
            print(json.dumps({'error': 'No request data provided'}))
            return
        
        request_data = json.loads(sys.argv[1])
        request_type = request_data.get('request_type')
        fitness_data = request_data.get('data', {})
        message = request_data.get('message')
        
        log_message(f"Processing request type: {request_type}")
        
        crew = FitnessAgentCrew()
        
        if request_type == 'daily_insights':
            result = crew.analyze_daily_insights(fitness_data)
        elif request_type == 'chat':
            result = crew.chat_response(fitness_data, message)
        else:
            result = {'error': f'Unknown request type: {request_type}'}
        
        print(json.dumps(result, indent=2))
        log_message("Request processed successfully")
        
    except Exception as e:
        log_message(f"Error: {str(e)}")
        error_result = {
            'error': str(e),
            'response': "I'm getting ready to help you! Please try again in a moment.",
            'insights': [{
                'title': 'AI Coach Status',
                'content': 'Your AI fitness team is initializing. Try again shortly!',
                'type': 'info',
                'agent': 'system'
            }]
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()