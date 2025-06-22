# backend/garmindb_service.py - GarminDB Integration Service
import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import schedule
import time
from pathlib import Path

class GarminDBService:
    def __init__(self, garmindb_path: str = None):
        """
        Initialize GarminDB service
        
        Args:
            garmindb_path: Path to GarminDB installation (optional)
        """
        self.garmindb_path = garmindb_path or os.path.expanduser("~/GarminDB")
        self.db_path = os.path.join(self.garmindb_path, "garmin.db")
        self.activities_db_path = os.path.join(self.garmindb_path, "garmin_activities.db")
        self.monitoring_db_path = os.path.join(self.garmindb_path, "garmin_monitoring.db")
        
        # Ensure database exists
        self._check_database_setup()
    
    def _check_database_setup(self):
        """Check if GarminDB is properly set up"""
        if not os.path.exists(self.db_path):
            print(f"⚠️  GarminDB not found at {self.garmindb_path}")
            print("📋 Setup instructions:")
            print("1. Install GarminDB: pip install garmindb")
            print("2. Run: garmindb_cli.py --all")
            print("3. Copy your Garmin data or set up auto-sync")
            return False
        return True
    
    def sync_garmin_data(self):
        """Trigger GarminDB sync to get latest data"""
        try:
            print("🔄 Syncing Garmin data...")
            # Run GarminDB import command
            cmd = ["garmindb_cli.py", "--import", "--analyze"]
            result = subprocess.run(cmd, cwd=self.garmindb_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Garmin data sync completed")
                return True
            else:
                print(f"❌ Sync failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Sync error: {e}")
            return False
    
    def get_latest_metrics(self, days_back: int = 1) -> Dict:
        """Get latest fitness metrics from GarminDB"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            metrics = {
                'steps': self._get_daily_steps(start_date, end_date),
                'averageHeartRate': self._get_average_heart_rate(start_date, end_date),
                'sleepScore': self._get_sleep_score(start_date, end_date),
                'stressLevel': self._get_stress_level(start_date, end_date),
                'bodyBattery': self._get_body_battery(start_date, end_date),
                'restingHeartRate': self._get_resting_heart_rate(start_date, end_date),
                'lastActivity': self._get_latest_activity(),
                'recoveryStatus': None,  # Will calculate this
                'recoveryAdvice': None,  # Will calculate this
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate recovery status
            metrics['recoveryStatus'] = self._calculate_recovery_status(metrics)
            metrics['recoveryAdvice'] = self._get_recovery_advice(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error getting metrics: {e}")
            return self._get_fallback_metrics()
    
    def _get_daily_steps(self, start_date: datetime, end_date: datetime) -> int:
        """Get daily steps from monitoring database"""
        try:
            conn = sqlite3.connect(self.monitoring_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT SUM(steps)
            FROM monitoring_info 
            WHERE timestamp BETWEEN ? AND ?
            AND steps IS NOT NULL
            """
            
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else 0
            
        except Exception as e:
            print(f"❌ Error getting steps: {e}")
            return 0
    
    def _get_average_heart_rate(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get average heart rate from monitoring data"""
        try:
            conn = sqlite3.connect(self.monitoring_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT AVG(heart_rate)
            FROM monitoring_hr 
            WHERE timestamp BETWEEN ? AND ?
            AND heart_rate IS NOT NULL AND heart_rate > 0
            """
            
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            result = cursor.fetchone()
            conn.close()
            
            return int(result[0]) if result and result[0] else None
            
        except Exception as e:
            print(f"❌ Error getting heart rate: {e}")
            return None
    
    def _get_sleep_score(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get sleep score from sleep data"""
        try:
            conn = sqlite3.connect(self.garmindb_path + "/garmin_summary.db")
            cursor = conn.cursor()
            
            query = """
            SELECT sleep_score
            FROM sleep_events 
            WHERE day BETWEEN ? AND ?
            AND sleep_score IS NOT NULL
            ORDER BY day DESC
            LIMIT 1
            """
            
            cursor.execute(query, (start_date.date().isoformat(), end_date.date().isoformat()))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else None
            
        except Exception as e:
            print(f"❌ Error getting sleep score: {e}")
            return None
    
    def _get_stress_level(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get average stress level"""
        try:
            conn = sqlite3.connect(self.monitoring_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT AVG(stress_level)
            FROM monitoring_info 
            WHERE timestamp BETWEEN ? AND ?
            AND stress_level IS NOT NULL AND stress_level >= 0
            """
            
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            result = cursor.fetchone()
            conn.close()
            
            return int(result[0]) if result and result[0] else None
            
        except Exception as e:
            print(f"❌ Error getting stress level: {e}")
            return None
    
    def _get_body_battery(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get latest body battery level"""
        try:
            conn = sqlite3.connect(self.monitoring_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT body_battery
            FROM monitoring_info 
            WHERE timestamp BETWEEN ? AND ?
            AND body_battery IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 1
            """
            
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else None
            
        except Exception as e:
            print(f"❌ Error getting body battery: {e}")
            return None
    
    def _get_resting_heart_rate(self, start_date: datetime, end_date: datetime) -> Optional[int]:
        """Get resting heart rate"""
        try:
            conn = sqlite3.connect(self.garmindb_path + "/garmin_summary.db")
            cursor = conn.cursor()
            
            query = """
            SELECT rhr
            FROM resting_hr 
            WHERE day BETWEEN ? AND ?
            AND rhr IS NOT NULL
            ORDER BY day DESC
            LIMIT 1
            """
            
            cursor.execute(query, (start_date.date().isoformat(), end_date.date().isoformat()))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else None
            
        except Exception as e:
            print(f"❌ Error getting resting heart rate: {e}")
            return None
    
    def _get_latest_activity(self) -> Optional[Dict]:
        """Get the most recent activity"""
        try:
            conn = sqlite3.connect(self.activities_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT name, start_time, sport, distance, avg_hr, calories
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
                    'distance': result[3] or 0,
                    'averageHeartRate': result[4] or 0,
                    'calories': result[5] or 0
                }
            return None
            
        except Exception as e:
            print(f"❌ Error getting latest activity: {e}")
            return None
    
    def _calculate_recovery_status(self, metrics: Dict) -> str:
        """Calculate recovery status based on available metrics"""
        sleep_score = metrics.get('sleepScore', 70)
        stress_level = metrics.get('stressLevel', 50)
        body_battery = metrics.get('bodyBattery', 70)
        rhr = metrics.get('restingHeartRate', 60)
        
        # Simple recovery calculation
        recovery_factors = []
        
        if sleep_score:
            if sleep_score >= 80: recovery_factors.append(2)
            elif sleep_score >= 65: recovery_factors.append(1)
            else: recovery_factors.append(-1)
        
        if stress_level:
            if stress_level <= 25: recovery_factors.append(2)
            elif stress_level <= 50: recovery_factors.append(1)
            else: recovery_factors.append(-1)
        
        if body_battery:
            if body_battery >= 80: recovery_factors.append(2)
            elif body_battery >= 60: recovery_factors.append(1)
            else: recovery_factors.append(-1)
        
        # Calculate overall recovery
        if not recovery_factors:
            return "Unknown Recovery"
        
        avg_recovery = sum(recovery_factors) / len(recovery_factors)
        
        if avg_recovery >= 1.5:
            return "Excellent Recovery"
        elif avg_recovery >= 0.5:
            return "Good Recovery"
        elif avg_recovery >= -0.5:
            return "Moderate Recovery"
        else:
            return "Poor Recovery"
    
    def _get_recovery_advice(self, metrics: Dict) -> str:
        """Get recovery advice based on metrics"""
        recovery_status = metrics.get('recoveryStatus', 'Unknown')
        
        advice_map = {
            'Excellent Recovery': 'Perfect day for high-intensity training! Your body is fully recovered.',
            'Good Recovery': 'Good day for moderate to high intensity exercise. Listen to your body.',
            'Moderate Recovery': 'Consider light to moderate activity today. Focus on active recovery.',
            'Poor Recovery': 'Rest day recommended. Prioritize sleep, hydration, and stress management.',
            'Unknown Recovery': 'Monitor how you feel and start with light activity.'
        }
        
        return advice_map.get(recovery_status, 'Listen to your body and train accordingly.')
    
    def _get_fallback_metrics(self) -> Dict:
        """Return fallback metrics when database is unavailable"""
        return {
            'steps': 0,
            'averageHeartRate': None,
            'sleepScore': None,
            'stressLevel': None,
            'bodyBattery': None,
            'restingHeartRate': None,
            'lastActivity': None,
            'recoveryStatus': 'Data Unavailable',
            'recoveryAdvice': 'Please sync your Garmin data to get personalized insights.',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_weekly_summary(self) -> Dict:
        """Get weekly fitness summary"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            conn = sqlite3.connect(self.monitoring_db_path)
            cursor = conn.cursor()
            
            # Get weekly steps
            steps_query = """
            SELECT DATE(timestamp) as day, SUM(steps) as daily_steps
            FROM monitoring_info 
            WHERE timestamp BETWEEN ? AND ?
            AND steps IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY day
            """
            
            cursor.execute(steps_query, (start_date.isoformat(), end_date.isoformat()))
            weekly_steps = cursor.fetchall()
            
            # Get activities
            activities_conn = sqlite3.connect(self.activities_db_path)
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
            
            conn.close()
            activities_conn.close()
            
            return {
                'weekly_steps': weekly_steps,
                'activity_count': activity_summary[0] if activity_summary else 0,
                'avg_distance': activity_summary[1] if activity_summary else 0,
                'total_calories': activity_summary[2] if activity_summary else 0,
                'period': f"{start_date.date()} to {end_date.date()}"
            }
            
        except Exception as e:
            print(f"❌ Error getting weekly summary: {e}")
            return {'error': str(e)}
    
    def setup_auto_sync(self, interval_hours: int = 2):
        """Setup automatic GarminDB sync"""
        def sync_job():
            print(f"🔄 Auto-sync triggered at {datetime.now()}")
            self.sync_garmin_data()
        
        # Schedule sync every X hours
        schedule.every(interval_hours).hours.do(sync_job)
        
        print(f"⏰ Auto-sync scheduled every {interval_hours} hours")
        return True

# Auto-sync runner (optional background service)
def run_auto_sync():
    """Run the auto-sync scheduler"""
    garmin_service = GarminDBService()
    garmin_service.setup_auto_sync(interval_hours=2)
    
    print("🚀 GarminDB auto-sync service started")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Test the service
    service = GarminDBService()
    metrics = service.get_latest_metrics()
    print("📊 Latest Metrics:")
    print(json.dumps(metrics, indent=2))
    
    weekly = service.get_weekly_summary()
    print("\n📈 Weekly Summary:")
    print(json.dumps(weekly, indent=2))