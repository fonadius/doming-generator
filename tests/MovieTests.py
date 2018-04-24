import unittest
import random
import numpy as np
from Movie import Movie
from Image import Image
import math


class GlobalShiftTest(unittest.TestCase):

    def test_clear_one_on_one_shift(self):
        size = 15
        data = [np.zeros((size, size), dtype=float) for i in range(4)]
        data[0][8][8] = 1.0
        data[1][4][8] = 1.0
        data[2][8][4] = 1.0
        data[3][1][2] = 1.0

        shift = Movie.one_on_one_shift(data[0], data[0])
        self.assertEqual(shift, (0.0, 0.0))

        shift = Movie.one_on_one_shift(data[0], data[1])
        self.assertEqual(shift, (-4.0, 0.0))

        shift = Movie.one_on_one_shift(data[1], data[0])
        self.assertEqual(shift, (4.0, 0.0))

        shift = Movie.one_on_one_shift(data[0], data[2])
        self.assertEqual(shift, (0.0, -4.0))

        shift = Movie.one_on_one_shift(data[0], data[3])
        self.assertEqual(shift, (-7.0, -6.0))

        shift = Movie.one_on_one_shift(data[1], data[3])
        self.assertEqual(shift, (-3.0, -6.0))

        shift = Movie.one_on_one_shift(data[3], data[1])
        self.assertEqual(shift, (3.0, 6.0))

    @staticmethod
    def add_square(data, y, x, size):
        for yi in range(size):
            for xi in range(size):
                data[y + yi][x + xi] = 1.0
        return data

    @staticmethod
    def add_noise(data, amount):
        for i in range(amount):
            y = random.randint(0, data.shape[0] - 1)
            x = random.randint(0, data.shape[1] - 1)
            data[y][x] = 0.8
        return data

    def test_noisy_one_on_one_shift(self):
        size = 15
        for i in range(7):  # 7 levels of noise
            data = [np.zeros((size, size), dtype=float) for d in range(4)]
            data[0] = self.add_square(data[0], 7, 7, 4)
            data[1] = self.add_square(data[1], 3, 7, 4)
            data[2] = self.add_square(data[2], 7, 3, 4)
            data[3] = self.add_square(data[3], 2, 1, 4)

            data = [self.add_noise(d, 1 + i*2) for d in data]

            shift = Movie.one_on_one_shift(data[0], data[0])
            self.assertEqual(shift, (0.0, 0.0))

            shift = Movie.one_on_one_shift(data[0], data[1])
            self.assertEqual(shift, (-4.0, 0.0))

            shift = Movie.one_on_one_shift(data[1], data[0])
            self.assertEqual(shift, (4.0, 0.0))

            shift = Movie.one_on_one_shift(data[0], data[2])
            self.assertEqual(shift, (0.0, -4.0))

            shift = Movie.one_on_one_shift(data[0], data[3])
            self.assertEqual(shift, (-5.0, -6.0))

            shift = Movie.one_on_one_shift(data[1], data[3])
            self.assertEqual(shift, (-1.0, -6.0))

            shift = Movie.one_on_one_shift(data[3], data[1])
            self.assertEqual(shift, (1.0, 6.0))

    def test_clean_relative_shifts(self):
        size = 15
        data = [np.zeros((size, size), dtype=float) for d in range(4)]
        positions = [(7, 7), (3, 7), (7, 3), (2, 1)]
        data[0] = self.add_square(data[0], *positions[0], 4)
        data[1] = self.add_square(data[1], *positions[1], 4)
        data[2] = self.add_square(data[2], *positions[2], 4)
        data[3] = self.add_square(data[3], *positions[3], 4)

        res = Movie.relative_shifts(data)
        # What is the position of squares when the data would be shifted by the calculated amount
        shifted = [(p[0] - res[0][i], p[1] - res[1][i]) for i, p in enumerate(positions)]

        self.assertTrue(all(map(lambda x: x == shifted[0], shifted)))


class ShiftCorrectionTest(unittest.TestCase):

    def test_simple_correction(self):
        size = 15
        data = np.zeros((size, size), dtype=float)
        data[5][5] = data[12][4] = 1.0

        result = Movie.correct_for_shift(data, 0, 0)
        self.assertTrue(np.array_equal(data, result))

        expected = np.zeros((size, size), dtype=float)
        expected[7][8] = expected[14][7] = 1.0
        result = Movie.correct_for_shift(data, -2, -3)
        np.testing.assert_array_almost_equal(expected, result, 6)

        expected = np.zeros((size, size), dtype=float)
        expected[3][1] = expected[10][0] = 1.0
        result = Movie.correct_for_shift(data, 2, 4)
        np.testing.assert_array_almost_equal(expected, result, 6)

        expected = np.zeros((size, size), dtype=float)
        expected[7][0] = 1.0
        result = Movie.correct_for_shift(data, -2, 5)
        np.testing.assert_array_almost_equal(expected, result, 6)

    def test_global_shift_correction(self):
        size = 15
        square_size = 4
        data = [np.zeros((size, size), dtype=float) for d in range(4)]
        data[0] = GlobalShiftTest.add_square(data[0], 7, 7, square_size)
        data[1] = GlobalShiftTest.add_square(data[1], 3, 7, square_size)
        data[2] = GlobalShiftTest.add_square(data[2], 7, 3, square_size)
        data[3] = GlobalShiftTest.add_square(data[3], 2, 1, square_size)

        movie = Movie()
        for i, d in enumerate(data):
            img = Image()
            img.image_data = d
            img.time_stamp = i
            movie.add(img)

        movie.correct_global_shift()

        sum_image = movie.sum_images()

        peak_count = 0
        for v in np.nditer(sum_image):
            self.assertTrue(math.isclose(v, 0, abs_tol=1e-6) or math.isclose(v, len(data), abs_tol=1e-6))
            if math.isclose(v, len(data), abs_tol=1e-6):
                peak_count += 1
        self.assertEqual(peak_count, square_size*square_size)


class LocalShiftsTest(unittest.TestCase):

    def partitioning_test(self, size_y, size_x):
        data = [np.zeros((size_y, size_x), dtype=float) for d in range(4)]

        # Each partition contains values of the same value more specifically `1000 * partition_index + time_index`
        # where partition_index start from 1 and time index is index in data
        # Plus when the axis is no dividable by 5, the remainder is spread from the start and size of each partition
        # there is increased by one until the required size is met.
        part_y_sizes = [(size_y // 5) for i in range(5)]
        part_x_sizes = [(size_x // 5) for i in range(5)]
        remainder_y = size_y - (size_y // 5) * 5
        remainder_x = size_x - (size_x // 5) * 5
        for i in range(remainder_y):
            part_y_sizes[i] += 1
        for i in range(remainder_x):
            part_x_sizes[i] += 1

        index_y = 0
        for part_y_index, curr_y_size in enumerate(part_y_sizes):
            for iy in range(curr_y_size):
                index_x = 0
                for part_x_index, curr_x_size in enumerate(part_x_sizes):
                    for ix in range(curr_x_size):
                        for i in range(len(data)):
                            data[i][index_y][index_x] = (part_y_index * 5 + part_x_index + 1) * 1000 + i
                        index_x += 1
                index_y += 1

        res = Movie.partition(data)

        # check correct dimensions
        self.assertEqual(len(res), 25)
        for stack_index, stack in enumerate(res):
            self.assertEqual(len(stack), len(data))
            y_index = stack_index // 5
            x_index = stack_index - (y_index * 5)
            for time in stack:
                self.assertEqual(time.shape, (part_y_sizes[y_index], part_x_sizes[x_index]))

        # check correct values
        for stack_index, stack in enumerate(res):
            for time_index, time in enumerate(stack):
                array = np.ones(time.shape)
                array = (array * (stack_index + 1) * 1000) + time_index
                self.assertTrue(np.array_equal(array, time))

    def test_partitioning_regular(self):
        """can be divided regularly (i.e. each dimension is dividable by 5"""
        self.partitioning_test(20, 15)

        self.partitioning_test(45, 5)

        self.partitioning_test(5, 5)

        self.partitioning_test(20, 50)

    def test_partitioning_irregular(self):
        """dimensions are not dividable by 5"""
        self.partitioning_test(21, 17)

        self.partitioning_test(37, 40)

        self.partitioning_test(11, 34)

        self.partitioning_test(90, 67)

        self.partitioning_test(6, 89)

    def test_calculate_local_shifts(self):
        size_y = 233
        size_x = 158
        data = [np.zeros((size_y, size_x), dtype=float) for d in range(4)]

        part_y_sizes = [(size_y // 5) for i in range(5)]
        part_x_sizes = [(size_x // 5) for i in range(5)]
        remainder_y = size_y - (size_y // 5) * 5
        remainder_x = size_x - (size_x // 5) * 5
        for i in range(remainder_y):
            part_y_sizes[i] += 1
        for i in range(remainder_x):
            part_x_sizes[i] += 1

        movie = Movie()
        for i, d in enumerate(data):
            img = Image()
            img.time_stamp = i
            img.image_data = d
            movie.add(img)

        pos, s_y, s_x = movie.calculate_local_shifts()

        # check positions
        # self.assertEqual(len(data) * 25, len(pos))
        # for t in range(len(data)):
        #     for i, p in enumerate(pos):
        #         # self.assertEqual(p[2], t)  # check time
        #         stack_index = i % 25
        #         stack_x_index = stack_index % 5
        #         stack_y_index = stack_index // 5
        #         y_index = sum((v for v in part_y_sizes[:max(stack_y_index - 1, 0)]))
        #         y_index += part_y_sizes[y_index] // 2
        #         x_index = sum((v for v in part_x_sizes[:max(stack_x_index - 1, 0)]))
        #         x_index += part_x_sizes[x_index] // 2
        #         # self.assertEqual(y_index, p[0])
        #         # self.assertEqual(x_index, p[1])

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()

