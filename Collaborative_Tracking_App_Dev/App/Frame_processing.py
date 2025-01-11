"""
Module Name: Frame_processing.py

Description:
    This module displays pictures and video media. It provides functionality to process
    and display video frames, apply annotations, and manage media selection through a
    graphical user interface (GUI) built with Tkinter. Users can select media files,
    view images or video, and visualize annotationson frames.

Usage:
    To run the application, instantiate the `Frame_Processing` class and call its methods
    for media selection and frame display.

Dependencies:
    - tkinter: For creating the GUI components.
    - cv2 (OpenCV): For image and video processing.
    - PIL (Pillow): For image handling and conversion to formats compatible with Tkinter.
    - UI_components: A custom module that provides UI components for the application.

Author: team 120
Date: 19/09/2024
"""

import sys
import os
#Used for testing:
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import UI_components

class Frame_Processing(UI_components.UI_Media_Components):
    def __init__(self):
        super().__init__()
    
    def display_frame(self, frame):
        """
        Process and display a given frame on a canvas.

        Args:
            frame: The input frame (image) to be processed and displayed on the canvas.

        Preconditions:
            - `frame` must be a valid image object compatible with the canvas (e.g., a PhotoImage object in Tkinter).
            - The canvas must be properly initialized and ready for image rendering.
        """
        frame = self.frame_processing(frame)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=frame)
        self.canvas.image = frame
        
    def frame_processing(self, frame):
        """
        Process an input frame to ensure it fits the canvas while maintaining its aspect ratio.

        Args:
            frame: The input frame to be processed.

        Returns:
            ImageTk.PhotoImage: The processed frame as a PhotoImage object ready for display on the canvas.

        Preconditions:
            - The canvas must be properly initialized and have a defined height.
        """
        canvas_height = self.canvas.winfo_height()
        new_height = canvas_height

        if hasattr(frame, 'shape'):
            aspect_ratio = frame.shape[1] / frame.shape[0]
            new_width = int(canvas_height * aspect_ratio)

            frame = cv2.resize(frame, (new_width, new_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
        else:
            if hasattr(frame, 'height'):
                aspect_ratio = frame.width / frame.height
                new_width = int(canvas_height * aspect_ratio)
                frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)

        frame = ImageTk.PhotoImage(frame)
        return frame

    def play_processed_video(self,frames):
        """
        Play a sequence of processed video frames on a canvas.

        Args:
            frames (list): A list of frames (images) to be displayed, which should be in a format 
                        compatible with the `frame_processing` method.

        Preconditions:
            - The `frames` list must contain valid image frames that can be processed.
            - The canvas must be properly initialized and ready for image rendering.

        Note:
            The method assumes that the `is_paused` attribute and `condition` threading condition are defined 
            to manage playback control. It also assumes that the `after` method is available for introducing 
            delays in the playback loop.
        """
        for frame in frames:
            # Handle pause if needed
            if self.is_paused:  # Synchronization with no busy waiting
                with self.condition:
                    self.condition.wait()

            # Resize and format the frame
            frame = self.frame_processing(frame)

            self.canvas.create_image(0, 0, anchor=tk.NW, image=frame)
            self.canvas.image = frame

            self.canvas.update()
            self.after(30)
        if not self.media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.replay_button.grid(row=0, column=3, padx=10, pady=10, sticky='w')

    def select_media(self):
        """
        Open a file dialog to allow the user to select a media file.

        The selected file path is stored in the `self.media_path` attribute for later use.
        If the user cancels the file selection, `self.media_path` will be set to an empty string.

        Preconditions:
        - This method should be called in a context where the GUI mainloop is running.
        """
        self.media_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(
                ("MP4 files", "*.mp4"),
                ("MP4 files", "*.avi"),
                ("Image files", "*.jpg"),
                ("Image files", "*.jpeg"),
                ("All files", "*.*")
            )
        )
    
    def process_annotations(self, frame, annotations):
        """
        Process and draw annotations on a given frame.

        For each annotation in the list, this method extracts the object ID, class name,
        confidence level, and bounding box coordinates. It then draws a circle at the center
        of the bounding box, a rectangle around the bounding box, and adds text annotations.

        Args:
            frame (numpy.ndarray): The image frame on which to draw annotations.
            annotations (list): A list of annotation dictionaries, where each dictionary contains
                                the keys "objectID", "class", "confidence", "bounding_box", and "colours".
                                - "bounding_box" should contain "x1", "y1", "x2", "y2".
                                - "colours" should contain "B", "G", "R" for color values.

        Returns:
            None

        Preconditions:
            - The `frame` must be a valid image array compatible with OpenCV.
            - The `annotations` list must be properly structured as described above.
        """
        for annotation in annotations:
            if annotation != []: # this if is done for filtered frames in which some boxes have all their content removed
                ID = annotation["objectID"]
                
                class_name=annotation["class"]
                confidence=annotation["confidence"]
                bbox = annotation["bounding_box"]
                colours=annotation["colours"]

                B,G,R=colours["B"],colours["G"],colours["R"]
                x1, y1 = bbox["x1"], bbox["y1"]
                x2, y2 = bbox["x2"], bbox["y2"]
                cx=int((x1+x2)/2)
                cy=int((y1+y2)/2)

                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(frame, str(ID), (cx, cy - 7), 0, 1, (0, 0, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
                cv2.putText(frame, f"{class_name} - {str(ID)} - {confidence}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (B, G, R), 2) 
        
    def redraw_boxes(self,media_path,annotations):
        """
        Read frames from a media file and redraw bounding boxes based on annotations.

        This method captures video frames from the specified media file, processes
        each frame to draw annotations (bounding boxes, circles, and text), and
        stores the processed frames for later use.

        Args:
            media_path (str): The file path to the media (video) file.
            annotations (list): A list of annotation lists, where each inner list contains
                                annotation dictionaries for a corresponding frame.

        Returns:
            None

        Preconditions:
            - The `media_path` must be a valid path to a video file accessible by OpenCV.
            - The `annotations` list must have the same length as the number of frames in the video.
        """
        media_capture = cv2.VideoCapture(media_path)
        self.current_frames=[]
        current_frame_index=0

        while media_capture.isOpened():
            ret, frame = media_capture.read()
            if not ret:
                break
                    
            if current_frame_index  < len(annotations):
                self.process_annotations(frame, annotations[current_frame_index])
                self.current_frames.append(frame)
            current_frame_index += 1
        media_capture.release()
    
    def get_coords(self,filteredBoxes):
        """
        Retrieve the coordinates of the bounding box for the current frame.

        This method extracts the bounding box coordinates from the filtered boxes 
        for the current frame index. It returns the coordinates in the order 
        [x1, x2, y1, y2].

        Args:
            filteredBoxes (list): A list of lists, where each inner list contains 
                                bounding box dictionaries for a corresponding frame.

        Returns:
            list: A list containing the bounding box coordinates in the format [x1, x2, y1, y2].

        Preconditions:
            - `filteredBoxes` must contain entries for `self.current_frame_index`.
            - The bounding box dictionary must contain the keys "bounding_box" 
            with valid coordinates "x1", "y1", "x2", and "y2".
        """
        print(filteredBoxes[self.current_frame_index])
        box=filteredBoxes[self.current_frame_index][0]
        bbox = box["bounding_box"]
        x1, y1 = bbox["x1"], bbox["y1"]
        x2, y2 = bbox["x2"], bbox["y2"]
        return [x1,x2,y1,y2]