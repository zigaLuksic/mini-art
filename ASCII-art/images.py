from PIL import Image


def load_image_to_array(path):
    image = Image.open(path)
    specs = {"mode": image.mode, "w": image.width,
             "h": image.height, "format": image.format}
    flat_arr = [p for p in image.getdata()]
    image_arr = [[flat_arr[(j * specs["w"])+i]
                  for i in range(specs["w"])]
                 for j in range(specs["h"])]
    return image_arr, specs


def save_array_as_image(image_arr, image_specs, path):
    size = (image_specs["w"], image_specs["h"])
    image = Image.new(image_specs["mode"], size)
    data = [p for line in image_arr for p in line]
    image.putdata(data)
    image.save(path)
