import math


def point_distance(p1, p2):
    """
    Calculated Euclidian distance between p1 and p2 in 2D.
    :param p1: point 1 saved as tuple or array as (y, x)
    :param p2: point 2 saved as tuple or array as (y, x)
    :return:
    """
    y_dist = p1[1] - p2[1]
    x_dist = p1[0] - p2[0]
    return (x_dist*x_dist + y_dist*y_dist) ** 0.5


def linear_interpolation(y1, x1, y2, x2, v11, v12, v21, v22, p_y, p_x):
    """Performs linear interpolation. With the following argument naming
       y1: v11 ......... v12
           .................
           ...... p ........
           .................
           .................
       y2: v21 ......... v22
           x1             x2
        (y increases from top to down, x increases from left to right)
        Values q_i are expected to be in strict orthogonal grid, where q11 and q21 have the same x coordinates (the same
        applies for q12 and q22) and q11 and q12 have the same y coordinates (the same applies for q21 and q22).

        :param y1 y position of v11 and v12
        :param x1 x position of v11 and v21
        :param y2 y position of v12 and v22
        :param x2 x position of v12 and v22
        :param v11 image value at <y1, x1>
        :param v12 image value at <y1, x2>
        :param v21 image value at <y2, x1>
        :param v22 image value at <y2, x2>
        :param p_x x position of calculated value
        :param p_y y position of calculated value
    """
    # x interpolation
    if x1 == x2:
        p1 = v11
        p2 = v21
    else:
        diffx = (x2 - x1)
        rat1 = (x2 - p_x) / diffx
        rat2 = (p_x - x1) / diffx

        p1 = v11 * rat1 + v12 * rat2
        p2 = v21 * rat1 + v22 * rat2

    # y interpolation
    if y1 == y2:
        p = p1
    else:
        diffy = (y2 - y1)
        rat1 = (y2 - p_y) / diffy
        rat2 = (p_y - y1) / diffy

        p = p1 * rat1 + p2 * rat2

    return p

