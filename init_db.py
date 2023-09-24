import sqlite3

connection = sqlite3.connect('database.db')


with open('schemas/videos.sql') as f:
    connection.executescript(f.read())

cursor = connection.cursor()

connection.commit()
connection.close()
