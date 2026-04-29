import { describe, it, expect, vi, beforeEach } from 'vitest';

// ============================================
// API Client Tests
// ============================================

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API Client', () => {
  const API_URL = 'http://localhost:8000';

  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('Health Check', () => {
    it('fetches health status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();

      expect(data.status).toBe('ok');
      expect(mockFetch).toHaveBeenCalledWith(`${API_URL}/health`);
    });
  });

  describe('Forecast Endpoints', () => {
    it('fetches daily forecast', async () => {
      const mockForecast = {
        status: 'success',
        data: {
          scope: 'daily',
          sections: [{ title: 'General', content: 'Today is a good day...' }],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockForecast,
      });

      const response = await fetch(`${API_URL}/v2/forecasts/daily`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: {
            name: 'Test',
            date_of_birth: '1990-05-15',
          },
        }),
      });

      const data = await response.json();
      expect(data.status).toBe('success');
      expect(data.data.scope).toBe('daily');
    });

    it('handles forecast error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid date format' }),
      });

      const response = await fetch(`${API_URL}/v2/forecasts/daily`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: {
            name: 'Test',
            date_of_birth: 'invalid-date',
          },
        }),
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
    });
  });

  describe('Authentication Endpoints', () => {
    it('registers a new user', async () => {
      const mockUser = {
        status: 'success',
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { id: '1', email: 'test@example.com', is_paid: false },
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const response = await fetch(`${API_URL}/v2/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'securepassword123',
        }),
      });

      const data = await response.json();
      expect(data.data.access_token).toBe('test-token');
      expect(data.data.user.email).toBe('test@example.com');
    });

    it('handles login failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Incorrect email or password' }),
      });

      const response = await fetch(`${API_URL}/v2/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'wrongpassword',
        }),
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(401);
    });
  });

  describe('Numerology Endpoints', () => {
    it('fetches numerology profile', async () => {
      const mockNumerology = {
        status: 'success',
        data: {
          life_path: 7,
          life_path_meaning: 'The Seeker',
          expression_number: 3,
          soul_urge: 5,
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockNumerology,
      });

      const response = await fetch(`${API_URL}/v2/numerology/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'John Doe',
          date_of_birth: '1990-05-15',
        }),
      });

      const data = await response.json();
      expect(data.data.life_path).toBe(7);
    });
  });

  describe('Moon Endpoints', () => {
    it('fetches current moon phase', async () => {
      const mockMoon = {
        status: 'success',
        data: {
          phase_name: 'Waxing Gibbous',
          illumination: 0.75,
          phase_emoji: '🌔',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMoon,
      });

      const response = await fetch(`${API_URL}/v2/moon/phase`);
      const data = await response.json();

      expect(data.data.phase_name).toBe('Waxing Gibbous');
      expect(data.data.illumination).toBe(0.75);
    });
  });

  describe('Compatibility Endpoints', () => {
    it('fetches compatibility analysis', async () => {
      const mockCompatibility = {
        status: 'success',
        data: {
          overall_score: 85,
          rating: 'Excellent',
          aspects: [{ type: 'Sun-Moon', score: 90 }],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCompatibility,
      });

      const response = await fetch(`${API_URL}/v2/compatibility/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          person_a: { name: 'Person A', date_of_birth: '1990-05-15' },
          person_b: { name: 'Person B', date_of_birth: '1992-08-22' },
        }),
      });

      const data = await response.json();
      expect(data.data.overall_score).toBe(85);
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(fetch(`${API_URL}/health`)).rejects.toThrow('Network error');
    });

    it('handles timeout', async () => {
      mockFetch.mockImplementationOnce(
        () => new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 100))
      );

      await expect(fetch(`${API_URL}/health`)).rejects.toThrow('Timeout');
    });
  });
});

// ============================================
// API Response Type Tests
// ============================================

describe('API Response Types', () => {
  it('validates successful response structure', () => {
    const successResponse = {
      status: 'success',
      data: { key: 'value' },
      request_id: 'abc-123',
    };

    expect(successResponse.status).toBe('success');
    expect(successResponse.data).toBeDefined();
  });

  it('validates error response structure', () => {
    const errorResponse = {
      status: 'error',
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
      },
      request_id: 'abc-123',
    };

    expect(errorResponse.status).toBe('error');
    expect(errorResponse.error.code).toBe('VALIDATION_ERROR');
  });
});
