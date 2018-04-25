import unittest
import MyMath


class LinearInterpolationTest(unittest.TestCase):

    def test_linear_interpolation(self):
        # In form (y1, x1, y2, x2, v11, v12, v21, v22, y, x, expected)
        # In form (q11, q12, q21, q22, y, x, expected)
        known_values = [
            # all points are one point
            (5.5, 5.5, 5.5, 5.5, 12.3, 12.3, 12.3, 12.3, 5.5, 5.5, 12.3),
            # all points lie on the same x coordinates
            (1, 1, 2, 1, 1, 1, 3, 3, 1.5, 1.5, 2),
            # all points lie on the same y coordinates
            (8, 8, 8, 11, 2, 4, 2, 4, 8, 10, 3 + 1/3),
            # point in the middle
            (1, 1, 4, 4, 1, 1, 2, 2, 2.5, 2.5, 1.5),
            # normal points
            (2.1, 1, 4.8, 3.62, 3.5, 1, 2, 4, 3.2, 2.5, 2.5072094995759118),
            (1, 3.12, 5.6, 12, 1, -2, 9.8, 5.1, 1.12, 10, -1.1291186839012923),
            (8.13, 4.82, 22.65, 4.99, 19, 17, 5, 24, 20.1, 4.87, 11.962202236266407),
        ]

        for item in known_values:
            self.assertAlmostEqual(MyMath.linear_interpolation(
                *(item[:-1])
            ), item[-1])


if __name__ == "__main__":
    unittest.main()