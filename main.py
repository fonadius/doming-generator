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

    print("Deformation successful.")


def restore_images(count):
    print("Starting restoration.")
    movie = Movie()
    for i in range(count):
        img = Image()
        img.load_dummy(i)
        movie.add(img)
    # movie.dummy_initialize()
    print("Images loaded.")

    movie.add_dummy_global_shift()

    for m in movie.micrographs:
        m.save("./")

    # movie.correct_global_shift()

    for i, m in enumerate(movie.micrographs):
        m.image_data = movie.correct_for_shift(m.image_data, -i, 0)
        m.save("./", "r")

    movie.save_sum("./")

    # print("Global correction performed.")
    #
    # local_shifts = movie.calculate_local_shifts()
    #
    # print("Local shifts calculated")
    #
    # model = DeformationModel()
    # model.initialize_model(*local_shifts)
    #
    # print("Deformation model calculated.")
    #
    # for i in range(len(movie.micrographs)):
    #     m = movie.micrographs[i]
    #     movie.micrographs[i] = model.apply_model(m, m.time_stamp, 0)
    #     movie.micrographs[i].save("./", "r" + str(i))
    #     print("Restored image " + str(i))
    #
    # movie.save_sum("./")
    # print("Restoration finished.")


if __name__ == "__main__":
    # deform_images(10)
    restore_images(10)

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

