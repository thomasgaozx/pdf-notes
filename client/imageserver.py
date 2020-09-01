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

Image Server Factory, ways to upload image.
"""
import os
from abc import ABC, abstractmethod

class BaseImageServer(ABC):
    @abstractmethod
    def upload_image(self, img_name, img_str):
        """ returns url of the image uploaded 
        :img_name: e.g. test.jpg, test.svg
        :img_str:  resp.content (string)
        """
        raise NotImplementedError()

class DefaultImageServer(BaseImageServer):
    """ creates a img/ directory under note path"""
    def __init__(self, note_path):
        self.path = os.path.join(os.path.dirname(note_path), 'img')
        os.makedirs(self.path, exist_ok=True)
    
    def upload_image(self, img_name, img_str):
        img_url = os.path.join(self.path, img_name)
        if os.path.isfile(img_url):
            raise Exception("Image {} already exists!".format(img_url))
        with open(img_url, 'wb') as f:
            f.write(img_str)
        return os.path.join('.', 'img', img_name) 

class LocalImageServer(BaseImageServer):
    """ save file directly to path."""
    def __init__(self, abs_path):
        """ please provide an absolute path """
        self.path = abs_path
        os.makedirs(self.path, exist_ok=True)

    def upload_image(self, img_name, img_str):
        img_url = os.path.join(self.path, img_name)
        if os.path.isfile(img_url):
            raise Exception("Image {} already exists!".format(img_url))
        with open(img_url, 'wb') as f:
            f.write(img_str)
        return img_url #doesn't seem to work!

def img_server_from_config(conf):
    """
    conf is of BaseConfiguration
    The URL-thing is bugged
    """
    if conf.imgserver == "default":
        return DefaultImageServer(conf.notes)
    elif os.access(conf.imgserver, os.W_OK):
        return LocalImageServer(conf.imgserver)
    
    raise NotImplementedError(conf.imgserver)

