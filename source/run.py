#!C:/Users/ADMIN/AppData/Local/Programs/Python/Python38/python.exe python3

import argparse
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from rich import print
import numpy as np
import time
import os

root = tk.Tk()
root.withdraw()

lookup = [bin(i)[2:].zfill(8) for i in range(256)] # A lookup bin.

#STATUS: WORK
def convert_to_binary(data):
    '''Conver the data to binary that is a string'''
    if isinstance(data, str):
        return ''.join(map(lambda i: lookup[ord(i)], data))
    elif isinstance(data, bytes) or isinstance(data, bytearray):
        return ''.join(map(lambda i: lookup[i], data))
    elif isinstance(data, int) or isinstance(data, bool):
        return lookup[data]
    else:
        raise TypeError("Unsupported type.")

#STATUS: WORK
def hide_text(image_path, secret_text_path, output_name):
    '''Hide the `secret_text_path`'s content into an image.. is it really that secret :3?'''
    
    try:
        image = Image.open(image_path)
    except Image.UnidentifiedImageError:
        print(f'[red bold][ERROR] Input image only accept: .png, .jpeg, .webp, any image formats\nYour file: {image_path}[/]')
        exit()
    with open(secret_text_path, 'r') as file:
        try:
            secret_text = file.read()
        except UnicodeDecodeError:
            print(f'[red bold][ERROR] Secret text only accept: .txt, .md, .log, any text formats\nYour file: {image_path}[/]')
            exit()
    data = convert_to_binary(secret_text)
    iter_data = iter(data)
    image_array = np.array(image) # The image will be converted to Numpy Array
    data_mask = np.array([int(next(iter_data, '0'), 2) for _ in range(np.prod(image_array.shape))]).reshape(image_array.shape) # The data mask
    image_array = (image_array & 254) | data_mask # Apply the mask to the Image
    image_array = image_array.astype(np.uint8) # Check if the data type is uint8 before converting back to original image.
    image = Image.fromarray(image_array) # Convert the numpy array to Image.
    image.save(output_name)

#STATUS: WORK
def convert_to_text(binary_data):
    '''Convert `binary_data` to original text'''
    # A fastest way I can found to convert a binary to a text
    return ''.join(map(lambda x: chr(int(x, 2)), map(''.join, zip(*[iter(binary_data)]*8))))

#STATUS: WORK
def reveal_text(image_path, output_text_path):
    '''Reveal the hidden text from an image and save it to a file'''
    try:
        image = Image.open(image_path)
    except Image.UnidentifiedImageError:
        print(f'[red bold][ERROR] Input image only accept: .png, .jpeg, .webp, any image formats\nYour file: {image_path}[/]')
        exit()

    pixels = np.array(image)
    binary_data = ''.join([np.binary_repr(pixel, width=8)[-1] for pixel in pixels.flatten()]) # The pixels converted to binary, taking the last bit of each.
    
    # Simply delete a filler character
    last_char_index = binary_data.find('00000000')
    if last_char_index != -1:
        binary_data = binary_data[:last_char_index]
        
    text = convert_to_text(binary_data)
    
    # Save the file.
    with open(output_text_path, 'w') as file:
        file.write(text)

#STATUS: WORK
def hide_image(input_image_path, target_image_path, output_image_path):
    # Open the Input image and Target image
    try:
        input_image = Image.open(input_image_path)
    except Image.UnidentifiedImageError:
        print(f'[red bold][ERROR] Input image only accept: .png, .jpeg, .webp, any image formats\nYour file: {input_image_path}[/]')
        exit()
    try:
        target_image = Image.open(target_image_path)
    except Image.UnidentifiedImageError:
        print(f'[red bold][ERROR] Target image only accept: .png, .jpeg, .webp, any image formats\nYour file: {target_image_path}[/]')
        exit()
    
    output_image = Image.new('RGB', target_image.size) # Create a new image for output

    # Iterate over every pixels in the target image.
    # Todo: I can just modify this codes and instead make it faster using NumPy, but I don't have much time to think, so Imma rest this out.
    for x in range(target_image.size[0]):
        for y in range(target_image.size[1]):
            target_pixel = list(target_image.getpixel((x, y)))

            # If the pixel is inside the bounds of the input image, modify it
            if x < input_image.size[0] and y < input_image.size[1]:
                input_pixel = list(input_image.getpixel((x, y)))

                # Hide the input pixel within the target pixel
                for i in range(3):  # Each RGB value
                    target_pixel[i] = (target_pixel[i] & 0xFE) | ((input_pixel[i] & 0x80) >> 7)

            # Save pixel in the output image
            output_image.putpixel((x, y), tuple(target_pixel))

    # Save output image
    output_image.save(output_image_path)

#STATUS: WORK
def reveal_image(input_image_path, output_image_path):
    # Open the input image
    try:
        input_image = Image.open(input_image_path)
    except Image.UnidentifiedImageError:
        print(f'[red bold][ERROR] Input image only accept: .png, .jpeg, .webp, any image formats\nYour file: {input_image_path}[/]')
        exit()
        

    # Create a new image for output
    output_image = Image.new('RGB', input_image.size)

    # Iterate over every pixel in the input image
    # Next version, I am gonna replace this whole code, so it uses NumPy. Again, I need a rest :)
    for x in range(input_image.size[0]):
        for y in range(input_image.size[1]):
            input_pixel = list(input_image.getpixel((x, y)))

            # Reveal hidden pixel
            revealed_pixel = [0, 0, 0]
            for i in range(3):  # Eeach RGB value
                revealed_pixel[i] = (input_pixel[i] & 0x01) << 7

            # Save pixel in the output image
            output_image.putpixel((x, y), tuple(revealed_pixel))

    # Save output image
    output_image.save(output_image_path)

def main():
    print('''
[red]         _____                                      _  [/]
[red]        |_   _|                                    | | [/]
[red]          | | _ __ ___   __ _  ___ _ __ _   _ _ __ | |_[/]
[red]          | || '_ ` _ \ / _` |/ __| '__| | | | '_ \| __|[/]
[red]         _| || | | | | | (_| | (__| |  | |_| | |_) | |_ [/]
         \___|_| |_| |_|\__, |\___|_|   \__, | .__/ \__| 
                         __/ |           __/ | |        
                        |___/           |___/|_|        v.0.1
        
        [red]By:DaemonPooling[/]             
    ''')
    print('')
    # Create a parser for the command-line arguments
    parser = argparse.ArgumentParser(prog="imgcrypt", description='Hide/Reveal an Image or Text on an image.')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-t', '--textXimage', action='store_true', help='A steganography technique that hides a Text in an Image')
    group1.add_argument('-i', '--imageXimage', action='store_true', help='A steganography technique that hides an Image in an Image')

    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('-e', '--encode', action='store_true', help='Encode an image')
    group2.add_argument('-d', '--decode', action='store_true', help='Decode an image')

    parser.add_argument('-o', '--output', type=str, required=False, help='Output file name')


    args = parser.parse_args()

    if args.imageXimage:
        if args.encode:
            # Ask the user to select the input and target image paths
            input_image_path = filedialog.askopenfilename(title = "Select hidden image", initialfile="target_image.jpg")
            target_image_path = filedialog.askopenfilename(title = "Select cover image", initialfile="cover_image.jpg")

            # Use the provided output file name, or ask the user to select the output image path
            if args.output:
                output_image_path = args.output + ".png"
            else:
                output_image_path = filedialog.asksaveasfilename(defaultextension=".png", title = "Select output image path")

            print(f'''[blue bold]Please wait for the process to complete. It may take longer depends on how big is the file. Ok? :D
            [cyan bold]Detailed information: [/]
                [white]- Hidden image: {input_image_path}[/]
                [white]- Hidden image's file size: {os.path.getsize(input_image_path)/1024} KB[/]
                [white]- Cover image: {target_image_path}[/]
                ''')

            start_time = time.time()
            hide_image(input_image_path, target_image_path, output_image_path)
            end_time = time.time()
            execution_time = end_time - start_time

            print(f'''[white]- Cover image's File size: {os.path.getsize(output_image_path)/1024} KB[/]
            [green bold] Process finished in {execution_time:2f}s, file [blue]{output_image_path}[/] has been created.''')

        elif args.decode:
            # Ask the user to select the input and output image paths
            input_image_path = filedialog.askopenfilename(title = "Select input image")

            # Use the provided output file name, or ask the user to select the output image path
            if args.output:
                output_image_path = args.output + ".png"
            else:
                output_image_path = filedialog.asksaveasfilename(defaultextension=".png", title = "Select output image path")
            print(f'''[blue bold]Please wait for the process to complete. It may take longer depends on how big is the file. Ok? :D
[cyan bold]Detailed information: [/]
    [white]- Target image: {input_image_path}[/]
    [white]- Target image's file size: {os.path.getsize(input_image_path)/1024} KB[/]
                  ''')
            start_time = time.time()
            reveal_image(input_image_path, output_image_path)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f'[green bold] Process finished in {execution_time:2f}s, file [blue]{output_image_path}[/] has been created.')
    elif args.textXimage:
        if args.encode:
            # Ask the user to select the input and target image paths
            input_image_path = filedialog.askopenfilename(title = "Select text to hide")
            target_image_path = filedialog.askopenfilename(title = "Select cover image")

            # Use the provided output file name, or ask the user to select the output image path
            if args.output:
                output_image_path = args.output + ".png"
            else:
                output_image_path = filedialog.asksaveasfilename(defaultextension=".png", title = "Select output image path")

            print(f'''[blue bold]Please wait for the process to complete. It may take longer depends on how big is the file. Ok? :D
[cyan bold]Detailed information: [/]
    [white]- Hidden text: {input_image_path}[/]
    [white]- Hidden image's file size: {os.path.getsize(input_image_path)/1024} KB[/]
    [white]- Cover image: {target_image_path}[/]
    [white]- Cover image's File size: {os.path.getsize(target_image_path)/1024} KB[/]
                  ''')
            start_time = time.time()
            hide_text(target_image_path, input_image_path, output_image_path)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f'[green bold] Process finished in {execution_time:2f}s, file [blue]{output_image_path}[/] has been created.')
        elif args.decode:
            # Ask the user to select the input and output image paths
            input_image_path = filedialog.askopenfilename(title = "Select image where text want to be decoded.")

            # Use the provided output file name, or ask the user to select the output image path
            if args.output:
                output_image_path = args.output + ".txt"
            else:
                output_image_path = filedialog.asksaveasfilename(defaultextension=".txt", title = "Select output text path")

            print(f'''[blue bold]Please wait for the process to complete. It may take longer depends on how big is the file. Ok? :D
[cyan bold]Detailed information: [/]
    [white]- Target image: {input_image_path}[/]
    [white]- Target image's file size: {os.path.getsize(input_image_path)/1024} KB[/]
                  ''')
            start_time = time.time()
            reveal_text(input_image_path, output_image_path)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f'[green bold] Process finished in {execution_time:2f}s, file [blue]{output_image_path}[/] has been created.')

if __name__ == "__main__":
    main()