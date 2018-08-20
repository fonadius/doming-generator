from image import Image

if __name__ == "__main__":
    img = Image()
    img.load_dummy(0, True)
    shiftsX = [-3, -5, -7, -4, -2,
               -2, -4, -4, -3, -1,
               0,  -2, -2, -1, 1,
               1,  3,   0,  2, 2,
               2,  5,  2,   4, 3]
    shiftsY = [1, 2, 2, 2, 1,
               1, 3, 3, 2, 1,
               2, 4, 3, 3, 2,
               3, 6, 4, 3, 5,
               5, 8, 6, 5, 5]
    img.shift_patches(shiftX, shiftsY)
