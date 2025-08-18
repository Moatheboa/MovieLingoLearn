from http.server import BaseHTTPRequestHandler, HTTPServer
import random
from urllib import parse
from urllib.parse import urlparse
import mimetypes
import json
import html

from DBHandler import DBHandler

db_initializing = DBHandler()
db_initializing.setup_schema("schema.sql")
db_initializing.add_movie("Prison Break", "")
db_initializing.add_subtitles(1, "ES", "spa_sub.srt")
db_initializing.add_subtitles(1, "EN", "eng_sub.srt")
db_initializing.close()


class Handler(BaseHTTPRequestHandler):

    current_id = 1  # Counter to keep track of which id is used as parameter to db: Later this will be fetched from speci. user's table.
    # if we reach [n-1] we need to reset or make other change, otherwise error if trying to access index.html after user has completed all sentences

    def add_headers(self):
        """
    Adds headers for extra security to be used for do_GET and do_POST:
    - Access-Control-Allow-Origin for CORS -> change later from localhost to real domain
    - Content-Security-Policy to help protect against XSS
    """
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")  # Only allows pages from http://localhost:8000 to fetch data.
        self.send_header(  # Only resources from same domain as server, self, is allowed to execute.
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
        )
        self.end_headers()


    def do_GET(self):
        db_get = DBHandler()
        
        # ---------- Sends sentences to js ---------
        parsed_url = urlparse(self.path)  # seperates the path from any query-parameters (otherwise causes problems when submitting register-form???)
        if self.path == "/getdata":
            img_path = "content/01_breaking_bad/images/1.jpg"
            english_sub = db_get.get_subtitles(1, Handler.current_id, "EN")
            spanish_sub = db_get.get_subtitles(1, Handler.current_id, "ES")
            spanish_shuffled = [word + " " for word in spanish_sub.split()]  # List comprehension: Adds a space after each word (even the last word!) so it can be compared to original sentence later
            random.shuffle(spanish_shuffled)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.add_headers()
            data = {  # using html.escape to prevent xss-attacks when sending data to client
                "spanish_shuffled": [html.escape(word) for word in spanish_shuffled],  # escape() word by word as the methods is used for strings, not lists.
                "english_sub": html.escape(english_sub),
                "img_path": html.escape(img_path)
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
                self.send_header("Content-type", mime_type or "application/octet-stream")  # Content-type is set based on file extension (mime_type). If unknown, "application/octet-stream" is default
                self.add_headers()
                self.wfile.write(content)

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found.")  # Replaces client's page with this message

        db_get.close()


    def do_POST(self):
        db_post = DBHandler()

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"))
        
        if self.path == "/":  # If the post is from the guess form
            user_answer = fields["user-answer"][0]

            right_answer = db_post.get_subtitles(1, Handler.current_id, "ES")
            if not right_answer.endswith(" "):
                right_answer += " "  # All words, incl the last word, gets an extra space when converted to shuffled list: we need to add a space here for comparison

            if user_answer == right_answer:
                Handler.current_id += 1  # Next time Db.find_by_id() is called new sentences will be collected

                # if there are no more sentences in db for this movie
                if Handler.current_id > db_post.get_nr_of_lines(1): # 1 is for movie_id 1, for now it is not dynamic since we only have one movie
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")  # For security, use text/plain instead of text/html unless necessary to do otherwise
                    self.add_headers()
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
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"wrong")
        
        elif self.path == '/register': # if post is from register form
            reg_username = fields["reg-username"][0]
            reg_password = fields["reg-password"][0]

            db_post.add_user(reg_username, reg_password)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.add_headers()
            self.wfile.write(b"success")
            return
        
        elif self.path == '/login': # if post is from login form
            username = fields["username"][0]
            password = fields["password"][0]

            result = db_post.login(username, password)
            if result > 0:  # password is correct
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.add_headers()
                self.wfile.write(b"correct")

            elif result < 0:  # password is incorrect
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.add_headers()
                self.wfile.write(b"wrong")

            else:  # No user with that username exists
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.add_headers()
                self.wfile.write(b"no such user")
            return

        db_post.close()


with HTTPServer(("", 8000), Handler) as server:
    server.serve_forever()
