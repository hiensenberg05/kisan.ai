/// <reference types="vite/client" />
// API Service for Kisan.ai Backend Integration
// Use VITE_API_URL for backend base URL (set in .env file)
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  response: string;
  category?: 'disease' | 'market' | 'scheme' | 'general';
}

export interface VoiceResponse {
  response_text: string;
  audio_url?: string;
}

export interface ImageAnalysisResponse {
  image_analysis: string;
  response: string;
  confidence?: number;
  disease_detected?: string;
  treatment_recommendations?: string[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class ApiService {
  private baseUrl = BASE_URL;

  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    try {
      const res = await fetch(`${this.baseUrl}/api/health`);
      const data = await res.json();
      return { success: data.success, data: data.data, error: data.error };
    } catch (error) {
      return { success: false, error: 'Health check failed' };
    }
  }

  async sendTextMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    try {
      const res = await fetch(`${this.baseUrl}/api/chat/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });
      const data = await res.json();
      if (data.success && data.data) {
        return { success: true, data: { response: data.data.response || data.data, category: data.data.category } };
      } else {
        return { success: false, error: data.error || 'Failed to process your message' };
      }
    } catch (error) {
      return { success: false, error: 'Failed to process your message' };
    }
  }

  async sendVoiceMessage(audioFile: File): Promise<ApiResponse<VoiceResponse>> {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      const res = await fetch(`${this.baseUrl}/api/chat/voice`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success && data.data) {
        return { success: true, data: { response_text: data.data.response_text, audio_url: data.data.audio_response } };
      } else {
        return { success: false, error: data.error || 'Failed to process voice message' };
      }
    } catch (error) {
      return { success: false, error: 'Failed to process voice message' };
    }
  }

  async analyzeImage(imageFile: File): Promise<ApiResponse<ImageAnalysisResponse>> {
    try {
      const formData = new FormData();
      formData.append('image_file', imageFile);
      const res = await fetch(`${this.baseUrl}/api/chat/image`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success && data.data) {
        return { success: true, data: data.data };
      } else {
        return { success: false, error: data.error || 'Failed to analyze image' };
      }
    } catch (error) {
      return { success: false, error: 'Failed to analyze image' };
    }
  }
}

export const apiService = new ApiService();