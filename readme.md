# PDF Notes

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

## Getting Started

Those are all you need to have:

- Docker Engine: be sure to enable SVM or Intel Virtualization Technology in BIOS
- Python 3.7+: `pip install -r requirements.txt`, we only use `requests` and `docker` library
- Browser
- Internet Connection (may be optional in the future)

Getting Started (Windows):

1. Clone the repository
2. Build docker image under `docker/` with tag `thomasgaozx/survival:0.6`, (this step won't be necessary in the future, obviously)
3. Right click any pdf file, `Open With -> Other Software -> launch.bat`, you should see a debug console pop up (don't close!) along with your default browser with the target pdf file opened.
4. Click `tools` button at the RHS of the navigation bar, modify your custom settings and click "Apply Settings", and you are good to go!

It's very easy to get this program running on other platforms, mimicking `launch.bat`.
One can always `cd` to project root, `python -m client`, and paste in pdf URL.


## Directory Structure

This project has 3 components:

- `client`: a local server that handles I/O operation and communication with the container and browser
  - `config/*`: all of the configuration files, a new configuration file will be generated for each new pdf document.
  - `__main__.py`: local server script, contains basically everything.
  - `configuration.py`: global configuration read/write
  - `imageserver.py`: means to upload an image screenshot to a server of your choice (currently only default server works)
  - `pdftext.py`: text processing that can convert a completely garbage sequence of text into near perfect markdown format.
- `docker`: handles elementary pdf processing and parsing, to minimize manual package installations for end-user.
  This component is not part of the production package, as the pre-built image will be fetched from remote tag.
  - `img_service.py`: container server script, handles all the actual text/image cropping.
- `pdf.js`: a forked [pdf.js](https://mozilla.github.io/pdf.js/) that handles pdf presentation and custom user operations.
  - `custom_board.js`: some UI elements that's essential to this project.

Of the 3 components, only the files under `client/` are actively running on your machine.
The files under `docker/` and `pdf.js/` are just for source-disclosure purposes.

## To Do

Package all programs into a single executable that will:

- [x] Take a local file url as an input, and can be chosen as an application to open the file
- [x] Ask user which file to take notes to.
- [x] Launch the pdf.js viewer with the target url opened
- [x] create the docker container, start service and copy the pdf file over for processing
- [ ] (Optional) package into one executable

Major Features:

- [x] From local server, launch docker image from remote tag, copy local pdf file into container
- [x] Write segments to the target notes url.
- [x] Load preset image and document servers to store files to.
  Might need to integrate "markdown server migration tool."
  [x] Also needs an abstract API for uploading an image to server.
  Optional image naming might require further frontend support.
- [ ] Implementing Logging and exception handling (quit program should problems arise)
- [ ] Some sort of feedback when "Apply Settings" failed.
- [ ] Reset button for configuration.
- [ ] Push docker image, and change the main program to load from docker image

Front-end UX Improvement:

- [x] Enable run-time customization of symbol replacement
- [ ] Use Javascript to asynchronously ping  and reflect local and container server status
  Alternatively, use local server to ping webpage and reflect status?
- [ ] Hotkey settings, by default `4` for cropping text, `5` for cropping svg, `6` for cropping jpeg.
- [x] Enable run-time permission of in-line formula detection

Further Functionality:

- [ ] Auto conversion of web-page to pdf via pandoc, and work with the pdf
- [ ] Auto citation tool (tbd)
- [ ] Information density level segregation (maintaining 2 docs?)
- [ ] OCR standalone formula parsing: use Harvard NLP running in container.
- [ ] OCR for paragraphs, as an alternative for text parsing (trade off being power consumption and time, of course).
- [ ] Implement more ImageServers, including these image servers: github? google drive? imgur?
- [ ] Code block support (using normal/OCR to get the text, and format automatically like VSCode `Shift+Alt+F`)

## Known Issues/Limitations

- **IMPORTANT**: only one file can be opened by this program at any moment in time. If you want to switch file, close *both* the pdf.js browser tab *and* the debug console *before* opening another file. There's currently no plan to support multiple file-processing.
- `Enable Inline Math` checkbox doesn't really change anything, so inline math detection is always enabled.
- Lack of feedback when Apply Settings, such that when something goes wrong, the user wouldn't know unless he/she opens up the dev console.
- Inline math detection regex requires a lot more tuning and testing. A automated testing mechanism is desirable. For example, given a set of regex and a set of test cases, the mechanism should return a score on success/false-positive rate. Proofread the pasted text in your markdown document carefully for some ridiculous inline-math detections.
- Nested list structure cannot be interpreted properly by the text-processing algorithm (for obvious reasons). However, it's pretty quick to fix that in the notes document so it shouldn't be an issue.
- Subscript detection _will_ have false positives, sometimes it can really mess up the inline formulas. That's why there is option to disable subscript detection.
- Superscript cannot be detected at all.
- Inline math formatting fails utterly when you have complex math structures like $\sum_{i=1}^\infty$.
- Some unicode characters might be broken due to pdf shenanigans.
- Some pdf document are not parsable and gives gibberish. OCR feature _will_ be supported in future versions.
