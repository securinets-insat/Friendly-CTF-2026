const form = document.querySelector('#fetch-form');
const urlInput = document.querySelector('#url');
const submitButton = document.querySelector('#submit-button');
const message = document.querySelector('#form-message');
const result = document.querySelector('#result');
const resultContent = document.querySelector('#result-content');
const copyButton = document.querySelector('#copy-button');

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle('error', isError);
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.querySelector('span').textContent = isLoading
    ? 'Fetching…'
    : 'Fetch URL';
}

function formatResponse(body) {
  try {
    return JSON.stringify(JSON.parse(body), null, 2);
  } catch {
    return body;
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const url = urlInput.value.trim();

  try {
    new URL(url);
  } catch {
    result.hidden = true;
    setMessage('Enter a complete public URL, including https://', true);
    urlInput.focus();
    return;
  }

  setLoading(true);
  setMessage('Retrieving response…');
  result.hidden = true;

  try {
    const response = await fetch(`/fetch?url=${encodeURIComponent(url)}`);
    const body = await response.text();

    if (!response.ok) {
      throw new Error(body || 'Unable to fetch this URL.');
    }

    resultContent.textContent = formatResponse(body);
    result.hidden = false;
    setMessage('Response received.');
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (error) {
    setMessage(error.message || 'Unable to fetch this URL.', true);
  } finally {
    setLoading(false);
  }
});

copyButton.addEventListener('click', async () => {
  await navigator.clipboard.writeText(resultContent.textContent);
  copyButton.textContent = 'Copied';

  setTimeout(() => {
    copyButton.textContent = 'Copy';
  }, 1500);
});
