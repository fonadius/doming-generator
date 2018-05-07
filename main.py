from image import Image
from deformation_model import DeformationModel
from movie import Movie
import numpy as np
from scipy import optimize


def deform_file(path=None, shape=None, time_points=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), coefficients=None, save=None,
                add_grid=True, verbose=True):
    """
    Deforms provided file based on the deformation model.
    :param path: Path to an image file in gray-scale, which should be loaded. If None scipy.misc.face is used instead.
    :param shape: array like object with at least two elements describing (width, height) of the image
    :param time_points: determines number of deformed images generated and their time
    :param coefficients: coefficients used in deformation model, describing the doming
    :param save: None - images are only returned, other inputs are regarded as folder paths where the result is saved
    in current working folder
    :param add_grid: True - black grid is drawn over the image to better show the resulting deformation
    :param verbose: True - printing additional information about the current process state
    :return: ([images], coefficients) - images are numpy array with resulting data ordered as time_points
                                      - coefficients are coefficients used in the deformation model
    """
    if verbose:
        print("Loading file")

    if path is None:
        img = Image()
        img.load_dummy(0, add_grid)
    else:
        img = Image(path, 0)

    if shape is None:
        img.shrink_to_resonable()
    else:
        img.resize(shape)

    if verbose:
        print("Applying model")

    model = DeformationModel()
    if coefficients is None:
        model.generate_random_coeffs()
        # todo: modify time coefficients to provide reasonable results for defined number of time_points
    else:
        model.coeffs = coefficients

    results = []
    for t in time_points:
        results.append(model.apply_model(img, 0, t, 2))
        if verbose:
            print("Generated deformation in time point:", t)

    if save:
        if verbose:
            print("Saving results")

        for t, i in zip(time_points, results):
            i.save(save, name="DeformationTime" + str(t))

    if verbose:
        print("Deformations finished.")

    return results, model.coeffs


def correct_files(paths=[], time_points=[], coefficients=None, save_path=None, save_partial=False, verbose=True):
    """
    Corrects motion (proof of concept implementation)
    :param paths: paths to deformed gray-scale files
    :param time_points: time_points of the provided files
    :param coefficients: coefficients used to correct motion, if None the whole calculation including coefficient
    estimation is performed
    :param save_path: None - result is only returned, any other value is treated as path to folder where to save result
    :param save_partial: True - partial results are saved into folder defined in save_path (individual corrected images)
    :param verbose: True - printing additional information about the current process state
    :return: numpy array representing the corrected image
    """

    if verbose:
        print("Loading files")

    movie = Movie()
    for p, t in zip(paths, time_points):
        img = Image(p, t)
        movie.add(img)

    if verbose:
        print("Correcting for global shift")
    movie.correct_global_shift()

    if coefficients is None:
        if verbose:
            print("Calculating local shifts")
        local_shifts = movie.calculate_local_shifts()

        if verbose:
            print("Estimating deformation model coefficients")
        model = DeformationModel()
        model.initialize_model(*local_shifts)
    else:
        model = DeformationModel()
        model.coeffs = coefficients

    if verbose:
        print("Applying model")

    for i in range(len(movie.micrographs)):
        m = movie.micrographs[i]
        movie.micrographs[i] = model.apply_model(m, m.time_stamp, 0, 2)
        if save_path and save_partial:
            movie.micrographs[i].save(save_path, name=("partial" + str(i)))
        if verbose:
            print("Restored image " + str(i))

    if save_path:
        movie.save_sum(save_path)

    if verbose:
        print("Restoration finished")

    return movie.sum_images()


# -------testing functions------


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
    deform_images(10)
    restore_images(10)

