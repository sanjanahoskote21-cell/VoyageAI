import axiosClient from './axiosClient';

export interface ChatResponse {
  reply: string;
}

export const sendChatMessage = async (tripId: string, message: string): Promise<ChatResponse> => {
  const response = await axiosClient.post<ChatResponse>(`/trips/${tripId}/chat`, { message });
  return response.data;
};