import numpy as np
from scipy import signal
from scipy import ndimage
from Image import Image


class Movie:

    def __init__(self):
        self.micrographs = []

    def add(self, img, data_check=True):
        if data_check
            if any(m.time_stamp == img.time_stamp for m in self.micrographs):
                raise RuntimeError("Movie contains two micrographs with equal time stamps.")

            if any(m.image_data.shape != img.shape for m in self.micrographs):
                raise RuntimeError("Movie contains micrographs with different shapes.")
                # TODO: maybe this should be possible?


        self.micrographs.append(img)

    @staticmethod
    def relative_shifts(raw_data):
        """Calculates shifts for list of two dimensional data with each other."""
        total_sum = np.sum(raw_data, axis=0)

        y_shifts = [0] * len(raw_data)
        x_shifts = [0] * len(raw_data)
        iteration = 0
        while iteration < 10:  # TODO: how many iterations?
            iteration += 1
            max_change = 0

            for i in range(len(raw_data)):
                current = raw_data[i]
                sum_without_current = total_sum - current

                # TODO: apply B-factor??

                y, x = Movie.one_on_one_shift(sum_without_current, current)
                y_shifts[i] += y
                x_shifts[i] += x

                raw_data[i] = Movie.correct_for_shift(current, y, x)
                total_sum = sum_without_current + raw_data[i]
                max_change = max(max_change, max(abs(x), abs(y)))

            if max_change < 0.2:  # TODO: what exact value?
                break

        return y_shifts, x_shifts

    def correct_global_shift(self):
        if not self.micrographs:
            return

        raw_data = [np.copy(m.image_data) for m in self.micrographs]

        y_shifts, x_shifts = self.relative_shifts(raw_data)

        for i, m in enumerate(self.micrographs):
            m.image_data = self.correct_for_shift(m.image_data, y_shifts[i], x_shifts[i])

    @staticmethod
    def partitions_sizes(shape, partition_axis_count=5):
        regular = (shape[0] // partition_axis_count,
                   shape[1] // partition_axis_count)
        sizes = ([regular[0]] * partition_axis_count,
                 [regular[1]] * partition_axis_count)

        def add(size, reminder):
            return [s + 1 if i < reminder else s for i, s in enumerate(size)]

        result = (add(sizes[0], shape[0] - regular[0] * partition_axis_count),
                  add(sizes[1], shape[1] - regular[1] * partition_axis_count))

        return result

    @staticmethod
    def partition(raw_data):
        """Returns partitioned micrographs i.e. each micrograph is divided into 25 partitions. When it is not possible
        to divide axis into 5 equal partitions several first partitions are expanded by one item.
        :param raw_data list of micrographs [micrograph][y][x]
        :return [stack_index \in <0,24>][micrograph][y][x]"""
        partition_size = 5

        # calculate where should the micrograph images be divided into partitions along horizontal and vertical axis
        def size_to_splits(size):
            return [sum(size[:i]) for i in range(len(size))][1:]
        sizes = Movie.partitions_sizes(raw_data[0].shape)

        vsplits = size_to_splits(sizes[0])
        hsplits = size_to_splits(sizes[1])

        # split all micrographs into partitions
        hsplited = [np.hsplit(l, hsplits) for l in raw_data]
        partitions_list = []
        for m in hsplited:
            partitions_list.append([np.vsplit(l, vsplits) for l in m])

        # reorder partitions
        # Now we have [micrograph][stack_index_y][stack_index_x][y][x]
        # and want [micrograph][stack_index \in <0,24>][y][x]
        partitions_list = [[micro[iy][ix] for ix in range(partition_size) for iy in range(partition_size)]
                           for micro in partitions_list]
        # we want [stack_index][micrograph][y][x]
        res = [[] for i in range(partition_size*partition_size)]
        for micro in partitions_list:
            for i, s in enumerate(micro):
                res[i].append(s)
        return res

    def calculate_local_shifts(self):
        """
        :return: ([(y,x,t)], [(shift_y, shift_x)])
        """
        raw_data = (m.image_data for m in self.micrographs)
        partitions = self.partition(raw_data)

        center_pos = [(sum(partitions), x, m.time_stamp)
                     for part_index in partitions for m in self.micrographs]

        data = [np.copy(m) for m in partitions]
        shifts = [self.relative_shifts(stack) for stack in data]
        # We have [stack][axis][time] and want [stack * time](shift_x, shift_y)
        time = len(shifts[0][0])
        time_stack = time * len(shifts)
        s_y = [None] * time_stack
        s_x = [None] * time_stack
        for ti in range(time):
            for si in range(len(shifts)):
                s_y[ti * len(shifts) + si] = shifts[si][0][ti]
                s_x[ti * len(shifts) + si] = shifts[si][1][ti]

        return center_pos, s_y, s_x

    @staticmethod
    def one_on_one_shift(main, template):
        """Calculates by how much is template shifted in relation to the main (template is doing the shifting)"""
        template = template[::-1, ::-1]  # we are using convolution
        corr = signal.fftconvolve(main, template)
        y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
        # resulting array has size + 2 * size // 2 size and no movement means that highest peak is at size // 2
        # coordinates (this works for odd sizes, even sizes are inherently imprecise so TODO:)
        y = (corr.shape[0] // 2) - y
        x = (corr.shape[1] // 2) - x
        return y, x

    def sum_images(self):
        """Sums all images"""
        return np.sum((m.image_data for m in self.micrographs), axis=0)  # // len(self.micrographs)

    def save_sum(self, folder_path):
        img = Image()
        img.time_stamp = 0
        img.image_data = self.sum_images()
        img.save(folder_path, "_total")

    @staticmethod
    def correct_for_shift(data, y_shift, x_shift):
        """Corrects for y_shift and x_shift. Meaning it shifts provided data by -y_shift and -x_shift"""
        if x_shift == 0 and y_shift == 0:
            return data
        return ndimage.interpolation.shift(data, (-y_shift, -x_shift), cval=0.0)
