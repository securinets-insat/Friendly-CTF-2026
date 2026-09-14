const express = require('express');
const axios = require('axios');
const path = require('path');

const FLAG=process.env.FLAG || 'Securinets{redacted}';
const PORT=process.env.PORT || 3000;
const BLOCKED = ['localhost', '127.0.0.1', '0.0.0.0'];

const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/fetch', async (req, res) => {
  const url = req.query.url;
  if (!url) {
    return res.status(400).send('Missing url parameter');
  }
  for (const blocked of BLOCKED) {
    if (url.includes(blocked)) {
      return res.status(403).send('Access to this host is blocked');
    }
  }
  try {
    const response = await axios.get(url);
    res.json(response.data);
  } catch (error) {
    res.status(500).send('Error fetching URL');
    console.error('Error fetching URL:', error.message);
  }
});

app.get('/flag', (req, res) => {
    const ip=req.socket.remoteAddress;
    console.log(`Request from IP: ${ip}`);
    const allowed = ['127.0.0.1', '::1', '::ffff:127.0.0.1'];
    if (!allowed.includes(ip)) {
        return res.status(403).send('Access denied');
    }
    res.send(FLAG);
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});