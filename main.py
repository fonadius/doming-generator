from Image import Image
from DeformationModel import DeformationModel


if __name__ == "__main__":
    orig = Image()
    orig.load("", 0)

    model = DeformationModel()
    model.initialize_model_randomly()

    deformed_image = model.apply_model(orig, 0, 1)
    deformed_image.save("./")

