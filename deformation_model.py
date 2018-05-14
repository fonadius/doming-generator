"""Remembers model of deformation and allows its generation"""
import numpy as np
import my_math
from image import Image
from scipy import optimize
import skimage.transform
import math


class DeformationModel:
    """Describes, creates and uses doming deformation model described by equation:
       S(x,y,t) = (a_0 + a_1*x + a_2*x^2 + a_3*y + a_4*y^2 + a_5*x*y) * (a_6*t + a_7*t^2 + a_8*t^3)"""

    def __init__(self):
        self.coeffs = np.zeros((18, 2))  # c_0 through c_17 (each coefficient is vector (y, x))

    def apply_model(self, original, t1, t2, resolution_scaling_factor=1):
        """Applies model and calculates other time position
            :param original numpy array representing an image in the time t1
            :param t1 time stamp of the 'original'
            :param t2 time stamp to which should the model move the 'original'
            :param resolution_scaling_factor in how much grater resolution should the deformation be calculated
            :returns numpy array with original image in time t2 base on the model"""
        img = Image()
        img.time_stamp = t2

        if t1 == t2:
            img.initialize_with_image(original)
            return img

        calc_shift_fnc = self.calculate_shift
        orig_get_fnc = original.get
        interp_fnc = my_math.linear_interpolation

        def generate(y, x):
            """Function describing the transformed image"""
            # the indices supplied to shift calculation must retain their original meaning
            realy = y / resolution_scaling_factor
            realx = x / resolution_scaling_factor

            # move to time t2
            posy = y + calc_shift_fnc(realy, realx, t2, 0) - calc_shift_fnc(realy, realx, t1, 0)
            posx = x + calc_shift_fnc(realy, realx, t2, 1) - calc_shift_fnc(realy, realx, t1, 1)

            x_left = int(posx)   # math.floor(pos[0])
            x_right = x_left + 1    # math.ceil(pos[0])
            y_down = int(posy)    # math.floor(pos[1])
            y_up = y_down + 1       # math.ceil(pos[1])

            v11 = orig_get_fnc(y_down, x_left, resolution_scaling_factor)
            v12 = orig_get_fnc(y_down, x_right, resolution_scaling_factor)
            v21 = orig_get_fnc(y_up, x_left, resolution_scaling_factor)
            v22 = orig_get_fnc(y_up, x_right, resolution_scaling_factor)

            return interp_fnc(y_down, x_left, y_up, x_right, v11, v12, v21, v22, posy, posx)

        img.image_data = np.fromfunction(np.vectorize(generate),
                                         (original.shape()[0] * resolution_scaling_factor,
                                          original.shape()[1] * resolution_scaling_factor))

        if resolution_scaling_factor != 1:
            img.image_data = skimage.transform.resize(img.image_data, original.shape(), preserve_range=True)

        return img

    def calculate_shift(self, y, x, t, axis):
        """
        Calculates shift on defined positions
        :param y:
        :param x:
        :param t:
        :param axis: 0 is y, 1 is x
        """
        return DeformationModel.calculate_shifts_from_coeffs(y, x, t, self.coeffs[axis])

    @staticmethod
    def calculate_shifts_from_coeffs(y, x, t, c):
        t2 = t * t
        t3 = t2 * t

        shift = (c[0] + c[1] * x + c[2] * x * x + c[3] * y + c[4] * y * y + c[5] * x * y) * \
                (c[6] * t + c[7] * t2 + c[8] * t3)

        return shift

    def initialize_model(self, positions, shifts_y, shifts_x):
        """
        Estimates model coefficients from calculated shifts.
        :param positions: Positions where shifts were calculated (y, x, time_stamp)
        :param shifts_y: shifts on y axis for positions
        :param shifts_x: shifts on x axis for positions
        :return:
        """
        shifts_y = list(map(lambda x: x*-1, shifts_y))
        shifts_x = list(map(lambda x: x*-1, shifts_x))

        def list_shift(pos, c):
            return np.array([DeformationModel.calculate_shifts_from_coeffs(p[0], p[1], p[2], c) for p in pos])

        def residuals(c, shift, pos):
            return shift - list_shift(pos, c)

        c0y = [1] * 9
        res_y = optimize.leastsq(residuals, c0y, args=(shifts_y, positions))[0]

        c0x = [1] * 9
        res_x = optimize.leastsq(residuals, c0x, args=(shifts_x, positions))[0]

        result = np.concatenate((res_y, res_x), axis=0).reshape(2, 9)

        self.coeffs = result

    def initialize_model_randomly(self, shape=None):
        """Randomly generates model with reasonable coefficients."""
        self.coeffs = self.generate_random_coeffs(shape)

    @staticmethod
    def generate_random_coeffs(shape=None):
        """Generates vector of reasonable random model coefficients a_i.
            shape is (height, width) tuple.
            Generated coefficients are in interval <-0.1,0.1> with c_0 in <-0.01, 0.01>.
            :param shape: Shape of the image for which the coefficients should be generated. If provided, the
            coefficients are modified to place the center of doming into the center of the picture."""
        flt = np.random.rand(2, 9)
        res = ((flt * 2) - 1) / 10
        res[0][0] = res[0][0] / 10
        res[1][0] = res[1][0] / 10

        if shape is not None:
            # move the center of deformation into middle of image
            halfy = shape[0] / 2
            halfx = shape[1] / 2

            for i in range(2):
                c = res[i]
                c[0] = c[0] - c[1]*halfx - c[3]*halfy + c[2]*halfx*halfx + c[5]*halfy*halfx + c[4]*halfy*halfy
                c[1] = c[1] - 2*c[2]*halfx - c[5]*halfy
                c[3] = c[3] - 2*c[4]*halfy - c[5]*halfx

        # the quadratic time element is decreased to produce slower deformation
        res[0][8] = res[0][8] / 100
        res[1][8] = res[1][8] / 100

        return res

