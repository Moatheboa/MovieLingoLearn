# How to structure everything: from where do we call functions, should cursor and connection be started and closed within each function or should the function take an open cursor as parameter? Should operations related to the same connection be a class?

import psycopg2
from psycopg2 import errors

def add_movie(cursor, title):
    sql = "INSERT INTO movies (title) VALUES(%s)" # %s is placeholder for sql-injection protection
    cursor.execute(sql, (title,)) # There need to be a parantes around and comma after title to make it into a tuple, which is what execute() demands as parameter for this.

def add_subtitles(cursor, movie_id, language, filepath):
    count = 0
    with open(filepath, "r", encoding="utf-8") as file:
        lines_list = file.read().split("\n\n")  # Separates content at empty line, each block becomming an element in the list.

        for block in lines_list:
            count += 1
            parts = block.strip().split("\n") # removes \n in start and end, then separates content at line break.
            # In case the file is broken somewhere, for example missing text, so that the block doesnt have +3 indexes, we will get indexoutofbounds.
            # How ever, if we do following if-solution we need to make sure we also skip the corresponding part in the other subtitles-file.
            if (len(parts) >= 3):  # Skips parts with less than 3 indexes to avoid error when calling index 2
                text_part = parts[2:]  # Skips the first two lines and takes the rest
                text = " ".join(text_part).strip()  # For now, I joined if there are two lines.
                sql = "INSERT INTO subtitles VALUES(%s, %s, %s, %s)"
                cursor.execute(sql, (movie_id, count, language, text))

connection = psycopg2.connect(
    dbname="movielingolearndb",
    user="postgres",
    password="Nobel11Post?",
    host="localhost",
    port="5432"
)

cursor = connection.cursor()

with open("schema.sql", "r") as f:
    sql = f.read()

sql_commands = [cmd.strip() for cmd in sql.split(';') if cmd.strip()]
#sql.split() seperates content of file into part, cmd, by every ; . strip() then removes every empty space. if cmd.strip() means if cmd contains anything (if cmd is empty it is considered false) then it is kept in the list.


for command in sql_commands:
    cursor.execute(command)
connection.commit()

try:
    add_movie(cursor, "Prison Break")
except psycopg2.Error as e:
    print("Something went wrong:", e)

try:
    add_subtitles(cursor, 1, 'EN', 'subtitles.srt')
except psycopg2.Error as e:
    print("Something went wrong:", e)

connection.commit()

cursor.close()
connection.close()
