/**
 * API Client with Cookie-based Authentication
 *
 * Provides a consistent interface for making API calls with
 * automatic CSRF protection and cookie-based authentication.
 */

import { authenticatedFetch, getCSRFToken } from './csrf.js';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * API Client class for making authenticated requests
 */
class APIClient {
  /**
   * Make a GET request
   * @param {string} endpoint - API endpoint path
   * @param {object} options - Additional fetch options
   * @returns {Promise<any>} JSON response
   */
  async get(endpoint, options = {}) {
    const response = await authenticatedFetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      ...options
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return response.json();
  }

  /**
   * Make a POST request
   * @param {string} endpoint - API endpoint path
   * @param {object} data - Request body data
   * @param {object} options - Additional fetch options
   * @returns {Promise<any>} JSON response
   */
  async post(endpoint, data = {}, options = {}) {
    const response = await authenticatedFetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: data,
      ...options
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return response.json();
  }

  /**
   * Make a PUT request
   * @param {string} endpoint - API endpoint path
   * @param {object} data - Request body data
   * @param {object} options - Additional fetch options
   * @returns {Promise<any>} JSON response
   */
  async put(endpoint, data = {}, options = {}) {
    const response = await authenticatedFetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      body: data,
      ...options
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return response.json();
  }

  /**
   * Make a DELETE request
   * @param {string} endpoint - API endpoint path
   * @param {object} options - Additional fetch options
   * @returns {Promise<any>} JSON response
   */
  async delete(endpoint, options = {}) {
    const response = await authenticatedFetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      ...options
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return response.json();
  }

  /**
   * Handle API errors
   * @param {Response} response - Fetch response object
   * @throws {Error} API error
   */
  async handleError(response) {
    let errorMessage = `API Error: ${response.status}`;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // Response body is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }

    // Handle unauthorized (redirect to login)
    if (response.status === 401) {
      window.location.href = '/login';
      throw new Error('Session expired. Please log in again.');
    }

    // Handle CSRF errors
    if (response.status === 403 && errorMessage.includes('CSRF')) {
      // CSRF token invalid or expired, try to refresh page to get new token
      console.error('CSRF token error, refreshing page...');
      window.location.reload();
      throw new Error('CSRF token error. Page will refresh.');
    }

    throw new Error(errorMessage);
  }
}

// Export singleton instance
export const api = new APIClient();

/**
 * Admin API endpoints
 */
export const adminAPI = {
  /**
   * Login as admin
   * @param {string} email - Admin email
   * @param {string} password - Admin password
   * @returns {Promise<object>} Login response
   */
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include', // Important: Include cookies
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  /**
   * Logout admin
   * @returns {Promise<void>}
   */
  async logout() {
    await api.post('/api/auth/logout');
    window.location.href = '/login';
  },

  /**
   * Get all users
   * @returns {Promise<array>} List of users
   */
  async getUsers() {
    return api.get('/api/admin/users');
  },

  /**
   * Create user
   * @param {object} userData - User data
   * @returns {Promise<object>} Created user
   */
  async createUser(userData) {
    return api.post('/api/admin/users', userData);
  },

  /**
   * Update user
   * @param {string} userId - User ID
   * @param {object} userData - User data
   * @returns {Promise<object>} Updated user
   */
  async updateUser(userId, userData) {
    return api.put(`/api/admin/users/${userId}`, userData);
  },

  /**
   * Delete user
   * @param {string} userId - User ID
   * @returns {Promise<object>} Delete response
   */
  async deleteUser(userId) {
    return api.delete(`/api/admin/users/${userId}`);
  }
};

/**
 * Portal (user) API endpoints
 */
export const portalAPI = {
  /**
   * Login as portal user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<object>} Login response
   */
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/user/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  /**
   * Register new portal user
   * @param {string} email - User email
   * @param {string} password - User password
   * @param {string} profileId - Profile ID from invite link
   * @returns {Promise<object>} Registration response
   */
  async register(email, password, profileId) {
    const response = await fetch(`${API_BASE_URL}/api/auth/user/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ email, password, profile_id: profileId })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  /**
   * Logout portal user
   * @returns {Promise<void>}
   */
  async logout() {
    await api.post('/api/auth/user/logout');
    window.location.href = '/user/login';
  },

  /**
   * Get user profile
   * @returns {Promise<object>} User profile
   */
  async getProfile() {
    return api.get('/api/me');
  },

  /**
   * Get user notes
   * @returns {Promise<array>} List of notes
   */
  async getNotes() {
    return api.get('/api/me/notes');
  },

  /**
   * Create note
   * @param {object} noteData - Note data
   * @returns {Promise<object>} Created note
   */
  async createNote(noteData) {
    return api.post('/api/me/notes', noteData);
  },

  /**
   * Update note
   * @param {string} noteId - Note ID
   * @param {object} noteData - Note data
   * @returns {Promise<object>} Updated note
   */
  async updateNote(noteId, noteData) {
    return api.put(`/api/me/notes/${noteId}`, noteData);
  },

  /**
   * Delete note
   * @param {string} noteId - Note ID
   * @returns {Promise<object>} Delete response
   */
  async deleteNote(noteId) {
    return api.delete(`/api/me/notes/${noteId}`);
  }
};

export default api;
