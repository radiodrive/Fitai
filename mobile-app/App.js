// mobile-app/App.js
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';

// Import screens
import Dashboard from './screens/Dashboard';
import ChatAgent from './screens/ChatAgent';
import DataSync from './screens/DataSync';

// Simple icon component (since vector icons might need setup)
const TabIcon = ({ name, focused }) => (
  <View style={[styles.iconContainer, focused && styles.iconFocused]}>
    <Text style={[styles.iconText, focused && styles.iconTextFocused]}>
      {name === 'Dashboard' ? '📊' : name === 'AI Coach' ? '🤖' : '🔄'}
    </Text>
  </View>
);

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <>
      <StatusBar style="auto" />
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused }) => (
              <TabIcon name={route.name} focused={focused} />
            ),
            tabBarActiveTintColor: '#007AFF',
            tabBarInactiveTintColor: 'gray',
            headerStyle: {
              backgroundColor: '#007AFF',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
            tabBarStyle: {
              backgroundColor: '#fff',
              borderTopWidth: 1,
              borderTopColor: '#e1e1e1',
              paddingBottom: 5,
              paddingTop: 5,
              height: 60,
            },
            tabBarLabelStyle: {
              fontSize: 12,
              fontWeight: '600',
            },
          })}
        >
          <Tab.Screen 
            name="Dashboard" 
            component={Dashboard}
            options={{
              title: 'Fitness Dashboard',
            }}
          />
          <Tab.Screen 
            name="AI Coach" 
            component={ChatAgent}
            options={{
              title: 'AI Fitness Coach',
            }}
          />
          <Tab.Screen 
            name="Sync" 
            component={DataSync}
            options={{
              title: 'Data Sync',
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </>
  );
}

const styles = StyleSheet.create({
  iconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 30,
    height: 30,
  },
  iconFocused: {
    backgroundColor: '#007AFF20',
    borderRadius: 15,
  },
  iconText: {
    fontSize: 20,
  },
  iconTextFocused: {
    fontSize: 22,
  },
});