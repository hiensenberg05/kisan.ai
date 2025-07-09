import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Loader2, Wifi, WifiOff } from 'lucide-react';
import { apiService } from '../services/api';

interface ConnectionStatus {
  backend: 'checking' | 'connected' | 'error';
  message: string;
}

const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    backend: 'checking',
    message: 'Checking connection...'
  });

  useEffect(() => {
    testConnection();
    // Check connection every 30 seconds
    const interval = setInterval(testConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const testConnection = async () => {
    try {
      const response = await apiService.healthCheck();
      
      if (response.success) {
        setStatus({
          backend: 'connected',
          message: 'Connected'
        });
      } else {
        setStatus({
          backend: 'error',
          message: 'Connection failed'
        });
      }
    } catch (error) {
      setStatus({
        backend: 'error',
        message: 'Offline'
      });
    }
  };

  const getStatusIcon = () => {
    switch (status.backend) {
      case 'checking':
        return <Loader2 className="h-4 w-4 animate-spin text-yellow-400" />;
      case 'connected':
        return <Wifi className="h-4 w-4 text-green-400" />;
      case 'error':
        return <WifiOff className="h-4 w-4 text-red-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status.backend) {
      case 'checking':
        return 'text-yellow-200';
      case 'connected':
        return 'text-green-200';
      case 'error':
        return 'text-red-200';
    }
  };

  const getStatusBg = () => {
    switch (status.backend) {
      case 'checking':
        return 'bg-yellow-500/20';
      case 'connected':
        return 'bg-green-500/20';
      case 'error':
        return 'bg-red-500/20';
    }
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${getStatusBg()} backdrop-blur-sm border border-white/20`}>
      {getStatusIcon()}
      <span className={`text-sm font-medium ${getStatusColor()}`}>
        {status.message}
      </span>
    </div>
  );
};

export default ConnectionTest;