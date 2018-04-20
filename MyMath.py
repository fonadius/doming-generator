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


def linear_interpolation(q11, q12, q21, q22, p_y, p_x):
    """Performs linear interpolation. With the following argument naming
        q11 ......... q12
        .................
        ...... p ........
        .................
        .................
        q21 ......... q22
        Values q_i are expected to be in strict orthogonal grid, where q11 and q21 have the same x coordinates (the same
        applies for q12 and q22) and q11 and q12 have the same y coordinates (the same applies for q21 and q22).

        :param q11 Value and position of near pixel. Saved as triplet (y, x, value)
        :param q12 Value and position of near pixel. Saved as triplet (y, x, value)
        :param q21 Value and position of near pixel. Saved as triplet (y, x, value)
        :param q22 Value and position of near pixel. Saved as triplet (y, x, value)
        :param p_x x position of calculated value
        :param p_y y position of calculated value
    """
    # x interpolation
    if q11[1] == q12[1]:
        p1 = q11[2]
        p2 = q21[2]
    else:
        rat_left = (p_x - q11[1]) / (q12[1] - q11[1])
        rat_right = (q12[1] - p_x) / (q12[1] - q11[1])

        p1 = q11[2] * rat_left + q12[2] * rat_right
        p2 = q21[2] * rat_left + q22[2] * rat_right

    # y interpolation
    if q11[0] == q21[0]:
        p = p1
    else:
        rat_top = (p_y - q11[0]) / (q21[0] - q11[0])
        rat_down = (q21[0] - p_y) / (q21[0] - q11[0])

        p = p1 * rat_top + p2 * rat_down

    return p

