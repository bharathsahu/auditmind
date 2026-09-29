import axios from 'axios';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach Authorization header if JWT token is saved in localStorage
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('auditmind_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const api = {
  // Auth
  login: async (username, password) => {
    const res = await client.post('/auth/login', { username, password });
    if (res.data && res.data.token) {
      localStorage.setItem('auditmind_token', res.data.token);
      localStorage.setItem('auditmind_user', JSON.stringify(res.data.user));
    }
    return res.data;
  },

  getCurrentUser: async () => {
    const res = await client.get('/auth/me');
    return res.data;
  },

  getAuditLogs: async () => {
    const res = await client.get('/auth/logs');
    return res.data;
  },

  logout: () => {
    localStorage.removeItem('auditmind_token');
    localStorage.removeItem('auditmind_user');
  },

  // Audits
  getAudits: async () => {
    const res = await client.get('/audits');
    return res.data;
  },
  createAudit: async (auditData) => {
    const res = await client.post('/audits', auditData);
    return res.data;
  },

  // Findings
  getFindings: async () => {
    const res = await client.get('/findings');
    return res.data;
  },
  createFinding: async (findingData) => {
    const res = await client.post('/findings', findingData);
    return res.data;
  },
  findSimilarFindings: async (findingId) => {
    const res = await client.post('/findings/similar', { finding_id: findingId });
    return res.data;
  },
  getRecurringFindings: async () => {
    const res = await client.get('/findings/analysis/recurring');
    return res.data;
  },

  // Remediations
  getRemediations: async () => {
    const res = await client.get('/remediations');
    return res.data;
  },
  updateRemediationStatus: async (remediationId, status, comments, evidence) => {
    const res = await client.put(`/remediations/${remediationId}/status`, { status, comments, evidence });
    return res.data;
  },

  // Documents
  getDocuments: async () => {
    const res = await client.get('/documents');
    return res.data;
  },
  uploadDocument: async (file, auditId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (auditId) formData.append('audit_id', auditId);
    
    const token = localStorage.getItem('auditmind_token');
    const headers = { 'Content-Type': 'multipart/form-data' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await axios.post(`${API_BASE}/documents/upload`, formData, { headers });
    return res.data;
  },

  // AI Assistant
  askAI: async (query) => {
    const res = await client.post('/ai/chat', { query });
    return res.data;
  },

  // Hindsight Memory Explorer
  getMemories: async () => {
    const res = await client.get('/hindsight/memories');
    return res.data;
  },
  getMemoryCategories: async () => {
    const res = await client.get('/hindsight/categories');
    return res.data;
  },
  getMemoryGraph: async () => {
    const res = await client.get('/hindsight/graph');
    return res.data;
  },
  recallMemory: async (query) => {
    const res = await client.post('/hindsight/recall', { query });
    return res.data;
  },
  reflectMemory: async (query) => {
    const res = await client.post('/hindsight/reflect', { query });
    return res.data;
  }
};
