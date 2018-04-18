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
        micrographs_raw_data[0][8][10] = 256
        micrographs_raw_data[1][10][5] = 256
        micrographs_raw_data[2][12][8] = 256
        self.micrographs = [Image() for i in micrographs_raw_data]
        for i in range(len(self.micrographs)):
            self.micrographs[i].image_data = micrographs_raw_data[i]
            self.micrographs[i].time_stamp = i

    def correct_global_shift(self):
        if not self.micrographs:
            return

        raw_data = [m.image_data for m in self.micrographs]

        total_sum_img = np.sum(raw_data, axis=0)

        x_shifts = [0] * len(raw_data)
        y_shifts = [0] * len(raw_data)
        iteration = 0
        while iteration < 100:
            iteration += 1
            max_change = 0

            for i in range(len(raw_data)):
                m = raw_data[i]
                sum_without_current = total_sum_img - m

                # TODO: apply B-factor??

                x, y = self.calculate_shift(sum_without_current, m)
                x_shifts[i] += x
                y_shifts[i] += y

                raw_data[i] = self.correct_for_shift(m, y, x)
                total_sum_img = sum_without_current + raw_data[i]
                max_change = max(max_change, max(abs(x), abs(y)))

            if max_change < 0.2:
                break

        return x_shifts, y_shifts

    def calculate_local_shifts(self):
        """
        :return: ([(x,y,t)], shifts_x, shifts_y)
        """
        raw_data = [m.image_data for m in self.micrographs]

        shape = self.micrographs[0].shape()
        height_step = shape[0] // 5
        width_step = shape[1] // 5
        positions = [(ix*width_step + width_step//2, iy*height_step + height_step//2, self.micrographs[i].time_stamp)
                     for iy in range(5) for ix in range(5) for i in range(len(self.micrographs))]

        lm = [np.hsplit(l, 5) for l in raw_data]
        partitions_list = []
        for m in lm:
            partitions_list.append([np.vsplit(l, 5) for l in m])

        reindexed = []  # new indexing [patch_stack][row_of_patch][col_of_patch]
        for x in range(5):
            for y in range(5):
                sub = []
                for m in range(len(partitions_list)):
                    sub.append(partitions_list[m][x][y])
                reindexed.append(sub)

        shifts = [self.calculate_shift(stack) for stack in reindexed]

        s = zip(*shifts)
        shifts_x = s[0]
        shifts_y = s[1]
        return positions, shifts_x, shifts_y

    def calculate_shift(self, main, template):
        """template is the one we want to move"""
        corr = signal.correlate2d(main, template, boundary='symm', mode='same')
        y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
        y -= (self.size / 2) - 1  # TODO: ???
        x -= (self.size / 2) - 1
        return x, y

    def sum_images(self):
        res_sum = np.zeros(self.micrographs[0].shape())
        for m in self.micrographs:
            res_sum += m
        return res_sum

    def save_sum(self, folder_path):
        img = Image()
        img.time_stamp = 0
        img.image_data = self.sum_images()
        img.save(folder_path, "_total")

    @staticmethod
    def correct_for_shift(data, y_shift, x_shift):
        if x_shift == 0 and y_shift == 0:
            return data
        return ndimage.interpolation.shift(data, (y_shift, x_shift))

