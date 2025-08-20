from http.server import BaseHTTPRequestHandler, HTTPServer
import random
from urllib import parse
from urllib.parse import urlparse
import mimetypes
import json
import html
from http import cookies
import uuid

from DBHandler import DBHandler

db_initializing = DBHandler()
db_initializing.setup_schema("schema.sql")
db_initializing.add_movie("Prison Break", "")
db_initializing.add_subtitles(1, "ES", "spa_sub.srt")
db_initializing.add_subtitles(1, "EN", "eng_sub.srt")
db_initializing.close()

sessions = {}  # session_id -> username. To keep track of logined users


class Handler(BaseHTTPRequestHandler):

    def add_xss_headers(self):
        """ Adds headers with CSP to help protect against XSS """

        self.send_header(  # Only resources from same domain as server, self, is allowed to execute:
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
        )
        self.end_headers()

    def get_session_user(self):
        """Returns username if valid session exists, else None."""
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        cookie = cookies.SimpleCookie(cookie_header)
        session_id = cookie.get("session_id")
        if session_id and session_id.value in sessions:  # Checks if the key (UUID) from the cookie exists, and it's value (username), in variable sessions
            return sessions[session_id.value]
        return None


    def do_GET(self):

        if self.path == "/favicon.ico":  # To prevent error because there's no favicon yet.
            self.send_response(204)  # No content
            self.end_headers()
            return

        db_get = DBHandler()
        user = self.get_session_user()  # Checks if the user is logged in
        scene = db_get.get_current_scene(user, 1) or 1  # The scene nr that the user is to work on. If first time, scene is set to 1

        # ---------- Sends sentences to js ---------
        if self.path == "/getdata":
            if not user:  # if user is not logged in
                self.send_response(401)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            img_path = "content/01_breaking_bad/images/1.jpg"
            english_sub = db_get.get_subtitles(1, scene, "EN")
            spanish_sub = db_get.get_subtitles(1, scene, "ES")
            spanish_shuffled = [word + " " for word in spanish_sub.split()]
            random.shuffle(spanish_shuffled)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.add_xss_headers()
            data = {
                "spanish_shuffled": [html.escape(word) for word in spanish_shuffled],
                "english_sub": html.escape(english_sub),
                "img_path": html.escape(img_path)
            }
            self.wfile.write(json.dumps(data).encode())
            return

        # ------------ Serve HTML pages --------------------
        if self.path == "/":
            if not user:  # The page should only show if user is logged in
                self.send_response(302)  # Redirect to login
                self.send_header("Location", "/login.html")
                self.end_headers()
                return
            file_path = "./index.html"  # if user is logged in it may go to index.html
        else:
            parsed_url = urlparse(self.path)
            file_path = "." + parsed_url.path

        try:
            with open(file_path, "rb") as file:
                content = file.read()
                self.send_response(200)
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header("Content-type", mime_type or "application/octet-stream")
                self.add_xss_headers()
                self.wfile.write(content)

        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"File not found.")

        db_get.close()


    def do_POST(self):
        db_post = DBHandler()
        user = self.get_session_user()
        scene = db_post.get_current_scene(user, 1) or 1

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"))
        
        if self.path == "/":  # If the post is from the guess form
            user_answer = fields["user-answer"][0]
            right_answer = db_post.get_subtitles(1, scene, "ES")

            if not right_answer.endswith(" "):
                right_answer += " "  # All words, incl the last word, gets an extra space when converted to shuffled list: we need to add a space here for comparison

            if user_answer == right_answer:
                scene += 1  # 
                db_post.update_scene_count(user, 1, scene)  # updates the scene count for the user and that movie in the db
                scene_from_db = db_post.get_current_scene(user, 1)

                # if there are no more sentences in db for this movie
                if scene > db_post.get_nr_of_lines(1):  # 1 is for movie_id 1, for now it is not dynamic since we only have one movie
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")  # For security, use text/plain instead of text/html unless necessary to do otherwise
                    self.end_headers()
                    self.wfile.write(b"congrats")
                    return
                
                else:  # user guess is correct
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"correct")
                    return

            else:  # user guess is wrong
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"wrong")
        
        elif self.path == '/register': # if post is from register form
            reg_username = fields["reg-username"][0]
            reg_password = fields["reg-password"][0]

            res = db_post.add_user(reg_username, reg_password)
            if res > 0: 
                db_post.new_user_movie(reg_username, 1)  # For now, since we only have one movie, it is added here at registration
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"success")
                return
            elif res < 0:
                self.send_response(409)  # 409: conflict
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"user exists")
                return
            else:
                self.send_response(500)  # 500: internal server error
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"exception")
        
        elif self.path == '/login':  # if post is from login form
            username = fields["username"][0]
            password = fields["password"][0]

            result = db_post.login(username, password)
            if result > 0:  # password is correct
                session_id = str(uuid.uuid4())  # generates a unique random UUID and converts it to a string
                sessions[session_id] = username  # Adds a key-value pair to the dictionary sessions with name session_id and value username

                self.send_response(200)
                cookie = cookies.SimpleCookie()
                cookie["session_id"] = session_id  # Adds name = "session-id" to cookie and gives it the value that is to be found in variable session_id
                cookie["session_id"]["httponly"] = True  # Protects against JS-access (XSS)
                cookie["session_id"]["path"] = "/"       # Makes it valid on the whole webpage
                self.send_header("Set-Cookie", cookie.output(header="", sep=""))  # Sends the cookie, (header="", sep="") i neccessary for BaseHTTPRequestHandler.

                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"correct")

            elif result < 0:  # password is incorrect
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"wrong")

            else:  # No user with that username exists
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"no such user")
            return

        db_post.close()


with HTTPServer(("", 8000), Handler) as server:
    server.serve_forever()
