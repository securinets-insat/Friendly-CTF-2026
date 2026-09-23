const seedrandom = require('seedrandom');

// Shared "random string" helper used for session tokens, password-reset
// tokens, and note-encryption keys. Seeding with a MongoDB ObjectId instead
// of crypto.randomBytes is the one bug this whole app hangs off of.
function generate(seed, byteLength) {
  const rng = seedrandom(seed.toString());
  let out = '';
  for (let i = 0; i < byteLength * 2; i++) {
    out += Math.floor(rng() * 16).toString(16);
  }
  return out;
}

module.exports = { generate };
