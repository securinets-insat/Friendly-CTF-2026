const express = require('express');
const path = require('path');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const secret = crypto.randomBytes(24).toString('hex');
const ADMIN_TOKEN = jwt.sign({ role: 'admin' }, secret, { expiresIn: '72h' });
const FLAG = process.env.FLAG || 'Securinets{redacted}';
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/admin-token', (req, res) => {
    return res.json({ 'Authorization token' : ADMIN_TOKEN });
});

app.get('/admin', (req, res) => {
    let token=req.headers['authorization'];
    if ( !token ) {
        return res.status(400).send('token missing');
    }
    if ( token  && !token.startsWith('Bearer ') ) {
        return res.status(400).send('Invalid token format');
    }
    let jwtoken = token.split(' ')[1];
    try {
        const decoded = jwt.verify(jwtoken, secret, { algorithms: ['HS256'] });
        if (decoded.role === 'admin') {
                res.send(`Welcome, admin! Here is the flag: ${FLAG}`);
        } else {
                res.status(403).send('Access denied');
        }
    } catch (err) {
            res.status(403).send('Access denied');
    } 
    
    
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});