import React, { useState, useRef, useEffect } from 'react';
import { chatWithCosmicGuide, type ChatMessage, fetchQuickInsight } from '../api/client';

interface Props {
  sunSign?: string;
  moonSign?: string;
  risingSign?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const QUICK_TOPICS = [
  { label: '💕 Love & Relationships', topic: 'love and relationships today' },
  { label: '💼 Career & Work', topic: 'career and work energy' },
  { label: '🌙 Rest & Sleep', topic: 'better sleep and rest' },
  { label: '🎯 Goals & Intentions', topic: 'setting goals and intentions' },
  { label: '⚡ Current Challenges', topic: 'what to watch out for right now' },
];

export function CosmicGuideChat({ sunSign, moonSign, risingSign }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hi${sunSign ? `, I can see you're a ${sunSign}` : ''}. Ask me anything about your reading — love, career, timing, or what to expect next.`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Convert messages to API format
      const history: ChatMessage[] = messages
        .filter((m) => m.id !== 'welcome')
        .map((m) => ({ role: m.role, content: m.content }));

      const response = await chatWithCosmicGuide(input, sunSign, moonSign, risingSign, history);

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat failed:', err);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickTopic = async (topic: string) => {
    if (loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: `Tell me about ${topic}`,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetchQuickInsight(topic, sunSign);

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.insight,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Quick insight failed:', err);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cosmic-guide-chat">
      <div className="chat-header">
        <span className="guide-avatar">🔮</span>
        <div className="guide-info">
          <h3 className="guide-name">Your Guide</h3>
          <span className="guide-status">
            {loading ? 'Thinking...' : 'Online • Ready to help'}
          </span>
        </div>
      </div>

      <div className="quick-topics">
        {QUICK_TOPICS.map((item) => (
          <button
            key={item.topic}
            className="quick-topic-btn"
            onClick={() => handleQuickTopic(item.topic)}
            disabled={loading}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {msg.role === 'assistant' && <span className="message-avatar">🔮</span>}
            <div className="message-content">
              <p>{msg.content}</p>
              <span className="message-time">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant loading">
            <span className="message-avatar">🔮</span>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="chat-input-form">
        <input
          type="text"
          className="chat-input"
          placeholder="What would you like to understand?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="send-button" disabled={loading || !input.trim()}>
          <span>✨</span>
        </button>
      </form>
    </div>
  );
}
