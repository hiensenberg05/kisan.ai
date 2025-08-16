import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Mic,
  Camera,
  Paperclip,
  MoreHorizontal,
  Bot,
  User,
  Volume2,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Image as ImageIcon,
  FileText,
  TrendingUp,
  Lightbulb
} from 'lucide-react';

// Custom Live Interaction Icon (waveform-style)
const LiveIcon = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    className={props.className}
  >
    <rect x="3" y="9" width="2" height="6" rx="1" />
    <rect x="7" y="5" width="2" height="14" rx="1" />
    <rect x="11" y="7" width="2" height="10" rx="1" />
    <rect x="15" y="4" width="2" height="16" rx="1" />
    <rect x="19" y="8" width="2" height="8" rx="1" />
  </svg>
);

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: 'Hello! I am your agricultural advisor. You can ask me about crop diseases, market prices, weather information, and government schemes. How can I help you?',
      timestamp: new Date(Date.now() - 300000),
      confidence: 95
    },
    {
      id: 2,
      type: 'user',
      content: 'My wheat crop has yellow spots. What should I do?',
      timestamp: new Date(Date.now() - 120000)
    },
    {
      id: 3,
      type: 'ai',
      content: 'Yellow spots on wheat are usually caused by Yellow Rust, a fungal disease.',
      timestamp: new Date(Date.now() - 60000),
      confidence: 92,
      suggestions: [
        { text: 'Spray Immediately', icon: <LiveIcon className="w-4 h-4" /> },
        { text: 'Treatment Cost', icon: <TrendingUp className="w-4 h-4" /> },
        { text: 'Prevention Methods', icon: <Lightbulb className="w-4 h-4" /> }
      ],
      attachments: [
        { type: 'image', url: '/wheat-rust-example.jpg', description: 'Yellow rust symptoms' }
      ]
    }
  ]);
  
  const [newMessage, setNewMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isMobileOptionsOpen, setIsMobileOptionsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const quickSuggestions = [
    'Weather Information',
    'Today\'s Prices',
    'Government Schemes',
    'Crop Advice'
  ];

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: newMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);

    setTimeout(() => {
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'I am preparing an answer to your question...',
        timestamp: new Date(),
        confidence: 88
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 2000);
  };

  const handleVoiceRecord = () => {
    setIsRecording(!isRecording);
    setIsMobileOptionsOpen(false);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('File uploaded:', file.name);
    }
    setIsMobileOptionsOpen(false);
  };

  const handleLiveInteraction = () => {
    console.log('Live Interaction initiated');
    setIsMobileOptionsOpen(false);
  };

  const handleSuggestionClick = (suggestion) => {
    setNewMessage(suggestion);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start space-x-3 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' 
                  ? 'bg-gradient-to-br from-green-500 to-emerald-600' 
                  : 'bg-gradient-to-br from-orange-500 to-amber-600'
              }`}>
                {message.type === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>

              {/* Message Content */}
              <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`rounded-2xl px-4 py-3 max-w-lg ${
                  message.type === 'user'
                    ? 'bg-green-500 text-white rounded-br-sm'
                    : 'bg-white border border-gray-200 text-gray-900 rounded-bl-sm shadow-sm'
                }`}>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  
                  {message.attachments && (
                    <div className="mt-3 space-y-2">
                      {message.attachments.map((attachment, index) => (
                        <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
                          <ImageIcon className="w-4 h-4 text-gray-600" />
                          <span className="text-xs text-gray-600">{attachment.description}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className={`flex items-center space-x-2 mt-2 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
                  
                  {message.type === 'ai' && (
                    <>
                      {message.confidence && (
                        <div className="flex items-center space-x-1">
                          <div className="text-xs text-gray-500">Confidence:</div>
                          <div className={`text-xs font-medium ${
                            message.confidence >= 90 ? 'text-green-600' : 
                            message.confidence >= 70 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {message.confidence}%
                          </div>
                        </div>
                      )}

                      <div className="flex items-center space-x-1">
                        <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                          <Volume2 className="w-3 h-3 text-gray-500 cursor-pointer" />
                        </button>
                        <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                          <Copy className="w-3 h-3 text-gray-500 cursor-pointer" />
                        </button>
                        {/* <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                          <ThumbsUp className="w-3 h-3 text-gray-500" />
                        </button>
                        <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                          <ThumbsDown className="w-3 h-3 text-gray-500" />
                        </button> */}
                      </div>
                    </>
                  )}
                </div>

                {message.suggestions && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion.text)}
                        className="flex items-center space-x-1 px-3 py-1 bg-orange-100 hover:bg-orange-200 text-orange-700 text-xs rounded-full transition-colors"
                      >
                        {suggestion.icon}
                        <span>{suggestion.text}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-600 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestions Bar */}
      {/* <div className="px-4 py-2 bg-white border-t border-gray-200">
        <div className="flex space-x-2 overflow-x-auto scrollbar-hide">
          {quickSuggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="flex-shrink-0 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div> */}

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex items-center space-x-3">
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/*,video/*,.pdf,.doc,.docx"
            onChange={handleFileUpload}
          />

          {isMobile && (
            <div className="relative">
              <button
                type="button"
                onClick={() => setIsMobileOptionsOpen(!isMobileOptionsOpen)}
                className="flex-shrink-0 p-2 bg-gradient-to-br from-orange-500 to-amber-600 text-white rounded-lg hover:from-orange-600 hover:to-amber-700 transition-colors cursor-pointer"
              >
                <MoreHorizontal className="w-5 h-5" />
              </button>

              {isMobileOptionsOpen && (
                <div className="absolute bottom-12 left-0 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <Paperclip className="w-4 h-4 mr-2" />
                    Upload File
                  </button>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Capture Image
                  </button>
                  <button
                    type="button"
                    onClick={handleLiveInteraction}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <LiveIcon className="w-4 h-4 mr-2" />
                    Live Interaction
                  </button>
                  <button
                    type="button"
                    onClick={handleVoiceRecord}
                    className={`flex items-center w-full px-4 py-2 text-sm ${
                      isRecording ? 'text-red-500' : 'text-gray-700 hover:bg-gray-100'
                    } transition-colors cursor-pointer`}
                  >
                    <Mic className="w-4 h-4 mr-2 cursor-pointer" />
                    {isRecording ? 'Stop Recording' : 'Voice Record'}
                  </button>
                </div>
              )}
            </div>
          )}

          {!isMobile && (
            <>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
              >
                <Camera className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={handleLiveInteraction}
                className="flex-shrink-0 p-2 bg-gradient-to-br from-orange-500 to-amber-600 text-white rounded-lg hover:from-orange-600 hover:to-amber-700 transition-colors cursor-pointer"
              >
                <LiveIcon className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={handleVoiceRecord}
                className={`flex-shrink-0 p-3 rounded-full transition-all cursor-pointer ${
                  isRecording 
                    ? 'bg-red-500 text-white animate-pulse' 
                    : 'bg-orange-500 hover:bg-orange-600 text-white'
                }`}
              >
                <Mic className="w-5 h-5" />
              </button>
            </>
          )}

          <div className="flex-1 relative">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your question or speak..."
              className="w-full px-4 py-2 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none transition-all text-sm"
              rows="1"
              style={{ lineHeight: '1.5rem' }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(e);
                }
              }}
            />
          </div>

          <button
            type="submit"
            disabled={!newMessage.trim()}
            className={`flex-shrink-0 p-3 rounded-full transition-all ${
              newMessage.trim()
                ? 'bg-green-500 hover:bg-green-600 text-white cursor-pointer'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </form>

        {isRecording && (
          <div className="flex items-center justify-center mt-3 space-x-2 text-red-500">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm">Recording... Tap to stop</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
