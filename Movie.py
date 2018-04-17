import numpy as np
from scipy import signal
from scipy import ndimage


class Movie:

    def __init__(self):
        self.micrographs = []
        self.size = 16

    def add(self, img, data_check=True):
        if data_check and any(m.time_stamp == img.time_stamp for m in self.micrographs):
            raise RuntimeError("Movie contains two micrographs with equal time stamps.")
        self.micrographs.append(img)

    def initialize(self, micrographs):
        # self.micrographs = micrographs
        self.micrographs = [np.zeros((self.size, self.size), dtype=int), np.zeros((self.size, self.size), dtype=int),
                            np.zeros((self.size, self.size), dtype=int)]
        self.micrographs[0][8][10] = 256
        self.micrographs[1][10][5] = 256
        self.micrographs[2][12][8] = 256

    def correct_global_shift(self):
        if not self.micrographs:
            return

        total_sum_img = np.sum(self.micrographs, axis=0)

        x_shifts = [0] * len(self.micrographs)
        y_shifts = [0] * len(self.micrographs)
        iteration = 0
        while iteration < 100:
            iteration += 1
            max_change = 0

            for i in range(len(self.micrographs)):
                m = self.micrographs[i]
                sum_without_current = total_sum_img - m

                # TODO: apply B-factor??

                x, y = self.calculate_shift(sum_without_current, m)
                x_shifts[i] += x
                y_shifts[i] += y

                self.micrographs[i] = self.correct_for_shift(m, y, x)
                total_sum_img = sum_without_current + self.micrographs[i]
                max_change = max(max_change, max(abs(x), abs(y)))

            if max_change < 0.2:
                break

        return x_shifts, y_shifts

    def correct_shifts(self, micro, shifts):
        res = np.zeros(micro[0].shape)
        for i in range(len(micro)):
            res += self.correct_for_shift(micro[i], shifts[i][1], shifts[i][0])
        return res

    def calculate_local_shifts(self, micrographs):
        lm = [np.hsplit(l, 5) for l in micrographs]
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
        return shifts

    def calculate_shift(self, main, template):
        """template is the one we want to move"""
        corr = signal.correlate2d(main, template, boundary='symm', mode='same')
        y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
        y -= (self.size / 2) - 1
        x -= (self.size / 2) - 1
        return x, y

    @staticmethod
    def correct_for_shift(data, y_shift, x_shift):
        if x_shift == 0 and y_shift == 0:
            return data
        return ndimage.interpolation.shift(data, (y_shift, x_shift))

