import { createContext, useState, useEffect, type ReactNode } from 'react';
import { loginUser, getCurrentUser, type UserResponse, type LoginPayload } from '../api/authApi';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginPayload) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On app load, check if a token already exists and fetch the user
  useEffect(() => {
    const token = localStorage.getItem('voyageai_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('voyageai_token');
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (credentials: LoginPayload) => {
    const { access_token } = await loginUser(credentials);
    localStorage.setItem('voyageai_token', access_token);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  };

  const logout = () => {
    localStorage.removeItem('voyageai_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}