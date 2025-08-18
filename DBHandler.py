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
        self.cursor.close()
        self.connection.close()

    # What is best? try/except with commit/rollback in each method or exception handling in main using methods for commit and rollback?
    # def rollback_close(self): 
    #     self.connection.rollback()
    #     self.cursor.close()
    #     self.connection.close()


    def setup_schema(self, schema_file):
        with open(schema_file, "r") as f:
            sql = f.read()
        sql_commands = [cmd.strip() for cmd in sql.split(';') if cmd.strip()]
        for command in sql_commands:
            self.cursor.execute(command)
        self.connection.commit()


    def add_movie(self, title, poster_path):
        sql = "INSERT INTO movies (title, poster_path) VALUES(%s, %s)"
        self.cursor.execute(sql, (title, poster_path))
        self.connection.commit()


    def add_subtitles(self, movie_id, language, filepath):
        count = 0
        with open(filepath, "r", encoding="utf-8") as file:
            lines_list = file.read().split("\n\n")
            nr_of_blocks = len(lines_list) # Nr of subtitles lines
            for block in lines_list:
                count += 1
                parts = block.strip().split("\n")
                if len(parts) >= 3:
                    text_part = parts[2:]
                    text = " ".join(text_part).strip()
                    sql = "INSERT INTO subtitles VALUES(%s, %s, %s, %s)"
                    self.cursor.execute(sql, (movie_id, count, language, text))
            
            sql2 = "UPDATE movies SET nr_of_lines = %s WHERE movie_id = %s"
            self.cursor.execute(sql2, (nr_of_blocks, movie_id))
            self.connection.commit()


    def get_nr_of_lines(self, movie_id):
        sql = "SELECT nr_of_lines FROM movies WHERE movie_id = %s"
        self.cursor.execute(sql, (movie_id,))
        result = self.cursor.fetchone() # result is a tuple
        if result:
            return result[0]  # result is an int
        return None


    def add_user(self, username, password):
        try:
            ph = PasswordHasher()
            hashed_pwd = ph.hash(password)
            sql = "INSERT INTO users (username, password) VALUES(%s, %s)"
            self.cursor.execute(sql, (username, hashed_pwd))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("Couldn't add user to database")
            print(e)


    def login(self, username, password):
        sql = "SELECT password FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        result = self.cursor.fetchone()
        if result == None:  # No user with that username
            return 0
        
        stored_hash = result[0]
        ph = PasswordHasher()
        try:
            ph.verify(stored_hash, password)
            return 1  # Password match
        except Exception as e:
            self.connection.rollback()
            return -1  #Password did not match
         

    def new_user_movie(self, user, movie_id):
        sql = "INSERT INTO user_scene_tracking (username, movie_id) VALUES(%s, %s)"
        self.cursor.execute(sql, (user, movie_id))
        self.connection.commit()

    
    def get_subtitles(self, movie_id, movie_scene, language):
        sql = "SELECT subtitle FROM subtitles WHERE movie_id = %s AND movie_scene = %s AND language = %s"
        self.cursor.execute(sql, (movie_id, movie_scene, language))
        result = self.cursor.fetchone() # result is a tuple
        if result:
            return result[0]  # Return a string
        return None

        


    def get_current_scene(self, user, movie_id):
        sql = "SELECT current_scene FROM user_scene_tracking WHERE username = %s AND movie_id = %s"
        self.cursor.execute(sql, (user, movie_id))
        return self.cursor.fetchone()
    

    def update_scene_count(self, user, movie_id, new_count):
        sql = "UPDATE user_scene_tracking SET current_scene = %s WHERE username = %s AND movie_id = %s"
        self.cursor.execute(sql, (new_count, user, movie_id))
        self.connection.commit()
