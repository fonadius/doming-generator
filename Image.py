"""Allows operations on image"""
from scipy import misc
import numpy as np


class Image:

    def __init__(self):
        self.image_data = None
        self.time_stamp = None

    def set_emtpy_image(self, shape, time_stamp):
        self.image_data = np.zeros(shape, dtype=int)
        self.time_stamp = time_stamp

    def initialize_with_image(self, other):
        self.image_data = np.copy(other.image_data)
        self.time_stamp = other.time_stamp

    def is_initialized(self):
        return self.time_stamp is not None and self.image_data is not None

    def height(self):
        return self.image_data.shape[0]

    def width(self):
        return self.image_data.shape[1]

    def load(self, path, time_stamp):
        # self.file = misc.imread(path)
        self.image_data = misc.face(True)
        self.time_stamp = time_stamp

    def save(self, folder_path):
        if not self.is_initialized():
            raise RuntimeError("Cannot saved uninitialized image")

        name = folder_path + str(self.time_stamp) + ".png"  #TODO: proper path joining
        # misc.imsave(name, self.image_data, "png")
        # TODO: implement
