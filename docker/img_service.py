import subprocess
import os
import re

from PIL import Image
from flask import Flask, send_file, request
#from flask_cors import CORS
import numpy as np

DEFAULT_DPI = 150
GARBAGE = "/tmp/garbage"
DIM_REGEX= re.compile(r'Page.+\d+.+size:[^\d]+(\d+)[^\d]+(\d+)[^a-z]+pts')

class PdfPage:
    def __init__(self, doc, page):
        self.doc = doc
        self.page = page
        self.pixel_height = None
        self.pixel_width = None
        self.point_height = None
        self.point_width = None

    def get_pixel_dimension(self, res=DEFAULT_DPI):
        """ returns (width, height) """
        if (self.pixel_height is not None):
            return
        page = self.page
        doc = self.doc
        pr = subprocess.call("pdftocairo -png -cropbox -singlefile -r {} -f {} -l {} {} {}".format(
            DEFAULT_DPI, page, page, doc, GARBAGE), shell=True, timeout=10)
        height, width, _ = np.array(Image.open(GARBAGE+".png")).shape
        self.pixel_height = height
        self.pixel_width = width
        return (width, height) # for debugging

    def get_pt_dimension(self):
        """ returns (width, height) """
        if (self.point_height is not None):
            return
        page = self.page
        page_info = subprocess.check_output("pdfinfo -f {} -l {} {}".format(
            page, page, self.doc), shell=True, timeout=10, text=True)
        _match = DIM_REGEX.search(page_info)
        width, height = int(_match.group(1)), int(_match.group(2))
        self.point_height = height
        self.point_width = width
        return (width, height)

    def crop_svg(self, x_pt, y_pt, w_pt, h_pt):
        """ output to garbage, that is /tmp/garbage """
        page = self.page
        #pdftocairo -svg -f 49 -l 49 -x 50 -y 364 -W 355 -H 138 -paperw 355 -paperh 138 test.pdf
        pr = subprocess.call("pdftocairo -svg -f {} -l {} -x {} -y {} -W {} -H {} -paperw {} -paperh {} {} {}".format(
            page, page, x_pt, y_pt, w_pt, h_pt, w_pt, h_pt, self.doc, GARBAGE+".svg"), shell=True, timeout=10)

    def crop_jpeg(self, x_pt, y_pt, w_pt, h_pt):
        """convert point to pixel"""
        page = self.page
        self.get_pixel_dimension()
        self.get_pt_dimension()
        x_ratio = self.pixel_width/self.point_width
        y_ratio = self.pixel_height/self.point_height
        pr = subprocess.call(
            "pdftocairo -jpeg -cropbox -singlefile -r {} -f {} -l {} -x {} -y {} -W {} -H {} {} {}".format(
                DEFAULT_DPI, page, page, int(x_pt*x_ratio), int(y_pt*y_ratio), int(w_pt*x_ratio),
                int(h_pt*y_ratio),self.doc, GARBAGE), shell=True, timeout=10)


    def crop_text(self, x_pt, y_pt, w_pt, h_pt):
        # For some really bizarre reason, the pdftotext uses mediabox instead of cropbox, and requires us
        # to input pixel coordinate (which makes no sense to me.) It easily messes up the coordinate you try
        # to select
        #
        # page = self.page
        # self.get_pixel_dimension()
        # self.get_pt_dimension()
        # x_ratio = self.pixel_width/self.point_width
        # y_ratio = self.pixel_height/self.point_height
        # pr = subprocess.call(
        #     "pdftotext -r {} -f {} -l {} -x {} -y {} -W {} -H {} -raw -layout -enc UTF-8 {} {}".format(
        #         DEFAULT_DPI, page, page, int(x_pt*x_ratio), int(y_pt*y_ratio), int(w_pt*x_ratio),
        #         int(h_pt*y_ratio), self.doc, GARBAGE + ".txt"), shell=True, timeout=10)

        """Plan B: and generally, convert pdf to pdf and then to text is a bad idea"""
        # crop to pdf without cropbox
        page = self.page
        pr = subprocess.call(
            "pdftocairo -pdf -f {} -l {} -x {} -y {} -W {} -H {} {} {}".format(page, page,
            x_pt, y_pt, w_pt, h_pt, self.doc, GARBAGE+".pdf"), shell=True, timeout=10)
        pr = subprocess.call(
            "pdftotext -raw -layout -enc UTF-8 {} {}".format(GARBAGE+".pdf", GARBAGE+".txt"),
            shell=True, timeout=10)


### Testing area

# print(PdfPage("test.pdf", 49).get_pt_dimension())
# print(PdfPage("test.pdf", 49).get_pixel_dimension())
# print(PdfPage("test.pdf", 49).crop_svg(50, 364, 355, 138))
# print(PdfPage("test.pdf", 49).crop_jpeg(50, 364, 355, 138))
# print(PdfPage("test.pdf", 49).crop_text(50, 364, 355, 138))
# print(PdfPage("test.pdf", 49).crop_jpeg(0, 0, 459, 666))

app = Flask(__name__)
pdf = "test.pdf"
#CORS(app)

### Working with pdf.js
@app.route('/status', methods=['GET'])
def helloworld():
    return "hello world"

@app.route('/imgtest', methods=['GET'])
def image_test():
    return send_file('/tmp/garbage.jpg', mimetype='image/jpeg')

@app.route('/croptext', methods=['POST'])
def service_text():
    req_json = request.json
    x,y,w,h = req_json['xywh']
    page = req_json['page']
    PdfPage(pdf, page).crop_text(x,y,w,h)
    return send_file(GARBAGE + '.txt', mimetype="text/plain")

@app.route('/cropjpeg', methods=['POST'])
def service_jpeg():
    """Need to trim the image, too"""
    req_json = request.json
    x,y,w,h = req_json['xywh']
    page = req_json['page']
    PdfPage(pdf, page).crop_jpeg(x,y,w,h)
    img = np.array(Image.open(GARBAGE+".jpg"))

    # image trimming algorithm: https://stackoverflow.com/a/14211727
    # might need to deal with opaque white (255) rather than transparent (0)
    img_bw = img.max(axis=2)
    img_bw[img_bw > 253] = 0
    non_empty_columns = np.where(img_bw.max(axis=0)>0)[0]
    non_empty_rows = np.where(img_bw.max(axis=1)>0)[0]
    cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

    trimmed_img = img[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]
    Image.fromarray(trimmed_img).save('/tmp/trimmed.jpg')

    return send_file('/tmp/trimmed.jpg', mimetype="	image/jpeg")

@app.route('/cropsvg', methods=['POST'])
def service_svg():
    req_json = request.json
    x,y,w,h = req_json['xywh']
    page = req_json['page']
    PdfPage(pdf, page).crop_svg(x,y,w,h)
    return send_file(GARBAGE+".svg")

@app.route('/croplatex', methods=['POST'])
def service_latex():
    """OCR: use harvard nlp to parse latex from jpeg"""
    raise NotImplementedError()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
