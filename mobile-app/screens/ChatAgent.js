// mobile-app/screens/ChatAgent.js
import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { api } from '../services/apiClient';

export default function ChatAgent() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your AI fitness coach team. I've got access to your fitness data and I'm here to help you achieve your goals! Ask me anything about your training, recovery, or health metrics.",
      isUser: false,
      agent: 'fitness_coach',
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef();

  const quickQuestions = [
    "How's my recovery today?",
    "Should I workout today?",
    "How did I sleep last night?",
    "Am I overtraining?",
    "What's my fitness trend?",
    "How many steps today?"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const sendMessage = async (messageText = inputText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: messageText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      console.log('💬 Sending message to AI:', messageText);
      
      const response = await api.chatWithAgent(messageText, messages.slice(-10));
      console.log('🤖 AI Response:', response.data);

      const agentMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        isUser: false,
        agent: response.data.agent_type || 'ai_coach',
        agentName: response.data.agent_name,
        timestamp: new Date(),
        insights: response.data.insights || []
      };

      setMessages(prev => [...prev, agentMessage]);

    } catch (error) {
      console.error('❌ Error sending message:', error);
      
      let errorMessage = "I'm having trouble connecting right now. ";
      
      if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
        errorMessage += "Make sure the backend server is running on localhost:3000.";
      } else {
        errorMessage += "Please try again in a moment.";
      }

      const errorResponse = {
        id: Date.now() + 1,
        text: errorMessage,
        isUser: false,
        agent: 'system',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuestion = (question) => {
    sendMessage(question);
  };

  const getAgentIcon = (agent) => {
    switch (agent) {
      case 'data_analyst': return '📊';
      case 'fitness_coach': return '🏃‍♂️';
      case 'health_monitor': return '🏥';
      case 'system': return '⚙️';
      default: return '🤖';
    }
  };

  const getAgentColor = (agent) => {
    switch (agent) {
      case 'data_analyst': return '#007AFF';
      case 'fitness_coach': return '#34C759';
      case 'health_monitor': return '#FF3B30';
      case 'system': return '#666';
      default: return '#5856D6';
    }
  };

  const formatAgentName = (agent, agentName) => {
    if (agentName) return agentName;
    if (!agent) return 'AI COACH';
    return agent.replace('_', ' ').toUpperCase();
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Quick Questions */}
      <View style={styles.quickQuestionsContainer}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.quickQuestionsScroll}
          contentContainerStyle={styles.quickQuestionsContent}
        >
          {quickQuestions.map((question, index) => (
            <TouchableOpacity
              key={index}
              style={styles.quickQuestionButton}
              onPress={() => handleQuickQuestion(question)}
              disabled={isLoading}
            >
              <Text style={styles.quickQuestionText}>{question}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
        keyboardShouldPersistTaps="handled"
      >
        {messages.map((message) => (
          <View
            key={message.id}
            style={[
              styles.messageContainer,
              message.isUser ? styles.userMessage : styles.agentMessage
            ]}
          >
            {!message.isUser && (
              <View style={styles.agentHeader}>
                <Text style={styles.agentIcon}>
                  {getAgentIcon(message.agent)}
                </Text>
                <Text style={[styles.agentName, { color: getAgentColor(message.agent) }]}>
                  {formatAgentName(message.agent, message.agentName)}
                </Text>
              </View>
            )}
            
            <Text style={[
              styles.messageText,
              message.isUser ? styles.userMessageText : styles.agentMessageText
            ]}>
              {message.text}
            </Text>
            
            {message.insights && message.insights.length > 0 && (
              <View style={styles.insightsContainer}>
                {message.insights.map((insight, index) => (
                  <View key={index} style={styles.insightItem}>
                    <Text style={styles.insightText}>💡 {insight}</Text>
                  </View>
                ))}
              </View>
            )}
            
            <Text style={styles.timestamp}>
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </Text>
          </View>
        ))}
        
        {isLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#007AFF" />
            <Text style={styles.loadingText}>AI Coach is thinking...</Text>
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Ask about your fitness data..."
          placeholderTextColor="#999"
          multiline
          maxLength={500}
          onSubmitEditing={() => sendMessage()}
          blurOnSubmit={false}
        />
        <TouchableOpacity
          style={[styles.sendButton, { opacity: inputText.trim() && !isLoading ? 1 : 0.5 }]}
          onPress={() => sendMessage()}
          disabled={!inputText.trim() || isLoading}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  quickQuestionsContainer: {
    backgroundColor: '#fff',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e1e1',
  },
  quickQuestionsScroll: {
    flexGrow: 0,
  },
  quickQuestionsContent: {
    paddingHorizontal: 16,
  },
  quickQuestionButton: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  quickQuestionText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 20,
  },
  messageContainer: {
    marginVertical: 4,
    maxWidth: '85%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
    borderRadius: 18,
    borderBottomRightRadius: 4,
    padding: 12,
  },
  agentMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    padding: 12,
    borderWidth: 1,
    borderColor: '#e1e1e1',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  agentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  agentIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  agentName: {
    fontSize: 12,
    fontWeight: '600',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: '#fff',
  },
  agentMessageText: {
    color: '#333',
  },
  insightsContainer: {
    marginTop: 8,
  },
  insightItem: {
    backgroundColor: '#f0f8ff',
    padding: 8,
    borderRadius: 8,
    marginBottom: 4,
  },
  insightText: {
    fontSize: 14,
    color: '#007AFF',
  },
  timestamp: {
    fontSize: 11,
    color: '#999',
    marginTop: 6,
    alignSelf: 'flex-end',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e1e1e1',
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  sendButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 60,
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});