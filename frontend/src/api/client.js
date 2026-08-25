import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

const TOKEN_KEY = "linguo_tokens";

export function getTokens() {
  try {
    return JSON.parse(localStorage.getItem(TOKEN_KEY)) || null;
  } catch {
    return null;
  }
}

export function setTokens(tokens) {
  if (tokens) localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  else localStorage.removeItem(TOKEN_KEY);
}

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
});

api.interceptors.request.use((config) => {
  const tokens = getTokens();
  if (tokens?.access) config.headers.Authorization = `Bearer ${tokens.access}`;
  return config;
});

function normalizeMediaUrls(data) {
  if (typeof data === "string") {
    return data.replace(/^https?:\/\/(?:127\.0\.0\.1|localhost):8001(\/.+)$/, "$1");
  }
  if (Array.isArray(data)) return data.map(normalizeMediaUrls);
  if (data && typeof data === "object") {
    const out = {};
    for (const key of Object.keys(data)) out[key] = normalizeMediaUrls(data[key]);
    return out;
  }
  return data;
}

api.interceptors.response.use((response) => {
  response.data = normalizeMediaUrls(response.data);
  return response;
});

let refreshPromise = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const tokens = getTokens();
    const isAuthRoute = original?.url?.startsWith("/auth/");

    if (
      error.response?.status === 401 &&
      tokens?.refresh &&
      !original._retry &&
      !isAuthRoute
    ) {
      original._retry = true;
      try {
        refreshPromise =
          refreshPromise ||
          axios.post(`${API_BASE}/api/auth/refresh/`, { refresh: tokens.refresh });
        const { data } = await refreshPromise;
        refreshPromise = null;
        setTokens({ access: data.access, refresh: data.refresh });
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (refreshError) {
        refreshPromise = null;
        setTokens(null);
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export function apiErrorMessage(error) {
  const data = error.response?.data;
  if (!data) return "Server bilan aloqa yo'q";
  if (typeof data.detail === "string") return data.detail;
  const firstKey = Object.keys(data)[0];
  if (firstKey) {
    const val = data[firstKey];
    return `${firstKey}: ${Array.isArray(val) ? val[0] : val}`;
  }
  return "Xatolik yuz berdi";
}
