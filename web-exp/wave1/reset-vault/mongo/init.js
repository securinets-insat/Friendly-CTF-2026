db = db.getSiblingDB('resetvault');

db.createCollection('users');
db.users.createIndex({ username: 1 }, { unique: true });

db.createCollection('notes');
db.notes.createIndex({ owner: 1 });

db.createCollection('sessions');
db.sessions.createIndex({ token: 1 }, { unique: true });

db.createCollection('resets');
db.resets.createIndex({ username: 1, token: 1 });
db.resets.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// Admin account + the flag note are NOT seeded here — they're created by
// the Node app itself on first boot (see server.js), so the ObjectId
// random-bytes component matches the same process that later generates
// player session cookies. Seeding it here would use a different process's
// random bytes and silently break the exploit chain.
