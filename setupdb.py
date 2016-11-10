import sqlite3
import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

dbPath = 'data.db';

conn = sqlite3.connect(dbPath)

userTable = ('CREATE TABLE IF NOT EXISTS user( '
             '   id integer primary key autoincrement not null, '
             '   username varchar(255) unique not null, '
             '   password varchar(255) not null, '
             '   first_name varchar(255), '
             '   last_name varchar(255), '
             '   favorite_color varchar(255) '
             ');')

conn.execute(userTable)

authTable = ('CREATE TABLE IF NOT EXISTS auth_token( '
             '  id integer primary key autoincrement not null, '
             '  token varchar(255) unique not null, '
             '  user_id integer not null, '
             '  created timestamp not null, '
             '  expires timestamp not null, '
             '  FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE '
             ');')

conn.execute(authTable)

conn.commit()
conn.close()
