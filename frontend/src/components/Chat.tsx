import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Mic, Image as ImageIcon, User, Bot, MicOff, Camera, MessageSquare } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { useToast } from './ui/Toaster';
import { apiService, ChatRequest } from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  imageUrl?: string;
  category?: 'disease' | 'market' | 'scheme' | 'general';
}

interface ChatProps {
  messages: Message[];
  addMessage: (userMsg: string, botMsg: string, imageUrl?: string, category?: Message['category']) => void;
}

const Chat: React.FC<ChatProps> = ({ messages, addMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [recordingChunks, setRecordingChunks] = useState<Blob[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { addToast } = useToast();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Text Message Handler
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    setIsLoading(true);
    try {
      const request: ChatRequest = { query: inputValue };
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

  // Voice Recording Handlers
  const startRecording = async () => {
    try {
      setIsRecording(true);
      setRecordingChunks([]);
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      
      recorder.ondataavailable = (e) => setRecordingChunks((prev) => [...prev, e.data]);
      recorder.onstop = async () => {
        setIsRecording(false);
        const audioBlob = new Blob(recordingChunks, { type: 'audio/wav' });
        setRecordingChunks([]);
        setIsLoading(true);
        
        try {
          const audioFile = new File([audioBlob], 'audio.wav', { type: 'audio/wav' });
          const response = await apiService.sendVoiceMessage(audioFile);
          
          if (response.success && response.data) {
            addMessage('🎤 Voice message', response.data.response_text);
            addToast({ type: 'success', message: 'Voice message processed!' });
          } else {
            addMessage('🎤 Voice message', response.error || 'Sorry, there was an error processing your voice input.');
            addToast({ type: 'error', message: 'Voice processing failed' });
          }
        } catch (err) {
          addMessage('🎤 Voice message', 'Sorry, there was an error processing your voice input.');
          addToast({ type: 'error', message: 'Voice processing error' });
        }
        
        setIsLoading(false);
      };
      
      recorder.start();
      addToast({ type: 'info', message: 'Recording started - speak now!' });
    } catch (error) {
      addToast({ type: 'error', message: 'Microphone access denied' });
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());
      addToast({ type: 'info', message: 'Processing your voice message...' });
    }
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
      case 'disease': return 'from-green-500 to-emerald-500';
      case 'market': return 'from-blue-500 to-cyan-500';
      case 'scheme': return 'from-purple-500 to-indigo-500';
      default: return 'from-gray-500 to-slate-500';
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-white via-green-50/30 to-blue-50/30 rounded-2xl shadow-inner overflow-hidden">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto chat-messages px-4 py-2 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 chat-message ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.type === 'bot' && (
              <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getCategoryColor(msg.category)} flex items-center justify-center shadow-lg flex-shrink-0`}>
                <Bot className="h-5 w-5 text-white" />
              </div>
            )}
            
            <div className={`max-w-[75%] ${msg.type === 'user' ? 'order-1' : ''}`}>
              <div className={`p-4 rounded-2xl shadow-md ${
                msg.type === 'user' 
                  ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white ml-auto' 
                  : 'bg-white border border-gray-100'
              }`}>
                {msg.type === 'bot' && (
                  <div className="flex items-center gap-2 mb-2 text-xs font-medium text-gray-500">
                    <span>{getCategoryIcon(msg.category)}</span>
                    <span>Kisan.ai Assistant</span>
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
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0">
                <User className="h-5 w-5 text-white" />
              </div>
            )}
          </div>
        ))}
        
        {(isLoading || isUploading) && (
          <div className="flex gap-3 justify-start chat-message">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center shadow-lg">
              <Loader2 className="h-5 w-5 text-white animate-spin" />
            </div>
            <div className="bg-white border border-gray-100 p-4 rounded-2xl shadow-md">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>{isUploading ? 'Analyzing image...' : 'Processing your request...'}</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white/80 backdrop-blur-sm border-t border-gray-200">
        <div className="flex items-center gap-3">
          {/* Voice Button */}
          <Button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading || isUploading}
            variant={isRecording ? 'secondary' : 'outline'}
            className={`p-3 rounded-full transition-all duration-200 ${
              isRecording ? 'recording-indicator animate-pulse' : ''
            }`}
            aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
          >
            {isRecording ? (
              <MicOff className="h-5 w-5" />
            ) : (
              <Mic className="h-5 w-5" />
            )}
          </Button>

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
            className="p-3 rounded-full"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>

          {/* Image Upload Button */}
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading || isRecording}
            variant="outline"
            className="p-3 rounded-full"
            aria-label="Upload image"
          >
            <Camera className="h-5 w-5" />
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2 mt-3 flex-wrap">
          <button
            onClick={() => setInputValue('What diseases are common in tomato plants?')}
            className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
          >
            🌱 Crop Diseases
          </button>
          <button
            onClick={() => setInputValue('What are current tomato prices?')}
            className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
          >
            📊 Market Prices
          </button>
          <button
            onClick={() => setInputValue('Tell me about PM-KISAN scheme')}
            className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
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