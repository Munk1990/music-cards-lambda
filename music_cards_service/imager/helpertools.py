def set_transparency(im, percent):
    rgba = im.convert("RGBA")
    pixels = rgba.getdata()

    newData = []
    for pixel in pixels:
        newData.append((pixel[0], pixel[1], pixel[2], int(pixel[3] * percent / 100)))

    rgba.putdata(newData)
    return rgba


def change_colors(im, target_color, replacement_color):
    rgba = im.convert("RGBA")
    pixels = rgba.getdata()
    newData = []
    for pixel in pixels:
        if pixel[0] == target_color[0] and pixel[1] == target_color[1] and pixel[2] == target_color[2]:
            newData.append((replacement_color[0], replacement_color[1], replacement_color[2], pixel[3]))
        else:
            newData.append((pixel[0], pixel[1], pixel[2], pixel[3]))
    rgba.putdata(newData)
    return rgba


def change_color_transparency(im, target_color, percent):
    rgba = im.convert("RGBA")
    pixels = rgba.getdata()
    newData = []
    for pixel in pixels:
        if pixel[0] == target_color[0] and pixel[1] == target_color[1] and pixel[2] == target_color[2]:
            newData.append((pixel[0], pixel[1], pixel[2], int(pixel[3] * percent / 100)))
        else:
            newData.append((pixel[0], pixel[1], pixel[2], pixel[3]))
    rgba.putdata(newData)
    return rgba

