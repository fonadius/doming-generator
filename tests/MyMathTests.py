import unittest
import MyMath


class LinearInterpolationTest(unittest.TestCase):

    def test_linear_interpolation(self):
        # In form (q11, q12, q21, q22, y, x, expected)
        known_values = [
            # all points are one point
            ((5.5, 5.5, 12.3), (5.5, 5.5, 12.3), (5.5, 5.5, 12.3), (5.5, 5.5, 12.3), 5.5, 5.5, 12.3),
            # all points lie on the same x coordinates
            ((1, 1, 1), (1, 1, 1), (2, 1, 3), (2, 1, 3), 1.5, 1.5, 2),
            # all points lie on the same y coordinates
            ((8, 8, 2), (8, 11, 4), (8, 8, 2), (8, 11, 4), 8, 10, 2 + 2/3),
            # point in the middle
            ((1, 1, 1), (1, 4, 1), (4, 1, 2), (4, 4, 2), 2.5, 2.5, 1.5),
            # normal points
            ((4.8, 1, 3.5), (4.8, 3.62, 1), (2.1, 1, 2), (2.1, 3.62, 4), 3.2, 2.5, 2.7065309584393553),
        ]

        for item in known_values:
            self.assertAlmostEqual(MyMath.linear_interpolation(
                item[0], item[1], item[2], item[3], item[4], item[5]
            ), item[6])


if __name__ == "__main__":
    unittest.main()