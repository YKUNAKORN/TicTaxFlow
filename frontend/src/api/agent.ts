import { apiClient } from './client';

interface ChatRequest {
  message: string;
}

interface ChatResponse {
  response: string;
  timestamp: string;
}

export const agentApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const requestData: ChatRequest = { message };
    return apiClient.post<ChatResponse>('/agent/chat', requestData, {
      requiresAuth: true,
    });
  },
};
