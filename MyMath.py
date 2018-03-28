def point_distance(p1, p2):
    """
    Calculated Euclidian distance between p1 and p2 in 2D.
    :param p1: point 1 saved as tuple or array as (x, y)
    :param p2: point 2 saved as tuple or array as (x, y)
    :return:
    """
    x_dist = p1[0] - p2[0]
    y_dist = p1[1] - p2[1]
    return (x_dist*x_dist + y_dist*y_dist) ** 0.5


def linear_interpolation(q11, q12, q21, q22, p_x, p_y):
    """Performs linear interpolation. With the following argument naming
        q11 ......... q12
        .................
        ...... p ........
        .................
        .................
        q21 ......... q22
        Values q_i are expected to be in strict orthogonal grid, where q11 and q21 have the same x coordinates (the same
        applies for q12 and q22) and q11 and q12 have the same y coordinates (the same applies for q21 and q22)
        :param q11 Value and position of near pixel. Saved as triplet (x, y, value)
        :param q12 Value and position of near pixel. Saved as triplet (x, y, value)
        :param q21 Value and position of near pixel. Saved as triplet (x, y, value)
        :param q22 Value and position of near pixel. Saved as triplet (x, y, value)
        :param p_x x position of calculated value
        :param p_y y position of calculated value
    """
    # x interpolation
    total_dist = q11[0] - q12[0]
    rat1 = (q11[0] - p_x) / total_dist
    rat2 = 1 - rat1

    p1 = q11[2] * rat1 + q12[2] * rat2
    p2 = q21[2] * rat1 + q22[2] * rat2

    # y interpolation
    total_dist = q11[1] - q21[1]
    rat1 = (q11[2] - p_y) / total_dist
    rat2 = 1 - rat1

    p = p1 * rat1 + p2 * rat2
    return p

