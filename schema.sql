-------------------------------------------FOR sqlite3-------------------------------------------------------

--CREATE TABLE users (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    firstname TEXT NOT NULL, -- first name of the user
--    lastname TEXT NOT NULL, -- last name of the user
--    email TEXT NOT NULL UNIQUE, -- email field added, unique constraint to ensure no duplicate emails
--    password TEXT NOT NULL,
 --   admin BOOLEAN NOT NULL -- true for professor, false for students
--);

--CREATE TABLE presence (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    userid INTEGER NOT NULL, -- reference to users table
--    date DATE NOT NULL, -- date of attendance
--    scannedat DATETIME, -- time of QR code scan
--    FOREIGN KEY (userid) REFERENCES users (id)
--);

--CREATE TABLE temp_codes (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    code TEXT NOT NULL,
--    generated_at DATETIME NOT NULL
--);



---------------------------------------------FOR POSTGRES----------------------------------------------------------

CREATE TABLE users (
    id serial PRIMARY KEY,
    firstname TEXT NOT NULL, 
    lastname TEXT NOT NULL, 
    email TEXT NOT NULL UNIQUE, ls
    password TEXT NOT NULL,
    admin BOOLEAN NOT NULL 
);

CREATE TABLE presence (
    id serial PRIMARY KEY,
    userid INTEGER NOT NULL, 
    date DATE NOT NULL, 
    scannedat TIMESTAMP, 
    FOREIGN KEY (userid) REFERENCES users (id)
);

CREATE TABLE temp_codes (
    id serial PRIMARY KEY,
    code TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL
);

CREATE TABLE code_usage (
    id serial PRIMARY KEY,
    code_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (code_id) REFERENCES temp_codes (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (code_id, user_id)  -- Ensure each user can only use a specific code once
);
