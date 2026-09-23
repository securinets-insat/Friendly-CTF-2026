const express = require('express');
const { ObjectId } = require('mongodb');
const tokenGen = require('../lib/tokenGen');
const aes = require('../lib/aes');

const OBJECT_ID_RE = /^[0-9a-fA-F]{24}$/;

function isNonEmptyString(v, maxLen) {
  return typeof v === 'string' && v.length > 0 && v.length <= maxLen;
}

module.exports = function notesRoutes(db, requireAuth) {
  const router = express.Router();
  const notes = db.collection('notes');
  const sessions = db.collection('sessions');

  router.get('/', requireAuth, async (req, res) => {
    const list = await notes
      .find({ owner: req.user.username })
      .sort({ createdAt: -1 })
      .toArray();

    const out = list.map((n) => {
      if (!n.encrypted) {
        return { _id: n._id, encrypted: false, content: n.content, createdAt: n.createdAt };
      }
      const keyHex = tokenGen.generate(n._id, 32);
      const content = aes.decrypt(n.ciphertext, n.iv, n.authTag, keyHex);
      return { _id: n._id, encrypted: true, content, createdAt: n.createdAt };
    });

    res.json(out);
  });

  router.post('/', requireAuth, async (req, res) => {
    const { content } = req.body || {};
    const encrypt = req.body && req.body.encrypt === true;

    if (!isNonEmptyString(content, 20000)) {
      return res.status(400).json({ error: 'content required' });
    }

    const _id = new ObjectId();

    if (encrypt) {
      const keyHex = tokenGen.generate(_id, 32);
      const { ciphertext, iv, authTag } = aes.encrypt(content, keyHex);
      await notes.insertOne({
        _id, owner: req.user.username, encrypted: true,
        ciphertext, iv, authTag, createdAt: new Date(),
      });
    } else {
      await notes.insertOne({
        _id, owner: req.user.username, encrypted: false,
        content, createdAt: new Date(),
      });
    }

    res.status(201).json({ message: 'Note created' });
  });

  // Encrypted notes are readable by anyone who knows the id, unauthenticated
  // — the app's own reasoning being "it's already encrypted, so exposing the
  // ciphertext isn't a real access-control decision". Plaintext notes still
  // require the requester to be the owner. A verified owner always gets the
  // note decrypted, same as GET /notes.
  router.get('/:id', async (req, res) => {
    const { id } = req.params;
    if (!OBJECT_ID_RE.test(id)) {
      return res.status(400).json({ error: 'invalid note id' });
    }

    const note = await notes.findOne({ _id: new ObjectId(id) });
    if (!note) return res.status(404).json({ error: 'not found' });

    const token = req.cookies?.session;
    const session = token ? await sessions.findOne({ token }) : null;
    const isOwner = !!session && session.username === note.owner;

    if (!note.encrypted && !isOwner) {
      return res.status(403).json({ error: 'forbidden' });
    }

    if (note.encrypted && !isOwner) {
      return res.json({
        owner: note.owner,
        encrypted: true,
        ciphertext: note.ciphertext,
        iv: note.iv,
        authTag: note.authTag,
        createdAt: note.createdAt,
      });
    }

    const content = note.encrypted
      ? aes.decrypt(note.ciphertext, note.iv, note.authTag, tokenGen.generate(note._id, 32))
      : note.content;

    res.json({ owner: note.owner, encrypted: note.encrypted, content, createdAt: note.createdAt });
  });

  return router;
};
