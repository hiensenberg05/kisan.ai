import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
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
  }, []);

  const testConnection = async () => {
    try {
      const response = await apiService.healthCheck();
      
      if (response.success) {
        setStatus({
          backend: 'connected',
          message: 'Backend connected successfully!'
        });
      } else {
        setStatus({
          backend: 'error',
          message: response.error || 'Backend connection failed'
        });
      }
    } catch (error) {
      setStatus({
        backend: 'error',
        message: 'Unable to connect to backend'
      });
    }
  };

  const getStatusIcon = () => {
    switch (status.backend) {
      case 'checking':
        return <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />;
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status.backend) {
      case 'checking':
        return 'text-yellow-600';
      case 'connected':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
    }
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      {getStatusIcon()}
      <span className={getStatusColor()}>{status.message}</span>
    </div>
  );
};

export default ConnectionTest; 