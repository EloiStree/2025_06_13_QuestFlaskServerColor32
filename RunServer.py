# pip install opencv-python flask jsonify Pillow pyzbar numpy pytesseract

import os
import struct
from flask import Flask, request, jsonify
from PIL import Image
import io
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import time
import cv2
import numpy as np

app = Flask(__name__)
import os

# Get the absolute path of the current file
file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(file_path)


def try_parse_width_height_color32_to_image(bytes_array_store_color32:str, width,height):
    image_as_bytes_array = np.frombuffer(bytes_array_store_color32, dtype=np.uint8)
    image_as_array = image_as_bytes_array.reshape((height, width, 4))  # Assuming 4 channels (RGBA)
    image = Image.fromarray(image_as_array, 'RGBA')
    return image

def try_parse_width_height_color32_bytes_to_image(bytes_color32):
    bytes_color32 = bytes_color32
    int_little_endian_width = int.from_bytes(bytes_color32[:4], byteorder='little')
    int_little_endian_height = int.from_bytes(bytes_color32[4:8], byteorder='little')
    bytes_color32 = bytes_color32[8:]
    image = try_parse_width_height_color32_to_image(bytes_color32,int_little_endian_width,int_little_endian_height)
    return image

def save_image_near_server(path_to_save_file:str , image: Image.Image):
    if path_to_save_file is not None:
        image.save(path_to_save_file, format='PNG')


def save_bytes_as_raw_color32(path_bytes_32:str, bytes_width_height_color32:bytes):
    with open(path_bytes_32, 'wb') as f:
        f.write(bytes_width_height_color32)

def save_raw_color32_and_image(file_name_no_extension:str, bytes_width_height_color32:bytes):
    int_little_endian_width = int.from_bytes(bytes_width_height_color32[:4], byteorder='little')
    int_little_endian_height = int.from_bytes(bytes_width_height_color32[4:8], byteorder='little')
    bytes_width_height_color32 = bytes_width_height_color32[8:]
    megas_bytes = len(bytes_width_height_color32) / (1024 * 1024)
    image_as_bytes_array = np.frombuffer(bytes_width_height_color32, dtype=np.uint8)
    pixel_count = image_as_bytes_array.size // 4  
    string_path_of_image = file_name_no_extension + '.color32'
    path_bytes_32 = os.path.join(directory_path, string_path_of_image)
    save_bytes_as_raw_color32(path_bytes_32, bytes_width_height_color32)

    path_image = os.path.join(directory_path, file_name_no_extension+ '.png')
    image = try_parse_width_height_color32_to_image(bytes_width_height_color32,int_little_endian_width,int_little_endian_height)
    save_image_near_server(path_image, image)
    return jsonify({'message': 'Image saved successfully'})



def dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

@app.route('/image/post/get_biggest_circle', methods=['POST'])
def get_biggest_circle():
    print ("Start Bigest Circle Detection")
    bytes_color32 = request.get_data()
    image = try_parse_width_height_color32_bytes_to_image(bytes_color32)

    prevCircle = None    
    gray_frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2GRAY)
    blur_frame = cv2.GaussianBlur(gray_frame, (17,17), 0)
    circles = cv2.HoughCircles(blur_frame, cv2.HOUGH_GRADIENT, 
                               dp=1.2,
                                 minDist=100,
                                   param1=100,
                                     param2=30,
                                       minRadius=75,
                                         maxRadius=0)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        chosen = None
        dist = 0
        for i in circles[0, :]:
            radius = i[2]
            if chosen is None:
                chosen = i
                dist = radius
            else:
                if radius > dist:
                    dist = radius
                    chosen = i
        if chosen is not None:
            return jsonify({
                'x': int(chosen[0]),
                'y': int(chosen[1]),
                'radius': int(chosen[2])
            })
    
    return "No circles found"

@app.route('/image/post/get_scancode', methods=['POST'])
def post_scan_from_color32():
    bytes_color32 = request.get_data()
    image = try_parse_width_height_color32_bytes_to_image(bytes_color32)
    decoded_objects = decode(image)
    barcode_data = ""
    for obj in decoded_objects:
        barcode_data += f"{obj.type}:{obj.data.decode('utf-8')}\n"
        print("Type:", obj.type)
        print("Data:", obj.data.decode("utf-8"))
    return barcode_data

@app.route('/image/post/get_text', methods=['POST'])
def post_tesseract_from_color32():
    bytes_color32 = request.get_data()
    image = try_parse_width_height_color32_bytes_to_image(bytes_color32)

    # not implemented yet
    return ""



@app.route('/image/save/png/date', methods=['POST'])
def save_image_with_date():
    date_time_yyyy_mm_dd_hh_mm_ss = time.strftime("%Y_%m_%d_%H_%M_%S")
    save_raw_color32_and_image('image_' + date_time_yyyy_mm_dd_hh_mm_ss, request.get_data())
    return jsonify({'message': 'Image saved successfully at ' + date_time_yyyy_mm_dd_hh_mm_ss})

@app.route('/image/save/png', methods=['POST'])
def save_image():
    save_raw_color32_and_image('image', request.get_data())
    return jsonify({'message': 'Image saved successfully'})



@app.route('/image/save/camerapi/context_imagexr', methods=['POST'])
def save_image_in_open_xr():

    # Save the OpenXR Root
    # Save the OpenXR Camera Center
    # Save the OpenXR Camera Left Eye
    # Save the OpenXR Camera Right Eye
    # Is Image left eye or right eye?

    # To code Later 
    return ""

@app.route('/image/save/camerapi/context_imagedepthxr', methods=['POST'])
def save_image_in_open_xr_with_depth():

    # Save the OpenXR Root
    # Save the OpenXR Camera Center
    # Save the OpenXR Camera Left Eye
    # Save the OpenXR Camera Right Eye
    # Is Image left eye or right eye?
    # Depth Array of depth values

    # To code Later 
    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
