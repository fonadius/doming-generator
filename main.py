from Image import Image
from DeformationModel import DeformationModel


if __name__ == "__main__":
    orig = Image()
    orig.load("", 0)

    model = DeformationModel()
    print("Applying model.")
    model.initialize_model_randomly()

    deformed_image = model.apply_model(orig, 0, 3)
    print("Model applied.")
    deformed_image.save("./")
    print("Run successful.")

