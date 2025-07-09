import React, { useState } from 'react';
import Chat from './components/Chat';
import ConnectionTest from './components/ConnectionTest';
import { ToasterProvider } from './components/ui/Toaster';
import { Leaf, Sparkles } from 'lucide-react';
import './App.css';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  imageUrl?: string;
  category?: 'disease' | 'market' | 'scheme' | 'general';
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([{
    id: '1',
    type: 'bot',
    content: `🙏 **Namaste! Welcome to Kisan.ai** 

I'm your personal agricultural assistant, here to help you with:

🌱 **Crop Disease Diagnosis** - Upload photos for instant analysis
📊 **Real-time Market Prices** - Get current rates for your crops  
🏛️ **Government Schemes** - Find subsidies and benefits
🎤 **Voice Support** - Speak in your local language

How can I help you today?`,
    timestamp: new Date(),
    category: 'general'
  }]);

  const addMessage = (userMsg: string, botMsg: string, imageUrl?: string, category?: Message['category']) => {
    setMessages(prev => [
      ...prev,
      { id: Date.now().toString(), type: 'user', content: userMsg, timestamp: new Date(), imageUrl },
      { id: (Date.now() + 1).toString(), type: 'bot', content: botMsg, timestamp: new Date(), category }
    ]);
  };

  return (
    <ToasterProvider>
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-green-50 via-blue-50 to-emerald-100 font-sans">
        <div className="w-full max-w-4xl h-[95vh] bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-green-100/50">
          {/* Header */}
          <header className="relative bg-gradient-to-r from-green-600 via-emerald-600 to-blue-600 px-6 py-5 shadow-lg">
            <div className="absolute inset-0 bg-black/10"></div>
            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Leaf className="h-10 w-10 text-white drop-shadow-lg" />
                  <Sparkles className="absolute -top-1 -right-1 h-4 w-4 text-yellow-300 animate-pulse" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white tracking-tight">
                    Kisan.ai
                  </h1>
                  <p className="text-sm text-white/90 font-medium">
                    🇮🇳 Empowering Indian Farmers with AI
                  </p>
                </div>
              </div>
              <ConnectionTest />
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6 overflow-hidden">
            <Chat messages={messages} addMessage={addMessage} />
          </main>

          {/* Footer */}
          <footer className="px-6 py-3 bg-gradient-to-r from-gray-50 to-gray-100 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <div className="flex items-center gap-4">
                <span>🌾 Powered by Google AI</span>
                <span>•</span>
                <span>🔒 Secure & Private</span>
              </div>
              <div className="flex items-center gap-2">
                <span>Made with ❤️ for Indian Farmers</span>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </ToasterProvider>
  );
};

export default App;