CREATE TABLE sqlite_sequence(name, seq);

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE categories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL
);

CREATE TABLE books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER UNIQUE,
    category_id INTEGER NULL,
    title TEXT NULL,
    description TEXT NULL,
    author TEXT NULL,
    date_published INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE files(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    book_id INTEGER UNIQUE,
    FOREIGN KEY (book_id) REFERENCES books(id)
    ON DELETE CASCADE
);

CREATE TABLE publisher(
    user_id INTEGER NOT NULL,
    first_name TEXT NULL,
    last_name TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE reader(
    user_id INTEGER NOT NULL,
    first_name TEXT NULL,
    last_name TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
    On DELETE CASCADE
);

CREATE TABLE read(
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    type TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE publish(
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id)
    ON DELETE CASCADE
);
