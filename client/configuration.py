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

Global configuration setting
"""
import os
import json

def get_config_path(pdf_name, pdf_size):
    """ generates a tailored configuration file for a given pdf """
    return "./client/config/{}{}.json".format(pdf_name, pdf_size)

TEMPLATE_CONF_FILE = "./client/config/template.json"

class BaseConfiguration:
    """ Read-only """
    def __init__(self, config_path=TEMPLATE_CONF_FILE):
        with open(config_path, encoding="utf-8") as conf_file:
            _raw_config = json.load(conf_file)
        self.load_from_json_dict(_raw_config)

    def load_from_json_dict(self, _raw_dict):
        """loads the configuration specific"""
        self.bad_symbol_patch = _raw_dict.get("badsymbol")
        self.custom_patch = _raw_dict.get("patch")
        self.inline_detection = _raw_dict.get("formuladetect")
        self.auto_subscript = _raw_dict.get("autosubscript")
        self.subscript_vars = _raw_dict.get("subscriptvars")
        self.notes = _raw_dict.get("notes")
        self.imgserver = _raw_dict.get("imgserver")

class GlobalConfiguration (BaseConfiguration):
    def __init__(self, pdf_path):
        self.name = os.path.basename(pdf_path)
        self.size = os.path.getsize(pdf_path)
        self.config_path = get_config_path(self.name, self.size)

        if os.path.isfile(self.config_path):
            with open(self.config_path, encoding="utf-8") as conf_file:
                print(self.config_path)
                _raw_config = json.load(conf_file)
            self.load_from_json_dict(_raw_config)
        else:
            super().__init__() # use template
            self.save_settings()

    def save_settings(self):
        with open(self.config_path, 'w+', encoding="utf-8") as conf_file:
            json.dump(self.dump_json_dict(), conf_file)

    def dump_json_dict(self):
        return {
            "badsymbol" : self.bad_symbol_patch,
            "patch" : self.custom_patch,
            "formuladetect" : self.inline_detection,
            "autosubscript" : self.auto_subscript,
            "subscriptvars" : self.subscript_vars,
            "notes" : self.notes,
            "imgserver" : self.imgserver
        }
