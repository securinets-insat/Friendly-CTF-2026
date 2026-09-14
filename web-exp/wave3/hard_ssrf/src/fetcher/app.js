const express = require('express');
const axios = require('axios');
const path = require('path');
const dns = require('dns').promises;
const { URL } = require('url');
const ipaddr = require('ipaddr.js');
const { setTimeout } = require('timers/promises');
const PORT=process.env.PORT || 3000;

const app = express();

async function isSafeUrl(urlString) {
  try {
    const url = new URL(urlString);
    const hostname = url.hostname;
    console.log(`Checking safety for URL: ${urlString}, Hostname: ${hostname}`);
    const addresses = await dns.lookup(hostname, { all: true });
    for (const addr of addresses) {
      const ip = ipaddr.parse(addr.address);
      if (ip.range() === 'loopback' || ip.range() === 'private' || ip.range() === 'linkLocal' ) {   
        return false;
      }
    }
    return true;
  } catch (error) {
    console.error('Error parsing URL:', error.message);
    return false;
  }
}

async function fetchUrl(url) {
  try {
    if (!await isSafeUrl(url)) {
      throw new Error('Access to this host is blocked');
    }

    let check;
    try {
      console.log(`Performing HEAD request to: ${url}`);
      check = await axios.head(url, {
        timeout: 5000,
        validateStatus: (status) => status >= 200 && status < 400
      });
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        console.warn('HEAD request timed out, trying GET after delay...');
        // HEAD timed out — try going straight for the GET after a delay
        await setTimeout(2000);
        const response = await axios.get(url);
        if (response.data) {
          return response.data;
        }
        throw new Error('GET after timeout returned no data');
      } else {
        throw new Error('error while checking URL: ' + error.message);
      }
    }

    await setTimeout(2000);
    if (check.status <500 ) {
      const response = await axios.get(url);
      return response.data;
    } else {
      throw new Error('not found or not accessible');
    }
  } catch (error) {
    console.error('Error fetching URL:', error.message);
    throw error;
  }
}

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
  fetchUrl(url)
    .then(data => {
      res.send(data);
    })
    .catch(error => {
      res.status(500).send(`Error fetching URL: ${error.message}`);
    });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});