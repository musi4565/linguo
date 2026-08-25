import { create } from "zustand";

import { api, getTokens, setTokens } from "../api/client";

export const useAuth = create((set) => ({
  user: null,

  async login(email, password) {
    const { data } = await api.post("/auth/login/", { email, password });
    setTokens({ access: data.access, refresh: data.refresh });
    set({ user: data.user });
    return data.user;
  },

  async register(name, email, password) {
    const { data } = await api.post("/auth/register/", { name, email, password });
    setTokens({ access: data.access, refresh: data.refresh });
    set({ user: data.user });
    return data.user;
  },

  async fetchUser() {
    const { data } = await api.get("/profile/");
    set({ user: data.user });
    return data;
  },

  setUser(user) {
    set({ user });
  },

  logout() {
    const tokens = getTokens();
    if (tokens?.refresh) {
      api.post("/auth/logout/", { refresh: tokens.refresh }).catch(() => {});
    }
    setTokens(null);
    set({ user: null });
  },
}));
