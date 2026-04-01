# PART C
from PIL import Image
import stepic

print("Opening secret image...")

# Open image with hidden information
stego_image = Image.open("profile_secret.png")

# Using stepic to decode information
hidden_data = stepic.decode(stego_image)

print("Successful! here is the info:")
print(hidden_data)
