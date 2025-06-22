# backend/garmindb_service.py - Python Bridge for GarminDB
import sys
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
from pathlib import Path

def log_message(message):
    """Log message to stderr (won't interfere with JSON output)"""
    print(f"[GarminDB Service] {message}", file=sys.stderr)

class GarminDBBridge:
    def __init__(self, garmindb_path: str = None):
        """Initialize GarminDB bridge"""
        self.garmindb_path = garmindb_path or os.path.expanduser("~/GarminDB")
        self.setup_database_paths()
        log_message(f"GarminDB path: {self.garmindb_path}")
    
    def setup_database_paths(self):
        """Setup database file paths"""
        self.databases = {
            'garmin': os.path.join(self.garmindb_path, "garmin.db"),
            'activities': os.path.join(self.garmindb_path, "garmin_activities.db"),
            'monitoring': os.path.join(self.garmindb_path, "garmin_monitoring.db"),
            'summary': os.path.join(self.garmindb_path, "garmin_summary.db")
        }
    
    def check_garmindb_status(self) -> Dict:
        """Check if GarminDB is properly set up"""
        try:
            # Check if directory exists
            if not os.path.exists(self.garmindb_path):
                return {
                    'connected': False,
                    'status': 'GarminDB directory not found',
                    'setup_required': True,
                    'path': self.garmindb_path
                }
            
            # Check if databases exist
            missing_dbs = []
            for db_name, db_path in self.databases.items():
                if not os.path.exists(db_path):
                    missing_dbs.append(db_name)
            
            if missing_dbs:
                return {
                    'connected': False,
                    'status': f'Missing databases: {", ".join(missing_dbs)}',
                    'setup_required': True,
                    'missing_databases': missing_dbs
                }
            
            # Check if databases have data
            try:
                conn = sqlite3.connect(self.databases['monitoring'])
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM monitoring_info LIMIT 1")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count == 0:
                    return {
                        'connected': True,
                        'status': 'GarminDB found but no data - run sync first',
                        'setup_required': False,
                        'has_data': False
                    }
                
                return {
                    'connected': True,
                    'status': 'GarminDB ready',
                    'setup_required': False,
                    'has_data': True,
                    'data_count': count
                }
                
            except sqlite3.Error as e:
                return {
                    'connected': False,
                    'status': f'Database error: {str(e)}',
                    'setup_required': True
                }
                
        except Exception as e:
            return {
                'connected': False,
                'status': f'Error checking GarminDB: {str(e)}',
                'setup_required': True
            }
    
    def sync_garmin_data(self) -> Dict:
        """Trigger GarminDB sync"""
        try:
            log_message("Starting GarminDB sync...")
            
            # Try to run garmindb_cli.py
            cmd = ["garmindb_cli.py", "--import", "--analyze", "--latest"]
            
            result = subprocess.run(
                cmd, 
                cwd=self.garmindb_path,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                log_message("GarminDB sync completed successfully")
                return {
                    'success': True,
                    'message': 'Data sync completed successfully',
                    'lastSync': datetime.now().isoformat(),
                    'output': result.stdout[-500:] if result.stdout else ""  # Last 500 chars
                }
            else:
                log_message(f"GarminDB sync failed: {result.stderr}")
                return {
                    'success': False,
                    'message': 'Sync failed - check GarminDB configuration',
                    'error': result.stderr[-500:] if result.stderr else "Unknown error",
                    'lastSync': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Sync timeout - process took too long',
                'lastSync': datetime.now().isoformat()
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': 'garmindb_cli.py not found - check GarminDB installation',
                'lastSync': datetime.now().isoformat()
            }
        except Exception as e:
            log_message(f"Sync error: {str(e)}")
            return {
                'success': False,
                'message': f'Sync error: {str(e)}',
                'lastSync': datetime.now().isoformat()
            }
    
    def get_latest_metrics(self, days_back: int = 1) -> Dict:
        """Get latest fitness metrics from GarminDB"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            log_message(f"Fetching metrics from {start_date} to {end_date}")
            
            metrics = {
                'steps': self._get_daily_steps(start_date, end_date),
                'averageHeartRate': self._get_average_heart_rate(start_date, end_date),
                'sleepScore': self._get_sleep_score(start_date, end_date),
                'stressLevel': self._get_stress_level(start_date, end_date),
                'bodyBattery': self._get_body_battery(start_date, end_date),
                'restingHeartRate': self._get_resting_heart_rate(start_date, end_date),
                'lastActivity': self._get_latest_activity(),
                'timestamp': datetime.now().isoformat(),
                'dataSource': 'garmindb'
            }
            
            # Calculate derived metrics
            metrics['recoveryStatus'] = self._calculate_recovery_status(metrics)
            metrics['recoveryAdvice'] = self._get_recovery_advice(metrics)
            
            log_message(f"Retrieved metrics: steps={metrics['steps']}, hr={metrics['averageHeartRate']}")
            return metrics
            
        except Exception as e:
            log_message(f"Error getting metrics: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'dataSource': 'error'
            }
    
    def _get_daily_steps(self, start_date: datetime, end_date: datetime) -> int:
        """Get daily steps from monitoring database"""
        try:
            conn = sqlite3.connect(self.databases['monitoring'])
            cursor = conn.cursor()
            
            # Try different table structures GarminDB might use
            queries = [
                "SELECT SUM(steps) FROM monitoring_info WHERE timestamp BETWEEN ? AND ? AND steps IS NOT NULL",
                "SELECT SUM(steps) FROM monitoring_daily WHERE day BETWEEN ? AND ? AND steps IS NOT NULL",
                "SELECT steps FROM monitoring_info WHERE DATE(timestamp) = DATE(?) ORDER BY timestamp DESC LIMIT 1"
            ]
            
            for query in queries:
                try:
                    if "daily" in query:
                        cursor.execute(query, (start_date.date().isoformat(), end_date.date().isoformat()))
                    elif "DATE(" in query:
                        cursor.execute(query, (end_date.isoformat(),))
                    else:
                        cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
                    
                    result = cursor.fetchone()
                    if result and result[0]:
                        conn.close()
                        return int(result[0])
                except sqlite3.Error:
                    continue
            
            conn.close()
            return 0
            
        except Exception as e:
            log_message(f"Error getting steps: {str(e)}")
            return 0
    
    def _get_average_heart_rate(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get average heart rate"""
        try:
            conn = sqlite3.connect(self.databases['monitoring'])
            cursor = conn.cursor()
            
            queries = [
                "SELECT AVG(heart_rate) FROM monitoring_hr WHERE timestamp BETWEEN ? AND ? AND heart_rate > 0",
                "SELECT AVG(avg_hr) FROM monitoring_info WHERE timestamp BETWEEN ? AND ? AND avg_hr > 0"
            ]
            
            for query in queries:
                try:
                    cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
                    result = cursor.fetchone()
                    if result and result[0]:
                        conn.close()
                        return int(result[0])
                except sqlite3.Error:
                    continue
            
            conn.close()
            return None
            
        except Exception as e:
            log_message(f"Error getting heart rate: {str(e)}")
            return None
    
    def _get_sleep_score(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get sleep score"""
        try:
            # Try summary database first
            for db_key in ['summary', 'garmin']:
                try:
                    conn = sqlite3.connect(self.databases[db_key])
                    cursor = conn.cursor()
                    
                    queries = [
                        "SELECT sleep_score FROM sleep_events WHERE day BETWEEN ? AND ? ORDER BY day DESC LIMIT 1",
                        "SELECT overall_score FROM sleep WHERE day BETWEEN ? AND ? ORDER BY day DESC LIMIT 1"
                    ]
                    
                    for query in queries:
                        try:
                            cursor.execute(query, (start_date.date().isoformat(), end_date.date().isoformat()))
                            result = cursor.fetchone()
                            if result and result[0]:
                                conn.close()
                                return int(result[0])
                        except sqlite3.Error:
                            continue
                    
                    conn.close()
                except:
                    continue
            
            return None
            
        except Exception as e:
            log_message(f"Error getting sleep score: {str(e)}")
            return None
    
    def _get_stress_level(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get stress level"""
        try:
            conn = sqlite3.connect(self.databases['monitoring'])
            cursor = conn.cursor()
            
            queries = [
                "SELECT AVG(stress_level) FROM monitoring_info WHERE timestamp BETWEEN ? AND ? AND stress_level >= 0",
                "SELECT stress FROM monitoring_stress WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC LIMIT 1"
            ]
            
            for query in queries:
                try:
                    cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
                    result = cursor.fetchone()
                    if result and result[0] is not None:
                        conn.close()
                        return int(result[0])
                except sqlite3.Error:
                    continue
            
            conn.close()
            return None
            
        except Exception as e:
            log_message(f"Error getting stress level: {str(e)}")
            return None
    
    def _get_body_battery(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get body battery level"""
        try:
            conn = sqlite3.connect(self.databases['monitoring'])
            cursor = conn.cursor()
            
            queries = [
                "SELECT body_battery FROM monitoring_info WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC LIMIT 1",
                "SELECT battery_level FROM body_battery WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC LIMIT 1"
            ]
            
            for query in queries:
                try:
                    cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
                    result = cursor.fetchone()
                    if result and result[0] is not None:
                        conn.close()
                        return int(result[0])
                except sqlite3.Error:
                    continue
            
            conn.close()
            return None
            
        except Exception as e:
            log_message(f"Error getting body battery: {str(e)}")
            return None
    
    def _get_resting_heart_rate(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get resting heart rate"""
        try:
            for db_key in ['summary', 'garmin']:
                try:
                    conn = sqlite3.connect(self.databases[db_key])
                    cursor = conn.cursor()
                    
                    queries = [
                        "SELECT rhr FROM resting_hr WHERE day BETWEEN ? AND ? ORDER BY day DESC LIMIT 1",
                        "SELECT resting_hr FROM daily_summary WHERE day BETWEEN ? AND ? ORDER BY day DESC LIMIT 1"
                    ]
                    
                    for query in queries:
                        try:
                            cursor.execute(query, (start_date.date().isoformat(), end_date.date().isoformat()))
                            result = cursor.fetchone()
                            if result and result[0]:
                                conn.close()
                                return int(result[0])
                        except sqlite3.Error:
                            continue
                    
                    conn.close()
                except:
                    continue
            
            return None
            
        except Exception as e:
            log_message(f"Error getting resting heart rate: {str(e)}")
            return None
    
    def _get_latest_activity(self) -> Optional[Dict]:
        """Get most recent activity"""
        try:
            conn = sqlite3.connect(self.databases['activities'])
            cursor = conn.cursor()
            
            query = """
            SELECT name, start_time, sport, distance, avg_hr, calories, elapsed_time
            FROM activities 
            WHERE start_time IS NOT NULL
            ORDER BY start_time DESC
            LIMIT 1
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'activityName': result[0] or 'Unknown Activity',
                    'startTime': result[1],
                    'sport': result[2] or 'unknown',
                    'distance': float(result[3]) if result[3] else 0,
                    'averageHeartRate': int(result[4]) if result[4] else 0,
                    'calories': int(result[5]) if result[5] else 0,
                    'duration': int(result[6]) if result[6] else 0
                }
            return None
            
        except Exception as e:
            log_message(f"Error getting latest activity: {str(e)}")
            return None
    
    def _calculate_recovery_status(self, metrics: Dict) -> str:
        """Calculate recovery status"""
        factors = []
        
        if metrics.get('sleepScore'):
            sleep = metrics['sleepScore']
            if sleep >= 80: factors.append(2)
            elif sleep >= 65: factors.append(1)
            else: factors.append(-1)
        
        if metrics.get('stressLevel'):
            stress = metrics['stressLevel']
            if stress <= 25: factors.append(2)
            elif stress <= 50: factors.append(1)
            else: factors.append(-1)
        
        if metrics.get('bodyBattery'):
            battery = metrics['bodyBattery']
            if battery >= 80: factors.append(2)
            elif battery >= 60: factors.append(1)
            else: factors.append(-1)
        
        if not factors:
            return "Recovery Data Unavailable"
        
        avg = sum(factors) / len(factors)
        
        if avg >= 1.5: return "Excellent Recovery"
        elif avg >= 0.5: return "Good Recovery"
        elif avg >= -0.5: return "Moderate Recovery"
        else: return "Poor Recovery"
    
    def _get_recovery_advice(self, metrics: Dict) -> str:
        """Get recovery advice"""
        status = metrics.get('recoveryStatus', 'Unknown')
        
        advice = {
            'Excellent Recovery': 'Perfect day for high-intensity training! Your metrics show full recovery.',
            'Good Recovery': 'Good day for moderate to high intensity exercise. Listen to your body.',
            'Moderate Recovery': 'Consider light to moderate activity. Focus on active recovery.',
            'Poor Recovery': 'Rest day recommended. Prioritize sleep, hydration, and stress management.',
            'Recovery Data Unavailable': 'Sync your Garmin data to get personalized recovery insights.'
        }
        
        return advice.get(status, 'Monitor how you feel and train accordingly.')
    
    def get_weekly_summary(self) -> Dict:
        """Get weekly fitness summary"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Get weekly steps data
            conn = sqlite3.connect(self.databases['monitoring'])
            cursor = conn.cursor()
            
            steps_query = """
            SELECT DATE(timestamp) as day, MAX(steps) as daily_steps
            FROM monitoring_info 
            WHERE timestamp BETWEEN ? AND ?
            AND steps IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY day
            """
            
            cursor.execute(steps_query, (start_date.isoformat(), end_date.isoformat()))
            weekly_steps = cursor.fetchall()
            conn.close()
            
            # Get activities summary
            activities_conn = sqlite3.connect(self.databases['activities'])
            activities_cursor = activities_conn.cursor()
            
            activities_query = """
            SELECT COUNT(*) as activity_count, 
                   AVG(distance) as avg_distance,
                   SUM(calories) as total_calories
            FROM activities 
            WHERE start_time BETWEEN ? AND ?
            """
            
            activities_cursor.execute(activities_query, (start_date.isoformat(), end_date.isoformat()))
            activity_summary = activities_cursor.fetchone()
            activities_conn.close()
            
            return {
                'weekly_steps': weekly_steps,
                'activity_count': activity_summary[0] if activity_summary else 0,
                'avg_distance': float(activity_summary[1]) if activity_summary and activity_summary[1] else 0,
                'total_calories': int(activity_summary[2]) if activity_summary and activity_summary[2] else 0,
                'period': f"{start_date.date()} to {end_date.date()}",
                'dataSource': 'garmindb'
            }
            
        except Exception as e:
            log_message(f"Error getting weekly summary: {str(e)}")
            return {
                'error': str(e),
                'dataSource': 'error'
            }

def main():
    """Main function to handle requests from Node.js"""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No request data provided'}))
        return
    
    try:
        # Parse request
        request_data = json.loads(sys.argv[1])
        action = request_data.get('action')
        params = request_data.get('params', {})
        garmindb_path = request_data.get('garmindb_path')
        
        # Initialize bridge
        bridge = GarminDBBridge(garmindb_path)
        
        # Handle different actions
        if action == 'check_status':
            result = bridge.check_garmindb_status()
        elif action == 'get_latest_metrics':
            result = bridge.get_latest_metrics()
        elif action == 'sync_data':
            result = bridge.sync_garmin_data()
        elif action == 'get_weekly_summary':
            result = bridge.get_weekly_summary()
        else:
            result = {'error': f'Unknown action: {action}'}
        
        # Return result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'message': 'GarminDB service error - check logs for details'
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()