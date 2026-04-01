# PART A
from PIL import Image


def set_LSB(value, bit):
    if bit == '0':
        value = value & 254

    else:
        value = value | 1
    return value

def get_LSB(value):
    # Checks if the pixel value is even or odd
    if value & 1 == 0:
        return '0'
    else:
        return '1'

def get_pixel_pairs(iterable):
    # Combines pixels into two groups
    a = iter(iterable)
    return zip(a, a)

def hide_message(image_path, secret_message, output_path):
    print(f"Hiding secret message in {image_path}...")

    # Adds a null character at the end for extractor to end
    secret_message += chr(0)

    # Opens image and converts RGB alpha
    c_image = Image.open(image_path)
    c_image = c_image.convert('RGBA')

    # Gets modified pixels
    out_image = Image.new(c_image.mode, c_image.size)
    pixList = list(c_image.getdata())
    newArray = []

    # Goes through characters in secret message
    for i in range(len(secret_message)):
        # Converts text character into binary string
        charInt = ord(secret_message[i])
        binary_char = str(bin(charInt))[2:].zfill(8)

        # Gets pixels from original image
        pix1 = pixList[i * 2]
        pix2 = pixList[(i * 2) + 1]

        newpix1 = []
        newpix2 = []

	# Hides first and last four bits in the first and second pixel's RGBA values
        for j in range(0, 4):
            newpix1.append(set_LSB(pix1[j], binary_char[j]))


        for j in range(0, 4):
            newpix2.append(set_LSB(pix2[j], binary_char[j + 4]))

        # Saves modified pixel into arrary
        newArray.append(tuple(newpix1))
        newArray.append(tuple(newpix2))

    # Copies the other original pixels
    pixels_used = len(secret_message) * 2
    newArray.extend(pixList[pixels_used:])

    # Saves the image and prints message
    out_image.putdata(newArray)
    out_image.save(output_path)
    print("Image saved successfully!")
    return output_path

def extract_message(image_path):
    print(f"Extracting hidden data from {image_path}...")
    c_image = Image.open(image_path)
    pixel_list = list(c_image.getdata())
    message = ""

    # Goes over pixel pairs
    for pix1, pix2 in get_pixel_pairs(pixel_list):
        message_byte = "0b"

        # Pull the hidden bits out of first and second pixel, and if it reaches a null character confirms end of message
        for p in pix1:
            message_byte += get_LSB(p)

        for p in pix2:
            message_byte += get_LSB(p)

        if message_byte == "0b00000000":
            break

        # Converts the binary message back to readable text
        message += chr(int(message_byte, 2))

    return message

if __name__ == "__main__":
    input_file = 'compay_logo.png'
    secret_ip = 'TARGET:192.168.1.50'
    output_file = 'company_logo_stego.png'

    hide_message(input_file, secret_ip, output_file)

    # Runs extraction and prints verification message
    extracted_text = extract_message(output_file)
    print(f"Verification check. Extracted text is: {extracted_text}")
