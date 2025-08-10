from http.server import BaseHTTPRequestHandler, HTTPServer
import random
from urllib import parse
from urllib.parse import urlparse
import mimetypes
import json

from DBHandler import DBHandler

dbHandler = DBHandler()
dbHandler.setup_schema("schema.sql")

class Db:
    spanish_answers = ["Esto es", "Hola", "Buenos dias"]
    english_answers = ["This is", "Hi", "Good morning"]
    img_path = ["content/01_breaking_bad/images/1.jpg", "content/01_breaking_bad/images/1.jpg", "content/01_breaking_bad/images/1.jpg"]

    def find_by_id(self, id):
        if id - 1 >= len(self.spanish_answers):
            return None  # User has already completed all sentences in database
        return (self.spanish_answers[id - 1], self.english_answers[id - 1], self.img_path[id-1])
    
    def add_movie(path):
        file = open(path)

class Handler(BaseHTTPRequestHandler):

    db = Db()
    current_id = 1  # Counter to keep track of which id is used as parameter to db
    # if we reach [n-1] we need to reset or make other change, otherwie error if trying to access index.html after user has completed all sentences


    def do_GET(self):

        # ---------- Sends sentences to js ---------
        parsed_url = urlparse(self.path)  # seperates the path from any query-parameters (otherwise causes problems when submitting register-form???)
        if self.path == "/getdata":
            spanish, english, img_path = Handler.db.find_by_id(Handler.current_id)
            spanish_shuffled = [word + " " for word in spanish.split()]  # Adds a space after each word (even the last word!) so it can be compared to original sentence later
            random.shuffle(spanish_shuffled)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")  # Allows js to fetch
            self.end_headers()
            data = {
                "spanish_shuffled": spanish_shuffled,
                "english": english,
                "img_path": img_path
            }
            self.wfile.write(json.dumps(data).encode())
            return

        # ------------ Sends to htlm --------------------
        

        if self.path == "/":
            file_path = "./index.html"
        else:
            file_path = "." + parsed_url.path

        try:
            with open(file_path, "rb") as file:
                content = file.read()
                self.send_response(200)
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header("Content-type", mime_type or "application/octet-stream")
                self.end_headers()
                self.wfile.write(content)

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found.")  # Replaces client's page with this message


    def do_POST(self):
        
        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"))
        
        if self.path == "/":  # If the post is from the guess form
            user_answer = fields["user-answer"][0]

            right_answer, _, _ = Handler.db.find_by_id(Handler.current_id)
            if not right_answer.endswith(" "):
                right_answer += " "  # All words, incl the last word, gets an extra space when converted to shuffled list: we need to add a space here for comparison

            if user_answer == right_answer:
                Handler.current_id += 1  # Next time Db.find_by_id() is called new sentences will be collected

                if Handler.db.find_by_id(Handler.current_id) == None:  # if there are no more sentences in db
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"congrats")
                    return
                
                else:  # user guess is correct
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"correct")
                    return

            else:  # user guess is wrong
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"wrong")
        
        elif self.path == '/register': # if post is from register form
            reg_username = fields["reg-username"][0]
            reg_password = fields["reg-password"][0]

            dbHandler.add_user(reg_username, reg_password)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"success")
            return
        
        elif self.path == '/login': # if post is from login form
            username = fields["username"][0]
            password = fields["password"][0]

            result = dbHandler.login(username, password)
            if result > 0:  # password is correct
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"correct")

            elif result < 0:  # password is incorrect
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"incorrect")

            else:  # No user with that username exists
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"no such user")
            return


with HTTPServer(("", 8000), Handler) as server:
    server.serve_forever()
