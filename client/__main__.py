"""
This script does all the heavy-lifting:

1. Start docker container (thomasgaozx/survival:version) to host pdf parsing service
2. Wait for service to go up
3. Send pdf file via http
4. Use some mechanism to notify this program that an image/text is ready on the docker web service
5. download image/text, process it and put into note document

Back notification mechanism:

1. Use requests and polling to download image/text?
   No, that'll either make requests too frequently, or have a massive delay between crop sent and text
   appended to notes. The former is annoying and the latter is unacceptable.
2. Use socket to transfer file?
   Can docker reach host ip? Requires more research on docker networking and ho to set host switch
   static ip, etc. host: connect to 0.0.0.0:10001, docker connect to 172.17.0.1?
   Actually, `ping host.docker.internal` does the trick
3. Receive notification from pdf.js? Seems like an easier approach, but I don't want to deal with
   javascript again!
4. Actually, use request to continue get from one endpoint with certain time out (30 seconds).
   Keep alive?

"""
import os
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from .pdftext import Markdown

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.bind((socket.gethostname(), 10001))
#sock.bind(("localhost", 10001))

#sock.connect(("host.docker.internal", 80))

def handle_cropped_text(txt):
    print(Markdown(txt).format_md())

def handle_cropped_svg(page, xywh):
    pass

def get_cropped_jpeg(page, xywh):
    pass

class ReqHandler(BaseHTTPRequestHandler):
    """
    Thanks to: https://stackoverflow.com/a/8480578
    """
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        status_code = 200
        content_len = int(self.headers.get('content-length',
            self.headers.get('Content-Length')))
        data = self.rfile.read(content_len).decode('utf-8')
        print("content length: {}\n data: {}".format(content_len, data))
        info = json.loads(data)

        endpoint = info['endpoint']
        del info['endpoint']
        resp = requests.post(os.path.join("http://localhost:10001/", endpoint), json=info)

        if resp.status_code != 200:
            status_code = resp.status_code
        elif endpoint == 'croptext':
            handle_cropped_text(resp.content.decode('utf-8'))
        elif endpoint == 'cropjpeg':
            with open('test.jpg', 'wb') as f:
                f.write(resp.content)
        elif endpoint == 'cropsvg':
            with open('test.svg', 'wb') as f:
                f.write(resp.content)

        #get_cropped_text(info['page'], info['xywh'])
        self.send_response(status_code, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

if __name__ == '__main__':
    _addr = ('localhost', 10002)
    httpd = HTTPServer(_addr, ReqHandler)
    httpd.serve_forever()
