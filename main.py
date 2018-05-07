from image import Image
from deformation_model import DeformationModel
from movie import Movie
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
        img.load("./" + str(i) + ".png", i)
        movie.add(img)
    print("Images loaded.")

    movie.correct_global_shift()

    # for i, m in enumerate(movie.micrographs):
    #     m.save("./", "globaly")

    print("Global correction performed.")

    local_shifts = movie.calculate_local_shifts()

    movie = Movie()
    for i in range(count):
        img = Image()
        img.load("./" + str(i) + ".png", i)
        movie.add(img)
    print("Images loaded.")

    print("Local shifts calculated")

    model = DeformationModel()
    model.initialize_model(*local_shifts)

    print("Deformation model calculated.")

    for i in range(len(movie.micrographs)):
        m = movie.micrographs[i]
        movie.micrographs[i] = model.apply_model(m, m.time_stamp, 0, 2)
        movie.micrographs[i].save("./", name=(str(i) + "resulting"))
        print("Restored image " + str(i))

    movie.save_sum("./")
    print("Restoration finished.")


def test_global_correction(count):
    print("Starting restoration.")
    movie = Movie()
    for i in range(count):
        img = Image()
        img.load_dummy(i)
        img.image_data = movie.correct_for_shift(img.image_data, 0, -i * 2)
        movie.add(img)
    print("Images loaded.")

    for m in movie.micrographs:
        m.save("./")

    movie.correct_global_shift()

    for i, m in enumerate(movie.micrographs):
        m.save("./", "r")

    movie.save_sum("./")


if __name__ == "__main__":
    # deform_images(10)
    restore_images(10)

