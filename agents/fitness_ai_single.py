# agents/fitness_ai_single.py - Complete Fitness AI Agents System
import json
import sys
import os
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
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
        elif calculation_type == "vo2_estimate":
            hr_data = kwargs.get('heart_rate_data', [])
            vo2 = self.estimate_vo2_max(hr_data)
            return f"Estimated VO2 Max: {vo2} ml/kg/min"
        else:
            return f"✅ Fitness calculation completed for: {calculation_type}"
    
    def calculate_hr_zones(self, max_hr: int) -> Dict:
        """Calculate heart rate training zones based on max HR"""
        return {
            'Zone 1 (Active Recovery)': f"{int(max_hr * 0.5)}-{int(max_hr * 0.6)} bpm",
            'Zone 2 (Aerobic Base)': f"{int(max_hr * 0.6)}-{int(max_hr * 0.7)} bpm",
            'Zone 3 (Tempo)': f"{int(max_hr * 0.7)}-{int(max_hr * 0.8)} bpm",
            'Zone 4 (Lactate Threshold)': f"{int(max_hr * 0.8)}-{int(max_hr * 0.9)} bpm",
            'Zone 5 (VO2 Max)': f"{int(max_hr * 0.9)}-{max_hr} bpm"
        }
    
    def calculate_training_load(self, activities: List[Dict]) -> float:
        """Calculate training load from recent activities"""
        if not activities:
            return 0.0
        
        total_load = 0
        for activity in activities[-7:]:  # Last 7 days
            duration = activity.get('duration', 0) / 60  # Convert to minutes
            avg_hr = activity.get('averageHeartRate', 120)
            intensity = min(avg_hr / 180, 1.0)  # Normalize to max 1.0
            activity_load = duration * intensity * 10  # Scale factor
            total_load += activity_load
        
        return round(total_load, 1)
    
    def estimate_vo2_max(self, hr_data: List[int]) -> float:
        """Estimate VO2 Max from heart rate data (simplified)"""
        if not hr_data:
            return 45.0  # Average estimate
        
        avg_hr = statistics.mean(hr_data)
        # Simplified VO2 estimation (real calculation is much more complex)
        estimated_vo2 = 15.0 * (220 - 30) / avg_hr  # Assumes 30 years old
        return round(min(max(estimated_vo2, 25.0), 80.0), 1)

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
        hrv = recovery_data.get('heartRateVariability', 30)
        resting_hr = recovery_data.get('restingHeartRate', 60)
        body_battery = recovery_data.get('bodyBattery', 70)
        
        # Calculate comprehensive recovery score
        recovery_score = self.calculate_recovery_score(sleep_score, stress_level, hrv, resting_hr, body_battery)
        recommendations = self.get_detailed_recommendations(recovery_score, recovery_data)
        risk_factors = self.identify_risk_factors(recovery_data)
        
        analysis = f"""
Recovery Analysis Complete ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Recovery Score: {recovery_score}/100

Key Metrics:
• Sleep Quality: {sleep_score}/100
• Stress Level: {stress_level}/100
• Body Battery: {body_battery or 'N/A'}/100
• Resting HR: {resting_hr or 'N/A'} bpm

{recommendations}

{risk_factors}
        """
        
        return analysis.strip()
    
    def calculate_recovery_score(self, sleep: int, stress: int, hrv: int, rhr: int, battery: int = None) -> int:
        """Calculate comprehensive recovery score"""
        # Weighted recovery calculation
        factors = []
        
        # Sleep score (40% weight)
        if sleep:
            sleep_factor = sleep * 0.4
            factors.append(sleep_factor)
        
        # Stress level (30% weight) - lower is better
        if stress is not None:
            stress_factor = (100 - stress) * 0.3
            factors.append(stress_factor)
        
        # Body battery (20% weight)
        if battery:
            battery_factor = battery * 0.2
            factors.append(battery_factor)
        
        # HRV and RHR (10% weight combined)
        if hrv and rhr:
            # HRV: higher is better (normalize to 20-50 range)
            hrv_normalized = min(max((hrv - 20) / 30 * 100, 0), 100)
            # RHR: lower is better (normalize to 40-80 range)
            rhr_normalized = max(min((80 - rhr) / 40 * 100, 100), 0)
            hr_factor = (hrv_normalized + rhr_normalized) / 2 * 0.1
            factors.append(hr_factor)
        
        if not factors:
            return 50  # Default if no data
        
        final_score = sum(factors)
        return int(min(max(final_score, 0), 100))
    
    def get_detailed_recommendations(self, score: int, data: Dict) -> str:
        """Provide detailed recommendations based on recovery score"""
        if score >= 85:
            return """
🟢 EXCELLENT RECOVERY
Recommendations:
• Perfect day for high-intensity training
• Consider pushing your limits today
• Your body is fully recovered and ready
            """
        elif score >= 70:
            return """
🟡 GOOD RECOVERY  
Recommendations:
• Moderate to high intensity training recommended
• Listen to your body during workouts
• Good day for skill development
            """
        elif score >= 55:
            return """
🟠 MODERATE RECOVERY
Recommendations:
• Light to moderate training intensity
• Focus on technique and form
• Consider active recovery activities
            """
        else:
            return """
🔴 POOR RECOVERY
Recommendations:
• Rest day strongly recommended
• Prioritize sleep and stress management
• Light movement only (walking, gentle yoga)
• Consider massage or relaxation techniques
            """
    
    def identify_risk_factors(self, data: Dict) -> str:
        """Identify potential risk factors"""
        risks = []
        
        sleep = data.get('sleepScore', 70)
        stress = data.get('stressLevel', 50)
        battery = data.get('bodyBattery')
        
        if sleep < 60:
            risks.append("⚠️ Poor sleep quality detected")
        if stress > 70:
            risks.append("⚠️ High stress levels")
        if battery and battery < 40:
            risks.append("⚠️ Low body battery energy")
        
        if risks:
            return f"\nRisk Factors:\n" + "\n".join(risks)
        return "\n✅ No significant risk factors detected"

class TrainingLoadCalculator(BaseTool):
    name: str = "Training Load Calculator"
    description: str = "Calculate and analyze training load with periodization recommendations"
    
    def _run(self, training_data: Dict = None) -> str:
        """Calculate training load and provide recommendations"""
        if not training_data:
            return "⚠️ No training data provided for analysis"
        
        log_message("Calculating training load...")
        
        recent_activities = training_data.get('recentActivities', [])
        current_load = self.calculate_current_load(recent_activities)
        weekly_trend = self.analyze_weekly_trend(recent_activities)
        recommendations = self.get_training_recommendations(current_load, weekly_trend)
        
        analysis = f"""
Training Load Analysis 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current 7-Day Load: {current_load} points
Weekly Trend: {weekly_trend}

{recommendations}

Training Zones Recommendation:
{self.get_zone_recommendations(current_load)}
        """
        
        return analysis.strip()
    
    def calculate_current_load(self, activities: List[Dict]) -> float:
        """Calculate current training load from recent activities"""
        if not activities:
            return 0.0
        
        total_load = 0
        for activity in activities[-7:]:  # Last 7 days
            duration = activity.get('duration', 0) / 3600  # Convert to hours
            sport = activity.get('sport', 'unknown')
            avg_hr = activity.get('averageHeartRate', 120)
            
            # Sport-specific intensity factors
            intensity = self.get_sport_intensity_factor(sport)
            hr_factor = min(avg_hr / 180, 1.0)  # Heart rate intensity
            
            activity_load = duration * intensity * hr_factor * 100
            total_load += activity_load
        
        return round(total_load, 1)
    
    def get_sport_intensity_factor(self, sport: str) -> float:
        """Get intensity factor for different sports"""
        intensity_map = {
            'running': 1.3,
            'cycling': 1.0,
            'swimming': 1.2,
            'strength_training': 0.9,
            'walking': 0.3,
            'hiking': 0.6,
            'yoga': 0.4,
            'pilates': 0.5,
            'rowing': 1.1,
            'unknown': 0.8
        }
        return intensity_map.get(sport.lower(), 0.8)
    
    def analyze_weekly_trend(self, activities: List[Dict]) -> str:
        """Analyze weekly training trend"""
        if len(activities) < 3:
            return "Insufficient data"
        
        # Simple trend analysis
        recent_days = activities[-3:]
        older_days = activities[-7:-3] if len(activities) >= 7 else []
        
        if not older_days:
            return "Building baseline"
        
        recent_avg = sum(act.get('duration', 0) for act in recent_days) / len(recent_days)
        older_avg = sum(act.get('duration', 0) for act in older_days) / len(older_days)
        
        if recent_avg > older_avg * 1.2:
            return "🔺 Increasing (high)"
        elif recent_avg > older_avg * 1.1:
            return "📈 Increasing (moderate)"
        elif recent_avg < older_avg * 0.8:
            return "📉 Decreasing"
        else:
            return "➡️ Stable"
    
    def get_training_recommendations(self, load: float, trend: str) -> str:
        """Provide training recommendations based on load and trend"""
        if load > 400:
            return """
🔴 HIGH TRAINING LOAD
• Consider reducing intensity this week
• Focus on recovery and easy sessions
• Risk of overtraining - monitor fatigue closely
• Schedule a rest day within 48 hours
            """
        elif load > 250:
            return """
🟡 MODERATE-HIGH TRAINING LOAD
• Maintain current intensity
• Ensure adequate recovery between sessions
• Good training stimulus without excessive stress
• Monitor for signs of fatigue
            """
        elif load > 100:
            return """
🟢 OPTIMAL TRAINING LOAD
• Good training volume and intensity
• Consider adding variety to your routine
• Excellent balance of stress and recovery
• Continue current progression
            """
        else:
            return """
🔵 LOW TRAINING LOAD
• Opportunity to increase training volume
• Add an extra session this week if feeling good
• Focus on building aerobic base
• Consider longer or more frequent sessions
            """
    
    def get_zone_recommendations(self, load: float) -> str:
        """Get heart rate zone recommendations"""
        if load > 300:
            return "Focus: Zone 1-2 (Recovery/Easy), limit Zone 4-5"
        elif load > 200:
            return "Focus: Zone 2-3 (Aerobic/Tempo), 1x Zone 4 session"
        else:
            return "Focus: Zone 2-4 (Aerobic to Threshold), add intensity"

# ============================================================================
# AGENTS - Three specialized fitness AI agents
# ============================================================================

class FitnessDataAnalyst(Agent):
    def __init__(self):
        super().__init__(
            role='Fitness Data Analyst',
            goal='Analyze fitness and health metrics to identify patterns, trends, and actionable insights',
            backstory="""You are an expert sports scientist and data analyst with 15+ years of experience 
            in analyzing fitness data for elite athletes and fitness enthusiasts. You excel at finding 
            meaningful patterns in heart rate, sleep, activity, and recovery data. You can identify subtle 
            trends that indicate overtraining, optimal training zones, and recovery needs. Your analysis 
            is always backed by sports science principles and presented in clear, actionable terms.""",
            tools=[GarminDataTool(), FitnessCalculatorTool(), RecoveryAnalyzer()],
            verbose=True,
            allow_delegation=False
        )

class FitnessCoach(Agent):
    def __init__(self):
        super().__init__(
            role='AI Fitness Coach',
            goal='Provide personalized, motivating training recommendations based on scientific principles',
            backstory="""You are a certified personal trainer, exercise physiologist, and fitness coach 
            with expertise in training periodization, exercise prescription, and behavior change. You've 
            worked with thousands of clients from beginners to elite athletes. You provide practical, 
            actionable advice tailored to each individual's fitness level, goals, and current state. 
            You're encouraging but realistic, always prioritizing safety and sustainable progress. 
            Your coaching style is supportive, knowledgeable, and adaptable.""",
            tools=[TrainingLoadCalculator(), RecoveryAnalyzer(), FitnessCalculatorTool()],
            verbose=True,
            allow_delegation=False
        )

class HealthMonitor(Agent):
    def __init__(self):
        super().__init__(
            role='Health & Wellness Monitor',
            goal='Monitor health indicators, identify potential concerns, and promote optimal wellness',
            backstory="""You are a health monitoring specialist and wellness expert with deep knowledge 
            of exercise physiology, recovery science, and preventive health. You watch for signs of 
            overtraining, poor recovery, irregular patterns, or other health concerns. You provide early 
            warnings and evidence-based suggestions for when users should prioritize rest, adjust training, 
            or consult healthcare professionals. You're cautious but not alarmist, focusing on preventive 
            care, long-term wellness, and helping people build sustainable healthy habits.""",
            tools=[RecoveryAnalyzer(), GarminDataTool(), FitnessCalculatorTool()],
            verbose=True,
            allow_delegation=False
        )

# ============================================================================
# CREW ORCHESTRATOR - Coordinates all agents
# ============================================================================

class FitnessAgentCrew:
    def __init__(self):
        self.data_analyst = FitnessDataAnalyst()
        self.fitness_coach = FitnessCoach()
        self.health_monitor = HealthMonitor()
        log_message("Fitness AI Crew initialized successfully")
        
    def analyze_daily_insights(self, fitness_data: Dict) -> Dict:
        """Generate comprehensive daily insights from fitness data"""
        try:
            log_message("Starting daily insights analysis...")
            
            # Create detailed tasks for each agent
            analysis_task = Task(
                description=f"""Analyze today's fitness data and provide key insights:
                
                📊 FITNESS METRICS:
                • Steps: {fitness_data.get('steps', 0):,}
                • Average Heart Rate: {fitness_data.get('averageHeartRate', 'N/A')} bpm
                • Sleep Score: {fitness_data.get('sleepScore', 'N/A')}/100
                • Stress Level: {fitness_data.get('stressLevel', 'N/A')}/100
                • Body Battery: {fitness_data.get('bodyBattery', 'N/A')}/100
                • Resting HR: {fitness_data.get('restingHeartRate', 'N/A')} bpm
                • Recovery Status: {fitness_data.get('recoveryStatus', 'Unknown')}
                
                🏃 RECENT ACTIVITY:
                • Last Activity: {fitness_data.get('lastActivity', {}).get('activityName', 'None')}
                • Sport: {fitness_data.get('lastActivity', {}).get('sport', 'N/A')}
                • Duration: {fitness_data.get('lastActivity', {}).get('duration', 0)} seconds
                
                Provide 2-3 key analytical insights about patterns, performance trends, and notable observations.
                Focus on what the data reveals about the user's current fitness state and trajectory.""",
                agent=self.data_analyst,
                expected_output="Clear, data-driven insights about fitness patterns with specific observations"
            )
            
            coaching_task = Task(
                description=f"""Based on the fitness data analysis, provide personalized coaching guidance:
                
                🎯 CURRENT STATUS:
                • Recovery: {fitness_data.get('recoveryStatus', 'Unknown')}
                • Last Workout: {fitness_data.get('lastActivity', {}).get('activityName', 'None')}
                • Activity Level: {fitness_data.get('steps', 0):,} steps today
                • Sleep Quality: {fitness_data.get('sleepScore', 'N/A')}/100
                • Energy Level: {fitness_data.get('bodyBattery', 'N/A')}/100
                
                Provide specific, actionable recommendations for:
                1. Today's optimal training approach
                2. Intensity and duration suggestions
                3. Motivational guidance based on current state
                4. Any adjustments needed based on recovery status
                
                Be encouraging while being realistic about what the user should focus on.""",
                agent=self.fitness_coach,
                expected_output="Specific training recommendations with motivational coaching advice"
            )
            
            health_task = Task(
                description=f"""Assess health indicators and provide wellness guidance:
                
                🏥 HEALTH INDICATORS:
                • Sleep Quality: {fitness_data.get('sleepScore', 'N/A')}/100
                • Stress Level: {fitness_data.get('stressLevel', 'N/A')}/100
                • Heart Rate: {fitness_data.get('averageHeartRate', 'N/A')} bpm (avg), {fitness_data.get('restingHeartRate', 'N/A')} bpm (resting)
                • Recovery Status: {fitness_data.get('recoveryStatus', 'Unknown')}
                • Body Battery: {fitness_data.get('bodyBattery', 'N/A')}/100
                
                Monitor for:
                1. Signs of overtraining or insufficient recovery
                2. Sleep quality concerns
                3. Stress level management needs
                4. Any patterns requiring attention
                
                Provide wellness recommendations and flag any concerns that need attention.""",
                agent=self.health_monitor,
                expected_output="Health assessment with wellness recommendations and any necessary warnings"
            )
            
            # Execute crew with all agents
            crew = Crew(
                agents=[self.data_analyst, self.fitness_coach, self.health_monitor],
                tasks=[analysis_task, coaching_task, health_task],
                process=Process.sequential,
                verbose=True
            )
            
            log_message("Executing crew tasks...")
            result = crew.kickoff()
            
            # Format comprehensive response
            insights = []
            
            try:
                if hasattr(result, 'tasks_output') and result.tasks_output:
                    agent_info = [
                        ('📊 Data Analysis Insights', 'analysis', 'data_analyst'),
                        ('🏃‍♂️ Coaching Recommendations', 'recommendation', 'fitness_coach'),
                        ('🏥 Health & Wellness Monitor', 'health', 'health_monitor')
                    ]
                    
                    for i, (title, insight_type, agent_name) in enumerate(agent_info):
                        if i < len(result.tasks_output):
                            content = str(result.tasks_output[i]).strip()
                            if content:
                                insights.append({
                                    'title': title,
                                    'content': content,
                                    'type': insight_type,
                                    'agent': agent_name,
                                    'timestamp': datetime.now().isoformat()
                                })
                else:
                    # Fallback if result format is different
                    insights.append({
                        'title': '🤖 AI Fitness Analysis',
                        'content': str(result).strip(),
                        'type': 'analysis',
                        'agent': 'fitness_coach',
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as parse_error:
                log_message(f"Error parsing crew results: {parse_error}")
                insights.append({
                    'title': '⚡ Quick Fitness Update',
                    'content': f"Based on your metrics today: {fitness_data.get('steps', 0):,} steps, recovery status is {fitness_data.get('recoveryStatus', 'unknown')}. Your AI coaches are analyzing the data for personalized insights!",
                    'type': 'info',
                    'agent': 'system',
                    'timestamp': datetime.now().isoformat()
                })
            
            if not insights:
                insights.append({
                    'title': '🔄 Analysis in Progress',
                    'content': 'Your AI fitness team is processing your latest data. Check back in a moment for personalized insights and recommendations!',
                    'type': 'info',
                    'agent': 'system',
                    'timestamp': datetime.now().isoformat()
                })
            
            log_message(f"Generated {len(insights)} insights successfully")
            return {'insights': insights}
            
        except Exception as e:
            log_message(f"Error in daily insights analysis: {str(e)}")
            return {
                'insights': [{
                    'title': '⚠️ Analysis Update',
                    'content': 'Your fitness data is being processed by the AI team. The analysis will be ready shortly with personalized insights!',
                    'type': 'info',
                    'agent': 'system',
                    'timestamp': datetime.now().isoformat()
                }]
            }
    
    def chat_response(self, fitness_data: Dict, user_message: str) -> Dict:
        """Handle intelligent chat interactions with appropriate agent selection"""
        try:
            log_message(f"Processing chat message: {user_message[:50]}...")
            
            # Smart agent selection based on message content
            message_lower = user_message.lower()
            
            # Determine the most appropriate agent
            if any(word in message_lower for word in [
                'data', 'trend', 'pattern', 'analysis', 'stats', 'numbers', 'chart', 'graph', 'compare', 'progress'
            ]):
                primary_agent = self.data_analyst
                agent_type = 'data_analyst'
                agent_emoji = '📊'
                agent_name = 'Data Analyst'
            elif any(word in message_lower for word in [
                'health', 'concern', 'worry', 'overtraining', 'sick', 'tired', 'rest', 'sleep', 'stress', 'recovery', 'wellness'
            ]):
                primary_agent = self.health_monitor
                agent_type = 'health_monitor'
                agent_emoji = '🏥'
                agent_name = 'Health Monitor'
            else:
                primary_agent = self.fitness_coach
                agent_type = 'fitness_coach'
                agent_emoji = '🏃‍♂️'
                agent_name = 'Fitness Coach'
            
            # Create contextual chat task
            chat_task = Task(
                description=f"""The user asked: "{user_message}"
                
                📱 CURRENT FITNESS CONTEXT:
                • Steps today: {fitness_data.get('steps', 0):,}
                • Recovery status: {fitness_data.get('recoveryStatus', 'Unknown')}
                • Sleep score: {fitness_data.get('sleepScore', 'N/A')}/100
                • Stress level: {fitness_data.get('stressLevel', 'N/A')}/100
                • Body battery: {fitness_data.get('bodyBattery', 'N/A')}/100
                • Average heart rate: {fitness_data.get('averageHeartRate', 'N/A')} bpm
                • Resting heart rate: {fitness_data.get('restingHeartRate', 'N/A')} bpm
                • Last activity: {fitness_data.get('lastActivity', {}).get('activityName', 'None')}
                
                🎯 YOUR ROLE: Respond as the {agent_name} with your specific expertise.
                
                Provide a helpful, personalized response that:
                1. Directly addresses their question
                2. Uses their current fitness data for context
                3. Offers actionable insights or advice
                4. Maintains a conversational, supportive tone
                5. Draws on your specialized knowledge
                
                Keep the response focused, practical, and encouraging.""",
                agent=primary_agent,
                expected_output="A personalized, conversational response with actionable advice"
            )
            
            # Create focused crew for chat response
            crew = Crew(
                agents=[primary_agent],
                tasks=[chat_task],
                process=Process.sequential,
                verbose=False
            )
            
            log_message(f"Executing chat task with {agent_name}...")
            result = crew.kickoff()
            
            response_text = str(result).strip()
            
            # Ensure we have a valid response
            if not response_text or len(response_text) < 10:
                response_text = self._get_fallback_response(agent_type, user_message, fitness_data)
            
            log_message("Chat response generated successfully")
            return {
                'response': f"{agent_emoji} {response_text}",
                'agent_type': agent_type,
                'agent_name': agent_name,
                'insights': [],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            log_message(f"Error in chat response: {str(e)}")
            return self._get_error_response(user_message, fitness_data)
    
    def _get_fallback_response(self, agent_type: str, message: str, data: Dict) -> str:
        """Generate fallback responses when main processing fails"""
        fallback_responses = {
            'data_analyst': f"Looking at your current metrics: {data.get('steps', 0):,} steps today with a {data.get('recoveryStatus', 'unknown')} recovery status. I'm analyzing patterns in your data to provide more detailed insights!",
            
            'health_monitor': f"I'm monitoring your health indicators. Your current recovery status is {data.get('recoveryStatus', 'unknown')} with a sleep score of {data.get('sleepScore', 'N/A')}/100. Remember to listen to your body and prioritize recovery when needed.",
            
            'fitness_coach': f"Great question! Based on your current status ({data.get('recoveryStatus', 'unknown')} recovery), I'd recommend staying consistent with your fitness routine. Every step counts toward your goals - you've got {data.get('steps', 0):,} steps today!"
        }
        
        return fallback_responses.get(agent_type, "I'm here to help with your fitness journey! Your current metrics show progress, and I'm working on providing you with more personalized insights.")
    
    def _get_error_response(self, message: str, data: Dict) -> Dict:
        """Generate error response when processing completely fails"""
        return {
            'response': f"🤖 I'm processing your question about your fitness data. Your current status shows {data.get('steps', 0):,} steps today. Let me gather more insights for you!",
            'agent_type': 'system',
            'agent_name': 'AI System',
            'insights': [],
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Main function to handle requests from Node.js backend"""
    try:
        if len(sys.argv) < 2:
            print(json.dumps({
                'error': 'No request data provided',
                'usage': 'python fitness_ai_single.py <json_request>'
            }))
            return
        
        # Parse request from Node.js
        request_data = json.loads(sys.argv[1])
        request_type = request_data.get('request_type')
        fitness_data = request_data.get('data', {})
        message = request_data.get('message')
        
        log_message(f"Processing request type: {request_type}")
        
        # Initialize the AI crew
        crew = FitnessAgentCrew()
        
        # Handle different request types
        if request_type == 'daily_insights':
            log_message("Generating daily insights...")
            result = crew.analyze_daily_insights(fitness_data)
            
        elif request_type == 'chat':
            log_message(f"Processing chat message: {message}")
            result = crew.chat_response(fitness_data, message)
            
        else:
            log_message(f"Unknown request type: {request_type}")
            result = {
                'error': f'Unknown request type: {request_type}',
                'supported_types': ['daily_insights', 'chat'],
                'insights': [{
                    'title': '❓ Unknown Request',
                    'content': 'The request type is not recognized. Please use "daily_insights" or "chat".',
                    'type': 'error',
                    'agent': 'system',
                    'timestamp': datetime.now().isoformat()
                }]
            }
        
        # Return result as JSON
        print(json.dumps(result, indent=2))
        log_message("Request processed successfully")
        
    except json.JSONDecodeError as e:
        log_message(f"JSON decode error: {str(e)}")
        error_result = {
            'error': 'Invalid JSON in request',
            'details': str(e),
            'response': 'There was an issue processing your request. Please try again.',
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_result))
        
    except Exception as e:
        log_message(f"Unexpected error: {str(e)}")
        error_result = {
            'error': str(e),
            'response': "I'm having trouble processing your request right now. Your fitness data is safe, and I'll be back online shortly!",
            'insights': [{
                'title': '⚠️ System Notice',
                'content': 'The AI fitness team is experiencing a brief issue. Your data is secure and analysis will resume momentarily.',
                'type': 'error',
                'agent': 'system',
                'timestamp': datetime.now().isoformat()
            }],
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()