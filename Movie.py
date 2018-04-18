import numpy as np
from scipy import signal
from scipy import ndimage
from Image import Image


class Movie:

    def __init__(self):
        self.micrographs = []

    def add(self, img, data_check=True):
        if data_check and any(m.time_stamp == img.time_stamp for m in self.micrographs):
            raise RuntimeError("Movie contains two micrographs with equal time stamps.")

        self.micrographs.append(img)

    def dummy_initialize(self):
        size = 16
        micrographs_raw_data = [np.zeros((size, size), dtype=int), np.zeros((size, size), dtype=int),
                                np.zeros((size, size), dtype=int)]
        micrographs_raw_data[0][10][5] = 256
        micrographs_raw_data[1][10][5] = 256
        micrographs_raw_data[2][10][5] = 256
        self.micrographs = [Image() for i in micrographs_raw_data]
        for i in range(len(self.micrographs)):
            self.micrographs[i].image_data = micrographs_raw_data[i]
            self.micrographs[i].time_stamp = i

    def add_dummy_global_shift(self):
        for i, m in enumerate(self.micrographs):
            self.micrographs[i].image_data = self.correct_for_shift(m.image_data, i*2, 0)

    @staticmethod
    def relative_shifts(raw_data):
        """Calculates shifts for list of two dimensional data with each other."""
        total_sum = np.sum(raw_data, axis=0)

        x_shifts = [0] * len(raw_data)
        y_shifts = [0] * len(raw_data)
        iteration = 0
        while iteration < 2:  # TODO: how many iterations?
            iteration += 1
            max_change = 0

            for i in range(len(raw_data)):
                current = raw_data[i]
                sum_without_current = total_sum - current

                # TODO: apply B-factor??

                x, y = Movie.one_on_one_shift(sum_without_current, current)
                x_shifts[i] += x
                y_shifts[i] += y

                raw_data[i] = Movie.correct_for_shift(current, x, y)
                total_sum = sum_without_current + raw_data[i]
                max_change = max(max_change, max(abs(x), abs(y)))

            if max_change < 0.2:  # TODO: what exact value?
                break

        return x_shifts, y_shifts

    def correct_global_shift(self):
        if not self.micrographs:
            return

        raw_data = [np.copy(m.image_data) for m in self.micrographs]

        x_shifts, y_shifts = self.relative_shifts(raw_data)

        for i, m in enumerate(self.micrographs):
            m.image_data = self.correct_for_shift(m.image_data, x_shifts[i], y_shifts[i])

    @staticmethod
    def partition(raw_data):
        """Returns partitioned micrographs i.e. each micrograph is divided into 25 partitions.
        And then the result is [stack_index \n <0,24>][micrograph][y][x]"""
        size = 5
        equal_hsplit = raw_data[0].shape[1] // size
        hsplits = [equal_hsplit * i for i in range(1, size)]
        equal_vsplit = raw_data[0].shape[0] // size
        vsplits = [equal_vsplit * i for i in range(1, size)]
        # TODO: do all of this in some nice numpy way???

        hsplited = [np.hsplit(l, hsplits) for l in raw_data]
        partitions_list = []
        for m in hsplited:
            partitions_list.append([np.vsplit(l, vsplits) for l in m])

        # Now we have [micrograph][stack_index_y][stack_index_x][y][x]
        # and want [micrograph][stack_index \in <0,24>][y][x]
        partitions_list = [[micro[iy][ix] for ix in range(size) for iy in range(size)]
                           for micro in partitions_list]
        # we want [stack_index][micrograph][y][x]
        res = [[] for i in range(size*size)]
        for micro in partitions_list:
            for i, s in enumerate(micro):
                res[i].append(s)
        return res

    def calculate_local_shifts(self):
        """
        :return: ([(x,y,t)], [(shift_x, shift_y)])
        """
        raw_data = [m.image_data for m in self.micrographs]

        shape = self.micrographs[0].shape()
        height_step = shape[0] // 5
        width_step = shape[1] // 5
        positions = [
            (ix * width_step + width_step // 2, iy * height_step + height_step // 2, self.micrographs[i].time_stamp)
            for iy in range(5) for ix in range(5) for i in range(len(self.micrographs))]  # TODO: last values may little bit off

        reindexed = self.partition(raw_data)

        data = [np.copy(m) for m in reindexed]
        shifts = [self.relative_shifts(stack) for stack in data]
        # We have [stack][axis][time] and want [stack * time](shift_x, shift_y)
        time = len(shifts[0][0])
        time_stack = time * len(shifts)
        s_x = [None] * time_stack
        s_y = [None] * time_stack
        for ti in range(time):
            for si in range(len(shifts)):
                s_x[ti * len(shifts) + si] = shifts[si][0][ti]
                s_y[ti * len(shifts) + si] = shifts[si][1][ti]

        return positions, s_x, s_y

    @staticmethod
    def one_on_one_shift(main, template):
        """template is the one we want to move"""
        corr = signal.correlate2d(main, template, boundary='symm', mode='same')
        y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
        y -= (main.shape[0] / 2) - 1
        x -= (main.shape[1] / 2) - 1
        return x, y

    def sum_images(self):
        """Sums all images"""
        return np.sum((m.image_data for m in self.micrographs), axis=0)  # // len(self.micrographs)

    def save_sum(self, folder_path):
        img = Image()
        img.time_stamp = 0
        img.image_data = self.sum_images()
        img.save(folder_path, "_total")

    @staticmethod
    def correct_for_shift(data, x_shift, y_shift):
        if x_shift == 0 and y_shift == 0:
            return data
        res = np.empty(data.shape)
        ndimage.interpolation.shift(data, (y_shift, x_shift), res, cval=0)
        return res
