const crypto = require('node:crypto');

module.exports = function makeFlag(configured = process.env.CHALLENGE_FLAG) {
  // CTFd validates the flag supplied for this team's instance. A local run
  // without an instancer still creates a fresh flag during initial seeding.
  return configured || `Securinets{${crypto.randomBytes(16).toString('hex')}}`;
};
