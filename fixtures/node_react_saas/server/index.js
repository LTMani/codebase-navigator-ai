const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth');
const projectRoutes = require('./routes/projects');
const billingRoutes = require('./routes/billing');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/billing', billingRoutes);

app.get('/health', (req, res) => {
    res.json({ status: 'ok', uptime: process.uptime() });
});

if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`SaaS Server running on port ${PORT}`);
    });
}

module.exports = app;
