const path = require('node:path');
const crypto = require('node:crypto');
const express = require('express');
const cookieParser = require('cookie-parser');
const bcrypt = require('bcryptjs');
const { MongoClient, ObjectId } = require('mongodb');

const authRoutes = require('./routes/auth');
const notesRoutes = require('./routes/notes');
const resetRoutes = require('./routes/reset');
const tokenGen = require('./lib/tokenGen');
const aes = require('./lib/aes');
const makeFlag = require('./lib/flag');

const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://mongo:27017/resetvault';

// Creates the admin account + its encrypted flag note using the app's own
// ObjectId/tokenGen/aes calls, so the "random" bytes match exactly what
// later gets leaked through a player's own session cookie. Seeding this
// from a separate process (e.g. the mongosh init script) would use a
// different set of random bytes and silently break the exploit chain.
async function seedAdmin(db) {
  const users = db.collection('users');
  const notes = db.collection('notes');

  const existingAdmin = await users.findOne({ username: 'admin' });
  if (existingAdmin) return;

  const adminPassword = crypto.randomBytes(24).toString('hex');
  const passwordHash = bcrypt.hashSync(adminPassword, 10);
  await users.insertOne({ username: 'admin', passwordHash, createdAt: new Date() });

  const flag = makeFlag();
  const _id = new ObjectId();
  const keyHex = tokenGen.generate(_id, 32);
  const { ciphertext, iv, authTag } = aes.encrypt(flag, keyHex);
  await notes.insertOne({
    _id, owner: 'admin', encrypted: true,
    ciphertext, iv, authTag, createdAt: new Date(),
  });
}

async function main() {
  const client = new MongoClient(MONGO_URI);
  await client.connect();
  const db = client.db();

  await seedAdmin(db);

  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '100kb' }));
  app.use(cookieParser());

  const { router: authRouter, requireAuth } = authRoutes(db);
  app.use('/', authRouter);
  app.use('/notes', notesRoutes(db, requireAuth));
  app.use('/', resetRoutes(db));

  app.get('/', (_req, res) => res.redirect('/login.html'));
  app.use(express.static(path.join(__dirname, 'public')));

  app.listen(PORT, () => {
    console.log(`Reset Vault listening on port ${PORT}`);
  });
}

main().catch((err) => {
  console.error('Fatal startup error:', err);
  process.exit(1);
});
