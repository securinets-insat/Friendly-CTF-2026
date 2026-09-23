const express = require('express');
const bcrypt = require('bcryptjs');
const { ObjectId } = require('mongodb');
const tokenGen = require('../lib/tokenGen');

function isNonEmptyString(v) {
  return typeof v === 'string' && v.length > 0 && v.length <= 256;
}

module.exports = function authRoutes(db) {
  const router = express.Router();
  const users = db.collection('users');
  const sessions = db.collection('sessions');

  async function requireAuth(req, res, next) {
    const token = req.cookies?.session;
    if (!token) return res.status(401).json({ error: 'Not logged in' });

    const session = await sessions.findOne({ token });
    if (!session) return res.status(401).json({ error: 'Invalid session' });

    req.user = { username: session.username };
    next();
  }

  router.post('/register', async (req, res) => {
    const { username, password } = req.body || {};
    if (!isNonEmptyString(username) || !isNonEmptyString(password)) {
      return res.status(400).json({ error: 'username and password required' });
    }

    const existing = await users.findOne({ username });
    if (existing) return res.status(409).json({ error: 'Username taken' });

    const passwordHash = bcrypt.hashSync(password, 10);
    await users.insertOne({ username, passwordHash, createdAt: new Date() });
    res.status(201).json({ message: 'Registered' });
  });

  router.post('/login', async (req, res) => {
    const { username, password } = req.body || {};
    if (!isNonEmptyString(username) || !isNonEmptyString(password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = await users.findOne({ username });
    if (!user || !bcrypt.compareSync(password, user.passwordHash)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Session token: seeded from a fresh ObjectId, same generator used for
    // password-reset tokens and note-encryption keys (see lib/tokenGen.js).
    const seed = new ObjectId();
    const token = tokenGen.generate(seed, 16);
    await sessions.insertOne({ token, username, createdAt: new Date() });

    res.cookie('session', token, { httpOnly: false, sameSite: 'lax' });
    res.json({ message: 'Logged in' });
  });

  router.post('/logout', async (req, res) => {
    const token = req.cookies?.session;
    if (token) await sessions.deleteOne({ token });
    res.clearCookie('session');
    res.json({ message: 'Logged out' });
  });

  return { router, requireAuth };
};
