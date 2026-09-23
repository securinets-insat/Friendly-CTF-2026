const express = require('express');
const bcrypt = require('bcryptjs');
const { ObjectId } = require('mongodb');
const tokenGen = require('../lib/tokenGen');

const RESET_TTL_MS = 45 * 1000;

function isNonEmptyString(v, maxLen) {
  return typeof v === 'string' && v.length > 0 && v.length <= maxLen;
}

module.exports = function resetRoutes(db) {
  const router = express.Router();
  const users = db.collection('users');
  const resets = db.collection('resets');

  router.post('/forgot-password', async (req, res) => {
    const { username } = req.body || {};
    if (!isNonEmptyString(username, 256)) {
      return res.status(400).json({ error: 'username required' });
    }

    const user = await users.findOne({ username });
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Reset token: same generator as session tokens and note-encryption
    // keys (see lib/tokenGen.js) — seeded from a fresh ObjectId instead of
    // crypto.randomBytes.
    const seed = new ObjectId();
    const token = tokenGen.generate(seed, 10);
    const now = new Date();
    await resets.insertOne({
      username, token, createdAt: now,
      expiresAt: new Date(now.getTime() + RESET_TTL_MS),
    });

    res.json({ message: 'Reset email sent' });
  });

  router.post('/reset-password', async (req, res) => {
    const { username, token, newPassword } = req.body || {};
    if (
      !isNonEmptyString(username, 256) ||
      !isNonEmptyString(token, 64) ||
      !isNonEmptyString(newPassword, 256)
    ) {
      return res.status(400).json({ error: 'username, token and newPassword required' });
    }

    const record = await resets.findOne({
      username, token, expiresAt: { $gt: new Date() },
    });
    if (!record) return res.status(400).json({ error: 'Invalid or expired token' });

    const passwordHash = bcrypt.hashSync(newPassword, 10);
    await users.updateOne({ username }, { $set: { passwordHash } });
    await resets.deleteOne({ _id: record._id });

    res.json({ message: 'Password updated' });
  });

  return router;
};
