// server.js - Main Node.js Backend
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { spawn } = require('child_process');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage for demo (use Redis/MongoDB in production)
let userSessions = {};
let garminCache = {};

// Garmin Connect API Service
class GarminService {
  constructor() {
    this.baseURL = 'https://connectapi.garmin.com';
    this.tokens = {};
  }

  async authenticate(username, password) {
    // Implement Garmin OAuth2 flow
    // This is a simplified version - real implementation needs OAuth2
    try {
      const response = await axios.post(`${this.baseURL}/oauth/request_token`, {
        username,
        password
      });
      return response.data;
    } catch (error) {
      throw new Error('Garmin authentication failed');
    }
  }

  async getLatestMetrics(userId) {
    // Check cache first
    const cacheKey = `metrics_${userId}_${new Date().toDateString()}`;
    if (garminCache[cacheKey]) {
      return garminCache[cacheKey];
    }

    try {
      // Fetch from Garmin API
      const [activities, dailyMetrics, sleepData, wellness] = await Promise.all([
        this.getRecentActivities(userId),
        this.getDailyMetrics(userId),
        this.getSleepData(userId),
        this.getWellnessData(userId)
      ]);

      const metrics = {
        steps: dailyMetrics.steps || 0,
        averageHeartRate: wellness.averageHeartRate || null,
        sleepScore: sleepData.sleepScore || null,
        stressLevel: wellness.stressLevel || null,
        recoveryStatus: this.calculateRecoveryStatus(wellness, sleepData),
        recoveryAdvice: this.getRecoveryAdvice(wellness, sleepData),
        lastActivity: activities[0] || null,
        timestamp: new Date().toISOString()
      };

      // Cache for 1 hour
      garminCache[cacheKey] = metrics;
      setTimeout(() => delete garminCache[cacheKey], 3600000);

      return metrics;
    } catch (error) {
      console.error('Error fetching Garmin metrics:', error);
      // Return mock data for development
      return this.getMockMetrics();
    }
  }

  async getRecentActivities(userId) {
    // Mock implementation
    return [
      {
        activityId: '12345',
        activityName: 'Morning Run',
        startTimeLocal: new Date().toISOString(),
        activityType: 'running',
        distance: 5000, // meters
        duration: 1800, // seconds
        averageHeartRate: 145,
        maxHeartRate: 165,
        calories: 350
      }
    ];
  }

  async getDailyMetrics(userId) {
    // Mock implementation
    return {
      steps: Math.floor(Math.random() * 5000) + 5000,
      floorsClimbed: Math.floor(Math.random() * 20) + 10,
      caloriesActive: Math.floor(Math.random() * 500) + 300,
      caloriesTotal: Math.floor(Math.random() * 800) + 1800
    };
  }

  async getSleepData(userId) {
    // Mock implementation
    return {
      sleepScore: Math.floor(Math.random() * 30) + 70,
      totalSleepTime: Math.floor(Math.random() * 120) + 420, // minutes
      deepSleep: Math.floor(Math.random() * 60) + 60,
      lightSleep: Math.floor(Math.random() * 180) + 240,
      remSleep: Math.floor(Math.random() * 60) + 90,
      awakeTime: Math.floor(Math.random() * 30) + 15
    };
  }

  async getWellnessData(userId) {
    // Mock implementation
    return {
      averageHeartRate: Math.floor(Math.random() * 20) + 65,
      restingHeartRate: Math.floor(Math.random() * 15) + 55,
      stressLevel: Math.floor(Math.random() * 40) + 20,
      bodyBattery: Math.floor(Math.random() * 40) + 60
    };
  }

  calculateRecoveryStatus(wellness, sleep) {
    const bodyBattery = wellness.bodyBattery || 70;
    const sleepScore = sleep.sleepScore || 70;
    const stressLevel = wellness.stressLevel || 30;

    if (bodyBattery > 80 && sleepScore > 80 && stressLevel < 30) {
      return 'Excellent Recovery';
    } else if (bodyBattery > 60 && sleepScore > 65 && stressLevel < 50) {
      return 'Good Recovery';
    } else if (bodyBattery > 40 && sleepScore > 50) {
      return 'Moderate Recovery';
    } else {
      return 'Poor Recovery';
    }
  }

  getRecoveryAdvice(wellness, sleep) {
    const bodyBattery = wellness.bodyBattery || 70;
    const sleepScore = sleep.sleepScore || 70;

    if (bodyBattery < 50) {
      return 'Consider light activity or rest today. Your body battery is low.';
    } else if (sleepScore < 60) {
      return 'Focus on better sleep tonight. Consider a rest day or light workout.';
    } else if (bodyBattery > 80 && sleepScore > 80) {
      return 'Great recovery! Perfect day for an intense workout.';
    } else {
      return 'Moderate activity recommended. Listen to your body.';
    }
  }

  getMockMetrics() {
    return {
      steps: 8547,
      averageHeartRate: 72,
      sleepScore: 78,
      stressLevel: 35,
      recoveryStatus: 'Good Recovery',
      recoveryAdvice: 'You\'re well-recovered from yesterday. Good day for a moderate workout.',
      lastActivity: {
        activityName: 'Morning Run',
        duration: 1800,
        distance: 5000
      },
      timestamp: new Date().toISOString()
    };
  }
}

// CrewAI Agent Service
class AgentService {
  constructor() {
    this.pythonProcess = null;
  }

  async callAgent(requestType, data, message = null) {
    return new Promise((resolve, reject) => {
      const payload = {
        request_type: requestType,
        data: data,
        message: message
      };

      // Spawn Python process to run CrewAI agents
      const pythonProcess = spawn('python', [
        './agents/main.py',
        JSON.stringify(payload)
      ]);

      let result = '';
      let error = '';

      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const response = JSON.parse(result);
            resolve(response);
          } catch (parseError) {
            reject(new Error('Failed to parse agent response'));
          }
        } else {
          reject(new Error(`Agent process failed: ${error}`));
        }
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        pythonProcess.kill();
        reject(new Error('Agent request timeout'));
      }, 30000);
    });
  }
}

const garminService = new GarminService();
const agentService = new AgentService();

// Routes

// Garmin API endpoints
app.get('/garmin/latest-metrics', async (req, res) => {
  try {
    const userId = req.headers['user-id'] || 'demo-user';
    const metrics = await garminService.getLatestMetrics(userId);
    res.json(metrics);
  } catch (error) {
    console.error('Error fetching metrics:', error);
    res.status(500).json({ error: 'Failed to fetch metrics' });
  }
});

app.post('/garmin/auth', async (req, res) => {
  try {
    const { username, password } = req.body;
    const tokens = await garminService.authenticate(username, password);
    res.json({ success: true, tokens });
  } catch (error) {
    res.status(401).json({ error: 'Authentication failed' });
  }
});

// Agent API endpoints
app.post('/agent/analyze', async (req, res) => {
  try {
    const { request_type, data } = req.body;
    const response = await agentService.callAgent(request_type, data);
    res.json(response);
  } catch (error) {
    console.error('Agent analysis error:', error);
    res.status(500).json({ 
      error: 'Analysis failed',
      insights: [
        {
          title: 'Welcome!',
          content: 'Connect your Garmin device to get personalized insights.',
          type: 'info',
          agent: 'system'
        }
      ]
    });
  }
});

app.post('/agent/chat', async (req, res) => {
  try {
    const { message, conversation_history } = req.body;
    const userId = req.headers['user-id'] || 'demo-user';
    
    // Get latest metrics for context
    const metrics = await garminService.getLatestMetrics(userId);
    
    const response = await agentService.callAgent('chat', metrics, message);
    res.json(response);
  } catch (error) {
    console.error('Chat agent error:', error);
    res.status(500).json({ 
      response: "I'm having trouble accessing your data right now. Please make sure your Garmin device is synced and try again.",
      agent_type: 'system'
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🚀 Fitness AI Agent Server running on port ${PORT}`);
  console.log(`📊 Garmin API endpoints ready`);
  console.log(`🤖 CrewAI agents initialized`);
});