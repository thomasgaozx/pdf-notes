let _is_drawiing = false;
let _SEL__ID = "garbage__________________________";
let _SEL__CLS = "__niice_"
let _IDLE_STATE = 0;
let _WAIT_STATE = 1;
let _DONE_STATE = 2;

let _cur_state = _IDLE_STATE;
var _x00, _y00, _x11, _y11, _sel__context, _sel_board, _sel__scaling, _sel__endpnt;

window.onload = function() {
    load_toolbar_button("TXT", "croptext");
    load_toolbar_button("SVG", "cropsvg");
    load_toolbar_button("JPG", "cropjpeg");
}

function load_toolbar_button(__bt_txt, __endpt) {
    _sel_button_toolbar = document.createElement("button");
    _sel_button_toolbar.setAttribute("class", "toolbarButton");
    _sel_button_toolbar.setAttribute("title", "Select area to process");
    _sel_button_toolbar.setAttribute("onclick", `create_sel_board_overlay('${__endpt}')`);
    //_sel_button_toolbar.setAttribute("id", "sel_board_tool_");
    _sel_button_toolbar.innerText = __bt_txt;
    document.getElementById("toolbarViewerRight").appendChild(_sel_button_toolbar);
}

function create_sel_board_overlay(__endpt) {
    var _vport = PDFViewerApplication.pdfViewer._getCurrentVisiblePage().views[0].view.viewport;
    _sel__scaling = _vport.scale;
    _sel__endpnt = __endpt
    var _wdth = _vport.width;//Math.floor(_vport.width);
    var _heit = _vport.height; //Math.floor(_vport.height);
    _create_sel_board(PDFViewerApplication.pdfViewer.currentPageNumber, _wdth, _heit);
}

function _create_sel_board(_pg_num, __wdth, _ht) {
    _SEL__ID = "garbage__________________________" + String(_pg_num)
    _sel_board = document.createElement("canvas")
    _sel_board.setAttribute("width", __wdth)
    _sel_board.setAttribute("height", _ht)
    _sel_board.setAttribute("class", _SEL__CLS)
    _sel_board.setAttribute("id", _SEL__ID)
    _sel_board.setAttribute("style",
        "border: 2px solid red; position: absolute; left: 0; top: 0; cursor: crosshair;");
    document.querySelector(`div.page[data-page-number='${_pg_num}']`).appendChild(_sel_board)
    
    _sel__context = _sel_board.getContext("2d");
    _sel_board.addEventListener('mousedown', e => {
        _x00 = e.offsetX;
        _y00 = e.offsetY;
        _is_drawiing = true;
    });

    _sel_board.addEventListener('mousemove', e => {
        if (_is_drawiing === true) {
            drawRect(_sel__context, _x00, _y00, e.offsetX, e.offsetY);
        }
    });
    //document.getElementById("sel_board_tool_").disabled=true;
    _cur_state = _WAIT_STATE;
}
// Add the event listeners for mousedown, mousemove, and mouseup
window.addEventListener('mouseup', e => {
    if (_is_drawiing === true) {
        _x11 = e.offsetX;
        _y11 = e.offsetY;
        drawRect(_sel__context, _x00, _y00, e.offsetX, e.offsetY);
        _is_drawiing = false;
        _cur_state = _DONE_STATE;
    }
});

window.addEventListener('keydown', e => {
    if (e.key == 'Enter') {
        if (_cur_state == _DONE_STATE) {
            console.log("x0,y0, x1,y1")
            console.log([_x00, _y00, _x11, _y11].map(e => e/_sel__scaling));

            ___x = Math.floor(_x00/_sel__scaling);
            ___y = Math.floor(_y00/_sel__scaling);
            ___w = Math.ceil(Math.abs(_x11-_x00)/_sel__scaling);
            ___h = Math.ceil(Math.abs(_y11-_y00)/_sel__scaling);

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "http://localhost:10002", true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
                endpoint : _sel__endpnt,
                xywh : [___x, ___y, ___w, ___h],
                page : PDFViewerApplication.pdfViewer.currentPageNumber
            }));

            document.getElementById(_SEL__ID).remove();
            //document.getElementById("sel_board_tool_").disabled=false;
            _cur_state = _IDLE_STATE;
        } else if (_cur_state == _WAIT_STATE) {
            console.log("Please select an area to operate.");
        }
    }
    _sel__context.clearRect(0, 0, _sel_board.width, _sel_board.height);
})

function drawRect(_sel__context, _x00, _y00, _x11, _y11) {
    // draw rectangle:
    _sel__context.clearRect(0, 0, _sel_board.width, _sel_board.height);

    _sel__context.beginPath();
    _sel__context.strokeStyle = 'black';
    _sel__context.lineWidth = 1;
    if (_x00 < _x11) {
        if (_y00 < _y11) {
            _sel__context.rect(_x00, _y00, _x11-_x00, _y11-_y00);
        } else {
            _sel__context.rect(_x00, _y11, _x11-_x00, _y00 - _y11);
        }
    } else {
        if (_y00 < _y11) {
            _sel__context.rect(_x11, _y00, _x00-_x11, _y11-_y00);
        } else {
            _sel__context.rect(_x11, _y11, _x00-_x11, _y00-_y11);
        }
    }
    _sel__context.stroke();
}
