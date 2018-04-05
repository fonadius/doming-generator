"""Allows operations on image"""
from scipy import misc
import numpy as np
import warnings
import skimage.transform
import os.path


class Image:

    def __init__(self):
        self.image_data = None
        self.time_stamp = None

    def __getitem__(self, item):
        """Accessing image data. Item should be two element list-like object of integers and is interpreted as (x,y)"""
        return self.get(item[0], item[1])

    def get(self, x, y):
        """Accessing image data"""
        x = max(min(x, self.width() - 1), 0)
        y = max(min(y, self.height() - 1), 0)
        return self.image_data[y][x]

    def __setitem__(self, key, value):
        """Setting image data. Key should be two element lit-like object of integers and is interpreted as (x,y)"""
        self.set(key[0], key[1], value)

    def set(self, x, y, value):
        """Setting image data."""
        if self.__outside_boundaries(x, y):
            # Do nothing, when trying to set element outside the image
            warnings.warn("Trying to set element (x:" + str(value[0]) + ", y:" + str(value[1]) + ") outside the image.")
            return

        self.image_data[y][x] = value

    def __outside_boundaries(self, x, y):
        return x < 0 or x >= self.width() or y < 0 or y >= self.height()

    def set_emtpy_image(self, shape, time_stamp):
        self.image_data = np.zeros(shape, dtype=int)
        self.time_stamp = time_stamp

    def initialize_with_image(self, other):
        self.image_data = np.copy(other.image_data)
        self.time_stamp = other.time_stamp

    def initialize_with_zero(self, shape):
        self.image_data = np.zeros(shape)
        self.time_stamp = 0

    def is_initialized(self):
        return self.time_stamp is not None and self.image_data is not None

    def shape(self):
        return self.image_data.shape

    def width(self):
        return self.image_data.shape[1]

    def height(self):
        return self.image_data.shape[0]

    def load(self, path, time_stamp):
        # self.file = misc.imread(path)
        self.image_data = misc.face(True)
        self.image_data = skimage.transform.resize(self.image_data, (384, 512))
        # self.image_data = skimage.transform.resize(self.image_data, (96, 128))
        self.time_stamp = time_stamp

    def save(self, folder_path):
        if not self.is_initialized():
            raise RuntimeError("Cannot saved uninitialized image")

        if not os.path.exists(folder_path):
            raise RuntimeError("Folder does not exists: '" + folder_path + "'")

        name = os.path.join(folder_path,str(self.time_stamp) + ".png")
        misc.imsave(name, self.image_data)
