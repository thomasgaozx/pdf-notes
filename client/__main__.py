"""
Copyright (C) 2020 Thomas Gao <thomasgaozx@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
======================================================================

Main Script:

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
import io
import requests
import tarfile
import json
import uuid
import docker
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from .pdftext import Markdown
from .configuration import GlobalConfiguration
from .imageserver import img_server_from_config

def prompt_pdf_url():
    return str(input(
        "Drag and Drop pdf file here and press enter:\n")).strip('"\'')

_container = [None]
_CONTAINER_ID = 'pdfparser'
pdf_url = prompt_pdf_url() if len(sys.argv) == 1 else sys.argv[1]

def start_container():
    client = docker.from_env()
    client.containers.prune() # for a clean start
    container_list = client.containers.list(filters={'name':_CONTAINER_ID})
    if len(container_list) == 0:
        _container[0] = client.containers.run(
            "thomasgaozx/survival:0.6", name=_CONTAINER_ID,
            remove=True, auto_remove=True, ports={80:10001}, detach=True)
    elif container_list[0].status == 'running':
        _container[0] = container_list[0]

    # im-memory compression and upload pdf to container /root
    pdf_compressed = io.BytesIO()
    pdf_tar = tarfile.open(fileobj=pdf_compressed, mode='w')
    pdf_tar.add(pdf_url, arcname='test.pdf')
    pdf_tar.close()
    pdf_compressed.seek(0)
    if not _container[0].put_archive("/root/", pdf_compressed):
        raise Exception("Failed to transfer pdf to container")

conf = [ GlobalConfiguration(pdf_url) ]
imgserver = [ img_server_from_config(conf[0]) ]

def write_cropped_text(txt):
    with open(conf[0].notes, 'a+', encoding='utf-8') as f:
        f.write(Markdown(txt, conf[0]).format_md())

def write_img_ref(img_name, img_url):
    with open(conf[0].notes, 'a+', encoding='utf-8') as f:
        f.write("![{}]({})".format(img_name, img_url))
        f.write('\n\n') #gap line?

class ReqHandler(BaseHTTPRequestHandler):
    """
    Thanks to: https://stackoverflow.com/a/8480578
    """
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """serves the pdf file so pdf.js can open dynamically"""
        if os.path.normpath(self.path) == os.path.normpath("/file"):
            self.send_response(200, "ok")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('content-type', 'application/pdf')
            self.end_headers()
            with open(pdf_url, 'rb') as f:
                self.wfile.write(f.read())

        elif os.path.normpath(self.path) == os.path.normpath("/config"):
            self.send_response(200, "ok")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(json.dumps(conf[0].dump_json_dict()).encode('utf-8')) # does it work???

    def do_POST(self):
        status_code = 200
        content_len = int(self.headers.get('content-length',
            self.headers.get('Content-Length')))
        data = self.rfile.read(content_len).decode('utf-8')
        print("content length: {}\n data: {}".format(content_len, data))
        info = json.loads(data)

        if os.path.normpath(self.path) == os.path.normpath("/snapshot"):
            # localhost:10002/snapshot
            endpoint = info['endpoint']
            del info['endpoint']
            try:
                resp = requests.post(os.path.join("http://localhost:10001/", endpoint), json=info)
                if resp.status_code != 200:
                    status_code = resp.status_code
                elif endpoint == 'croptext':
                    write_cropped_text(resp.content.decode('utf-8'))
                elif endpoint == 'cropjpeg':
                    imgname = info.get("title", uuid.uuid4().hex)+".jpg"
                    imgname = imgname.replace(' ', '-')
                    imgurl = imgserver[0].upload_image(imgname, resp.content)
                    write_img_ref(imgname, imgurl)
                elif endpoint == 'cropsvg':
                    imgname = info.get("title", uuid.uuid4().hex)+".svg"
                    imgname = imgname.replace(' ', '-')
                    imgurl = imgserver[0].upload_image(imgname, resp.content)
                    write_img_ref(imgname, imgurl)
            except Exception:
                print("daemon ran into some problems")
                raise
        elif os.path.normpath(self.path) == os.path.normpath("/config"):
            conf[0].load_from_json_dict(info)
            conf[0].save_settings()
            imgserver[0] = img_server_from_config(conf[0])

        #get_cropped_text(info['page'], info['xywh'])
        self.send_response(status_code, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

if __name__ == '__main__':
    start_container()

    webbrowser.get().open("https://thomasgaozx.github.io/pdf.js.build/web/viewer.html")

    _addr = ('localhost', 10002)
    httpd = ThreadingHTTPServer(_addr, ReqHandler) #fallback: HTTPServer(_addr, ReqHandler)
    httpd.serve_forever()
