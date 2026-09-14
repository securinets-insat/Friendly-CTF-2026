const grid = document.querySelector('#book-grid');
const search = document.querySelector('#book-search');
const count = document.querySelector('#book-count');
const dialog = document.querySelector('#book-dialog');
const closeDialog = document.querySelector('.close-dialog');
const coverClasses = ['gatsby', 'mockingbird', 'nineteen'];
let books = [];

function coverClass(index) { return coverClasses[index % coverClasses.length]; }

function displayBooks(items) {
  count.textContent = `${items.length} ${items.length === 1 ? 'book' : 'books'}`;
  if (!items.length) {
    grid.innerHTML = '<p class="empty">No books found. Try another title or author.</p>';
    return;
  }
  grid.innerHTML = items.map((book, index) => `
    <button class="book-card" type="button" data-id="${book.id}" aria-label="View ${book.title}">
      <span class="book-cover ${coverClass(index)}">
        <span class="cover-type">Margin library</span>
        <span class="cover-title">${book.title}</span>
        <span class="cover-author">${book.author}</span>
      </span>
      <span class="book-meta"><h3>${book.title}</h3><p>${book.author}</p></span>
    </button>
  `).join('');
}

function openBook(book) {
  const index = books.findIndex(item => item.id === book.id);
  const dialogCover = document.querySelector('#dialog-cover');
  dialogCover.className = `dialog-cover book-cover ${coverClass(index)}`;
  dialogCover.innerHTML = `<span class="cover-type">Margin library</span><span class="cover-title">${book.title}</span><span class="cover-author">${book.author}</span>`;
  document.querySelector('#dialog-title').textContent = book.title;
  document.querySelector('#dialog-author').textContent = book.author;
  document.querySelector('#dialog-description').textContent = book.description;
  const download = document.querySelector('#dialog-download');
  download.href = '#';
  download.dataset.filename = book.filename;
  dialog.showModal();
}

grid.addEventListener('click', event => {
  const card = event.target.closest('.book-card');
  if (card) openBook(books.find(book => String(book.id) === card.dataset.id));
});
closeDialog.addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
document.querySelector('#dialog-download').addEventListener('click', async event => {
  event.preventDefault();
  const link = event.currentTarget;
  const originalText = link.innerHTML;
  link.textContent = 'Preparing download…';
  try {
    const response = await fetch('/books/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file: link.dataset.filename })
    });
    if (!response.ok) throw new Error('Download failed');
    const objectUrl = URL.createObjectURL(await response.blob());
    const download = document.createElement('a');
    download.href = objectUrl;
    download.download = link.dataset.filename;
    download.click();
    URL.revokeObjectURL(objectUrl);
  } catch {
    link.textContent = 'Could not download — try again';
    return;
  }
  link.innerHTML = originalText;
});
search.addEventListener('input', () => {
  const term = search.value.trim().toLowerCase();
  displayBooks(books.filter(book => `${book.title} ${book.author} ${book.description}`.toLowerCase().includes(term)));
});

fetch('/books')
  .then(response => response.ok ? response.json() : Promise.reject())
  .then(data => { books = data; displayBooks(books); })
  .catch(() => { grid.innerHTML = '<p class="empty">The library is unavailable right now. Please try again shortly.</p>'; });
