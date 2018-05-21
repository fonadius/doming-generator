from image import Image
from deformation_model import DeformationModel
from movie import Movie
import numpy as np
from scipy import optimize
import mrcfile as mrc


def deform_file(path=None, shape=None, time_points=None, coefficients=None, save=None,
                add_grid=True, save_movie=True, verbose=True):
    """
    Deforms provided file based on the deformation model.
    :param path: Path to an image file in gray-scale, which should be loaded. If None scipy.misc.face is used instead.
    :param shape: array like object with at least two elements describing (width, height) of the image
    :param time_points: determines number of deformed images generated and their time (None is equal to range(10))
    :param coefficients: coefficients used in deformation model, describing the doming
    :param save: None - images are only returned, other inputs are regarded as folder paths where the results are saved
    :param add_grid: True - black grid is drawn over the image to better show the resulting deformation
    :param save_movie: True - if save=True then also the movie of the deformed images is saved as a STAR file format (with
    the individual images saved as mrc files)
    :param verbose: True - printing additional information about the current process state
    :return: ([images], coefficients) - images are numpy array with resulting data ordered as time_points
                                      - coefficients are coefficients used in the deformation model
    """
    if time_points is None:
        time_points = range(10)

    if verbose:
        print("Loading file")

    if path is None:
        img = Image()
        img.load_dummy(0, add_grid)
    else:
        img = Image(path, 0)

    if shape is None:
        img.shrink_to_reasonable()
    else:
        img.resize(shape)

    if verbose:
        print("Applying model")

    model = DeformationModel()
    if coefficients is None:
        model.initialize_model_randomly(img.shape(), max(time_points))
    else:
        model.coeffs = coefficients

    results = []
    for t in time_points:
        results.append(model.apply_model(img, 0, t))
        if verbose:
            print("Generated deformation in time point:", t)

    if save:
        if verbose:
            print("Saving results")

        for i in results:
            i.save(save, name="DeformationTime" + str(i.time_stamp))

        if save_movie:
            movie = Movie()
            for i in results:
                movie.add(i, True)
            movie.save_movie_starfile("./", "movie")

    results = [i.image_data for i in results]

    if verbose:
        print("Deformations finished.")

    return results, model.coeffs


def motion_correct_files(paths=[], time_points=[], coefficients=None, save_path=None, save_partial=False, verbose=True):
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
        movie.micrographs[i] = model.apply_model(m, m.time_stamp, 0)
        if save_path and save_partial:
            movie.micrographs[i].save(save_path, name=("partial" + str(i)))
        if verbose:
            print("Restored image " + str(i))

    if save_path:
        movie.save_sum(save_path)

    if verbose:
        print("Restoration finished")

    return movie.sum_images()


if __name__ == "__main__":
    time_span = 10
    time_step = 0.5
    time_points = [x * time_step for x in range(int(time_span / time_step))]
    results, coeffs = deform_file(save="./", time_points=time_points, verbose=True)

    paths = ["DeformationTime"+str(x) + ".png" for x in time_points]
    motion_correct_files(paths=paths, time_points=time_points, save_path="./", save_partial=True, verbose=True)

