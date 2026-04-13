import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../utils/api';

const AuthContext = createContext(null);
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('dept_token');
    const savedUser = localStorage.getItem('dept_user');
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch {}
    }
    setLoading(false);
  }, []);

  const _storeSession = (data) => {
    setUser(data.user);
    setToken(data.access_token);
    localStorage.setItem('dept_token', data.access_token);
    localStorage.setItem('dept_refresh_token', data.refresh_token);
    localStorage.setItem('dept_user', JSON.stringify(data.user));
  };

  const loginStudent = useCallback(async (email, password) => {
    const data = await authAPI.login(email, password);
    _storeSession(data);
    return data.user;
  }, []);

  const loginAdmin = useCallback(async (email, password) => {
    const data = await authAPI.adminLogin(email, password);
    _storeSession(data);
    return data.user;
  }, []);

  const registerStudent = useCallback(async (formData) => {
    const data = await authAPI.register(formData);
    _storeSession(data);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try { await authAPI.logout(); } catch {}
    setUser(null);
    setToken(null);
    localStorage.removeItem('dept_token');
    localStorage.removeItem('dept_refresh_token');
    localStorage.removeItem('dept_user');
  }, []);

  const isStudent = user?.role === 'student';
  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{
      user, token, loading,
      loginStudent, loginAdmin, registerStudent, logout,
      isStudent, isAdmin,
    }}>
      {children}
    </AuthContext.Provider>
  );
};
