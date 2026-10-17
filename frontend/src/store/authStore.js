import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { configureApi } from '../services/api';
import {
  decodeToken,
  login as loginRequest,
  register as registerRequest,
} from '../services/authService';
import { getCurrentClient } from '../services/clientService';
import { useFinanceStore } from './financeStore';
import { useDemoStore } from './demoStore';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      sessionExpired: false,

      login: async (username, password) => {
        const tokens = await loginRequest(username, password);
        const claims = decodeToken(tokens.access);
        set({
          accessToken: tokens.access,
          refreshToken: tokens.refresh,
          user: { username, id: claims.user_id ?? null, client: null },
          isAuthenticated: true,
          sessionExpired: false,
        });
        try {
          useDemoStore.getState().addNotification({
            kind: 'login',
            title: 'Nouvelle connexion',
            message: 'Vous vous êtes connecté depuis cet appareil.',
          });
        } catch {
          /* demo store optionnel */
        }
        get().loadClient();
      },

      /** Après inscription : utilise les tokens renvoyés par /auth/register/ */
      completeRegistration: async (data) => {
        const access = data.access;
        const refresh = data.refresh;
        const claims = decodeToken(access);
        const username = data.user?.username || data.user?.email || '';
        set({
          accessToken: access,
          refreshToken: refresh,
          user: {
            username,
            id: claims.user_id ?? data.user?.id ?? null,
            client: data.client || null,
          },
          isAuthenticated: true,
          sessionExpired: false,
        });
        if (!data.client) get().loadClient();
      },

      loadClient: async () => {
        try {
          const client = await getCurrentClient();
          if (client) set((s) => ({ user: { ...s.user, client } }));
        } catch {
          /* fiche client optionnelle pour naviguer */
        }
      },

      setClient: (client) => set((s) => ({ user: { ...s.user, client } })),

      setTokens: (access, refresh) =>
        set((s) => ({
          accessToken: access,
          refreshToken: refresh ?? s.refreshToken,
        })),

      logout: (expired = false) => {
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
          sessionExpired: expired === true,
        });
        try {
          useFinanceStore.getState().reset();
        } catch {
          /* */
        }
      },
    }),
    {
      name: 'finova-auth',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (s) => ({
        accessToken: s.accessToken,
        refreshToken: s.refreshToken,
        user: s.user,
        isAuthenticated: s.isAuthenticated,
      }),
    },
  ),
);

configureApi({
  getAccessToken: () => useAuthStore.getState().accessToken,
  getRefreshToken: () => useAuthStore.getState().refreshToken,
  onTokenRefreshed: (access, refresh) =>
    useAuthStore.getState().setTokens(access, refresh),
  onSessionExpired: () => useAuthStore.getState().logout(true),
});
