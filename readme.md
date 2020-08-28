# PDF Notes

## Why

Easy way to take notes from pdfs textbooks/journals.

- **Text cropping**: draw a rectangle and press enter, the text contained within the rectangle
  will be properly formatted into markdown format, and appended to your current note-taking
  document. By default it will not detect in-line formula, but you can enable it at run time.
  The appended text will reflect in real time if you are using vscode.
- **Image cropping**: draw a rectangle, it will auto trim the whitespace and render a **jpeg** file.
  It can also render an svg file.
  This file will be uploaded to your favorite image server, with its url appended to markdown.
  By default, it uses "LocalImageServer" that simply creates an `img/` directory in your repo root.
  If you want to use imgur or your own images servers, you may need to implement your own ImageServer
  class conforming to the BaseImageServer API standard.
- **Formula cropping** (coming soon): draw a rectangle around the stand-alone formula, and OCR will
  be applied to parse it into latex, and append to the document of your choosing.
- **Auto citation**: tentative feature. The local server has all the information to create a proper,
  paged citation for each paragraph/image/formula cropped, but how to present it in markdown without
  heavy-repetitions and poor-readability requires some clever design.

## Directory Structure

This project has 3 components:

- `client`: a local server that handles I/O operation and communication with the container and browser
  - `__main__.py`: local server script
  - `pdftext.py`: text processing that can convert a completely garbage sequence of text into near perfect markdown format.
- `docker`: handles elementary pdf processing and parsing, to minimize manual package installations for end-user.
  This component is not part of the production package, as the pre-built image will be fetched from remote tag.
  - `img_service.py`: container server script, handles all the actual text/image cropping.
- `pdf.js`: a forked [pdf.js](https://mozilla.github.io/pdf.js/) that handles pdf presentation and custom user operations.
  - `custom_board.js`: some UI elements that's essential to this project.

## To Do

Package all programs into a single executable that will: 

- Take a local file url as an input, and can be chosen as an application to open the file
- Ask user which file to take notes to.
- Launch the pdf.js viewer with the target url opened
- create the docker container, start service and copy the pdf file over for processing
- (Optional) package into one executable

Major Features:

- From local server, launch docker image from remote tag, copy local pdf file into container
- Write segments to the target notes url.
- Load preset image and document servers to store files to.
  Might need to integrate "markdown server migration tool."
  Also needs a abstract API for uploading an image to server.
  Optional image naming might require further frontend support.
- Implementing Logging and exception handling (quit program should problems arise)
- OCR standalone formula parsing: use Harvard NLP running in container.

Front-end UX Improvement:

- Enable run-time customization of symbol replacement
- Use Javascript to asynchronously ping  and reflect local and container server status
  Alternatively, use local server to ping webpage and reflect status?
- Hotkey settings, by default `4` for cropping text, `5` for cropping svg, `6` for cropping jpeg.
- Enable run-time permission of in-line formula detection

Further Functionality:

- Auto conversion of web-page to pdf via pandoc, and work with the pdf
- Auto citation tool (tbd)
- Information density level segregation (maintaining 2 docs?)
