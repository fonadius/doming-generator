"""Allows operations on image"""
from scipy import misc
import numpy as np
import warnings
import skimage.transform


class Image:

    def __init__(self):
        self.image_data = None
        self.time_stamp = None

    def __getitem__(self, item):
        """Accessing image data. Item should be two element list-like object of integers and is interpreted as (x,y)"""
        # TODO: check for tuple, list or numpy
        if self.__outside_boundaries(item):
            item[0] = max(min(item[0], self.width() - 1), 0)
            item[1] = max(min(item[1], self.height() - 1), 0)
            return self.__getitem__(item)

        return self.image_data[item[1]][item[0]]

    def __setitem__(self, key, value):
        """Setting image data. Key should be two element lit-like object of integers and is interpreted as (x,y)"""
        # TODO: check for tuple, list or numpy
        if self.__outside_boundaries(key):
            # Do nothing, when trying to set element outside the image
            warnings.warn("Trying to set element (x:" + str(value[0]) + ", y:" + str(value[1]) + ") outside the image.")
            return
        self.image_data[key[1]][key[0]] = value

    def __outside_boundaries(self, key):
        return key[0] < 0 or key[0] >= self.width() or key[1] < 0 or key[1] >= self.height()

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

    def height(self):
        return self.image_data.shape[0]

    def width(self):
        return self.image_data.shape[1]

    def shape(self):
        return self.image_data.shape

    def load(self, path, time_stamp):
        # self.file = misc.imread(path)
        self.image_data = misc.face(True)
        self.image_data = skimage.transform.resize(self.image_data, (256, 192))
        self.time_stamp = time_stamp

    def save(self, folder_path):
        if not self.is_initialized():
            raise RuntimeError("Cannot saved uninitialized image")

        name = folder_path + str(self.time_stamp) + ".png"  #TODO: proper path joining
        misc.imsave(name, self.image_data)
