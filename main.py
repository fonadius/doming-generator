from Image import Image
from DeformationModel import DeformationModel
from Movie import Movie
import numpy as np
from scipy import optimize


def deform_images(count):
    print("Deforming images")
    orig = Image()
    orig.load_dummy(0)

    model = DeformationModel()
    print("Applying model.")
    model.initialize_model_randomly(orig.image_data.shape)

    for i in range(count):
        deformed_image = model.apply_model(orig, 0, i)
        deformed_image.save("./")
        print("Done iteration ", i)

    print("Run successful.")


def restore_images(count):
    movie = Movie()
    for i in range(count):
        movie.add(Image("./" + str(i) + ".png", i))

    movie = Movie()
    movie.initialize(micro)
    global_shifts = movie.correct_global_shift(micro)

    micro = movie.correct_for_shift(micro, global_shifts)

    local_shifts = movie.calculate_local_shifts(micro)

    model = DeformationModel()
    model.initialize_model(local_shifts, False)

    for m in micro:
        img = model.apply_model(m, 5, 0)
        img.saver("./")


if __name__ == "__main__":
    # model = DeformationModel()
    # model.initialize_model_randomly()
    #
    # def shift(x, y, t, c):
    #     return (c[0] + c[1] * x + c[2] * x * x + c[3] * y + c[4] * y * y + c[5] * x * y) * \
    #             (c[6] * t + c[7] * t*t + c[8] * t*t*t)
    #
    # def shift_list(xs, ys, ts, c):
    #     return np.array([shift(xs[i], ys[i], ts[i], c) for i in range(len(xs))])
    #
    # def residuals(c, shifts, xs, ys, ts):
    #     return shifts - shift_list(xs, ys, ts, c)
    #
    # c0 = np.array([1] * 9)
    #
    # xs = [10, 30, 50, 70, 90] * 5
    # ys = [10] * 5
    # ys += [30] * 5
    # ys += [50] * 5
    # ys += [70] * 5
    # ys += [90] * 5
    # ts = [1] * 25
    # shifts = np.array([shift(xs[i], ys[i], ts[i], model.coeffs[0]) for i in range(len(xs))])
    #
    # res = optimize.leastsq(residuals, c0, args=(shifts, xs, ys, ts))
    #
    # print(model.coeffs[0])
    # print(res[0])

