import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Mic, Image as ImageIcon, User, Bot, Play } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // --- Text Message ---
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    setIsLoading(true);
    try {
      const request: ChatRequest = { query: inputValue };
      const response = await apiService.sendTextMessage(request);
      if (response.success && response.data) {
        addMessage(inputValue, response.data.response);
      } else {
        addMessage(inputValue, response.error || 'Sorry, there was an error processing your request.');
      }
    } catch (err) {
      addMessage(inputValue, 'Sorry, there was an error connecting to the backend.');
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

  // --- Voice Recording ---
  const startRecording = async () => {
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
          addMessage('[Voice message]', response.data.response_text);
        } else {
          addMessage('[Voice message]', response.error || 'Sorry, there was an error processing your voice input.');
        }
      } catch (err) {
        addMessage('[Voice message]', 'Sorry, there was an error processing your voice input.');
      }
      setIsLoading(false);
    };
    recorder.start();
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    }
  };

  // --- Image Upload ---
  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    try {
      const response = await apiService.analyzeImage(file);
      if (response.success && response.data) {
        addMessage('[Photo uploaded]', `${response.data.image_analysis}\n\n${response.data.response}`, URL.createObjectURL(file));
      } else {
        addMessage('[Photo uploaded]', response.error || 'Sorry, there was an error analyzing the image.', URL.createObjectURL(file));
      }
    } catch (err) {
      addMessage('[Photo uploaded]', 'Sorry, there was an error analyzing the image.');
    }
    setIsUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-purple-100 via-purple-50 to-white rounded-2xl p-4 shadow-inner overflow-hidden">
      <div className="flex-1 overflow-y-auto pr-2 mb-2" style={{ maxHeight: '60vh' }}>
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 mb-2 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.type === 'user' ? (
              <>
                <div className="flex flex-col items-end">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center shadow">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <div className="max-w-[80vw] md:max-w-[60vw] p-3 rounded-2xl shadow-md bg-purple-200 text-purple-900 self-end">
                      {msg.imageUrl && <img src={msg.imageUrl} alt="uploaded" className="mt-2 max-w-xs rounded-lg border" />}
                      <p className="text-base whitespace-pre-line break-words">{msg.content}</p>
                      <span className="text-xs opacity-70 mt-1 block text-right">{msg.timestamp.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="flex flex-col items-start">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center shadow">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div className="max-w-[80vw] md:max-w-[60vw] p-3 rounded-2xl shadow-md bg-white text-purple-900 self-start border border-purple-100">
                      {msg.imageUrl && <img src={msg.imageUrl} alt="uploaded" className="mt-2 max-w-xs rounded-lg border" />}
                      <div className="flex items-center gap-2 mb-1">
                        <Play className="h-4 w-4 text-purple-400 cursor-pointer hover:text-purple-600 transition" />
                        <span className="text-xs text-purple-400">Bot</span>
                      </div>
                      <p className="text-base whitespace-pre-line break-words">{msg.content}</p>
                      <span className="text-xs opacity-70 mt-1 block text-left">{msg.timestamp.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        ))}
        {(isLoading || isUploading) && (
          <div className="flex gap-3 justify-start mb-2">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-200 flex items-center justify-center">
              <Loader2 className="h-4 w-4 text-purple-600 animate-spin" />
            </div>
            <div className="bg-white text-purple-700 p-3 rounded-lg border border-purple-100">
              <p className="text-sm">Processing...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="sticky bottom-0 left-0 w-full flex gap-2 items-center mt-2 bg-white/90 rounded-xl p-2 shadow-md border border-purple-100">
        <Button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isLoading || isUploading}
          className={`rounded-full p-2 ${isRecording ? 'bg-purple-200 animate-pulse' : ''}`}
          aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
        >
          <Mic className={`h-5 w-5 ${isRecording ? 'animate-pulse text-purple-600' : 'text-purple-500'}`} />
        </Button>
        <Input
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder={isRecording ? 'Recording... Speak now!' : 'Type your question...'}
          disabled={isLoading || isUploading || isRecording}
          className="flex-1 bg-transparent border-none focus:ring-0 text-lg"
        />
        <Button
          onClick={handleSendMessage}
          disabled={isLoading || isUploading || !inputValue.trim() || isRecording}
          className="rounded-full p-2 bg-purple-500 hover:bg-purple-600 text-white"
          aria-label="Send message"
        >
          <Send className="h-5 w-5" />
        </Button>
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading || isUploading || isRecording}
          className="rounded-full p-2 bg-purple-100 hover:bg-purple-200 text-purple-700"
          aria-label="Upload image"
        >
          <ImageIcon className="h-5 w-5" />
        </Button>
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