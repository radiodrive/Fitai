# agents/main.py - CrewAI Fitness Agents Main File
import json
import sys
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from typing import Any, Dict, List
import os

# Import custom tools
from tools.garmin_tools import GarminDataTool, FitnessCalculatorTool
from tools.fitness_calculations import RecoveryAnalyzer, TrainingLoadCalculator

class FitnessDataAnalyst(Agent):
    def __init__(self):
        super().__init__(
            role='Fitness Data Analyst',
            goal='Analyze fitness and health metrics to identify patterns, trends, and insights',
            backstory="""You are an expert data analyst specializing in fitness and health metrics. 
            You excel at finding patterns in heart rate, sleep, activity, and recovery data. 
            You can identify trends that indicate overtraining, optimal training zones, and recovery needs.""",
            tools=[GarminDataTool(), FitnessCalculatorTool(), RecoveryAnalyzer()],
            verbose=True,
            allow_delegation=False
        )

class FitnessCoach(Agent):
    def __init__(self):
        super().__init__(
            role='AI Fitness Coach',
            goal='Provide personalized training recommendations and motivation based on user data',
            backstory="""You are a certified personal trainer and fitness coach with deep knowledge 
            of exercise science, training periodization, and recovery. You provide practical, 
            actionable advice tailored to each individual's fitness level and goals.""",
            tools=[TrainingLoadCalculator(), RecoveryAnalyzer()],
            verbose=True,
            allow_delegation=False
        )

class HealthMonitor(Agent):
    def __init__(self):
        super().__init__(
            role='Health Monitor',
            goal='Monitor health indicators and flag potential concerns or areas for improvement',
            backstory="""You are a health monitoring specialist who watches for signs of overtraining, 
            poor recovery, irregular patterns, or other health concerns. You provide early warnings 
            and suggest when users should consider rest or consult healthcare professionals.""",
            tools=[RecoveryAnalyzer(), GarminDataTool()],
            verbose=True,
            allow_delegation=False
        )

class FitnessAgentCrew:
    def __init__(self):
        self.data_analyst = FitnessDataAnalyst()
        self.fitness_coach = FitnessCoach()
        self.health_monitor = HealthMonitor()
        
    def analyze_daily_insights(self, fitness_data: Dict) -> Dict:
        """Generate daily insights from fitness data"""
        
        # Create tasks for each agent
        analysis_task = Task(
            description=f"""Analyze this fitness data and identify key patterns:
            Steps: {fitness_data.get('steps', 0)}
            Heart Rate: {fitness_data.get('averageHeartRate', 'N/A')}
            Sleep Score: {fitness_data.get('sleepScore', 'N/A')}
            Stress Level: {fitness_data.get('stressLevel', 'N/A')}
            Recovery Status: {fitness_data.get('recoveryStatus', 'Unknown')}
            
            Provide 2-3 key insights about trends, performance, and areas of concern.""",
            agent=self.data_analyst,
            expected_output="A list of 2-3 analytical insights about the user's fitness patterns"
        )
        
        coaching_task = Task(
            description=f"""Based on the fitness data analysis, provide personalized coaching advice:
            Current recovery: {fitness_data.get('recoveryStatus', 'Unknown')}
            Recent activity: {fitness_data.get('lastActivity', {})}
            
            Give specific, actionable recommendations for today's training.""",
            agent=self.fitness_coach,
            expected_output="Specific training recommendations and motivational coaching advice"
        )
        
        health_task = Task(
            description=f"""Monitor the health indicators and flag any concerns:
            Sleep Score: {fitness_data.get('sleepScore', 'N/A')}
            Stress Level: {fitness_data.get('stressLevel', 'N/A')}
            Heart Rate: {fitness_data.get('averageHeartRate', 'N/A')}
            
            Check for signs of overtraining, poor recovery, or other health concerns.""",
            agent=self.health_monitor,
            expected_output="Health status assessment and any warnings or recommendations"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[self.data_analyst, self.fitness_coach, self.health_monitor],
            tasks=[analysis_task, coaching_task, health_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Format response
        insights = []
        
        # Parse results from each agent
        if hasattr(result, 'tasks_output'):
            for i, task_output in enumerate(result.tasks_output):
                agent_names = ['Data Analyst', 'Fitness Coach', 'Health Monitor']
                insights.append({
                    'title': f'{agent_names[i]} Insights',
                    'content': str(task_output),
                    'type': 'analysis' if i == 0 else 'recommendation' if i == 1 else 'health',
                    'agent': ['data_analyst', 'fitness_coach', 'health_monitor'][i]
                })
        else:
            # Fallback if result format is different
            insights.append({
                'title': 'Fitness Analysis',
                'content': str(result),
                'type': 'analysis',
                'agent': 'fitness_coach'
            })
        
        return {'insights': insights}
    
    def chat_response(self, fitness_data: Dict, user_message: str) -> Dict:
        """Handle chat interactions with the AI agents"""
        
        # Determine which agent should respond based on message content
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['data', 'trend', 'pattern', 'analysis', 'stats']):
            primary_agent = self.data_analyst
            agent_type = 'data_analyst'
        elif any(word in message_lower for word in ['health', 'concern', 'worry', 'overtraining', 'sick']):
            primary_agent = self.health_monitor
            agent_type = 'health_monitor'
        else:
            primary_agent = self.fitness_coach
            agent_type = 'fitness_coach'
        
        # Create chat task
        chat_task = Task(
            description=f"""The user asked: "{user_message}"
            
            Current fitness data context:
            - Steps today: {fitness_data.get('steps', 0)}
            - Recovery status: {fitness_data.get('recoveryStatus', 'Unknown')}
            - Sleep score: {fitness_data.get('sleepScore', 'N/A')}
            - Stress level: {fitness_data.get('stressLevel', 'N/A')}
            - Average heart rate: {fitness_data.get('averageHeartRate', 'N/A')}
            
            Provide a helpful, personalized response based on their data.""",
            agent=primary_agent,
            expected_output="A personalized response to the user's question based on their fitness data"
        )
        
        # Create single-agent crew for chat
        crew = Crew(
            agents=[primary_agent],
            tasks=[chat_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        return {
            'response': str(result),
            'agent_type': agent_type,
            'insights': []  # Could add related insights here
        }

def main():
    """Main function to handle requests from Node.js backend"""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No request data provided'}))
        return
    
    try:
        # Parse request from Node.js
        request_data = json.loads(sys.argv[1])
        request_type = request_data.get('request_type')
        fitness_data = request_data.get('data', {})
        message = request_data.get('message')
        
        # Initialize crew
        crew = FitnessAgentCrew()
        
        # Handle different request types
        if request_type == 'daily_insights':
            result = crew.analyze_daily_insights(fitness_data)
        elif request_type == 'chat':
            result = crew.chat_response(fitness_data, message)
        else:
            result = {'error': f'Unknown request type: {request_type}'}
        
        # Return result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'insights': [{
                'title': 'System Notice',
                'content': 'Unable to process request at this time. Please try again.',
                'type': 'error',
                'agent': 'system'
            }]
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()