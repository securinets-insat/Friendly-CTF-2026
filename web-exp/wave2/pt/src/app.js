const express = require('express');
const path = require('path');
const Database = require('better-sqlite3');
const PORT = process.env.PORT || 3000;

const app = express();
DB_PATH = process.env.DB_PATH || 'library.db';
const db = new Database(DB_PATH);
const BOOKS_DIR = path.join(__dirname, 'public', 'books');

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

db.exec(`
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT NOT NULL,
    filename TEXT NOT NULL
);
`);

db.exec(`
INSERT INTO books (title, author, description, filename) VALUES
    ('The Great Gatsby', 'F. Scott Fitzgerald', 'A novel set in the Roaring Twenties.', 'the-great-gatsby.pdf'),
    ('To Kill a Mockingbird', 'Harper Lee', 'A novel about racial injustice in the Deep South.', 'to-kill-a-mockingbird.pdf'),
    ('1984', 'George Orwell', 'A dystopian novel about totalitarianism.', '1984.pdf');
`);

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/books', (req, res) => {
    books = db.prepare('SELECT * FROM books').all();
    return res.json(books);
    
});

app.get('/books/:id', (req, res) => {
    const book = db.prepare('SELECT * FROM books WHERE id = ?').get(req.params.id);
    if (!book) {
        return res.status(404).json({ error: 'Book not found' });
    }
    return res.json(book);
});

app.post('/books/download', (req, res) => {
    const file = req.body.file;
    if (!file) {
        return res.status(400).json({ error: 'File parameter is required' });
    }
    const filePath = path.join(BOOKS_DIR, file);
    res.sendFile(filePath, (err) => {
        if (err) {
            console.error('Error sending file:', err);
            res.status(500).json({ error: 'Error sending file' });
        }
    });
});


app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});