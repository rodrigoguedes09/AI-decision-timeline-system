import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get list of decisions with optional filters
 */
export const getDecisions = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);
  if (filters.source) params.append('source', filters.source);
  if (filters.minConfidence !== null && filters.minConfidence !== undefined) {
    params.append('min_confidence', filters.minConfidence);
  }
  if (filters.maxConfidence !== null && filters.maxConfidence !== undefined) {
    params.append('max_confidence', filters.maxConfidence);
  }
  if (filters.search) params.append('search', filters.search);
  if (filters.tag) params.append('tag', filters.tag);
  if (filters.sort) params.append('sort', filters.sort);
  
  const response = await api.get(`/decisions?${params.toString()}`);
  return response.data;
};

/**
 * Get full details of a specific decision
 */
export const getDecision = async (decisionId) => {
  const response = await api.get(`/decisions/${decisionId}`);
  return response.data;
};

/**
 * Get decision data for replay mode
 */
export const getDecisionReplay = async (decisionId) => {
  const response = await api.get(`/decisions/${decisionId}/replay`);
  return response.data;
};

/**
 * Create a new decision
 */
export const createDecision = async (decisionData) => {
  const response = await api.post('/decisions', decisionData);
  return response.data;
};

/**
 * Get statistics about decision traces
 */
export const getStats = async (days = 7) => {
  const response = await api.get(`/traces/stats?days=${days}`);
  return response.data;
};

/**
 * Get advanced statistics overview
 */
export const getStatsOverview = async (days = 30) => {
  const response = await api.get(`/stats/overview?days=${days}`);
  return response.data;
};

/**
 * Get statistics timeline for charts
 */
export const getStatsTimeline = async (days = 30) => {
  const response = await api.get(`/stats/timeline?days=${days}`);
  return response.data;
};

/**
 * Export decisions to CSV
 */
export const exportDecisionsCSV = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.source) params.append('source', filters.source);
  if (filters.minConfidence) params.append('min_confidence', filters.minConfidence);
  
  const url = `${API_BASE_URL}/decisions/export/csv?${params.toString()}`;
  window.open(url, '_blank');
};

/**
 * Export decisions to JSON
 */
export const exportDecisionsJSON = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.source) params.append('source', filters.source);
  if (filters.minConfidence) params.append('min_confidence', filters.minConfidence);
  
  const url = `${API_BASE_URL}/decisions/export/json?${params.toString()}`;
  window.open(url, '_blank');
};

/**
 * Get timeline data
 */
export const getTimelineData = async (days = 7) => {
  const response = await api.get(`/traces/timeline?days=${days}`);
  return response.data;
};

/**
 * Search decisions
 */
export const searchDecisions = async (query, limit = 20) => {
  const response = await api.get(`/traces/search?query=${encodeURIComponent(query)}&limit=${limit}`);
  return response.data;
};

/**
 * Get all tags
 */
export const getTags = async () => {
  const response = await api.get('/traces/tags');
  return response.data;
};

export default api;
