// mobile-app/components/MetricCard.js
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const MetricCard = ({ title, value, subtitle, target, icon, color = '#007AFF' }) => {
  // Calculate progress if target is provided
  const progressPercentage = target ? 
    (parseInt(String(value).replace(/[,\s]/g, '')) / parseInt(String(target).replace(/[,\s]/g, ''))) * 100 : 0;
  
  // Format large numbers
  const formatValue = (val) => {
    if (typeof val === 'number' && val > 999) {
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.icon}>{icon || '📊'}</Text>
        <Text style={styles.title}>{title}</Text>
      </View>
      
      <View style={styles.valueContainer}>
        <Text style={[styles.value, { color }]}>
          {formatValue(value)}
        </Text>
        {subtitle && (
          <Text style={styles.subtitle}>{subtitle}</Text>
        )}
      </View>
      
      {target && (
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill, 
                { 
                  width: `${Math.min(Math.max(progressPercentage, 0), 100)}%`, 
                  backgroundColor: color 
                }
              ]} 
            />
          </View>
          <Text style={styles.target}>Goal: {formatValue(target)}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    margin: 8,
    width: '45%',
    minHeight: 120,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  icon: {
    fontSize: 20,
    marginRight: 8,
  },
  title: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  valueContainer: {
    marginBottom: 8,
  },
  value: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 12,
    fontWeight: 'normal',
    color: '#666',
  },
  progressContainer: {
    marginTop: 8,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#f0f0f0',
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: 4,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  target: {
    fontSize: 11,
    color: '#666',
  },
});

export default MetricCard;