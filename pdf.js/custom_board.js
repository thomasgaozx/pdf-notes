// Copyright (C) 2020 Thomas Gao <thomasgaozx@gmail.com>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
// ======================================================================
let _is_drawiing = false;
let _SEL__ID = "garbage__________________________";
let _SEL__CLS = "__niice_";
let _BAD_SYMBOL_PATCH__ID = "_____BAD_SYMBOLLL___"
let _CUS_PATCH_SETTINGS_ID_ = "_CUS_PATCH_SETTINGS_____"
let _ENABLE_INLINE_FORMULA_ID = "_____ENable_inLiNE_______"
let _AUTO_SUBSCRIPT________ID = "________ENABLE_SUB______"
let _SUBSCRIPT_VAR_________ID = "SUBSCRIPTABLE_______VAAR__"
let _NOTE_PATH____ID = "________notE_PAtH_";
let _IMG_SERVER____ID = "IMAGE_SERVER_PATH______"
let _IMG_FIGURE____ID = "IMAGE_FIGURE_______"
let _IDLE_STATE = 0;
let _WAIT_STATE = 1;
let _DONE_STATE = 2;
let _settings_changedd = false;

let _cur_state = _IDLE_STATE;
var _x00, _y00, _x11, _y11, _sel__context, _sel_board, _sel__scaling, _sel__endpnt;

window.onload = function() {
    load_toolbar_button("TXT", "croptext");
    load_toolbar_button("SVG", "cropsvg");
    load_toolbar_button("JPG", "cropjpeg");

    // open pdf file dynamically
    PDFViewerApplication.open('http://localhost:10002/file')

    // remove open file button
    open_file_button = document.getElementById("openFile")
    open_file_button.parentNode.removeChild(open_file_button)

    // move the settings icon to rightmost position
    _tools_button_ = document.getElementById("secondaryToolbarToggle")
    _tools_button_.parentNode.appendChild(_tools_button_)

    _load_custom_setting_board();
}

function _load_custom_setting_board() {
    // reset tools container
    _tools_menu = document.getElementById("secondaryToolbarButtonContainer")
    _tools_menu.innerHTML ="";

    // create bad-symbol patch:
    _bad_symbol_ = document.createElement('textarea');
    _bad_symbol_.name = 'bad_symbol';
    _bad_symbol_.id = _BAD_SYMBOL_PATCH__ID;
    _bad_symbol_.rows = 10;
    _bad_symbol_.cols= 40;

    // create user-customization form:
    _patch_field = document.createElement('textarea');
    _patch_field.name = 'user_patch';
    _patch_field.id = _CUS_PATCH_SETTINGS_ID_;
    _patch_field.rows = 10;
    _patch_field.cols= 40;

    // inline_formula checkbox
    _inline_formula_checkbox = document.createElement("INPUT");
    _inline_formula_checkbox.type = "checkbox";
    _inline_formula_checkbox.id = _ENABLE_INLINE_FORMULA_ID;

    // auto_subscription checkbox
    _auto_subscript_checkbox = document.createElement("INPUT");
    _auto_subscript_checkbox.type = "checkbox";
    _auto_subscript_checkbox.id = _AUTO_SUBSCRIPT________ID;

    // subscriptable variables
    _subscript_vars = document.createElement("INPUT");
    _subscript_vars.type = "text";
    _subscript_vars.id = _SUBSCRIPT_VAR_________ID;

    // note path
    _note_path = document.createElement("INPUT");
    _note_path.type = "text";
    _note_path.id = _NOTE_PATH____ID;

    // image server path
    _img_server = document.createElement("INPUT");
    _img_server.type = "text";
    _img_server.id = _IMG_SERVER____ID;

    // apply button
    _apply_custom_settings = document.createElement("button");
    _apply_custom_settings.innerText = "Apply Settings";
    _apply_custom_settings.setAttribute("onclick", "apply_settings_();");

    _tools_menu.appendChild(__LABEL__("Bad Symbol Patch"));
    _tools_menu.appendChild(_bad_symbol_);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("Custom Patch"));
    _tools_menu.appendChild(_patch_field);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("\nEnable Inline Formula Detection"));
    _tools_menu.appendChild(_inline_formula_checkbox);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("\nEnable Auto-Subscript"));
    _tools_menu.appendChild(_auto_subscript_checkbox);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("\nSubscriptable Variables"));
    _tools_menu.appendChild(_subscript_vars);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("\nSave To Path"));
    _tools_menu.appendChild(_note_path);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("\nImage Server URL"));
    _tools_menu.appendChild(_img_server);
    _tools_menu.appendChild(document.createElement("DIV"));
    _tools_menu.appendChild(__LABEL__("\nConfirmation"));
    _tools_menu.appendChild(_apply_custom_settings);

    // override max width
    max_width_override__ = document.createElement("STYLE");
    max_width_override__.innerText = "#secondaryToolbarButtonContainer { max-width: 500px !important; } ";
    document.head.appendChild(max_width_override__);

    // read current configuration
    var _loaded_config;
    try {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://localhost:10002/config", false);
        xhr.send(null);
        _loaded_config = JSON.parse(xhr.responseText);
        console.log(_loaded_config)
    } catch(err) {
        // TODO: feedback?
        console.log("badness")
        console.log(err.message)
    }
    _bad_symbol_.value = JSON.stringify(_loaded_config.badsymbol);
    _patch_field.value = JSON.stringify(_loaded_config.patch);
    _inline_formula_checkbox.checked = _loaded_config.formuladetect;
    _auto_subscript_checkbox.checked = _loaded_config.autosubscript;
    _subscript_vars.value = JSON.stringify(_loaded_config.subscriptvars);
    _note_path.value = _loaded_config.notes;
    _img_server.value = _loaded_config.imgserver;

}

function __LABEL__(l__name) {
    ___label = document.createElement('LABEL');
    ___label.innerText = l__name + ": \n";
    return ___label;
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

        if (_sel__endpnt === "cropsvg" || _sel__endpnt === "cropjpeg") {
            prompt_enter_title(e);
        }
    }
});

function prompt_enter_title(e) {
    var __figure_title = document.getElementById(_IMG_FIGURE____ID);
    if (__figure_title === null) {
        __figure_title = document.createElement("INPUT");
        __figure_title.type = "text";
        __figure_title.id = _IMG_FIGURE____ID;

        _sel_board.parentNode.appendChild(__figure_title);
    }
    __figure_title.setAttribute("style", `position: absolute; left: ${e.offsetX}px; top: ${e.offsetY}px`);
    __figure_title.focus();
}

window.addEventListener('keydown', e => {
    if (e.key == 'Enter') {
        if (_cur_state == _DONE_STATE) {
            console.log("x0,y0, x1,y1")
            console.log([_x00, _y00, _x11, _y11].map(e => e/_sel__scaling));

            ___x = Math.floor(_x00/_sel__scaling);
            ___y = Math.floor(_y00/_sel__scaling);
            ___w = Math.ceil(Math.abs(_x11-_x00)/_sel__scaling);
            ___h = Math.ceil(Math.abs(_y11-_y00)/_sel__scaling);

            post_info = {
                endpoint : _sel__endpnt,
                xywh : [___x, ___y, ___w, ___h],
                page : PDFViewerApplication.pdfViewer.currentPageNumber,
            }

            // patch title (if exist)
            var _img_fig_title = document.getElementById(_IMG_FIGURE____ID);
            if (_img_fig_title !== null) {
                if (_img_fig_title.value != "") {
                    post_info.title = _img_fig_title.value;
                }
                _img_fig_title.parentNode.removeChild(_img_fig_title);
            }

            // post request
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "http://localhost:10002/snapshot", false);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(post_info));

            _sel__context.clearRect(0, 0, _sel_board.width, _sel_board.height);
            document.getElementById(_SEL__ID).remove();

            //document.getElementById("sel_board_tool_").disabled=false;
            _cur_state = _IDLE_STATE;
        } else if (_cur_state == _WAIT_STATE) {
            console.log("Please select an area to operate.");
        }
    }
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

function apply_settings_() {
    var xhr = new XMLHttpRequest();
    // xhr.onreadystatechange = function () {
    //     if (xhr.readyState == 4 && xhr.status == 200) {
    //         // TODO: something
    //     }
    // }
    xhr.open("POST", "http://localhost:10002/config", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        badsymbol : JSON.parse(document.getElementById(_BAD_SYMBOL_PATCH__ID).value),
        patch : JSON.parse(document.getElementById(_CUS_PATCH_SETTINGS_ID_).value),
        formuladetect : document.getElementById(_ENABLE_INLINE_FORMULA_ID).checked,
        autosubscript : document.getElementById(_AUTO_SUBSCRIPT________ID).checked,
        subscriptvars : JSON.parse(document.getElementById(_SUBSCRIPT_VAR_________ID).value),
        notes : document.getElementById(_NOTE_PATH____ID).value,
        imgserver : document.getElementById(_IMG_SERVER____ID).value
    }));
}
