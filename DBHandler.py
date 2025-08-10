import psycopg2
from psycopg2 import errors
from argon2 import PasswordHasher

class DBHandler:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="movielingolearndb",
            user="postgres",
            password="Nobel11Post?",
            host="localhost",
            port="5432"
        )
        self.cursor = self.connection.cursor()


    def close(self):
        # self.connection.commit() -> Maybe better to always close cursor and connection when commiting: so using this method each time to commit instead of having commit() in every method?
        self.cursor.close()
        self.connection.close()


    def setup_schema(self, schema_file):
        with open(schema_file, "r") as f:
            sql = f.read()
        sql_commands = [cmd.strip() for cmd in sql.split(';') if cmd.strip()]
        for command in sql_commands:
            self.cursor.execute(command)
        self.connection.commit()


    def add_movie(self, title):
        sql = "INSERT INTO movies (title) VALUES(%s)"
        self.cursor.execute(sql, (title,))
        self.connection.commit()


    def add_subtitles(self, movie_id, language, filepath):
        count = 0
        with open(filepath, "r", encoding="utf-8") as file:
            lines_list = file.read().split("\n\n")
            for block in lines_list:
                count += 1
                parts = block.strip().split("\n")
                if len(parts) >= 3:
                    text_part = parts[2:]
                    text = " ".join(text_part).strip()
                    sql = "INSERT INTO subtitles VALUES(%s, %s, %s, %s)"
                    self.cursor.execute(sql, (movie_id, count, language, text))
            self.connection.commit()


    def add_user(self, username, password):
        try:
            ph = PasswordHasher()
            hashed_pwd = ph.hash(password)
            sql = "INSERT INTO users (username, password) VALUES(%s, %s)"
            self.cursor.execute(sql, (username, hashed_pwd))
            self.connection.commit()
        except Exception as e:
            print("Couldn't add user to database")
            print(e)


# Is it better to manipulate webpage directly from method or from server.py's do_post where method is called?
    def login(self, username, password):
        sql = "SELECT password FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        result = self.cursor.fetchone()
        if result == None:  # No user with that username
            return 0
        
        stored_hash = result[0]
        ph = PasswordHasher
        try:
            ph.verify(stored_hash, password)
            return 1  # Password match
        except Exception as e:
            return -1  #Password did not match    


    def get_current_scene(self, user, movie_id):
        sql = "SELECT current_scene FROM user_scene_tracking WHERE username = %s AND movie_id = %s"
        self.cursor.execute(sql, (user, movie_id))
        return self.cursor.fetchone()

    def new_user_movie(self, user, movie_id):
        sql = "INSERT INTO user_scene_tracking (username, movie_id) VALUES(%s, %s)"
        self.cursor.execute(sql, (user, movie_id))
        self.connection.commit()

    def update_scene_count(self, user, movie_id, new_count):
        sql = "UPDATE user_scene_tracking SET current_scene = %s WHERE username = %s AND movie_id = %s"
        self.cursor.execute(sql, (new_count, user, movie_id))
        self.connection.commit()
