import numpy as np
from scipy import signal
from scipy import ndimage
from image import Image
import os.path
import mrcfile as mrc


class Movie:

    def __init__(self):
        self.micrographs = []
        self.partitions_size = 5

    def add(self, img, data_check=True):
        if data_check:
            if any(m.time_stamp == img.time_stamp for m in self.micrographs):
                raise RuntimeError("Movie contains two micrographs with equal \
                                   time stamps.")

            if any(m.shape() != img.shape() for m in self.micrographs):
                raise RuntimeError("Movie contains micrographs with different \
                                   shapes.")

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
            m.image_data = self.correct_for_shift(m.image_data, y_shifts[i],
                                                  x_shifts[i])

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

    def partition(self, raw_data):
        """Returns partitioned micrographs i.e. each micrograph is divided into
        25 partitions. When it is not possible to divide axis into 5 equal
        partitions several first partitions are expanded by one item.
        :param raw_data list of micrographs [micrograph][y][x]
        :return [stack_index \in <0,24>][micrograph][y][x]"""
        partition_size = self.partitions_size

        # calculate where should the micrograph images be divided into
        # partitions along horizontal and vertical axis
        def size_to_splits(size):
            return [sum(size[:i]) for i in range(len(size))][1:]
        sizes = self.partitions_sizes(raw_data[0].shape)

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
        partitions_list = [[micro[iy][ix] for ix in range(partition_size)
                            for iy in range(partition_size)]
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
        psize = self.partitions_size
        raw_data = [m.image_data for m in self.micrographs]
        partitions = self.partition(raw_data)

        # calculate positions
        center_pos = []
        for it in range(len(raw_data)):
            last = [0, 0]
            for ip, p in enumerate(partitions):
                size_y = p[it].shape[0]
                size_x = p[it].shape[1]


                center_pos.append((last[0] + size_y // 2,
                                   last[1] + size_x // 2,
                                   self.micrographs[it].time_stamp))

                last[1] += size_x
                if (ip + 1) % psize == 0:  # in next iteration is a new line
                    last[1] = 0
                    last[0] += size_y

        # calculate shifts
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
        """Calculates by how much is template shifted in relation to the main
        (template is doing the shifting)"""
        template = template[::-1, ::-1]  # we are using convolution
        corr = signal.fftconvolve(main, template)
        y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
        # resulting array has size + 2 * size // 2 size and no movement means
        # that highest peak is at size // 2 coordinates (this works for odd
        # sizes, even sizes are inherently imprecise so TODO:)
        y = (corr.shape[0] // 2) - y
        x = (corr.shape[1] // 2) - x
        return y, x

    def load_compact_mrc(self, file_path, time_points):
        """Loads movie from mrc file. (All frames are saved in one mrc file)"""
        with mrc.open(file_path) as f:
            img_count = f.data.shape[2]
            split_axis = list(range(1, img_count))
            splitted = np.dsplit(f.data, split_axis)
            indiv_img = np.squeeze(splitted, axis=2)

            # add images into self
            if len(self.micrographs) != 0:  # already conatins data
                warning.warn("Loading mrc file data inro non-empty file.")
                self.micrographs = []

            if len(time_points) != len(indiv_img):
                raise ValueError("Lenght of time_points doesn't corresponds " +
                                 "to the number of images contained in file.")

            for img,t in zip(indiv_img, time_points):
                self.add(Image(time_stamp = t, img_data = img))


    def sum_images(self):
        """Sums all images"""
        return np.sum((m.image_data for m in self.micrographs), axis=0)

    def save_movie_mrc(self, file_path):
        """Saves the whole movie into mrc file without dose informations"""
        if len(self.micrographs) == 0:
            warning.warn("Trying to save movie without frames")
            return

        # merge images into one 3D one with float32 data format (float64 is not
        # compatible with mrc file format)
        res = np.dstack([i.image_data for i in self.micrographs])
        cp = res.astype(dtype=np.float32)

        with mrc.new(file_path + "movie.mrc", overwrite=True) as f:
            f.set_data(cp)

    def save_movie_starfile(self, folder_path, file_name):
        """Saves the whole movie into STAR format file defined in XMIPP
        (http://xmipp.cnb.csic.es/twiki/bin/view/Xmipp/FileFormats#Metadata_Files),
        where each image is individually saved into mrc file. Beside references
        to the images, the STAR file also contains time stamps for each image.
        _image and _time_stamp labels inside _data_movie_stack.
        :param folder_path: where to save the individual files
        :param file_name: how should be files named. STAR file will be
            "'name'.xmd" the image files will be imgxx_name.mrc, where xx is id
            of image eg. 01, 23, ...."""
        # save the images into mrc file
        names = [file_name + str(i).zfill(2) + ".mrc" for i in
                 range(len(self.micrographs))]
        for name, img in zip(names, self.micrographs):
            img.save_mrc(os.path.join(folder_path, name))

        # create the encapsulating STAR file
        with open(os.path.join(folder_path, file_name + ".xmd"), "w") as f:
            f.write("# XMIPP_STAR_1 *\n")
            f.write("#########################################################\
                    #################\n")
            f.write("# This file contains movie stack. Each _image item is name\
                    of a mrc file with one frame and ")
            f.write("_time is its timestamp\n")
            f.write("#########################################################\
                    #################\n")
            f.write("\n")
            f.write("data_movie_stack\n")
            f.write("loop_\n")
            f.write("  _image\n")
            f.write("  _time\n")

            for name, img in zip(names, self.micrographs):
                f.write("  " + name + "  " + str(img.time_stamp) + "\n")

    def save_sum(self, folder_path, ending = "_total"):
        img = Image()
        img.time_stamp = 0
        img.image_data = self.sum_images()
        img.save(folder_path, ending)

    @staticmethod
    def correct_for_shift(data, y_shift, x_shift):
        """Corrects for y_shift and x_shift. Meaning it shifts provided data by
        -y_shift and -x_shift"""
        if x_shift == 0 and y_shift == 0:
            return data
        return ndimage.interpolation.shift(data, (-y_shift, -x_shift), cval=0.0)
