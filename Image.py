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

        self.minx = 0
        self.maxx = 0
        self.miny = 0
        self.maxy = 0

    def __getitem__(self, item):
        """Accessing image data. Item should be two element list-like object of integers and is interpreted as (x,y)"""
        if self.__outside_boundaries(item):
            x = max(min(item[0], self.maxx), self.minx)
            y = max(min(item[1], self.maxy), self.miny)
            return self.image_data[y][x]

        return self.image_data[item[1] - self.miny][item[0] - self.minx]

    def __setitem__(self, key, value):
        """Setting image data. Key should be two element lit-like object of integers and is interpreted as (x,y)"""
        if self.__outside_boundaries(key):
            # Do nothing, when trying to set element outside the image
            warnings.warn("Trying to set element (x:" + str(value[0]) + ", y:" + str(value[1]) + ") outside the image.")
            return
        self.image_data[key[1] - self.miny][key[0] - self.minx] = value

    def __outside_boundaries(self, key):
        return key[0] < self.minx or key[0] > self.maxx or key[1] < self.miny or key[1] > self.maxy

    def set_emtpy_image(self, shape, time_stamp):
        self.image_data = np.zeros(shape, dtype=int)
        self.time_stamp = time_stamp

    def initialize_with_image(self, other):
        self.image_data = np.copy(other.image_data)
        self.time_stamp = other.time_stamp
        self.minx = other.minx
        self.maxx = other.maxx
        self.miny = other.miny
        self.maxy = other.maxy

    def initialize_with_zero(self, shape):
        self.image_data = np.zeros(shape)
        self.time_stamp = 0
        self.minx = -int(shape[1] / 2)
        self.maxx = shape[1] + self.minx - 1
        self.miny = -int(shape[0] / 2)
        self.maxy = shape[0] + self.miny - 1

    def is_initialized(self):
        return self.time_stamp is not None and self.image_data is not None

    def shape(self):
        return self.image_data.shape

    def load(self, path, time_stamp):
        # self.file = misc.imread(path)
        self.image_data = misc.face(True)
        self.image_data = skimage.transform.resize(self.image_data, (512, 384))
        # self.image_data = skimage.transform.resize(self.image_data, (128, 96))
        self.time_stamp = time_stamp

        self.minx = -int(self.image_data.shape[1] / 2)
        self.maxx = self.image_data.shape[1] + self.minx - 1
        self.miny = -int(self.image_data.shape[0] / 2)
        self.maxy = self.image_data.shape[0] + self.miny - 1

    def save(self, folder_path):
        if not self.is_initialized():
            raise RuntimeError("Cannot saved uninitialized image")

        if not os.path.exists(folder_path):
            raise RuntimeError("Folder does not exists: '" + folder_path + "'")

        name = os.path.join(folder_path,str(self.time_stamp) + ".png")
        misc.imsave(name, self.image_data)
