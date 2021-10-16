DROP TABLE IF EXISTS thilab_users;

CREATE TABLE thilab_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  surname TEXT NOT NULL,
  dateOfBirth TEXT ,
  isMember INTEGER NOT NULL
);

