from http.server import BaseHTTPRequestHandler, HTTPServer
import random
from urllib import parse
import mimetypes
import json

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
        
    #def add_movie_to_db(movie_id, title):
        #connect to db
        #add row with id and title

    #def add_subtitles_to_db(movie_id, language, path):
        #read file and make list with sentences.for each line make a new row with same movie_id, same language, calculate scene_id and subtitle.


class Handler(BaseHTTPRequestHandler):

    db = Db()
    current_id = 1  # Counter to keep track of which id is used as parameter to db
    # if we reach [n-1] we need to reset or make other change, otherwie error if trying to access index.html after user has completed all sentences


    def do_GET(self):

        # ---------- Sends sentences to js ---------
        spanish, english, img_path = Handler.db.find_by_id(Handler.current_id)
        spanish_shuffled = [word + " " for word in spanish.split()]  # Adds a space after each word (even the last word!) so it can be compared to original sentence later
        random.shuffle(spanish_shuffled)

        if self.path == "/getdata":
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
        file_path = "." + self.path
        if self.path == "/":
            file_path = "./index.html"

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

        right_answer, _, _ = Handler.db.find_by_id(Handler.current_id)
        if not right_answer.endswith(" "):
            right_answer += " "  # All words, incl the last word, gets an extra space when converted to shuffled list: we need to add a space here for comparison

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"))
        user_answer = fields["user-answer"][0]

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


with HTTPServer(("", 8000), Handler) as server:
    server.serve_forever()
