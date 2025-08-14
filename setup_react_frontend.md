# React Frontend Setup Guide

## Step 1: Create New GitHub Repository

1. Go to GitHub and create a new repository named `family-point-system-frontend`
2. Initialize with README
3. Clone to your local machine

## Step 2: Create React App

```bash
# Navigate to your projects directory
cd "path/to/your/projects"

# Create React app
npx create-react-app family-point-system-frontend
cd family-point-system-frontend

# Install additional dependencies
npm install axios react-router-dom @heroicons/react
npm install @simplewebauthn/browser
npm install tailwindcss @tailwindcss/forms

# Initialize Tailwind CSS
npx tailwindcss init -p
```

## Step 3: Basic Project Structure

Create the following directory structure:

```
src/
├── components/
│   ├── auth/
│   ├── parent/
│   ├── child/
│   └── common/
├── services/
├── hooks/
├── context/
└── utils/
```

## Step 4: Environment Configuration

Create `.env` file:
```
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_WEBAUTHN_RP_ID=localhost
REACT_APP_WEBAUTHN_RP_NAME=Family Point System
```

## Step 5: Basic API Service

Create `src/services/api.js`:
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/api/login', credentials),
  register: (userData) => api.post('/auth/api/register', userData),
  logout: () => api.post('/auth/api/logout'),
  getCurrentUser: () => api.get('/auth/api/me'),
  validateParentCode: (code) => api.get(`/auth/api/parent-code/${code}`),
};

// Parent endpoints
export const parentAPI = {
  getDashboard: () => api.get('/parent/api/dashboard'),
  getChildren: () => api.get('/parent/api/children'),
  getChild: (id) => api.get(`/parent/api/children/${id}`),
  removeChild: (id) => api.delete(`/parent/api/children/${id}`),
  getProfile: () => api.get('/parent/api/profile'),
  updateProfile: (data) => api.put('/parent/api/profile', data),
};

// Child endpoints
export const childAPI = {
  getDashboard: () => api.get('/child/api/dashboard'),
  getProfile: () => api.get('/child/api/profile'),
  updateProfile: (data) => api.put('/child/api/profile', data),
  getParent: () => api.get('/child/api/parent'),
};

export default api;
```

## Step 6: Authentication Context

Create `src/context/AuthContext.js`:
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data.user);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await authAPI.login(credentials);
    if (response.data.success) {
      setUser(response.data.user);
      return response.data;
    }
    throw new Error(response.data.message);
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    if (response.data.success) {
      return response.data;
    }
    throw new Error(response.data.message);
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
    isParent: user?.role === 'parent',
    isChild: user?.role === 'child',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Step 7: Basic App Structure

Update `src/App.js`:
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import ParentDashboard from './components/parent/Dashboard';
import ChildDashboard from './components/child/Dashboard';
import LoadingSpinner from './components/common/LoadingSpinner';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" />;
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to={`/${user.role}/dashboard`} />;
  }

  return children;
};

const AppRoutes = () => {
  const { user, loading } = useAuth();

  if (loading) return <LoadingSpinner />;

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to={`/${user.role}/dashboard`} /> : <LoginForm />
      } />
      <Route path="/register" element={
        user ? <Navigate to={`/${user.role}/dashboard`} /> : <RegisterForm />
      } />
      <Route path="/parent/dashboard" element={
        <ProtectedRoute requiredRole="parent">
          <ParentDashboard />
        </ProtectedRoute>
      } />
      <Route path="/child/dashboard" element={
        <ProtectedRoute requiredRole="child">
          <ChildDashboard />
        </ProtectedRoute>
      } />
      <Route path="/" element={
        user ? <Navigate to={`/${user.role}/dashboard`} /> : <Navigate to="/login" />
      } />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## Step 8: Run and Test

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The React app will run on `http://localhost:3000` and communicate with your Flask API on `http://localhost:5000`.

## Next Steps

1. Create the individual components (LoginForm, RegisterForm, etc.)
2. Implement Passkey authentication
3. Style with Tailwind CSS
4. Add error handling and loading states
5. Implement the remaining features (tasks, points, rewards)

This setup provides a solid foundation for your React frontend that will consume the Flask API backend.
