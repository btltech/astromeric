/**
 * Custom hook for authentication
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    is_paid: boolean;
  };
}

export function useAuth() {
  const { token, user, setAuth, logout, setLoading, setError } = useStore();

  const isAuthenticated = !!token;

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError('');

      try {
        const data = await apiFetch<AuthResponse>('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });

        setAuth(data.access_token, data.user);
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Login failed';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [setAuth, setLoading, setError]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError('');

      try {
        const data = await apiFetch<AuthResponse>('/auth/register', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });

        setAuth(data.access_token, data.user);
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Registration failed';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [setAuth, setLoading, setError]
  );

  const handleLogout = useCallback(() => {
    logout();
  }, [logout]);

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout: handleLogout,
  };
}
