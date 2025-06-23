# 🏃‍♂️ Garmin Fitness AI Agent

A complete fitness application that combines your Garmin device data with AI-powered insights and coaching. Get personalized recommendations, track your progress, and chat with specialized AI agents about your health and fitness.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-iOS%20%7C%20Android%20%7C%20Web-lightgrey)
![Backend](https://img.shields.io/badge/backend-Node.js-green)
![AI](https://img.shields.io/badge/AI-CrewAI-purple)

## ✨ Features

### 📊 **Fitness Dashboard**
- Real-time metrics from your Garmin device
- Steps, heart rate, sleep score, stress levels
- Recovery status with personalized advice
- Beautiful metric cards with progress tracking

### 🤖 **AI-Powered Coaching**
- **Data Analyst Agent**: Analyzes patterns and trends in your fitness data
- **Fitness Coach Agent**: Provides personalized training recommendations
- **Health Monitor Agent**: Watches for overtraining and recovery needs
- Natural language chat interface for asking questions

### 🔄 **Data Synchronization**
- Direct integration with Garmin devices via GarminDB
- Automatic data sync and processing
- Privacy-focused local data storage
- Demo mode for testing without real device

### 📱 **Cross-Platform Mobile App**
- React Native app for iOS, Android, and Web
- Real-time dashboard updates
- Intuitive chat interface with AI agents
- Offline-capable with local data caching

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.11+ with pip
- **Expo CLI** for mobile development
- **Garmin device** (optional - works with demo data)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/garmin-fitness-ai.git
cd garmin-fitness-ai

# Install backend dependencies
cd backend
npm install
npm install --save-dev nodemon

# Install AI agent dependencies
cd ../agents
pip install crewai crewai-tools openai python-dotenv requests

# Install mobile app dependencies
cd ../mobile-app
npm install
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/stack
npm install react-native-screens react-native-safe-area-context axios
```

### Configuration

#### Backend Environment
Create `backend/.env`:
```env
NODE_ENV=development
PORT=3000
GARMINDB_PATH=C:\Users\YourUsername\GarminDB
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### Mobile App Configuration
Update `mobile-app/services/apiClient.js`:
```javascript
// Replace with your computer's IP address for mobile testing
const COMPUTER_IP = '192.168.1.XXX';
```

### Running the Application

#### Start Backend Server
```bash
cd backend
npm run dev
# Server runs on http://localhost:3000
```

#### Start AI Agents (Optional - Backend works with demo data)
```bash
cd agents
# Test agents work:
python test_agent.py
```

#### Start Mobile App
```bash
cd mobile-app
npm start
# Choose your platform: Web (w), iOS (i), or Android (a)
```

## 🏗️ Architecture

```
garmin-fitness-ai/
├── backend/                 # Node.js API server
│   ├── server.js           # Main server file
│   ├── garmindb_service.py # Python bridge for GarminDB
│   └── .env               # Environment variables
├── agents/                 # Python AI agents
│   ├── fitness_ai_single.py # Main AI agent file
│   ├── test_agent.py      # Testing utilities
│   └── requirements.txt   # Python dependencies
└── mobile-app/            # React Native application
    ├── App.js            # Main app component
    ├── screens/          # App screens
    ├── components/       # Reusable components
    └── services/         # API clients
```

## 🤖 AI Agents

### Data Analyst Agent
- **Role**: Analyze fitness metrics and identify patterns
- **Capabilities**: Trend analysis, performance insights, data visualization
- **Tools**: Statistical analysis, heart rate zone calculations

### Fitness Coach Agent  
- **Role**: Provide personalized training recommendations
- **Capabilities**: Workout planning, goal setting, motivation
- **Tools**: Training load calculation, exercise prescription

### Health Monitor Agent
- **Role**: Monitor health indicators and flag concerns
- **Capabilities**: Recovery analysis, overtraining detection
- **Tools**: Sleep analysis, stress monitoring, injury prevention

## 📊 Data Sources

### Garmin Integration
- **Primary**: GarminDB for direct device data access
- **Metrics**: Steps, heart rate, sleep, stress, activities
- **Frequency**: Real-time sync with automatic updates

### Supported Garmin Devices
- Forerunner series (235, 245, 255, 945, 955, etc.)
- Vivoactive series (3, 4, 5)
- Fenix series (6, 7, 8)
- Venu series (1, 2, 3)
- Any device compatible with Garmin Connect

## 🔧 Setup Options

### Option 1: Demo Mode (Recommended for Testing)
- Works immediately without Garmin device
- Uses realistic sample fitness data
- Perfect for development and testing
- AI agents provide coaching based on demo metrics

### Option 2: GarminDB Integration (Real Data)
```bash
# Install GarminDB
pip install garmindb

# Create data directory
mkdir ~/GarminDB
cd ~/GarminDB

# Download and import your Garmin data
garmindb_cli.py --all --download --import --analyze
```

### Option 3: Garmin Connect API (Advanced)
- Requires Garmin Developer API access
- More complex setup but official integration
- Rate limits and authentication requirements

## 📱 Mobile App Features

### Dashboard Screen
- **Metrics Display**: Steps, heart rate, sleep score, stress
- **Recovery Status**: AI-calculated recovery recommendations  
- **Progress Tracking**: Goals and achievements
- **Quick Insights**: At-a-glance fitness summary

### AI Coach Screen
- **Natural Chat**: Ask questions in plain language
- **Quick Questions**: Pre-built common queries
- **Multi-Agent**: Different specialists for different topics
- **Contextual**: Responses based on your current data

### Data Sync Screen
- **Connection Status**: Real-time sync monitoring
- **Manual Sync**: Force data refresh
- **Setup Guide**: Instructions for GarminDB
- **Privacy Info**: Data handling transparency

## 🔮 AI Capabilities

### Smart Question Handling
```
User: "How's my recovery today?"
Health Monitor: "Based on your sleep score of 82/100 and low stress levels, 
you're well-recovered. Great day for moderate to high intensity training!"

User: "Should I workout today?"  
Fitness Coach: "With your current training load and excellent recovery, 
I recommend a 30-45 minute moderate intensity session. Focus on what feels good!"

User: "What's my fitness trend?"
Data Analyst: "Your weekly step average increased 12% and heart rate variability 
improved. You're building strong aerobic fitness - keep it up!"
```

### Personalized Insights
- **Training Recommendations**: Based on recovery and load
- **Health Warnings**: Early overtraining detection
- **Goal Optimization**: Adaptive targets based on progress
- **Motivation**: Encouraging and realistic coaching

## 🛠️ Development

### Running in Development
```bash
# Backend with hot reload
cd backend && npm run dev

# Mobile app with Expo
cd mobile-app && npm start

# Test AI agents
cd agents && python test_agent.py
```

### API Endpoints

#### Fitness Data
- `GET /garmin/latest-metrics` - Current fitness metrics
- `POST /garmin/sync` - Trigger data synchronization
- `GET /garmin/weekly-summary` - 7-day fitness summary

#### AI Agents
- `POST /agent/analyze` - Get daily insights
- `POST /agent/chat` - Chat with AI coaches

#### System
- `GET /health` - Backend health check
- `GET /setup/garmindb-status` - Setup status

### Testing

#### Backend API Testing
```bash
# Test metrics endpoint
curl http://localhost:3000/garmin/latest-metrics

# Test AI chat
curl -X POST http://localhost:3000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How am I doing?", "conversation_history": []}'
```

#### Mobile App Testing
```bash
# Web version (easiest)
cd mobile-app && npm start
# Press 'w' for web

# iOS Simulator
expo start --ios

# Android Emulator  
expo start --android
```

## 🔒 Privacy & Security

### Data Handling
- **Local Processing**: All AI analysis happens on your server
- **No Cloud Storage**: Data stays on your devices
- **Encrypted Transit**: HTTPS for all communications
- **Minimal Collection**: Only fitness metrics, no personal info

### Open Source
- **Full Transparency**: All code is open source
- **Self-Hosted**: Run entirely on your own infrastructure  
- **No Tracking**: No analytics or user tracking
- **Data Ownership**: You control all your fitness data

## 🚀 Deployment

### Development (Local)
- Backend: `http://localhost:3000`
- Mobile: Expo Development Server
- AI Agents: Local Python execution

### Production Options

#### Backend Deployment
```bash
# Railway
railway deploy

# Heroku
git push heroku main

# Docker
docker build -t garmin-fitness-ai .
docker run -p 3000:3000 garmin-fitness-ai
```

#### Mobile App Deployment
```bash
# iOS App Store
expo build:ios

# Google Play Store
expo build:android

# Web Hosting
expo build:web
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- **JavaScript**: ESLint + Prettier
- **Python**: Black + isort + flake8
- **React Native**: Standard React patterns
- **Documentation**: Comprehensive inline comments

## 📋 Roadmap

### Version 1.1
- [ ] Nutrition tracking integration
- [ ] Advanced sleep analysis
- [ ] Workout plan generation
- [ ] Social features and challenges

### Version 1.2
- [ ] Multiple device support
- [ ] Advanced ML models
- [ ] Injury prediction
- [ ] Integration with other fitness platforms

### Version 2.0
- [ ] Wearable app companion
- [ ] Real-time coaching during workouts
- [ ] Advanced biometric analysis
- [ ] Personalized training programs

## 🆘 Troubleshooting

### Common Issues

#### "Failed to load dashboard data"
```bash
# Check backend is running
cd backend && npm run dev

# Verify IP address in mobile app
# Update mobile-app/services/apiClient.js with correct IP
```

#### "Python was not found"
```bash
# Install Python 3.11+
# Add Python to PATH during installation
# Test: python --version
```

#### "AI agents not responding"
```bash
# Test agents directly
cd agents && python test_agent.py

# Check Python dependencies
pip install -r requirements.txt
```

#### "GarminDB setup required"
```bash
# For real data, install GarminDB:
pip install garmindb
mkdir ~/GarminDB
garmindb_cli.py --all

# Or continue with demo data (works great!)
```

#### Mobile app won't connect
```bash
# Find your IP address
ipconfig  # Windows
ifconfig  # Mac/Linux

# Update mobile-app/services/apiClient.js
const COMPUTER_IP = 'YOUR_ACTUAL_IP';
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/garmin-fitness-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/garmin-fitness-ai/discussions)
- **Email**: support@yourproject.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI**: For the amazing AI agent framework
- **GarminDB**: For reverse-engineering Garmin data access
- **React Native**: For cross-platform mobile development
- **Expo**: For simplifying mobile app development
- **Garmin**: For creating amazing fitness devices

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/garmin-fitness-ai?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/garmin-fitness-ai?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/garmin-fitness-ai)
![GitHub license](https://img.shields.io/github/license/yourusername/garmin-fitness-ai)

---

**Built with ❤️ for the fitness community. Stay healthy, stay active! 🏃‍♂️💪**

## 🔗 Links

- [Demo Video](https://youtube.com/watch?v=your-demo)
- [Documentation](https://docs.yourproject.com)
- [API Reference](https://api.yourproject.com/docs)
- [Community Discord](https://discord.gg/your-invite)