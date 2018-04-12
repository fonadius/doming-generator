from Image import Image
from DeformationModel import DeformationModel
from Movie import Movie


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
    micro = []
    for i in range(count):
        micro.append(Image())
        micro[-1].load("./" + str(i) + ".png", i)

    movie = Movie()
    movie.initialize(micro)
    global_shifts = movie.calculate_shifts(micro)

    micro = movie.correct_for_shift(micro, global_shifts)

    local_shifts = movie.calculate_local_shifts(micro)

    model = DeformationModel()
    model.initialize_model(local_shifts, False)

    for m in micro:
        img = model.apply_model(m, 5, 0)
        img.saver("./")


if __name__ == "__main__":
    restore_images(10)

