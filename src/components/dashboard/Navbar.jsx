import React, { useState } from 'react';
import {
  Bell,
  Settings,
  User,
  Menu,
  X,
  Wheat,
  Search,
  ChevronDown,
  LogOut,
  HelpCircle,
  Globe
} from 'lucide-react';

const Navbar = ({ onMenuToggle, isMobileMenuOpen = false }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notificationCount, setNotificationCount] = useState(3);

  const notifications = [
    {
      id: 1,
      type: 'alert',
      title: 'Weather Alert',
      message: 'Heavy rainfall expected tomorrow',
      time: '2 hours ago',
      unread: true
    },
    {
      id: 2,
      type: 'market',
      title: 'Price Update',
      message: 'Wheat prices increased by 2.4%',
      time: '4 hours ago',
      unread: true
    },
    {
      id: 3,
      type: 'calendar',
      title: 'Growth Stage',
      message: 'Your crop entered flowering stage',
      time: '1 day ago',
      unread: false
    }
  ];

  const userMenuItems = [
    { icon: <User className="w-4 h-4" />, label: 'Profile', action: () => {} },
    { icon: <Settings className="w-4 h-4" />, label: 'Settings', action: () => {} },
    { icon: <Globe className="w-4 h-4" />, label: 'Language', action: () => {} },
    { icon: <HelpCircle className="w-4 h-4" />, label: 'Help & Support', action: () => {} },
    { icon: <LogOut className="w-4 h-4" />, label: 'Sign Out', action: () => {} }
  ];

  const handleNotificationClick = (id) => {
    // Mark notification as read
    console.log('Notification clicked:', id);
  };

  const clearNotifications = () => {
    setNotificationCount(0);
    setShowNotifications(false);
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-4 lg:px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Left Side */}
        <div className="flex items-center space-x-4">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuToggle}
            className="lg:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {isMobileMenuOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>

          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-2 rounded-lg">
              <Wheat className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-lg font-bold text-gray-900">KisanMitra AI</span>
              <div className="text-xs text-gray-500">Agricultural Advisor</div>
            </div>
          </div>
        </div>

        {/* Center - Search Bar (Desktop) */}

        {/* Right Side */}
        <div className="flex items-center space-x-2">

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
            >
              <Bell className="w-5 h-5" />
              {notificationCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {notificationCount > 9 ? '9+' : notificationCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-100">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
                    {notificationCount > 0 && (
                      <button
                        onClick={clearNotifications}
                        className="text-xs text-orange-600 hover:text-orange-700"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {notifications.map((notification) => (
                    <button
                      key={notification.id}
                      onClick={() => handleNotificationClick(notification.id)}
                      className={`w-full text-left p-4 hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-b-0 ${
                        notification.unread ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          notification.unread ? 'bg-blue-500' : 'bg-transparent'
                        }`}></div>
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">
                            {notification.title}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            {notification.message}
                          </div>
                          <div className="text-xs text-gray-500 mt-2">
                            {notification.time}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
                {notifications.length === 0 && (
                  <div className="p-8 text-center text-gray-500">
                    <Bell className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <div className="text-sm">No notifications</div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-600 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-sm font-medium text-gray-900">Ramesh Kumar</div>
                <div className="text-xs text-gray-500">Farmer</div>
              </div>
              <ChevronDown className="w-4 h-4 hidden sm:block" />
            </button>

            {/* User Dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-100">
                  <div className="text-sm font-medium text-gray-900">Ramesh Kumar</div>
                  <div className="text-xs text-gray-500">ramesh.kumar@email.com</div>
                </div>
                <div className="py-2">
                  {userMenuItems.map((item, index) => (
                    <button
                      key={index}
                      onClick={item.action}
                      className="w-full text-left flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      {item.icon}
                      <span>{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Search Bar */}
      {/* <div className="md:hidden mt-3">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="w-4 h-4 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Ask me anything about farming..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all text-sm"
          />
        </div>
      </div> */}
    </nav>
  );
};

export default Navbar;