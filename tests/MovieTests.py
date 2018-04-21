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


if __name__ == "__main__":
    unittest.main()

