var colorInput = document.querySelector('#button-color');
var viewButton = document.querySelector('#view-btn');
var saveColorButton = document.querySelector('#save-button-color');

function applyStyle(value) {
  var color = window.DOMPurify.sanitize(value);
  viewButton.setAttribute('style', 'background-color: ' + color);
  return color;
}

function saveButtonColor() {
  var color = applyStyle(colorInput.value);
  fetch(colorInput.dataset.saveUrl, {
    method: 'POST',
    body: new URLSearchParams({ color: color }),
    keepalive: true
  }).catch(function () {
    console.error('Could not save button color preference.');
  });
}

function openRandomNote() {
  var noteIds = JSON.parse(viewButton.dataset.noteIds || '[]');
  if (!noteIds.length) {
    window.alert('Create a note before viewing a random one.');
    return;
  }

  var randomId = noteIds[Math.floor(Math.random() * noteIds.length)];
  window.location.assign('/note/' + randomId);
}

if (colorInput && viewButton && saveColorButton && window.DOMPurify) {
  applyStyle(colorInput.value);
  saveColorButton.addEventListener('click', saveButtonColor);
  viewButton.addEventListener('click', openRandomNote);
}
