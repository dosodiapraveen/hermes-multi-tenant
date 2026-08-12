/**
 * CSRF Token Utilities
 *
 * Provides functions for reading and managing CSRF tokens
 * from cookies for protection against cross-site request forgery.
 */

/**
 * Get a cookie value by name
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null if not found
 */
export function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
}

/**
 * Get the CSRF token from cookies
 * @returns {string|null} CSRF token or null if not found
 */
export function getCSRFToken() {
  return getCookie('csrf_token');
}

/**
 * Check if user is authenticated by checking for auth cookie
 * @returns {boolean} True if authenticated
 */
export function isAuthenticated() {
  // Check for either admin_token or portal_token cookie
  return getCookie('admin_token') !== null || getCookie('portal_token') !== null;
}

/**
 * Check if user is admin
 * @returns {boolean} True if admin authenticated
 */
export function isAdminAuthenticated() {
  return getCookie('admin_token') !== null;
}

/**
 * Check if portal user is authenticated
 * @returns {boolean} True if portal user authenticated
 */
export function isPortalAuthenticated() {
  return getCookie('portal_token') !== null;
}

/**
 * Add CSRF token to fetch request headers
 * @param {object} headers - Existing headers object
 * @returns {object} Headers with CSRF token added
 */
export function addCSRFHeader(headers = {}) {
  const csrfToken = getCSRFToken();
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  return headers;
}

/**
 * Make an authenticated API request with CSRF protection
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
export async function authenticatedFetch(url, options = {}) {
  // Ensure credentials are included for cookies
  options.credentials = 'include';

  // Add CSRF token header for state-changing methods
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
    options.headers = addCSRFHeader(options.headers || {});
  }

  // Ensure Content-Type is set for JSON requests
  if (options.body && typeof options.body === 'object') {
    options.headers = options.headers || {};
    if (!options.headers['Content-Type']) {
      options.headers['Content-Type'] = 'application/json';
    }
    if (typeof options.body !== 'string') {
      options.body = JSON.stringify(options.body);
    }
  }

  return fetch(url, options);
}

/**
 * Logout by calling logout endpoint to clear cookies
 * @param {string} logoutUrl - Logout endpoint URL
 * @returns {Promise<void>}
 */
export async function logout(logoutUrl = '/api/auth/logout') {
  try {
    await authenticatedFetch(logoutUrl, {
      method: 'POST'
    });
  } catch (error) {
    console.error('Logout error:', error);
  }
  // Redirect to login regardless of API call success
  window.location.href = '/login';
}

/**
 * Clear all authentication state (for emergency logout)
 * Note: This won't clear httpOnly cookies, use logout() for proper cleanup
 */
export function clearAuthState() {
  // Clear any localStorage remnants from old auth system
  localStorage.removeItem('token');
  localStorage.removeItem('admin_token');
  localStorage.removeItem('portal_token');
  localStorage.removeItem('profile_id');
}
