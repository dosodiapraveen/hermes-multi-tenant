/**
 * Centralized API client with caching, retry logic, and request deduplication
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second

class APIClient {
  constructor() {
    this.cache = new Map()
    this.pendingRequests = new Map()
  }

  /**
   * Get authentication token from cookie or localStorage
   */
  getToken() {
    // Try cookie first (newer method)
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'portal_token') {
        return value
      }
    }

    // Fallback to localStorage (backward compatibility)
    return localStorage.getItem('portal_token')
  }

  /**
   * Get CSRF token from cookie
   */
  getCsrfToken() {
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'csrf_token') {
        return value
      }
    }
    return null
  }

  /**
   * Build request headers
   */
  getHeaders(includeAuth = true, includeCsrf = false) {
    const headers = {
      'Content-Type': 'application/json'
    }

    if (includeAuth) {
      const token = this.getToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    if (includeCsrf) {
      const csrfToken = this.getCsrfToken()
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      }
    }

    return headers
  }

  /**
   * Generate cache key from URL and options
   */
  getCacheKey(url, options = {}) {
    return `${url}:${JSON.stringify(options.params || {})}`
  }

  /**
   * Check if cached response is still valid
   */
  isCacheValid(cacheEntry) {
    if (!cacheEntry) return false
    return Date.now() - cacheEntry.timestamp < CACHE_TTL
  }

  /**
   * Make HTTP request with retry logic
   */
  async makeRequest(url, options = {}, retryCount = 0) {
    try {
      const response = await fetch(url, options)

      // Handle non-2xx responses
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`)
        error.status = response.status

        // Try to parse error message from response
        try {
          const data = await response.json()
          error.message = data.detail || data.message || error.message
        } catch (e) {
          // Response not JSON, use status text
        }

        throw error
      }

      return await response.json()
    } catch (error) {
      // Retry on network errors or 5xx errors
      const shouldRetry =
        retryCount < MAX_RETRIES &&
        (!error.status || error.status >= 500)

      if (shouldRetry) {
        const delay = RETRY_DELAY * Math.pow(2, retryCount) // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay))
        return this.makeRequest(url, options, retryCount + 1)
      }

      throw error
    }
  }

  /**
   * GET request with caching
   */
  async get(endpoint, params = {}, options = {}) {
    const { skipCache = false } = options
    const queryString = new URLSearchParams(params).toString()
    const url = `${API_BASE}${endpoint}${queryString ? `?${queryString}` : ''}`
    const cacheKey = this.getCacheKey(url)

    // Check cache
    if (!skipCache) {
      const cached = this.cache.get(cacheKey)
      if (this.isCacheValid(cached)) {
        return cached.data
      }
    }

    // Check if request is already pending (request deduplication)
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey)
    }

    // Make request
    const requestPromise = this.makeRequest(url, {
      method: 'GET',
      headers: this.getHeaders(true, false),
      credentials: 'include'
    })

    // Store pending request
    this.pendingRequests.set(cacheKey, requestPromise)

    try {
      const data = await requestPromise

      // Cache response
      if (!skipCache) {
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now()
        })
      }

      return data
    } finally {
      // Remove from pending requests
      this.pendingRequests.delete(cacheKey)
    }
  }

  /**
   * POST request
   */
  async post(endpoint, body = {}, options = {}) {
    const url = `${API_BASE}${endpoint}`

    return this.makeRequest(url, {
      method: 'POST',
      headers: this.getHeaders(true, true),
      credentials: 'include',
      body: JSON.stringify(body)
    })
  }

  /**
   * PUT request
   */
  async put(endpoint, body = {}, options = {}) {
    const url = `${API_BASE}${endpoint}`

    return this.makeRequest(url, {
      method: 'PUT',
      headers: this.getHeaders(true, true),
      credentials: 'include',
      body: JSON.stringify(body)
    })
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`

    return this.makeRequest(url, {
      method: 'DELETE',
      headers: this.getHeaders(true, true),
      credentials: 'include'
    })
  }

  /**
   * Clear cache (all or specific endpoint)
   */
  clearCache(endpoint = null) {
    if (endpoint) {
      const keysToDelete = []
      for (const key of this.cache.keys()) {
        if (key.startsWith(`${API_BASE}${endpoint}`)) {
          keysToDelete.push(key)
        }
      }
      keysToDelete.forEach(key => this.cache.delete(key))
    } else {
      this.cache.clear()
    }
  }

  /**
   * Track analytics event
   */
  async trackEvent(eventType, eventCategory, eventData = {}) {
    try {
      await this.post('/api/me/analytics/track', {
        event_type: eventType,
        event_category: eventCategory,
        event_data: eventData
      })
    } catch (error) {
      // Silently fail analytics tracking to not disrupt user experience
      console.warn('Analytics tracking failed:', error)
    }
  }
}

// Export singleton instance
export default new APIClient()
