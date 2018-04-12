"""Remembers model of deformation and allows its generation"""
import numpy as np
import MyMath
from Image import Image
import math
from scipy import optimize


class DeformationModel:
    """Describes, creates and uses doming deformation model described by equation:
       S(x,y,t) = (a_0 + a_1*x + a_2*x^2 + a_3*y + a_4*y^2 + a_5*x*y) * (a_6*t + a_7*t^2 + a_8*t^3)"""

    def __init__(self):
        self.coeffs = np.zeros((18, 2))  # c_0 through c_17 (each coefficient is vector (x, y))
        self.forward_model = False  # Does the model describes movement forward or backward in time?
        self.initialized = False

    def apply_model(self, original, t1, t2):
        """Applies model and calculates other time position
            :param original numpy array representing an image in the time t1
            :param t1 time stamp of the 'original'
            :param t2 time stamp to which should the model move the 'original'
            :returns numpy array with original image in time t2 base on the model"""
        if not self.initialized:
            raise RuntimeError("Model is not initialized.")

        if (self.forward_model and t2 < t1) or (not self.forward_model and t1 < t2):
            raise AttributeError("Model cannot go in this time direction.")

        img = Image()
        img.initialize_with_zero(original.shape())
        img.time_stamp = t2

        if t1 == t2:
            img.initialize_with_image(original)
            return img

        def generate(y, x):
            """Function describing the transformed image"""
            # move to time t2
            posx = x + self.calculate_shift(x, y, t2, 0) - self.calculate_shift(x, y, t1, 0)
            posy = y + self.calculate_shift(x, y, t2, 1) - self.calculate_shift(x, y, t1, 1)

            x_left = int(posx)    # math.floor(pos[0])
            x_right = x_left + 1    # math.ceil(pos[0])
            y_down = int(posy)    # math.floor(pos[1])
            y_up = y_down + 1       # math.ceil(pos[1])

            q11 = (x_left, y_up, original.get(x_left, y_up))
            q21 = (x_left, y_down, original.get(x_left, y_down))
            q12 = (x_right, y_up, original.get(x_right, y_up))
            q22 = (x_right, y_down, original.get(x_right, y_down))

            return MyMath.linear_interpolation(q11, q21, q12, q22, posx, posy)

        img.image_data = np.fromfunction(np.vectorize(generate), original.image_data.shape)

        return img

    def calculate_shift(self, x, y, t, axis):
        t2 = t*t
        t3 = t2*t

        c = self.coeffs[axis]
        shift = (c[0] + c[1] * x + c[2] * x * x + c[3] * y + c[4] * y * y + c[5] * x * y) * \
                (c[6] * t + c[7] * t2 + c[8] * t3)

        return shift

    def initialize_model(self, shift_vectors, time_forward=True):
        """Initialize model by least square approximation from provided 'shift_vectors'. To generate
            :param shift_vectors np.array with three elements [0] - x shift, [1] - y shift, [2] - time stamp"""

        def f(v, c):
            x = v[0]
            y = v[1]
            t = v[2]

            t2 = t * t
            t3 = t2 * t

            shift = (c[0] + c[1] * x + c[2] * x * x + c[3] * y + c[4] * y * y + c[5] * x * y) * \
                    (c[6] * t + c[7] * t2 + c[8] * t3)
            return shift

        def residual(c, val):
            return f(c) - val

        x0 = [0,] * 9

        solX = optimize.leastsq(residual, x0)[0]

        y0 = [0, ] * 9

        solY = optimize.leastsq(residual, y0)[0]

        self.initialize_model_randomly(time_forward=False)

    def initialize_model_randomly(self, shape=None, time_forward=True):
        """Randomly generates model with reasonable coefficients."""
        self.coeffs = self.generate_random_coeffs(shape)
        self.forward_model = time_forward
        self.initialized = True

    @staticmethod
    def generate_random_coeffs(shape=None):
        """Generates vector of reasonable random model coefficients a_i.
            shape is (height, width) tuple"""
        # TODO: coefficients should not be just random but also reasonable
        flt = np.random.rand(2, 9)
        scale = np.ones((2, 9)) / 100
        res = flt * scale

        # move the center of the doming into the middle of the picture
        if shape:
            res[0][0] = -shape[1] / 2
            res[1][0] = -shape[0] / 2
        return res

