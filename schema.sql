CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL, -- first name of the user
    lastname TEXT NOT NULL, -- last name of the user
    email TEXT NOT NULL UNIQUE, -- email field added, unique constraint to ensure no duplicate emails
    password TEXT NOT NULL,
    admin BOOLEAN NOT NULL -- true for professor, false for students
);

CREATE TABLE presence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL, -- reference to users table
    date DATE NOT NULL, -- date of attendance
    scannedat DATETIME, -- time of QR code scan
    FOREIGN KEY (userid) REFERENCES users (id)
);
