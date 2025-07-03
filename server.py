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
    
class Handler(BaseHTTPRequestHandler):

    current_id = 1  # Counter to keep track of which id is used as parameter to db
    db = Db()

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
                self.wfile.write(bytes("Congrats, you completed all sentences!", "utf8"))
                return
            
            else:  # user is redirected to the page again and new sentences are loaded
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return

        else:  # if user guessed wrong
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("Wrong!", "utf8"))
            # --> no new sentences, but reset screen so user can try again        


with HTTPServer(("", 8000), Handler) as server:
    server.serve_forever()

# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib import parse
# import mimetypes

# class handler(BaseHTTPRequestHandler):
    
#     # def do_GET(self):
#     #     db = Db()
#     #     file_path = "." + self.path
#     #     english_sentence, spanish_sentence = db.find_by_id(1)

#     #     try:
#     #         with open(file_path, "rb") as file:  # rb means read binary
#     #             content = file.read()
#     #             content2 = content.replace(b"english_sentence", english_sentence.encode("utf-8"))  # Both parameters need to be in bytes since content is binary

#     #             self.send_response(200)

#     #             # Guesses MIME-typ: the html file in general will be html, and the jpg-img will be jpg.
#     #             mime_type, _ = mimetypes.guess_type(file_path)
#     #             self.send_header("Content-type", mime_type or "application/octet-stream")  # send_header sends meta info to client
#     #             self.end_headers()  # appl... is default for binary files if guess can't be made
#     #             self.wfile.write(content2)
#     # except FileNotFoundError:
#     # self.send_response(404)
#     # self.end_headers()
#     # self.wfile.write(b"File not found.")  # Replaces client's page with this message

#     def do_GET(self):
#         file_path = "." + self.path
#         if self.path == "/":
#             file_path = "./index.html"  # servera startsidan om bara "/"

#         try:
#             with open(file_path, "rb") as file:
#                 content = file.read()
#                 self.send_response(200)
#                 mime_type, _ = mimetypes.guess_type(file_path)
#                 self.send_header("Content-type", mime_type or "application/octet-stream")
#                 self.end_headers()
#                 self.wfile.write(content)

#         except FileNotFoundError:
#             self.send_response(404)
#             self.end_headers()
#             self.wfile.write(b"File not found.")  # Replaces client's page with this message

#     # def do_GET(self):
#     #     self.send_response(200)
#     #     self.send_header("Content-type", "text/html")
#     #     self.end_headers()
#     #     file_name = self.path

#     #     file = open("." + file_name, "r")
#     #     content = file.read()
#     #     file.close()

#     #     message = content
#     #     self.wfile.write(bytes(message, "utf8"))

#     def do_POST(self):
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()

#         right_answer = "Buenos dias."

#         length = int(self.headers.get("content-length"))
#         field_data = self.rfile.read(length)
#         fields = parse.parse_qs(str(field_data, "UTF-8"))
#         user_answer = fields["user_answer"][0]

#         if user_answer == right_answer:
#             message = "correct answer"
#         else:
#             message = "Wrong!"

#         self.wfile.write(bytes(message, "utf8"))

# class Db:
#     spanish_answers = ["Hola", "Buenos dias"]
#     english_answers = ["Hi", "Good morning"]

#     def find_by_id(self, id):
#         return (self.spanish_answers[id - 1], self.english_answers[id - 1])
        

# with HTTPServer(("", 8000), handler) as server:
#     server.serve_forever()