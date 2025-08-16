import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Mic,
  Camera,
  Brain,
  TrendingUp,
  Shield,
  Globe,
  Leaf,
  Sun,
  CloudRain,
  Smartphone,
  Users,
  Award,
  ArrowRight,
  Play,
  CheckCircle,
  MessageCircle,
  BarChart3,
  Lightbulb,
  Menu,
  X,
  Wheat,
  Sprout,
  TreePine,
  User,
} from "lucide-react";

const LandingPage = () => {
  const [currentGreetingIndex, setCurrentGreetingIndex] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const greetings = [
    { text: "Hello", lang: "English" },
    { text: "नमस्ते", lang: "Hindi" },
    { text: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ", lang: "Punjabi" },
    { text: "வணக்கம்", lang: "Tamil" },
    { text: "నమస్కారం", lang: "Telugu" },
    { text: "নমস্কার", lang: "Bengali" },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentGreetingIndex((prev) => (prev + 1) % greetings.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: <Camera className="w-6 h-6" />,
      title: "Instant Crop Disease Diagnosis",
      titleHi: "तत्काल फसल रोग निदान",
      description:
        "Take a photo of your diseased plant and get instant AI-powered diagnosis with economical treatment suggestions.",
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Real-Time Market Insights",
      titleHi: "वास्तविक समय बाजार जानकारी",
      description:
        "Get up-to-date crop prices, market trends, and optimal selling recommendations for maximum profit.",
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Government Scheme Guidance",
      titleHi: "सरकारी योजना मार्गदर्शन",
      description:
        "Navigate subsidies and government schemes with simple explanations in your local language.",
    },
    {
      icon: <Mic className="w-6 h-6" />,
      title: "Voice-First Regional Language",
      titleHi: "आवाज़ में क्षेत्रीय भाषा",
      description:
        "Speak in your dialect and get natural responses. No literacy barriers, just conversation.",
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Crop Growth Monitoring",
      titleHi: "फसल विकास निगरानी",
      description:
        "Track your crop's health and growth stages with visual progress bars and yield predictions.",
    },
    {
      icon: <CloudRain className="w-6 h-6" />,
      title: "Weather-Linked Smart Alerts",
      titleHi: "मौसम आधारित स्मार्ट अलर्ट",
      description:
        "Receive timely weather warnings and irrigation reminders based on local conditions.",
    },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-2 rounded-lg">
                <Wheat className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">
                KisanMitra AI
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                How It Works
              </a>
              <a
                href="#contact"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Contact
              </a>
              <button 
                onClick={() => navigate("/auth")}
                className="text-orange-600 hover:text-orange-700 font-medium"
              >
                Login
              </button>
              <button 
                onClick={() => navigate("/auth")}
                className="bg-gradient-to-r from-orange-500 to-amber-600 text-white px-4 py-2 rounded-lg hover:from-orange-600 hover:to-amber-700 transition-all"
              >
                Sign Up
              </button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-600 hover:text-gray-900"
              >
                {mobileMenuOpen ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100">
            <div className="px-4 pt-2 pb-4 space-y-2">
              <a href="#features" className="block py-2 text-gray-600">
                Features
              </a>
              <a href="#how-it-works" className="block py-2 text-gray-600">
                How It Works
              </a>
              <a href="#contact" className="block py-2 text-gray-600">
                Contact
              </a>
              <button 
                onClick={() => navigate("/auth")}
                className="block w-full text-left py-2 text-orange-600"
              >
                Login
              </button>
              <button 
                onClick={() => navigate("/auth")}
                className="block w-full mt-2 bg-gradient-to-r from-orange-500 to-amber-600 text-white px-4 py-2 rounded-lg"
              >
                Sign Up
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-orange-50 to-amber-50 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8 items-center">
            {/* Left Content */}
            <div className="lg:col-span-6">
              {/* Greeting Animation */}
              <div className="mb-8 py-4">
                <div className="text-5xl md:text-6xl lg:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-amber-600 animate-pulse leading-tight">
                  {greetings[currentGreetingIndex].text}
                </div>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
                AI-Powered{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-amber-600">
                  Agricultural
                </span>{" "}
                Advisor
              </h1>

              <p className="text-lg text-gray-600 mb-8 leading-relaxed max-w-lg">
                Get expert agricultural advice in your local language. From crop
                disease diagnosis to market insights - everything you need for
                successful farming, powered by AI.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button
                  onClick={() => navigate("/dashboard")}
                  className="bg-gradient-to-r from-orange-500 to-amber-600 text-white text-lg font-semibold px-8 py-4 rounded-xl hover:from-orange-600 hover:to-amber-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2 shadow-lg cursor-pointer"
                >
                  <span>शुरू करें / Get Started</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-orange-600" />
                  <span>Real-time insights</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-orange-600" />
                  <span>7+ Languages</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-orange-600" />
                  <span>Free to use</span>
                </div>
              </div>
            </div>

            {/* Right Content - Agriculture Field Artwork */}
            <div className="lg:col-span-6 flex justify-center items-center">
              <img
                src="/hero.jpg"
                alt="Agriculture Field"
                className="w-full max-w-xl rounded-3xl shadow-2xl object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features for{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-amber-600">
                Modern Farming
              </span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-orange-500 to-amber-600 mx-auto rounded"></div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group bg-white border-2 border-gray-100 rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 hover:border-orange-200 hover:-translate-y-1"
              >
                <div className="text-orange-600 mb-4 group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section
        id="how-it-works"
        className="py-20 bg-gradient-to-br from-orange-50 to-amber-50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              How Krishi Mitra Works
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="bg-gradient-to-br from-orange-500 to-amber-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <MessageCircle className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                1. Ask Your Question
              </h3>
              <p className="text-gray-600">
                Speak or type in your preferred language
              </p>
            </div>

            <div className="text-center group">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <Brain className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                2. AI Analyzes
              </h3>
              <p className="text-gray-600">
                Advanced AI processes your query with local context
              </p>
            </div>

            <div className="text-center group">
              <div className="bg-gradient-to-br from-emerald-500 to-teal-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <Lightbulb className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                3. Get Expert Advice
              </h3>
              <p className="text-gray-600">
                Receive actionable insights and recommendations
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-3 rounded-lg">
                  <Wheat className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">कृषि मित्र AI</h3>
                  <p className="text-gray-400">
                    Your Trusted Agricultural Advisor
                  </p>
                </div>
              </div>
              <p className="text-gray-300 mb-4 max-w-md">
                Empowering farmers across India with AI-powered agricultural
                insights, real-time market data, and expert guidance in local
                languages.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-300">
                <li>
                  <button
                    onClick={() => navigate("/auth")}
                    className="hover:text-orange-400 transition-colors"
                  >
                    Get Started
                  </button>
                </li>
                <li>
                  <a
                    href="#features"
                    className="hover:text-orange-400 transition-colors"
                  >
                    Features
                  </a>
                </li>
                <li>
                  <a
                    href="#how-it-works"
                    className="hover:text-orange-400 transition-colors"
                  >
                    How It Works
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="hover:text-orange-400 transition-colors"
                  >
                    Support
                  </a>
                </li>
              </ul>
            </div>

            {/* Languages */}
            <div>
              <h4 className="text-lg font-semibold mb-4">
                Supported Languages
              </h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>🇮🇳 हिंदी (Hindi)</li>
                <li>🇺🇸 English</li>
                <li>🇮🇳 ਪੰਜਾਬੀ (Punjabi)</li>
                <li>🇮🇳 தமிழ் (Tamil)</li>
                <li>🇮🇳 తెలుగు (Telugu)</li>
                <li>🇮🇳 বাংলা (Bengali)</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2024 Krishi Mitra AI. Made with ❤️ for Indian Farmers
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;