import axiosClient from './axiosClient';

export interface PlaceResponse {
  id: string;
  name: string;
  category: string;
  city: string;
  latitude: number;
  longitude: number;
}

export const searchPlaces = async (query?: string, city?: string): Promise<PlaceResponse[]> => {
  const response = await axiosClient.get<PlaceResponse[]>('/places/', {
    params: { query, city },
  });
  return response.data;
};