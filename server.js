const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage for rides
let rides = [];
let rideIdCounter = 1;

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'Server is running', 
    timestamp: new Date().toISOString() 
  });
});

// Submit ride request endpoint
app.post('/api/rides', (req, res) => {
  const { source_location, dest_location, user_id } = req.body;

  // Validate required fields
  if (!source_location || !dest_location || !user_id) {
    return res.status(400).json({ 
      error: 'Missing required fields: source_location, dest_location, user_id' 
    });
  }

  // Create ride object
  const newRide = {
    id: rideIdCounter++,
    user_id: parseInt(user_id),
    source_location,
    dest_location,
    status: 'pending',
    created_at: new Date().toISOString()
  };

  // Add to in-memory storage
  rides.push(newRide);

  // Print the required message and display data
  console.log('\n📝 We will store this data in Postgres now');
  console.log('==========================================');
  console.log('📊 Ride Request Data:');
  console.log('- Ride ID:', newRide.id);
  console.log('- User ID:', newRide.user_id);
  console.log('- Source Location:', newRide.source_location);
  console.log('- Destination Location:', newRide.dest_location);
  console.log('- Status:', newRide.status);
  console.log('- Timestamp:', newRide.created_at);
  console.log('==========================================\n');

  res.status(201).json({
    success: true,
    message: 'Ride request submitted successfully',
    data: newRide
  });
});

// Get all rides (for testing)
app.get('/api/rides', (req, res) => {
  res.json({
    success: true,
    data: rides
  });
});

// Get rides by user_id
app.get('/api/rides/user/:user_id', (req, res) => {
  const { user_id } = req.params;
  const userRides = rides.filter(ride => ride.user_id === parseInt(user_id));
  
  res.json({
    success: true,
    data: userRides
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚗 Mini Uber Server running on http://localhost:${PORT}`);
  console.log(`📡 API endpoints available at:`);
  console.log(`   - POST http://localhost:${PORT}/api/rides (submit ride request)`);
  console.log(`   - GET  http://localhost:${PORT}/api/rides (get all rides)`);
  console.log(`   - GET  http://localhost:${PORT}/api/rides/user/:user_id (get user rides)`);
});

module.exports = app;