// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import { useState, useEffect } from 'react';
import './App.css';
import Chat from './Chat.jsx';

const App = () => {
  document.documentElement.lang = 'en';

  // Get user ID from backend on load
  const [userId, setUserId] = useState('Loading...');

  useEffect(() => {
    fetch('/user-info')
      .then(res => res.json())
      .then(data => setUserId(data.user_id || 'Unknown'))
      .catch(() => setUserId('Unknown'));
  }, []);

  return (
    <div className="page-content-container">
      <h1>🌟 LifePath AI - Your Personal Growth Companion</h1>
      <div className="user-indicator">
        👤 Active Persona: <strong>{userId}</strong>
      </div>
      <div className="chat-disclaimer">
        I remember your life experiences and help you reflect on your personal growth journey. What would you like to talk about?
      </div>
      <Chat/>
    </div>
  );
};

export default App;
