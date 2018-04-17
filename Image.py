"""Allows operations on image"""
from scipy import misc
from scipy import ndimage
import numpy as np
import warnings
import skimage.transform
import os.path


class Image:

    def __init__(self, path=None, time_stamp=None):
        self.image_data = None
        self.time_stamp = None

        if path and time_stamp:
            self.load(path, time_stamp)

    def __getitem__(self, item):
        """Accessing image data. Item should be two element list-like object of integers and is interpreted as (x,y)"""
        return self.get(item[0], item[1])

    def get(self, x, y):
        """Accessing image data"""
        if self.__outside_boundaries(x, y):
            return 0.0
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

    def initialize_with_image(self, other):
        self.image_data = np.copy(other.image_data)
        self.time_stamp = other.time_stamp

    def initialize_with_zero(self, shape):
        self.image_data = np.zeros(shape)
        self.time_stamp = 0

    def is_initialized(self):
        return self.time_stamp is not None and self.image_data is not None

    def correct_for_shift(self, x_shift, y_shift):
        self.image_data = ndimage.interpolation.shift(self.image_data, (-y_shift, -x_shift))

    def shape(self):
        return self.image_data.shape

    def width(self):
        return self.image_data.shape[1]

    def height(self):
        return self.image_data.shape[0]

    def load_dummy(self, time_stamp):
        self.image_data = misc.face(True)
        self.shrink()
        self.time_stamp = time_stamp

    def load(self, path, time_stamp):
        self.image_data = misc.imread(path)
        # self.smaller()
        self.time_stamp = time_stamp

    def shrink(self):
        # self.image_data = skimage.transform.resize(self.image_data, (384, 512))
        self.image_data = skimage.transform.resize(self.image_data, (192, 256))
        # self.image_data = skimage.transform.resize(self.image_data, (96, 128))

    def save(self, folder_path):
        if not self.is_initialized():
            raise RuntimeError("Cannot saved uninitialized image")

        if not os.path.exists(folder_path):
            raise RuntimeError("Folder does not exists: '" + folder_path + "'")

        name = os.path.join(folder_path,str(self.time_stamp) + ".png")
        misc.imsave(name, self.image_data)

    def saver(self, folder_path):
        if not self.is_initialized():
            raise RuntimeError("Cannot saved uninitialized image")

        if not os.path.exists(folder_path):
            raise RuntimeError("Folder does not exists: '" + folder_path + "'")

        name = os.path.join(folder_path,str(self.time_stamp) + "r.png")
        misc.imsave(name, self.image_data)