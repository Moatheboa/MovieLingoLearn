from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import mimetypes

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
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
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        db = Db()
        right_answer, _ = db.find_by_id(1)
        print(right_answer)

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"))
        user_answer = fields["user-answer"][0]
        print(user_answer)

        if user_answer == right_answer:
            message = "correct answer"
        else:
            message = "Wrong!"

        self.wfile.write(bytes(message, "utf8"))

class Db:
    spanish_answers = ["Esto debo ser obtenido del server", "Hola", "Buenos dias"]
    english_answers = ["This should be fetched from server", "Hi", "Good morning"]

    def find_by_id(self, id):
        return (self.spanish_answers[id - 1], self.english_answers[id - 1])
        

with HTTPServer(("", 8000), handler) as server:
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
