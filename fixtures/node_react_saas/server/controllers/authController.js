const jwt = require('jsonwebtoken');

class AuthController {
    async register(req, res) {
        const { email, password, companyName } = req.body;
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const token = jwt.sign({ email, companyName }, 'saas-jwt-secret', { expiresIn: '7d' });
        return res.status(201).json({ token, user: { email, companyName } });
    }

    async login(req, res) {
        const { email, password } = req.body;
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const token = jwt.sign({ email }, 'saas-jwt-secret', { expiresIn: '7d' });
        return res.json({ token, user: { email } });
    }

    async getProfile(req, res) {
        return res.json({ user: { email: 'admin@saasplatform.io', plan: 'enterprise' } });
    }
}

module.exports = new AuthController();
