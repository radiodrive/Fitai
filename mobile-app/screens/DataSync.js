// mobile-app/screens/DataSync.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { api } from '../services/apiClient';

export default function DataSync() {
  const [isConnected, setIsConnected] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSync, setLastSync] = useState(null);
  const [syncStatus, setSyncStatus] = useState('Checking connection...');
  const [setupInfo, setSetupInfo] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      console.log('🔍 Checking GarminDB status...');
      
      // Check backend health first
      const healthResponse = await api.checkHealth();
      console.log('💗 Backend health:', healthResponse.data);
      
      // Check GarminDB setup status
      const statusResponse = await api.getSetupStatus();
      console.log('📊 GarminDB status:', statusResponse.data);
      
      setSetupInfo(statusResponse.data);
      setIsConnected(statusResponse.data.connected || false);
      setSyncStatus(statusResponse.data.status || 'Unknown status');
      
      if (statusResponse.data.lastSync) {
        setLastSync(statusResponse.data.lastSync);
      }
      
    } catch (error) {
      console.error('❌ Error checking connection status:', error);
      setIsConnected(false);
      
      if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
        setSyncStatus('Backend server not running');
      } else {
        setSyncStatus('Connection error');
      }
    } finally {
      setRefreshing(false);
    }
  };

  const syncData = async () => {
    try {
      setIsSyncing(true);
      setSyncStatus('Syncing data...');
      
      console.log('🔄 Starting data sync...');
      const response = await api.syncGarminData();
      console.log('✅ Sync result:', response.data);
      
      if (response.data.success) {
        setLastSync(response.data.lastSync || new Date().toISOString());
        setSyncStatus('Sync completed successfully');
        
        Alert.alert(
          'Sync Complete', 
          'Your fitness data has been updated successfully!',
          [{ text: 'OK', onPress: checkConnectionStatus }]
        );
      } else {
        setSyncStatus('Sync failed - ' + (response.data.message || 'Unknown error'));
        Alert.alert(
          'Sync Failed', 
          response.data.message || 'Unable to sync data. Check your GarminDB setup.'
        );
      }
      
    } catch (error) {
      console.error('❌ Sync error:', error);
      setSyncStatus('Sync failed - connection error');
      
      let errorMessage = 'Failed to sync data. ';
      if (error.code === 'NETWORK_ERROR') {
        errorMessage += 'Check that the backend server is running.';
      } else {
        errorMessage += 'Please try again.';
      }
      
      Alert.alert('Sync Error', errorMessage);
    } finally {
      setIsSyncing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    checkConnectionStatus();
  };

  const getStatusIcon = () => {
    if (isSyncing) return '🔄';
    if (isConnected && setupInfo?.has_data) return '✅';
    if (isConnected && !setupInfo?.has_data) return '⚠️';
    return '❌';
  };

  const getStatusColor = () => {
    if (isSyncing) return '#FF9500';
    if (isConnected && setupInfo?.has_data) return '#34C759';
    if (isConnected && !setupInfo?.has_data) return '#FF9500';
    return '#FF3B30';
  };

  const formatLastSync = (timestamp) => {
    if (!timestamp) return 'Never';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return 'Unknown';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Data Sync</Text>
        <Text style={styles.subtitle}>
          Manage your Garmin data integration
        </Text>
      </View>

      {/* Connection Status */}
      <View style={[styles.statusCard, { borderLeftColor: getStatusColor() }]}>
        <View style={styles.statusHeader}>
          <Text style={styles.statusIcon}>{getStatusIcon()}</Text>
          <View style={styles.statusInfo}>
            <Text style={[styles.statusTitle, { color: getStatusColor() }]}>
              {isConnected ? 'Connected' : 'Not Connected'}
            </Text>
            <Text style={styles.statusText}>{syncStatus}</Text>
          </View>
        </View>
        
        {lastSync && (
          <Text style={styles.lastSyncText}>
            Last sync: {formatLastSync(lastSync)}
          </Text>
        )}
        
        {setupInfo?.data_count && (
          <Text style={styles.dataCountText}>
            📊 {setupInfo.data_count} data points available
          </Text>
        )}
      </View>

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity 
          style={[styles.syncButton, isSyncing && styles.buttonDisabled]} 
          onPress={syncData}
          disabled={isSyncing}
        >
          {isSyncing ? (
            <View style={styles.buttonContent}>
              <ActivityIndicator color="#fff" size="small" />
              <Text style={styles.buttonText}>Syncing...</Text>
            </View>
          ) : (
            <View style={styles.buttonContent}>
              <Text style={styles.buttonIcon}>🔄</Text>
              <Text style={styles.buttonText}>
                {isConnected ? 'Sync Now' : 'Test Connection'}
              </Text>
            </View>
          )}
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.refreshButton} 
          onPress={checkConnectionStatus}
          disabled={isSyncing}
        >
          <View style={styles.buttonContent}>
            <Text style={styles.buttonIcon}>🔍</Text>
            <Text style={styles.buttonText}>Check Status</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* Setup Instructions (if needed) */}
      {setupInfo?.setup_required && (
        <View style={styles.setupSection}>
          <Text style={styles.setupTitle}>🛠️ Setup Required</Text>
          <Text style={styles.setupText}>
            To get real Garmin data, you need to set up GarminDB:
          </Text>
          
          {setupInfo.setup_instructions && (
            <View style={styles.instructionsList}>
              {setupInfo.setup_instructions.map((instruction, index) => (
                <Text key={index} style={styles.instructionItem}>
                  {instruction}
                </Text>
              ))}
            </View>
          )}
          
          <Text style={styles.setupNote}>
            💡 For now, the app works with demo data so you can test all features!
          </Text>
        </View>
      )}

      {/* Data Information */}
      <View style={styles.infoSection}>
        <Text style={styles.sectionTitle}>What data do we sync?</Text>
        
        <View style={styles.dataList}>
          <View style={styles.dataItem}>
            <Text style={styles.dataIcon}>🚶</Text>
            <Text style={styles.dataText}>Daily activity (steps, calories, distance)</Text>
          </View>
          
          <View style={styles.dataItem}>
            <Text style={styles.dataIcon}>❤️</Text>
            <Text style={styles.dataText}>Heart rate and workout data</Text>
          </View>
          
          <View style={styles.dataItem}>
            <Text style={styles.dataIcon}>😴</Text>
            <Text style={styles.dataText}>Sleep tracking and recovery metrics</Text>
          </View>
          
          <View style={styles.dataItem}>
            <Text style={styles.dataIcon}>🧠</Text>
            <Text style={styles.dataText}>Stress levels and wellness data</Text>
          </View>
          
          <View style={styles.dataItem}>
            <Text style={styles.dataIcon}>🔋</Text>
            <Text style={styles.dataText}>Body battery and energy levels</Text>
          </View>
        </View>
      </View>

      {/* Privacy Notice */}
      <View style={styles.privacySection}>
        <Text style={styles.privacyTitle}>🔒 Privacy & Security</Text>
        <Text style={styles.privacyText}>
          Your fitness data is processed locally and securely. We never share your personal 
          information with third parties. All data stays on your device and your personal server.
        </Text>
      </View>

      {/* Debug Info (Development only) */}
      {__DEV__ && setupInfo && (
        <View style={styles.debugSection}>
          <Text style={styles.debugTitle}>🔧 Debug Info</Text>
          <Text style={styles.debugText}>Connected: {setupInfo.connected ? 'Yes' : 'No'}</Text>
          <Text style={styles.debugText}>Has Data: {setupInfo.has_data ? 'Yes' : 'No'}</Text>
          <Text style={styles.debugText}>Setup Required: {setupInfo.setup_required ? 'Yes' : 'No'}</Text>
          {setupInfo.path && (
            <Text style={styles.debugText}>Path: {setupInfo.path}</Text>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e1e1',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  statusCard: {
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
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  statusIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  statusInfo: {
    flex: 1,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  lastSyncText: {
    fontSize: 12,
    color: '#999',
    marginTop: 8,
  },
  dataCountText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  actionsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  syncButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  refreshButton: {
    backgroundColor: '#34C759',
    borderRadius: 12,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  buttonIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  setupSection: {
    margin: 20,
    backgroundColor: '#fff3cd',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#ffeaa7',
  },
  setupTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#856404',
    marginBottom: 12,
  },
  setupText: {
    fontSize: 14,
    color: '#856404',
    marginBottom: 12,
    lineHeight: 20,
  },
  instructionsList: {
    marginBottom: 12,
  },
  instructionItem: {
    fontSize: 13,
    color: '#856404',
    marginBottom: 4,
    paddingLeft: 8,
  },
  setupNote: {
    fontSize: 13,
    color: '#856404',
    fontStyle: 'italic',
  },
  infoSection: {
    margin: 20,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  dataList: {
    gap: 12,
  },
  dataItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dataIcon: {
    fontSize: 20,
    marginRight: 12,
    width: 30,
  },
  dataText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
    lineHeight: 20,
  },
  privacySection: {
    margin: 20,
    backgroundColor: '#e8f4fd',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#bee5eb',
  },
  privacyTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0c5460',
    marginBottom: 12,
  },
  privacyText: {
    fontSize: 14,
    color: '#0c5460',
    lineHeight: 20,
  },
  debugSection: {
    margin: 20,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#495057',
  },
  debugText: {
    fontSize: 12,
    color: '#6c757d',
    marginBottom: 4,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
  },
});