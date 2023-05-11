

CREATE TABLE IF NOT EXISTS users(
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL);

CREATE TABLE IF NOT EXISTS posts(
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
time integer NOT NULL,
user_id INTEGER,
FOREIGN KEY (user_id) REFERENCES users(id));


CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    post_id INTEGER,
    comment_text TEXT NOT NULL,
    time integer NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

ALTER TABLE posts ADD COLUMN img BLOB DEFAULT NULL;
