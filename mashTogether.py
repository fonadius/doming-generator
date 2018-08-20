#!/usr/bin/python3
from image import Image
from movie import Movie
import glob, os, sys

if __name__ == "__main__":
    folder = sys.argv[1]
    output = sys.argv[2]
    os.chdir(folder)
    file_list = list(glob.glob("*.jpg"))
    file_list.sort()
    movie = Movie()
    for f in file_list:
        path = folder + "/" + f
        img = Image(path, 0)
        movie.add(img, data_check=False)
    movie.save_movie_mrc(output)


