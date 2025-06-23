// server.js - Updated Node.js Backend with GarminDB Integration
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage for demo (use Redis/MongoDB in production)
let userSessions = {};
let garminCache = {};

// GarminDB Service Integration
class GarminDBService {
  constructor() {
    this.garmindbPath = process.env.GARMINDB_PATH || path.join(process.env.HOME, 'GarminDB');
    this.pythonService = path.join(__dirname, 'garmindb_service.py');
  }

  async callGarminDBService(action, params = {}) {
    return new Promise((resolve, reject) => {
      const payload = {
        action: action,
        params: params,
        garmindb_path: this.garmindbPath
      };

      // Spawn Python process to interact with GarminDB
      const pythonProcess = spawn('python3', [
        this.pythonService,
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
            console.error('Parse error:', parseError);
            resolve(this.getFallbackData(action));
          }
        } else {
          console.error(`GarminDB service failed: ${error}`);
          resolve(this.getFallbackData(action));
        }
      });

      // Timeout after 15 seconds
      setTimeout(() => {
        pythonProcess.kill();
        resolve(this.getFallbackData(action));
      }, 15000);
    });
  }

  getFallbackData(action) {
    const fallbackData = {
      get_latest_metrics: {
        steps: Math.floor(Math.random() * 5000) + 5000,
        averageHeartRate: Math.floor(Math.random() * 20) + 70,
        sleepScore: Math.floor(Math.random() * 30) + 70,
        stressLevel: Math.floor(Math.random() * 40) + 20,
        bodyBattery: Math.floor(Math.random() * 40) + 60,
        restingHeartRate: Math.floor(Math.random() * 15) + 55,
        lastActivity: {
          activityName: 'Morning Walk',
          sport: 'walking',
          distance: 3200,
          calories: 180
        },
        recoveryStatus: 'Demo Mode - Good Recovery',
        recoveryAdvice: 'This is demo data. Connect your Garmin device for real insights.',
        timestamp: new Date().toISOString(),
        dataSource: 'fallback'
      },
      sync_data: {
        success: false,
        message: 'GarminDB not available - using demo data',
        lastSync: new Date().toISOString()
      },
      get_weekly_summary: {
        weekly_steps: [
          ['2024-01-15', 8500],
          ['2024-01-16', 12000],
          ['2024-01-17', 6200],
          ['2024-01-18', 9800],
          ['2024-01-19', 11500],
          ['2024-01-20', 7300],
          ['2024-01-21', 10200]
        ],
        activity_count: 4,
        avg_distance: 5000,
        total_calories: 1200,
        period: 'Last 7 days (Demo)'
      }
    };

    return fallbackData[action] || { error: 'Unknown action' };
  }

  async getLatestMetrics(userId) {
    // Check cache first
    const cacheKey = `metrics_${userId}_${new Date().toDateString()}`;
    if (garminCache[cacheKey]) {
      return garminCache[cacheKey];
    }

    try {
      const metrics = await this.callGarminDBService('get_latest_metrics', { user_id: userId });
      
      // Cache for 30 minutes
      garminCache[cacheKey] = metrics;
      setTimeout(() => delete garminCache[cacheKey], 1800000);
      
      return metrics;
    } catch (error) {
      console.error('Error fetching GarminDB metrics:', error);
      return this.getFallbackData('get_latest_metrics');
    }
  }

  async syncGarminData(userId) {
    try {
      console.log('🔄 Triggering GarminDB sync...');
      const result = await this.callGarminDBService('sync_data', { user_id: userId });
      
      // Clear cache after sync
      Object.keys(garminCache).forEach(key => {
        if (key.includes(userId)) {
          delete garminCache[key];
        }
      });
      
      return result;
    } catch (error) {
      console.error('Error syncing GarminDB:', error);
      return this.getFallbackData('sync_data');
    }
  }

  async getWeeklySummary(userId) {
    try {
      return await this.callGarminDBService('get_weekly_summary', { user_id: userId });
    } catch (error) {
      console.error('Error getting weekly summary:', error);
      return this.getFallbackData('get_weekly_summary');
    }
  }

  async checkGarminDBStatus() {
    try {
      const result = await this.callGarminDBService('check_status');
      return result;
    } catch (error) {
      return {
        connected: false,
        status: 'GarminDB not available',
        setup_required: true,
        message: 'Please install and configure GarminDB'
      };
    }
  }
}

// CrewAI Agent Service (unchanged)
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

      // Use the single file version
      const pythonProcess = spawn('python3', [
        './agents/fitness_ai_single.py',  // ← Make sure this path is correct
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

const garminService = new GarminDBService();
const agentService = new AgentService();

// Routes

// Garmin/GarminDB API endpoints
app.get('/garmin/latest-metrics', async (req, res) => {
  try {
    const userId = req.headers['user-id'] || 'demo-user';
    console.log(`📊 Fetching latest metrics for user: ${userId}`);
    
    const metrics = await garminService.getLatestMetrics(userId);
    
    // Add helpful status for demo
    if (metrics.dataSource === 'fallback') {
      metrics.demoNotice = 'This is demo data. To get real data: 1) Install GarminDB, 2) Sync your Garmin device, 3) Restart the server';
    }
    
    res.json(metrics);
  } catch (error) {
    console.error('Error fetching metrics:', error);
    res.status(500).json({ 
      error: 'Failed to fetch metrics',
      suggestion: 'Check if GarminDB is installed and configured'
    });
  }
});

app.post('/garmin/sync', async (req, res) => {
  try {
    const userId = req.headers['user-id'] || 'demo-user';
    console.log(`🔄 Syncing Garmin data for user: ${userId}`);
    
    const result = await garminService.syncGarminData(userId);
    res.json(result);
  } catch (error) {
    console.error('Error syncing data:', error);
    res.status(500).json({ 
      error: 'Sync failed',
      suggestion: 'Ensure GarminDB is properly installed and your Garmin device is connected'
    });
  }
});

app.get('/garmin/status', async (req, res) => {
  try {
    const status = await garminService.checkGarminDBStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({
      connected: false,
      status: 'Error checking GarminDB status',
      error: error.message
    });
  }
});

app.get('/garmin/weekly-summary', async (req, res) => {
  try {
    const userId = req.headers['user-id'] || 'demo-user';
    const summary = await garminService.getWeeklySummary(userId);
    res.json(summary);
  } catch (error) {
    console.error('Error getting weekly summary:', error);
    res.status(500).json({ error: 'Failed to get weekly summary' });
  }
});

// Agent API endpoints (unchanged)
app.post('/agent/analyze', async (req, res) => {
  try {
    const { request_type, data } = req.body;
    console.log(`🤖 Running agent analysis: ${request_type}`);
    
    const response = await agentService.callAgent(request_type, data);
    res.json(response);
  } catch (error) {
    console.error('Agent analysis error:', error);
    res.status(500).json({ 
      error: 'Analysis failed',
      insights: [
        {
          title: '🤖 AI Coach Status',
          content: 'Your AI agents are getting ready! In the meantime, sync your Garmin data for personalized insights.',
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
    
    console.log(`💬 Chat request: "${message}"`);
    
    // Get latest metrics for context
    const metrics = await garminService.getLatestMetrics(userId);
    
    const response = await agentService.callAgent('chat', metrics, message);
    res.json(response);
  } catch (error) {
    console.error('Chat agent error:', error);
    res.status(500).json({ 
      response: "I'm getting ready to help you! Please make sure your Garmin data is synced and try again.",
      agent_type: 'system'
    });
  }
});

// Setup and installation helper endpoints
app.get('/setup/garmindb-status', async (req, res) => {
  try {
    const status = await garminService.checkGarminDBStatus();
    
    if (!status.connected) {
      status.setup_instructions = [
        "1. Install GarminDB: pip install garmindb",
        "2. Create data directory: mkdir ~/GarminDB",
        "3. Copy your Garmin data or set up auto-import",
        "4. Run initial import: garmindb_cli.py --all",
        "5. Restart this server"
      ];
    }
    
    res.json(status);
  } catch (error) {
    res.json({
      connected: false,
      error: error.message,
      setup_instructions: [
        "Install GarminDB first: pip install garmindb",
        "Follow GarminDB documentation for setup"
      ]
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    services: {
      garmindb: 'Available',
      agents: 'Available'
    }
  });
});

// Development helper - trigger manual sync
app.post('/dev/trigger-sync', async (req, res) => {
  if (process.env.NODE_ENV === 'production') {
    return res.status(403).json({ error: 'Not available in production' });
  }
  
  try {
    const userId = req.headers['user-id'] || 'demo-user';
    const result = await garminService.syncGarminData(userId);
    res.json({ 
      message: 'Sync triggered',
      result: result 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Fitness AI Agent Server running on port ${PORT}`);
  console.log(`📊 GarminDB integration ready`);
  console.log(`🤖 CrewAI agents initialized`);
  console.log(`💡 Setup help available at: http://localhost:${PORT}/setup/garmindb-status`);
  
  // Check GarminDB status on startup
  garminService.checkGarminDBStatus().then(status => {
    if (status.connected) {
      console.log(`✅ GarminDB connected successfully`);
    } else {
      console.log(`⚠️  GarminDB setup required - visit /setup/garmindb-status for instructions`);
    }
  });
});