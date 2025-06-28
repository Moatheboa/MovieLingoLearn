from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import mimetypes

class handler(BaseHTTPRequestHandler):
        
    def do_GET(self):
        file_path = "." + self.path

        try:
            with open(file_path, "rb") as file:  # rb means read binary
                content = file.read()
                self.send_response(200)

                # Guesses MIME-typ: the html file in general will be html, and the jpg-img will be jpg.
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header("Content-type", mime_type or "application/octet-stream")  # send_header sends meta info to client
                self.end_headers()  # appl... is default for binary files if guess can't be made

                self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found.")  # Replaces client's page with this message

    # def do_GET(self):
    #     self.send_response(200)
    #     self.send_header("Content-type", "text/html")
    #     self.end_headers()
    #     file_name = self.path

    #     file = open("." + file_name, "r")
    #     content = file.read()
    #     file.close()

    #     message = content
    #     self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        right_answer = "Buenos dias."

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"))
        user_answer = fields["user_answer"][0]

        if user_answer == right_answer:
            message = "correct answer"
        else:
            message = "Wrong!"

        self.wfile.write(bytes(message, "utf8"))


with HTTPServer(("", 8000), handler) as server:
    server.serve_forever()
