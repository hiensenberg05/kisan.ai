import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Mic, User, Bot, MicOff, Camera, Volume2, VolumeX, AlertCircle } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { useToast } from './ui/Toaster';
import { apiService, ChatRequest } from '../services/api';
import { speechToText } from '../utils/speechRecognition';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  imageUrl?: string;
  category?: 'disease' | 'market' | 'scheme' | 'general';
  isPlaying?: boolean;
}

interface ChatProps {
  messages: Message[];
  addMessage: (userMsg: string, botMsg: string, imageUrl?: string, category?: Message['category']) => void;
}

const Chat: React.FC<ChatProps> = ({ messages, addMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isSpeechSupported, setIsSpeechSupported] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { addToast } = useToast();
  
  // Simple session id per tab
  const [sessionId] = useState<string>(() => {
    return (crypto?.randomUUID && crypto.randomUUID()) || `${Date.now()}-${Math.random().toString(36).slice(2,8)}`;
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Text Message Handler
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    setIsLoading(true);
    try {
      const request: ChatRequest = { query: inputValue, session_id: sessionId };
      const response = await apiService.sendTextMessage(request);
      
      if (response.success && response.data) {
        addMessage(inputValue, response.data.response, undefined, response.data.category);
        addToast({ type: 'success', message: 'Message sent successfully!' });
      } else {
        addMessage(inputValue, response.error || 'Sorry, there was an error processing your request.');
        addToast({ type: 'error', message: 'Failed to send message' });
      }
    } catch (err) {
      addMessage(inputValue, 'Sorry, there was an error connecting to the backend.');
      addToast({ type: 'error', message: 'Connection error' });
    }
    
    setInputValue('');
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  useEffect(() => {
    // Check if speech recognition is supported
    setIsSpeechSupported(speechToText.isSupported());
    
    // Cleanup on unmount
    return () => {
      if (isRecording) {
        speechToText.stopListening();
      }
    };
  }, [isRecording]);

  // Voice Recording Handlers with improved speech recognition
  const startRecording = async () => {
    if (!isSpeechSupported) {
      addToast({
        type: 'error',
        message: 'Speech recognition is not supported in your browser. Please use Chrome, Edge, or another modern browser.',
        duration: 5000
      });
      return;
    }
    
    try {
      setIsRecording(true);
      setInterimTranscript('');
      
      speechToText.startListening(
        (text, isFinal) => {
          if (isFinal) {
            // Send the final transcript to the server
            handleSendVoiceText(text);
          } else {
            // Show interim results
            setInterimTranscript(text);
          }
        },
        (error) => {
          console.error('Speech recognition error:', error);
          addToast({
            type: 'error',
            message: `Speech recognition error: ${error}`,
            duration: 3000
          });
          setIsRecording(false);
        },
        () => {
          // onEnd callback
          setIsRecording(false);
        }
      );
      
      addToast({
        type: 'info',
        message: 'Speak now...',
        duration: 2000
      });
      
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      addToast({
        type: 'error',
        message: 'Failed to access microphone. Please check permissions.',
        duration: 4000
      });
      setIsRecording(false);
    }
  };
  
  const stopRecording = () => {
    speechToText.stopListening();
    setIsRecording(false);
    setInterimTranscript('');
  };
  
  const handleSendVoiceText = async (text: string) => {
    if (!text.trim()) {
      addToast({ type: 'error', message: 'No speech detected. Please try again.' });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const request: ChatRequest = { 
        query: text, 
        session_id: sessionId,
        is_voice: true
      };
      
      const response = await apiService.sendTextMessage(request);
      
      if (response.success && response.data) {
        addMessage(text, response.data.response, undefined, response.data.category);
        addToast({ type: 'success', message: 'Voice message processed!' });
      } else {
        addMessage(text, response.error || 'Sorry, there was an error processing your voice input.');
        addToast({ type: 'error', message: 'Voice processing failed' });
      }
    } catch (err) {
      console.error('Error processing voice message:', err);
      addMessage('🎤 Voice message', 'Sorry, there was an error processing your voice input.');
      addToast({ type: 'error', message: 'Voice processing error' });
    }
    
    setIsLoading(false);
  };

  // Image Upload Handler
  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setIsUploading(true);
    addToast({ type: 'info', message: 'Analyzing your image...' });
    
    try {
      const response = await apiService.analyzeImage(file);
      
      if (response.success && response.data) {
        const imageUrl = URL.createObjectURL(file);
        addMessage('📸 Photo uploaded for analysis', `${response.data.image_analysis}\n\n${response.data.response}`, imageUrl);
        addToast({ type: 'success', message: 'Image analyzed successfully!' });
      } else {
        addMessage('📸 Photo uploaded', response.error || 'Sorry, there was an error analyzing the image.', URL.createObjectURL(file));
        addToast({ type: 'error', message: 'Image analysis failed' });
      }
    } catch (err) {
      addMessage('📸 Photo uploaded', 'Sorry, there was an error analyzing the image.');
      addToast({ type: 'error', message: 'Image upload error' });
    }
    
    setIsUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Get the best available voice for Indian English
  const getBestIndianVoice = (): SpeechSynthesisVoice | null => {
    const voices = window.speechSynthesis.getVoices();
    
    // Priority: en-IN > en-GB > en-US > any other English voice
    const voicePriorities = [
      { lang: 'en-IN', name: 'Google हिंदी' },  // Google Hindi (often works for English with Indian accent)
      { lang: 'en-IN', name: 'Microsoft Ravi' },
      { lang: 'en-IN', name: 'Microsoft Heera' },
      { lang: 'en-GB', name: 'Google UK English Female' },
      { lang: 'en-US', name: 'Google US English' },
      { lang: 'en', name: 'Google UK English Female' },
      { lang: 'en', name: 'Google US English' },
      { lang: 'en', name: 'Microsoft David' },
      { lang: 'en', name: 'Microsoft Zira' },
    ];

    for (const priority of voicePriorities) {
      const voice = voices.find(v => 
        (v.lang.includes(priority.lang) || v.lang.startsWith(priority.lang)) && 
        v.name.includes(priority.name)
      );
      if (voice) return voice;
    }

    // Fallback to any Indian English voice
    const indianVoice = voices.find(v => v.lang.includes('en-IN'));
    if (indianVoice) return indianVoice;

    // Fallback to any English voice
    const englishVoice = voices.find(v => v.lang.startsWith('en'));
    if (englishVoice) return englishVoice;

    // Fallback to any available voice
    return voices[0] || null;
  };

  // TTS (Text-to-Speech) Handler with enhanced voice selection
  const handlePlayTTS = async (messageId: string, text: string) => {
    try {
      // If clicking the same message that's currently playing, stop it
      if (playingMessageId === messageId) {
        window.speechSynthesis.cancel();
        setPlayingMessageId(null);
        return;
      }

      // Stop any currently playing speech
      window.speechSynthesis.cancel();
      
      // Set the new playing message
      setPlayingMessageId(messageId);
      
      // Create new utterance with better settings for Indian English
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Configure speech parameters for better Indian English
      utterance.rate = 0.95;          // Slightly slower for better clarity
      utterance.pitch = 1.05;         // Slightly higher pitch for better intelligibility
      utterance.volume = 1.0;         // Maximum volume
      
      // Get and set the best available voice
      const voice = getBestIndianVoice();
      if (voice) {
        utterance.voice = voice;
        utterance.lang = voice.lang;  // Ensure correct language is set
      }
      
      // Handle when speech ends
      utterance.onend = () => {
        // Only reset if this is still the current playing message
        if (playingMessageId === messageId) {
          setPlayingMessageId(null);
        }
      };
      
      // Handle any errors
      utterance.onerror = (event) => {
        console.error('SpeechSynthesis error:', event);
        if (playingMessageId === messageId) {
          setPlayingMessageId(null);
        }
        addToast({ type: 'error', message: 'Speech playback failed' });
      };
      
      // Add a small delay to ensure voice is ready
      setTimeout(() => {
        try {
          window.speechSynthesis.speak(utterance);
          addToast({ 
            type: 'info', 
            message: `Playing response with ${voice?.name || 'default voice'}` 
          });
        } catch (err) {
          console.error('Error starting speech synthesis:', err);
          addToast({ type: 'error', message: 'Failed to start speech' });
          setPlayingMessageId(null);
        }
      }, 100);
    } catch (error) {
      addToast({ type: 'error', message: 'Failed to play audio' });
      setPlayingMessageId(null);
    }
  };

  const getCategoryIcon = (category?: string) => {
    switch (category) {
      case 'disease': return '🌱';
      case 'market': return '📊';
      case 'scheme': return '🏛️';
      default: return '🤖';
    }
  };

  const getCategoryColor = (category?: string) => {
    switch (category) {
      case 'disease': return 'from-emerald-400 via-green-500 to-teal-600';
      case 'market': return 'from-blue-400 via-cyan-500 to-indigo-600';
      case 'scheme': return 'from-purple-400 via-violet-500 to-fuchsia-600';
      default: return 'from-orange-400 via-pink-500 to-rose-600';
    }
  };

  const getCategoryBubbleColor = (category?: string) => {
    switch (category) {
      case 'disease': return 'from-emerald-50 via-green-50 to-teal-50 border-emerald-200';
      case 'market': return 'from-blue-50 via-cyan-50 to-indigo-50 border-blue-200';
      case 'scheme': return 'from-purple-50 via-violet-50 to-fuchsia-50 border-purple-200';
      default: return 'from-orange-50 via-pink-50 to-rose-50 border-orange-200';
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-white via-green-50/30 to-blue-50/30 rounded-2xl shadow-inner overflow-hidden">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto chat-messages px-4 py-2 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 chat-message ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.type === 'bot' && (
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getCategoryColor(msg.category)} flex items-center justify-center shadow-xl flex-shrink-0 ring-2 ring-white ring-opacity-30`}>
                <Bot className="h-6 w-6 text-white drop-shadow-sm" />
              </div>
            )}
            
            <div className={`max-w-[75%] ${msg.type === 'user' ? 'order-1' : ''}`}>
              <div className={`p-4 rounded-2xl shadow-lg ${
                msg.type === 'user' 
                  ? 'bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 text-white ml-auto' 
                  : `bg-gradient-to-br ${getCategoryBubbleColor(msg.category)} border-2`
              }`}>
                {msg.type === 'bot' && (
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-xs font-medium text-gray-600">
                      <span>{getCategoryIcon(msg.category)}</span>
                      <span>Kisan.ai Assistant</span>
                    </div>
                    <button
                      onClick={() => handlePlayTTS(msg.id, msg.content)}
                      className={`p-1.5 rounded-full transition-all duration-200 hover:bg-gray-100 ${
                        playingMessageId === msg.id ? 'bg-blue-100 text-blue-600 animate-pulse' : 'text-gray-400 hover:text-gray-600'
                      }`}
                      aria-label={playingMessageId === msg.id ? 'Stop audio' : 'Listen to response'}
                    >
                      {playingMessageId === msg.id ? (
                        <VolumeX className="h-4 w-4" />
                      ) : (
                        <Volume2 className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                )}
                
                {msg.imageUrl && (
                  <div className="mb-3">
                    <img 
                      src={msg.imageUrl} 
                      alt="uploaded" 
                      className="max-w-full h-auto rounded-lg border-2 border-white/20 shadow-sm" 
                    />
                  </div>
                )}
                
                <div className={`text-sm leading-relaxed whitespace-pre-line ${
                  msg.type === 'user' ? 'text-white' : 'text-gray-800'
                }`}>
                  {msg.content}
                </div>
                
                <div className={`text-xs mt-2 ${
                  msg.type === 'user' ? 'text-white/70 text-right' : 'text-gray-400'
                }`}>
                  {msg.timestamp.toLocaleTimeString('en-IN', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            </div>
            
            {msg.type === 'user' && (
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 via-purple-500 to-indigo-600 flex items-center justify-center shadow-xl flex-shrink-0 ring-2 ring-white ring-opacity-30">
                <User className="h-6 w-6 text-white drop-shadow-sm" />
              </div>
            )}
          </div>
        ))}
        
        {(isLoading || isUploading) && (
          <div className="flex gap-3 justify-start chat-message">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-400 via-orange-500 to-red-500 flex items-center justify-center shadow-xl animate-pulse ring-2 ring-white ring-opacity-30">
              <Loader2 className="h-6 w-6 text-white animate-spin drop-shadow-sm" />
            </div>
            <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 border-2 border-amber-200 p-4 rounded-2xl shadow-lg">
              <div className="flex items-center gap-2 text-sm text-amber-700 font-medium">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>{isUploading ? '🖼️ Analyzing your image...' : '🧠 Thinking about your question...'}</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gradient-to-r from-white/90 via-blue-50/80 to-purple-50/80 backdrop-blur-sm border-t border-gradient-to-r from-blue-200 to-purple-200">
        <div className="flex items-center gap-3">
          {/* Voice Button with improved feedback */}
          <div className="relative">
            <Button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading || isUploading || !isSpeechSupported}
              className={`p-3 rounded-full transition-all duration-200 shadow-lg ${
                isRecording 
                  ? 'bg-gradient-to-br from-red-400 via-pink-500 to-red-600 text-white animate-pulse shadow-red-200' 
                  : 'bg-gradient-to-br from-green-400 via-emerald-500 to-teal-600 text-white hover:from-green-500 hover:via-emerald-600 hover:to-teal-700 shadow-green-200'
              } ${!isSpeechSupported ? 'opacity-50 cursor-not-allowed' : ''}`}
              aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
              title={!isSpeechSupported ? 'Speech recognition not supported in this browser' : undefined}
            >
              {isRecording ? (
                <div className="flex items-center">
                  <span className="relative flex h-3 w-3 mr-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                  </span>
                  <MicOff className="h-5 w-5" />
                </div>
              ) : (
                <Mic className="h-5 w-5" />
              )}
            </Button>
            
            {!isSpeechSupported && (
              <div className="absolute -top-2 -right-2">
                <div className="relative group">
                  <AlertCircle className="h-5 w-5 text-yellow-500" />
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 px-3 py-2 bg-yellow-50 text-yellow-800 text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                    Voice input is not supported in this browser. Please use Chrome, Edge, or another modern browser.
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Show interim transcription */}
          {isRecording && interimTranscript && (
            <div className="absolute bottom-full left-0 right-0 mb-2 px-4 py-2 bg-blue-50 text-blue-800 text-sm rounded-lg shadow-md">
              <div className="font-medium mb-1">Listening...</div>
              <div className="italic">{interimTranscript}</div>
            </div>
          )}

          {/* Text Input */}
          <div className="flex-1">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={isRecording ? '🎤 Recording... Speak now!' : '💬 Ask about crops, prices, or schemes...'}
              disabled={isLoading || isUploading || isRecording}
              className="border-2 border-gray-200 focus:border-green-500 rounded-full px-6 py-3 text-base"
            />
          </div>

          {/* Send Button */}
          <Button
            onClick={handleSendMessage}
            disabled={isLoading || isUploading || !inputValue.trim() || isRecording}
            className="p-3 rounded-full bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-600 text-white hover:from-blue-500 hover:via-indigo-600 hover:to-purple-700 shadow-lg shadow-blue-200 transition-all duration-200"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>

          {/* Image Upload Button */}
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading || isRecording}
            className="p-3 rounded-full bg-gradient-to-br from-orange-400 via-pink-500 to-red-500 text-white hover:from-orange-500 hover:via-pink-600 hover:to-red-600 shadow-lg shadow-orange-200 transition-all duration-200"
            aria-label="Upload image"
          >
            <Camera className="h-5 w-5" />
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2 mt-3 flex-wrap">
          <button
            onClick={() => setInputValue('What diseases are common in tomato plants?')}
            className="px-4 py-2 text-xs bg-gradient-to-r from-emerald-100 via-green-100 to-teal-100 text-emerald-700 font-medium rounded-full hover:from-emerald-200 hover:via-green-200 hover:to-teal-200 transition-all duration-200 shadow-sm border border-emerald-200"
          >
            🌱 Crop Diseases
          </button>
          <button
            onClick={() => setInputValue('What are current tomato prices?')}
            className="px-4 py-2 text-xs bg-gradient-to-r from-blue-100 via-cyan-100 to-indigo-100 text-blue-700 font-medium rounded-full hover:from-blue-200 hover:via-cyan-200 hover:to-indigo-200 transition-all duration-200 shadow-sm border border-blue-200"
          >
            📊 Market Prices
          </button>
          <button
            onClick={() => setInputValue('Tell me about PM-KISAN scheme')}
            className="px-4 py-2 text-xs bg-gradient-to-r from-purple-100 via-violet-100 to-fuchsia-100 text-purple-700 font-medium rounded-full hover:from-purple-200 hover:via-violet-200 hover:to-fuchsia-200 transition-all duration-200 shadow-sm border border-purple-200"
          >
            🏛️ Government Schemes
          </button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
      </div>
    </div>
  );
};

export default Chat;