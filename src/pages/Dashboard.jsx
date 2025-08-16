import React, { useState, useEffect } from 'react';
import Navbar from '../components/dashboard/Navbar';
import Chat from '../components/dashboard/ChatPanel';
import Sidebar from '../components/dashboard/Sidebar';

const Dashboard = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarVisible, setIsSidebarVisible] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Handle responsive behavior
  useEffect(() => {
    const checkScreenSize = () => {
      const mobile = window.innerWidth < 1024; // lg breakpoint
      setIsMobile(mobile);
      if (mobile) {
        setIsSidebarVisible(false); // Hide sidebar on mobile by default
      } else {
        setIsSidebarVisible(true); // Show sidebar on desktop
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const handleMenuToggle = () => {
    if (isMobile) {
      setIsMobileMenuOpen(!isMobileMenuOpen);
    } else {
      setIsSidebarVisible(!isSidebarVisible);
    }
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Navigation Bar */}
      <Navbar 
        onMenuToggle={handleMenuToggle}
        isMobileMenuOpen={isMobileMenuOpen}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Sidebar - Desktop */}
        {!isMobile && (
          <div className={`fixed left-0 top-16 bottom-0 z-20 transform transition-transform duration-300 ${
            isSidebarVisible ? 'translate-x-0' : '-translate-x-full'
          }`}>
            <Sidebar />
          </div>
        )}

        {/* Chat Area */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${
          isSidebarVisible && !isMobile ? 'ml-80' : 'ml-0'
        }`}>
          <Chat />
        </div>

        {/* Mobile Menu Overlay */}
        {isMobile && isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
              onClick={closeMobileMenu}
            />
            
            {/* Mobile Sidebar */}
            <div className="fixed left-0 top-0 bottom-0 z-40 w-80 transform transition-transform duration-300 lg:hidden">
              <div className="h-full bg-white">
                {/* Mobile Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Dashboard</h2>
                  <button
                    onClick={closeMobileMenu}
                    className="p-2 text-gray-500 hover:text-gray-700 rounded-lg"
                  >
                    ×
                  </button>
                </div>
                
                {/* Sidebar Content */}
                <div className="h-full overflow-hidden">
                  <Sidebar />
                </div>
              </div>
            </div>
          </>
        )}

        {/* Mobile Context Panel Drawer Toggle Button */}
        {/* {isMobile && !isMobileMenuOpen && (
          <div className="fixed bottom-4 right-4 z-20">
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="bg-gradient-to-r from-orange-500 to-amber-600 text-white p-3 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        )} */}
      </div>

      {/* Mobile Bottom Drawer */}
      {isMobile && (
        <div className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 transform transition-transform duration-300 z-30 ${
          isMobileMenuOpen ? 'translate-y-0' : 'translate-y-full'
        } lg:hidden`}>
          <div className="max-h-96 overflow-y-auto">
            {/* Drag Handle */}
            <div className="flex justify-center py-2">
              <div className="w-12 h-1 bg-gray-300 rounded-full"></div>
            </div>
            
            {/* Quick Context Cards */}
            <div className="p-4 space-y-4">
              {/* Weather Summary */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Weather</div>
                    <div className="text-lg font-bold text-gray-900">28°C</div>
                    <div className="text-xs text-gray-600">Partly Cloudy</div>
                  </div>
                  <div className="text-blue-500">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Market Summary */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Market</div>
                    <div className="text-lg font-bold text-gray-900">Wheat ₹2,150</div>
                    <div className="text-xs text-green-600">+2.4% ↑</div>
                  </div>
                  <div className="text-green-500">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Crop Progress */}
              <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium text-gray-700">Crop Stage</div>
                  <div className="text-sm font-bold text-orange-600">65% Complete</div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gradient-to-r from-orange-400 to-amber-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
                <div className="text-xs text-gray-600 mt-1">Flowering Stage</div>
              </div>

              {/* View Full Dashboard Button */}
              {/* <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="w-full bg-gradient-to-r from-orange-500 to-amber-600 text-white py-3 rounded-lg font-medium hover:from-orange-600 hover:to-amber-700 transition-all"
              >
                View Full Dashboard
              </button> */}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;