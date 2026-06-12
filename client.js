const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const CLIENT_PORT = 4000;
const SERVER_URL = 'http://localhost:3000';

// Middleware
app.use(cors());
app.use(express.json());

// Client API Endpoints

// Health check for client
app.get('/api/client/health', (req, res) => {
  res.json({ 
    status: 'Client API is running', 
    server_url: SERVER_URL,
    timestamp: new Date().toISOString() 
  });
});

// Client API to submit ride request
app.post('/api/client/ride-request', async (req, res) => {
  const { source_location, dest_location, user_id } = req.body;

  // Validate required parameters
  if (!source_location || !dest_location || !user_id) {
    return res.status(400).json({
      error: 'Missing required parameters: source_location, dest_location, user_id'
    });
  }

  try {
    console.log('🔄 Client API: Processing ride request...');
    console.log('📍 Source:', source_location);
    console.log('📍 Destination:', dest_location);
    console.log('👤 User ID:', user_id);

    // Forward request to server
    const serverResponse = await axios.post(`${SERVER_URL}/api/rides`, {
      source_location,
      dest_location,
      user_id
    });

    console.log('✅ Client API: Request forwarded to server successfully');

    res.json({
      success: true,
      message: 'Ride request submitted via Client API',
      client_timestamp: new Date().toISOString(),
      server_response: serverResponse.data
    });

  } catch (error) {
    console.error('❌ Client API Error:', error.message);
    
    if (error.response) {
      // Server responded with error
      res.status(error.response.status).json({
        error: 'Server error',
        details: error.response.data
      });
    } else if (error.request) {
      // No response from server
      res.status(503).json({
        error: 'Unable to connect to server',
        server_url: SERVER_URL
      });
    } else {
      // Other error
      res.status(500).json({
        error: 'Client API internal error',
        details: error.message
      });
    }
  }
});

// Client API to get ride history
app.get('/api/client/rides/:user_id', async (req, res) => {
  const { user_id } = req.params;

  try {
    console.log(`🔍 Client API: Fetching rides for user ${user_id}`);
    
    const serverResponse = await axios.get(`${SERVER_URL}/api/rides/user/${user_id}`);
    
    res.json({
      success: true,
      message: 'Ride history fetched via Client API',
      user_id,
      rides: serverResponse.data.data
    });

  } catch (error) {
    console.error('❌ Client API Error fetching rides:', error.message);
    
    if (error.response) {
      res.status(error.response.status).json({
        error: 'Server error',
        details: error.response.data
      });
    } else {
      res.status(503).json({
        error: 'Unable to connect to server',
        server_url: SERVER_URL
      });
    }
  }
});

// Client API to get all rides (admin endpoint)
app.get('/api/client/rides', async (req, res) => {
  try {
    console.log('🔍 Client API: Fetching all rides');
    
    const serverResponse = await axios.get(`${SERVER_URL}/api/rides`);
    
    res.json({
      success: true,
      message: 'All rides fetched via Client API',
      rides: serverResponse.data.data
    });

  } catch (error) {
    console.error('❌ Client API Error fetching all rides:', error.message);
    
    if (error.response) {
      res.status(error.response.status).json({
        error: 'Server error',
        details: error.response.data
      });
    } else {
      res.status(503).json({
        error: 'Unable to connect to server',
        server_url: SERVER_URL
      });
    }
  }
});

// Start client API
app.listen(CLIENT_PORT, () => {
  console.log(`🚕 Mini Uber Client API running on http://localhost:${CLIENT_PORT}`);
  console.log(`📡 Client API endpoints:`);
  console.log(`   - POST http://localhost:${CLIENT_PORT}/api/client/ride-request`);
  console.log(`   - GET  http://localhost:${CLIENT_PORT}/api/client/rides/:user_id`);
  console.log(`   - GET  http://localhost:${CLIENT_PORT}/api/client/rides`);
  console.log(`🔗 Connects to server at: ${SERVER_URL}`);
});

module.exports = app;