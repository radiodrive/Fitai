// mobile-app/screens/Dashboard.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import MetricCard from '../components/MetricCard';
import InsightCard from '../components/InsightCard';
import { api } from '../services/apiClient';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [insights, setInsights] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Loading dashboard data...');
      
      // Fetch latest Garmin metrics
      const metricsResponse = await api.getLatestMetrics();
      console.log('📊 Metrics loaded:', metricsResponse.data);
      setMetrics(metricsResponse.data);

      // Get AI insights from CrewAI agents
      try {
        const insightsResponse = await api.getDailyInsights(metricsResponse.data);
        console.log('🤖 Insights loaded:', insightsResponse.data);
        setInsights(insightsResponse.data.insights || []);
      } catch (insightError) {
        console.log('⚠️ Insights failed, using fallback');
        setInsights([{
          title: '🤖 AI Coach Status',
          content: 'Your AI fitness coaches are getting ready! Sync your data for personalized insights.',
          type: 'info',
          agent: 'system'
        }]);
      }

    } catch (error) {
      console.error('❌ Error loading dashboard:', error);
      setError(error);
      
      // Show user-friendly error
      if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
        Alert.alert(
          'Connection Error', 
          'Unable to connect to the fitness server. Make sure the backend is running on localhost:3000'
        );
      } else {
        Alert.alert('Error', 'Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const formatDate = () => {
    return new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning! 🌅';
    if (hour < 17) return 'Good afternoon! ☀️';
    return 'Good evening! 🌙';
  };

  if (loading && !metrics) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading your fitness data...</Text>
        <Text style={styles.loadingSubtext}>Connecting to backend server</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.welcomeText}>{getGreeting()}</Text>
        <Text style={styles.dateText}>{formatDate()}</Text>
        {metrics?.dataSource === 'fallback' && (
          <Text style={styles.demoText}>
            📱 Demo Mode - Install GarminDB for real data
          </Text>
        )}
      </View>

      {/* Key Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Today's Metrics</Text>
        <View style={styles.metricsGrid}>
          <MetricCard
            title="Steps"
            value={metrics?.steps?.toLocaleString() || '0'}
            target="10,000"
            icon="🚶"
            color="#34C759"
          />
          <MetricCard
            title="Heart Rate"
            value={metrics?.averageHeartRate || '--'}
            subtitle="avg bpm"
            icon="❤️"
            color="#FF3B30"
          />
          <MetricCard
            title="Sleep Score"
            value={metrics?.sleepScore || '--'}
            subtitle="/100"
            icon="😴"
            color="#5856D6"
          />
          <MetricCard
            title="Stress Level"
            value={metrics?.stressLevel || '--'}
            subtitle="/100"
            icon="🧠"
            color="#FF9500"
          />
        </View>
      </View>

      {/* Recovery Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recovery Status</Text>
        <View style={[styles.recoveryCard, getRecoveryCardStyle(metrics?.recoveryStatus)]}>
          <Text style={styles.recoveryTitle}>
            {metrics?.recoveryStatus || 'Calculating...'}
          </Text>
          <Text style={styles.recoverySubtitle}>
            {metrics?.recoveryAdvice || 'Analyzing your recent activity...'}
          </Text>
        </View>
      </View>

      {/* AI Insights */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Coach Insights</Text>
        {insights.length > 0 ? (
          insights.map((insight, index) => (
            <InsightCard
              key={index}
              title={insight.title}
              content={insight.content}
              type={insight.type}
              agent={insight.agent}
              timestamp={insight.timestamp}
            />
          ))
        ) : (
          <View style={styles.noInsights}>
            <Text style={styles.noInsightsIcon}>🤖</Text>
            <Text style={styles.noInsightsText}>
              Your AI coaches are analyzing your data...
            </Text>
            <Text style={styles.noInsightsSubtext}>
              Pull down to refresh or visit the AI Coach tab
            </Text>
          </View>
        )}
      </View>

      {/* Debug Info (only in dev) */}
      {__DEV__ && (
        <View style={styles.debugSection}>
          <Text style={styles.debugTitle}>🔧 Debug Info</Text>
          <Text style={styles.debugText}>
            Backend: {metrics ? '✅ Connected' : '❌ Disconnected'}
          </Text>
          <Text style={styles.debugText}>
            Data Source: {metrics?.dataSource || 'unknown'}
          </Text>
          <Text style={styles.debugText}>
            Last Update: {metrics?.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : 'N/A'}
          </Text>
        </View>
      )}
    </ScrollView>
  );

  function getRecoveryCardStyle(status) {
    switch (status) {
      case 'Excellent Recovery':
        return { borderLeftColor: '#34C759' };
      case 'Good Recovery':
        return { borderLeftColor: '#007AFF' };
      case 'Moderate Recovery':
        return { borderLeftColor: '#FF9500' };
      case 'Poor Recovery':
        return { borderLeftColor: '#FF3B30' };
      default:
        return { borderLeftColor: '#666' };
    }
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginTop: 16,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e1e1',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  dateText: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  demoText: {
    fontSize: 14,
    color: '#FF9500',
    marginTop: 8,
    fontStyle: 'italic',
  },
  section: {
    marginVertical: 10,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    paddingHorizontal: 20,
    marginBottom: 15,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 10,
    justifyContent: 'space-between',
  },
  recoveryCard: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  recoveryTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  recoverySubtitle: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  noInsights: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 30,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  noInsightsIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  noInsightsText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    fontWeight: '500',
  },
  noInsightsSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  debugSection: {
    margin: 20,
    padding: 16,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  debugText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
});