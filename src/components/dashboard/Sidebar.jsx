import React, { useState } from 'react';
import {
  Cloud,
  CloudRain,
  Sun,
  Thermometer,
  Droplets,
  Wind,
  TrendingUp,
  TrendingDown,
  Calendar,
  Sprout,
  Wheat,
  TreePine,
  Phone,
  MessageCircle,
  ExternalLink,
  AlertTriangle,
  MapPin,
  ChevronRight,
  IndianRupee
} from 'lucide-react';

const Sidebar = () => {
  const [activeTab, setActiveTab] = useState('weather');

  // Sample data
  const weatherData = {
    current: {
      temp: 28,
      condition: 'Partly Cloudy',
      humidity: 65,
      windSpeed: 12,
      icon: <Cloud className="w-8 h-8 text-blue-500" />
    },
    forecast: [
      { day: 'Today', temp: '28°/22°', rain: 20, icon: <Cloud className="w-6 h-6 text-blue-500" /> },
      { day: 'Tomorrow', temp: '30°/24°', rain: 60, icon: <CloudRain className="w-6 h-6 text-blue-600" /> },
      { day: 'Wed', temp: '26°/20°', rain: 80, icon: <CloudRain className="w-6 h-6 text-blue-700" /> }
    ],
    alerts: [
      { type: 'warning', message: 'Heavy rainfall expected in 2 days', urgent: true }
    ]
  };

  const marketData = [
    { crop: 'Wheat', price: 2150, change: +50, changePercent: +2.4 },
    { crop: 'Rice', price: 3200, change: -75, changePercent: -2.3 },
    { crop: 'Tomato', price: 1800, change: +120, changePercent: +7.1 },
    { crop: 'Onion', price: 2500, change: +200, changePercent: +8.7 },
    { crop: 'Potato', price: 1200, change: -30, changePercent: -2.4 }
  ];

  const cropCalendar = {
    currentStage: 'Flowering',
    progress: 65,
    stages: [
      { name: 'Sowing', completed: true, icon: <Sprout className="w-4 h-4" /> },
      { name: 'Germination', completed: true, icon: <Sprout className="w-4 h-4" /> },
      { name: 'Vegetative', completed: true, icon: <TreePine className="w-4 h-4" /> },
      { name: 'Flowering', completed: false, active: true, icon: <Wheat className="w-4 h-4" /> },
      { name: 'Harvesting', completed: false, icon: <Wheat className="w-4 h-4" /> }
    ]
  };

  const quickActions = [
    { title: 'Government Schemes', subtitle: 'PM-KISAN, Subsidies', icon: <ExternalLink className="w-5 h-5" />, color: 'bg-blue-500' },
    { title: 'Expert Contacts', subtitle: 'Agricultural Officers', icon: <Phone className="w-5 h-5" />, color: 'bg-green-500' },
    { title: 'Community Forum', subtitle: 'Connect with farmers', icon: <MessageCircle className="w-5 h-5" />, color: 'bg-purple-500' },
    { title: 'Emergency Helpline', subtitle: '24/7 Support', icon: <Phone className="w-5 h-5" />, color: 'bg-red-500' }
  ];

  const tabs = [
    { id: 'weather', label: 'Weather', icon: <Cloud className="w-4 h-4" /> },
    { id: 'market', label: 'Market', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'calendar', label: 'Calendar', icon: <Calendar className="w-4 h-4" /> },
    // { id: 'actions', label: 'Quick Actions', icon: <MessageCircle className="w-4 h-4" /> }
  ];

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center space-x-1 py-2 px-3 rounded-md text-xs font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-white text-orange-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Weather Tab */}
        {activeTab === 'weather' && (
          <div className="space-y-4">
            {/* Current Weather */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Kharagpur</span>
                </div>
                {weatherData.current.icon}
              </div>
              <div className="mb-2">
                <div className="text-3xl font-bold text-gray-900">{weatherData.current.temp}°C</div>
                <div className="text-sm text-gray-600">{weatherData.current.condition}</div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex items-center space-x-1">
                  <Droplets className="w-3 h-3 text-blue-500" />
                  <span className="text-gray-600">{weatherData.current.humidity}%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Wind className="w-3 h-3 text-gray-500" />
                  <span className="text-gray-600">{weatherData.current.windSpeed} km/h</span>
                </div>
              </div>
            </div>

            {/* Weather Alerts */}
            {weatherData.alerts.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <div className="flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />
                  <div>
                    <div className="text-sm font-medium text-amber-800">Weather Alert</div>
                    <div className="text-xs text-amber-700 mt-1">
                      {weatherData.alerts[0].message}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Forecast */}
            <div>
              <div className="text-sm font-semibold text-gray-900 mb-3">3-Day Forecast</div>
              <div className="space-y-2">
                {weatherData.forecast.map((day, index) => (
                  <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {day.icon}
                      <span className="text-sm font-medium text-gray-700">{day.day}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{day.temp}</div>
                      <div className="text-xs text-blue-600">{day.rain}% rain</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Market Tab */}
        {activeTab === 'market' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-gray-900">Market Prices</div>
              <div className="text-xs text-gray-500">Last updated: 2h ago</div>
            </div>
            
            <div className="space-y-2">
              {marketData.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{item.crop}</div>
                    <div className="flex items-center space-x-1 text-xs">
                      <IndianRupee className="w-3 h-3 text-gray-600" />
                      <span className="text-gray-600">{item.price}/quintal</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`flex items-center space-x-1 text-xs font-medium ${
                      item.change > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {item.change > 0 ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      <span>{item.changePercent > 0 ? '+' : ''}{item.changePercent}%</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {item.change > 0 ? '+' : ''}₹{item.change}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full text-left p-3 bg-orange-50 hover:bg-orange-100 rounded-lg border border-orange-200 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-orange-700">View Full Market Report</div>
                  <div className="text-xs text-orange-600">Detailed analysis & trends</div>
                </div>
                <ChevronRight className="w-4 h-4 text-orange-600" />
              </div>
            </button>
          </div>
        )}

        {/* Calendar Tab */}
        {activeTab === 'calendar' && (
          <div className="space-y-4">
            <div>
              <div className="text-sm font-semibold text-gray-900 mb-3">Crop Growth Progress</div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm font-medium text-gray-700">Current Stage</div>
                  <div className="text-sm font-bold text-green-700">{cropCalendar.currentStage}</div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                  <div 
                    className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${cropCalendar.progress}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-600 text-center">{cropCalendar.progress}% Complete</div>
              </div>
            </div>

            <div>
              <div className="text-sm font-semibold text-gray-900 mb-3">Growth Stages</div>
              <div className="space-y-2">
                {cropCalendar.stages.map((stage, index) => (
                  <div 
                    key={index} 
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-all ${
                      stage.active 
                        ? 'bg-green-100 border border-green-200' 
                        : stage.completed 
                          ? 'bg-gray-50' 
                          : 'bg-gray-50 opacity-60'
                    }`}
                  >
                    <div className={`p-1 rounded-full ${
                      stage.active 
                        ? 'bg-green-500 text-white' 
                        : stage.completed 
                          ? 'bg-green-400 text-white' 
                          : 'bg-gray-300 text-gray-500'
                    }`}>
                      {stage.icon}
                    </div>
                    <div>
                      <div className={`text-sm font-medium ${
                        stage.active ? 'text-green-800' : 'text-gray-700'
                      }`}>
                        {stage.name}
                      </div>
                    </div>
                    {stage.completed && (
                      <div className="ml-auto">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;