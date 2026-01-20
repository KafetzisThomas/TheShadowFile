# source: https://www.geeksforgeeks.org/python/image-based-steganography-using-python/

import warnings

# silence this specific pillow deprecation warning for now
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*getdata.*")

import os
import sys
from PIL import Image
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

banner = rf"""{Fore.LIGHTGREEN_EX}{Style.BRIGHT}
  ________        _____ __              __              _______ __   
 /_  __/ /_  ___ / ___// /_  ____ _____/ /___ _      __/ ____(_) /__ 
  / / / __ \/ _ \\__ \/ __ \/ __ `/ __  / __ \ | /| / / /_  / / / _ \
 / / / / / /  __/__/ / / / / /_/ / /_/ / /_/ / |/ |/ / __/ / / /  __/
/_/ /_/ /_/\___/____/_/ /_/\__,_/\__,_/\____/|__/|__/_/   /_/_/\___/ 

By KafetzisThomas
"""

def genData(data):
    """
    Converts input text into a list of 8-bit binary strings.
    """
    return [format(ord(i), '08b') for i in data]

def modPix(pix, data):
    """
    Modifies pixel values to encode the binary data.
    """
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)
    
    for i in range(lendata):
        # Extract 3 pixels (9 values) at a time
        pixels = [value for value in next(imdata)[:3] + next(imdata)[:3] + next(imdata)[:3]]

        # Modify pixel values based on binary data
        for j in range(8):
            if datalist[i][j] == '0' and pixels[j] % 2 != 0:
                pixels[j] -= 1
            elif datalist[i][j] == '1' and pixels[j] % 2 == 0:
                pixels[j] = pixels[j] - 1 if pixels[j] != 0 else pixels[j] + 1
        
        # Set termination flag (last pixel even means continue, odd means stop)
        if i == lendata - 1:
            pixels[-1] |= 1  # Make odd (stop flag)
        else:
            pixels[-1] &= ~1  # Make even (continue flag)
        
        yield tuple(pixels[:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

def encode(newimg, data):
    """
    Encodes the modified pixel data into the new image.
    """
    w = newimg.size[0]
    (x, y) = (0, 0)
    
    # TODO: replace Image.Image.getdata() with get_flattened_data()
    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        x = 0 if x == w - 1 else x + 1
        y += 1 if x == 0 else 0

    return newimg

def decode(image):
    """
    Decodes hidden text from an image.
    """
    imgdata = iter(image.getdata())
    data = ""

    while True:
        pixels = [value for value in next(imgdata)[:3] + next(imgdata)[:3] + next(imgdata)[:3]]
        binstr = ''.join(['1' if i % 2 else '0' for i in pixels[:8]])
        data += chr(int(binstr, 2))

        if pixels[-1] % 2 != 0:
            break

    return data

def main():
    print(banner)
    print(f"{Fore.LIGHTCYAN_EX}[1] Embed Secret{Fore.RESET}   - Hide a text message inside an image")
    print(f"{Fore.LIGHTCYAN_EX}[2] Extract Secret{Fore.RESET} - Reveal a hidden message from an image")
    
    try:
        choice = input(f"\n{Fore.LIGHTYELLOW_EX}root@theshadowfile:~# {Fore.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTCYAN_EX}[!] Exiting...")
        sys.exit()

    if choice == '1':
        img = input("Enter image filename (e.g. ENTER: jack_russell.jpg): ")
        try:
            image = Image.open(img or "jack_russell.jpg", 'r')
            data = input("Enter secret message: ")
            if not data:
                raise ValueError("Secret message cannot be empty.")

            newimg = image.copy()
            encoded_image = encode(newimg, data)

            filename = input("Enter output filename (e.g. ENTER: hidden.png): ")
            save_path = os.path.join("output", filename or "hidden.png")
            encoded_image.save(save_path)

            print(f"{Fore.LIGHTGREEN_EX}[+] Secret hidden in output/{filename} successfully!{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[!] Error: {e}{Fore.RESET}")

    elif choice == '2':
        img = input("Enter image filename (e.g. ENTER: output/hidden.png): ")
        try:
            image = Image.open(img or "output/hidden.png", 'r')
            hidden_text = decode(image)
            print("\n" + Fore.GREEN + "--------------------" + "-" * len(hidden_text))
            print(f"[+] HIDDEN MESSAGE: {Fore.LIGHTRED_EX}{hidden_text}")
            print(Fore.GREEN + "--------------------" + "-" * len(hidden_text))
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[!] Error: {e}{Fore.RESET}")

    else:
        print(f"{Fore.LIGHTRED_EX}[!] Invalid selection. Exiting...")

if __name__ == "__main__":
    main()
