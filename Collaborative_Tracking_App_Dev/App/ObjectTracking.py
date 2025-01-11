"""
Module Name: ObjectTracking.py

Description:
    This module implements object tracking using a YOLO instance. 
    It captures video frames, feeds them to the YOLO instance to detects items and
    and annotates each frame with bounding boxes, class names, and color information,
    then calculates tracking parameters across frames to track objects in a video.

Usage:
    To run the application, invoke the media_capture() function with the path to a video file.

Dependencies:
    - OpenCV
    - NumPy
    - YOLO (YOLO_API)
    - colormath

Author: team 120
Date: 19/09/2024
"""

import sys
import os
#Used for testing:
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import cv2
from YOLO.YOLO_API import YOLO_model
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
import math

# Instantialize the YOLO model
model = YOLO_model()

def parse_results(class_id, score, box, average_colour, class_labels, class_colours):
    """
    Parse the results from YOLO model.

    This function extracts and processes bounding box and class information from 
    the detection results. It computes the center coordinates of the bounding box, 
    retrieves the class name and its associated color, and converts the average color 
    from sRGB to Lab color space.

    Args:
        class_id (int): The index of the detected class.
        score (list or array): The confidence score for the detection.
        box (tuple): A tuple containing the bounding box coordinates (x1, y1, x2, y2).
        average_colour (tuple): A tuple representing the average color (R, G, B).
        class_labels (list): A list of class names corresponding to class IDs.
        class_colours (list): A list of colors corresponding to class IDs.

    Returns:
        list: A list containing the bounding box coordinates, center coordinates, 
              class name, Lab color representation, RGB color values, confidence score, 
              and a placeholder string.

    Preconditions:
        - `class_id` must be a valid index in `class_labels` and `class_colours`.
        - `box` must contain four numeric values representing the bounding box corners.
        - `average_colour` must contain three numeric values representing RGB color.
    """
    confidence=round(score[0],2)
    class_name=class_labels[class_id]
    (x1, y1, x2, y2) = box
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)

    class_colour=class_colours[class_id]
    B, G, R = class_colour[0], class_colour[1], class_colour[2]

    srgb = sRGBColor(average_colour[0]/255.0, average_colour[1]/255.0, average_colour[2]/255.0)
    lab = convert_color(srgb, LabColor)

    return [x1, y1, x2, y2, cx, cy, class_name, lab, B, G, R, confidence, "placeholder"]

def delta_e_cie2000(lab1, lab2):
    """
    Popular algorithm to compare two LAB colours

    This function computes the perceptual difference between two colors
    represented in the CIELAB color space using the CIEDE2000 formula. 
    This formula accounts for various factors that influence human perception
    of color differences.

    Args:
        lab1 (LabColor): The first color in Lab color space.
        lab2 (LabColor): The second color in Lab color space.

    Returns:
        float: The calculated CIEDE2000 color difference between `lab1` and `lab2`.

    """
    L1, a1, b1 = lab1.lab_l, lab1.lab_a, lab1.lab_b
    L2, a2, b2 = lab2.lab_l, lab2.lab_a, lab2.lab_b

    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)

    C_mean = (C1 + C2) / 2

    G = 0.5 * (1 - math.sqrt(C_mean**7 / (C_mean**7 + 25**7)))

    a1_prime = (1 + G) * a1
    a2_prime = (1 + G) * a2

    C1_prime = math.sqrt(a1_prime**2 + b1**2)
    C2_prime = math.sqrt(a2_prime**2 + b2**2)

    h1_prime = math.atan2(b1, a1_prime) if b1 != 0 or a1_prime != 0 else 0
    h2_prime = math.atan2(b2, a2_prime) if b2 != 0 or a2_prime != 0 else 0

    if h1_prime < 0:
        h1_prime += 2 * math.pi
    if h2_prime < 0:
        h2_prime += 2 * math.pi

    delta_L_prime = L2 - L1
    delta_C_prime = C2_prime - C1_prime

    delta_h_prime = h2_prime - h1_prime
    if abs(h1_prime - h2_prime) > math.pi:
        if h2_prime <= h1_prime:
            delta_h_prime += 2 * math.pi
        else:
            delta_h_prime -= 2 * math.pi

    delta_H_prime = 2 * math.sqrt(C1_prime * C2_prime) * math.sin(delta_h_prime / 2)

    L_mean_prime = (L1 + L2) / 2
    C_mean_prime = (C1_prime + C2_prime) / 2

    h_mean_prime = (h1_prime + h2_prime) / 2
    if abs(h1_prime - h2_prime) > math.pi:
        h_mean_prime += math.pi
    if h_mean_prime >= 2 * math.pi:
        h_mean_prime -= 2 * math.pi

    T = (1 - 0.17 * math.cos(h_mean_prime - math.radians(30)) +
            0.24 * math.cos(2 * h_mean_prime) +
            0.32 * math.cos(3 * h_mean_prime + math.radians(6)) -
            0.20 * math.cos(4 * h_mean_prime - math.radians(63)))

    SL = 1 + ((0.015 * ((L_mean_prime - 50) ** 2)) / math.sqrt(20 + (L_mean_prime - 50) ** 2))
    SC = 1 + 0.045 * C_mean_prime
    SH = 1 + 0.015 * C_mean_prime * T

    delta_theta = math.radians(30) * math.exp(-((h_mean_prime - math.radians(275)) / math.radians(25))**2)
    RC = 2 * math.sqrt(C_mean_prime**7 / (C_mean_prime**7 + 25**7))

    RT = -math.sin(2 * delta_theta) * RC

    delta_E = math.sqrt(
        (delta_L_prime / SL) ** 2 +
        (delta_C_prime / SC) ** 2 +
        (delta_H_prime / SH) ** 2 +
        RT * (delta_C_prime / SC) * (delta_H_prime / SH)
    )

    return delta_E

def calculate_overlap_area(box1, box2):
    """
    Calculate the percentage of overlap between two bounding boxes.

    This function computes the Intersection over Union (IoU) percentage
    between two boxes defined by their corner coordinates. It returns the 
    percentage of the overlap area relative to the total area of the boxes.

    Args:
        box1 (tuple): A tuple containing the coordinates of the first box 
                      in the format (x1, y1, x2, y2).
        box2 (tuple): A tuple containing the coordinates of the second box 
                      in the format (x1, y1, x2, y2).

    Returns:
        float: The percentage of overlap between the two boxes. If there 
               is no overlap, returns 0.0.

    Preconditions:
        - The coordinates in the boxes must be in the format (x1, y1, x2, y2),
          where (x1, y1) are the coordinates of the top-left corner and 
          (x2, y2) are the coordinates of the bottom-right corner.
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Determine the coordinates of the intersection rectangle
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)

    # Check if there is no overlap
    if x_left >= x_right or y_top >= y_bottom:
        return 0.0  # No overlap

    # Calculate the intersection area
    overlap_width = x_right - x_left
    overlap_height = y_bottom - y_top
    intersection_area = overlap_width * overlap_height

    # Calculate the area of both boxes
    area_box1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area_box2 = (x2_2 - x1_2) * (y2_2 - y1_2)

    # Calculate the union area
    union_area = area_box1 + area_box2 - intersection_area

    # Calculate the percentage of overlap (IoU)
    overlap_percentage = (intersection_area / union_area) * 100

    return overlap_percentage

def media_capture(file_path):
    """
    Captures video frames and annotates detected objects using a YOLO model.

    This function processes a video file frame by frame, detecting objects using 
    the YOLO model and annotating each frame with bounding boxes, class names, 
    and other information. It tracks the detected objects across frames 
    and handles object tracking.

    Args:
        file_path (str): The path to the video file to be processed.

    Returns:
        tuple: A tuple containing:
            - processed_frames (list): A list of frames with annotations applied.
            - annotations (list): A list of annotations for each detected object in each frame.

    Preconditions:
        - The input video file must be in a format supported by OpenCV.
        - The YOLO model must be initialized and accessible via the global `model` variable.
    """
    cap = cv2.VideoCapture(file_path) # Captures a video
    count = 0 # Keeps track of number of objects

    class_labels = model.get_classes() # Class names
    class_colours = model.get_colours() # Class colours

    annotations=[] # Array that will keep annotations to dump to file
    processed_frames=[] # Array that will keep annotated frames
    
    tracking_objects = {}
    track_id = 0

    disappeared_objects = {}

    while True:
        json_frame_annotations=[] # Array that keeps track of the json annotations of the current frame
        dict_frame_annotations={} # Dictionary to keep info of each frame
        ret, frame = cap.read() # Read a frame from the video cap
        count += 1 
        if not ret:
            break

        # Point to current frame
        bbox_cur_frame = []

        # Results from the YOLO model for the frame
        (class_ids, scores, boxes, average_colours) = model.detect_frame(frame)

        for (class_id, score, box, average_colour) in zip(class_ids, scores, boxes, average_colours):
            object_details = parse_results(class_id, score, box, average_colour, class_labels, class_colours)
            
            bbox_cur_frame.append(tuple(object_details[:8]))
            dict_frame_annotations[tuple(object_details[:8])] = object_details

        # Only at the beginning we compare previous and current frame
        if count == 1:
            for pt in bbox_cur_frame:
                tracking_objects[track_id]=pt
                dict_frame_annotations[pt][12] = track_id 
                track_id += 1

        else:
            tracking_objects_copy = tracking_objects.copy()
            bbox_cur_frame_copy = bbox_cur_frame.copy()

            for object_id, pt2 in tracking_objects_copy.items():
                object_exists = False
                for pt in bbox_cur_frame_copy:
                    box1 = (pt[0],pt[1],pt[2],pt[3])
                    box2 = (pt2[0],pt2[1],pt2[2],pt2[3])

                    cx_1 = int(pt[4])
                    cy_1 = int(pt[5])
                    cx_2 = int(pt2[4])
                    cy_2 = int(pt2[5])

                    class1 = str(pt[6])
                    class2 = str(pt2[6])

                    LAB_1 = pt[7]
                    LAB_2 = pt2[7]

                    overlap =  calculate_overlap_area(box1, box2)
                    distance = math.hypot(cx_2 - cx_1, cy_2 - cy_1) 
                    delta_e = delta_e_cie2000(LAB_1,LAB_2)

                    if (class1==class2) and (distance < 20 or overlap > 60) and delta_e <= 10:
                        tracking_objects[object_id] = pt
                        object_exists = True
                        dict_frame_annotations[pt][12] = object_id
                        if pt in bbox_cur_frame:
                            bbox_cur_frame.remove(pt)
                        continue
                
                if not object_exists:
                    disappeared_objects[object_id] = pt2
                    tracking_objects.pop(object_id)

            # Check for objects that may have reappeared
            for object_id, pt2 in list(disappeared_objects.items()):
                for pt in bbox_cur_frame.copy():
                    class1 = str(pt[6])
                    class2 = str(pt2[6])

                    LAB_1 = pt[7]
                    LAB_2 = pt2[7]

                    delta_e = delta_e_cie2000(LAB_1,LAB_2)

                    if class1==class2 and delta_e < 5:  # If the object reappears close to its last position
                        tracking_objects[object_id] = pt  # Reassign the same object_id
                        dict_frame_annotations[pt][12] = object_id
                        if pt in bbox_cur_frame:
                            bbox_cur_frame.remove(pt)  # Remove from unmatched objects
                        del disappeared_objects[object_id]  # Remove from disappeared list
                        break

            # Add new IDs found
            for pt in bbox_cur_frame:
                tracking_objects[track_id] = pt
                dict_frame_annotations[pt][12] = track_id
                track_id += 1

        for an in dict_frame_annotations.values():
            x1, y1, x2, y2, cx, cy, B, G, R = map(int, (an[0], an[1], an[2], an[3], an[4], an[5], an[8], an[9], an[10]))
            class_name = str(an[6])
            confidence = str(an[11])
            IDstr = str(an[12])

            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, IDstr, (cx, cy - 7), 0, 1, (0, 0, 255), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
            cv2.putText(frame, f"{class_name} - {IDstr} - {confidence}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (B, G, R), 2)
            annotation = {
                "class": class_name,
                "confidence": confidence,
                "objectID": IDstr,
                "colours": {
                    "B":B,
                    "G":G,
                    "R":R,
                },

                "bounding_box": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                },
            }
            json_frame_annotations.append(annotation)

        annotations.append(json_frame_annotations)
        processed_frames.append(frame)
    return processed_frames, annotations