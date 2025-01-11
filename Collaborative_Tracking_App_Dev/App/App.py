"""
Module Name: App.py

Description:
    This module manages video playback and annotation processing. 
    It can load media files (images or videos), track and display 
    frames, and manage annotations associated with the frames. 
    The MediaPlayer class inherits from Frame_Processing 
    and implements threading for playback. Users can select media files 
    for playback, apply filters, and edit annotations.

Usage:
    To run the application, instantiate the MediaPlayer class and call 
    its mainloop() method to start the GUI.

Dependencies:
    - cv2 (OpenCV): For video processing and frame manipulation.
    - PIL (Pillow): For image handling.
    - threading: For managing concurrent video playback.
    - json: For loading and saving annotation data.
    - Frame_processing: custom
    - ObjectTracking: custom
    - ObjectManager: custom

Author: team 120
Date: 19/09/2024
"""

import sys
import os
#Used for testing:
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import cv2
from PIL import Image
import threading
import json
from pathlib import Path
from Frame_processing import Frame_Processing
import ObjectTracking     
from ObjectManager import ObjManager      

class MediaPlayer(Frame_Processing):
    """
    A class to manage video playback and annotation processing.

    Inherits from the `Frame_Processing` class and provides functionality 
    to load videos, track current frames, and manage annotations.

    Attributes:
        current_frame_index (int): Index of the currently processed frame.
        current_frames (list): A list to store frames from the currently loaded video.
        frame_annotations (list): A list to store annotations corresponding to the frames.
        isAnalising (bool): Flag indicating whether the media is currently being analyzed.
        loadVideo (threading.Condition): Condition variable for thread synchronization when loading videos.
        filteredAnno (list): A list to store filtered annotations.
        json_path (str): Path to the JSON file containing annotations.

    Methods:
        __init__(): Initializes a MediaPlayer instance and sets up attributes.
    """

    def __init__(self):
        super().__init__()
        self.current_frame_index = 0  # Track the current frame index 
        self.current_frames=[] #The mechanism for accessing the same video between modes
        self.frame_annotations=[]
        self.isAnalising=False
        self.loadVideo = threading.Condition()
        self.filteredAnno = []
        self.json_path = ""
    
    def manage_media(self):
        """
        Manage the selection and playback of media files.

        This method prompts the user to select a media file. Based on the file type,
        it either loads and displays an image or starts video playback. It sets up the 
        necessary threads and UI elements for playback control.

        Preconditions:
            - The method assumes that the media selection and UI setup have been properly initialized.
            - If a video file is selected, the method expects that `play_video` is defined to handle playback.
        """
        self.select_media()
        
        if self.media_path:
            if self.media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.current_frame = Image.open(self.media_path)
                self.display_frame(self.current_frame)
            else:
                self.video_capture = cv2.VideoCapture(self.media_path)
                if not self.video_thread:
                    self.video_thread = threading.Thread(target=self.play_video)
                    self.video_thread.start()
                    
                    self.pause_button.grid(row=0, column=2, padx=10, pady=10, sticky='w')
            self.YOLO_button.grid(row=0, column=5, padx=10, pady=10, sticky='e')
    
    def start_YOLO(self):
        self.YOLO_thread = threading.Thread(target=self.run_YOLO)
        self.YOLO_thread.start()   

    def start_replay(self):
        self.replay_thread = threading.Thread(target=self.replay_toggle)
        self.replay_thread.start()          

    def play_video(self):
        """
        Continuously read and store frames from the video capture.

        This method runs in a separate thread when the play action is initiated. It reads
        frames from the video until there are no more frames to read or an error occurs. 
        It manages playback pauses through synchronization, ensuring no busy waiting.

        Preconditions:
            - The `video_capture` must be properly initialized and opened before this method is called.
            - The `is_paused` attribute must be managed appropriately to control playback state.
        """ 
        frames=[]
        while True:
            if self.is_paused:  # Synchronization with no busy waiting
                with self.condition:
                    self.condition.wait()
            else:
                ret, frame = self.video_capture.read()
                if not ret:
                    # No more frames or error occurred; break the loop
                    break
                frames.append(frame)
        self.current_frames = frames

        print("[App] Done loading all frames")
        
        for frame in self.current_frames:
            if self.is_paused:  # Synchronization with no busy waiting
                with self.condition:
                    self.condition.wait()
            if not self.isAnalising:
                self.display_frame(frame)
                self.after(30)
        if not self.isAnalising:
            self.replay_button.grid(row=0, column=3, padx=10, pady=10, sticky='w')
    
    def toggle_pause(self):
        """
        Toggle the playback state between paused and playing.

        This method changes the `is_paused` attribute to reflect the new playback state.
        It updates the pause button text accordingly and notifies any waiting threads
        if playback is resumed.

        Preconditions:
            - The `pause_button` must be properly configured in the UI.
        """
        self.is_paused = not self.is_paused
        self.pause_button.config(text="\u25B6" if self.is_paused else "\u23F8")
        if not self.is_paused:
            with self.condition:
                self.condition.notify_all()

    
    def replay_toggle(self):        
        """
        Toggle the replay state for the video playback.

        This method changes the `replay` attribute to indicate whether the video should 
        be replayed. If replaying is enabled, it hides the replay button and plays 
        the processed video frames. The replay state is reset to `False` after playback.

        Preconditions:
            - The `replay_button` must be properly configured in the UI.
            - The `current_frames` must contain valid frames to play.
        """
        self.replay = not self.replay

        if self.replay:
            self.replay_button.grid_forget()
            self.play_processed_video(self.current_frames)
            self.replay = False
            
    def run_YOLO(self):
        """
        Run the YOLO object detection on the selected media file.

        This method pauses the current playback if it's running, updates the UI to indicate 
        that processing is underway, and invokes the YOLO object detection. It processes the 
        frames and retrieves annotations, then resumes playback of the processed frames. 
        Additionally, it saves the annotations to a JSON file.

        Preconditions:
            - The `media_path` must be a valid path to a media file.
        """
        if not self.is_paused:
            self.toggle_pause()

        self.isAnalising = True
        file_path = self.media_path
        self.YOLO_button.config(text="Loading...")
        self.view.update_idletasks()
        self.after(30)
        
        filename = Path(file_path).stem + ".json"
        
        print("[App] Running YOLO")
        processed_frames, annotations = ObjectTracking.media_capture(file_path)
        
        if self.is_paused:  #Pause whatever is playing 
            self.toggle_pause()

        self.current_frames = processed_frames
        self.YOLO_button.config(text="Let's YOLO")
        self.play_processed_video(self.current_frames)

        json_path = Path("./App/JSON_files") / filename
        # Save annotations to a JSON file
        with json_path.open(mode='w') as json_file:
            json.dump(annotations, json_file, indent=4)
        
        self.YOLO_button.forget()
            
    def open_existing(self):
        """
        Open an existing media file and load associated annotations.

        This method allows the user to select a media file and attempts to load 
        its corresponding annotation data from a JSON file. It redraws boxes based 
        on the loaded annotations and updates the UI for playback controls if 
        the media is a video file.

        Preconditions:
            - The corresponding JSON file must exist for the selected media.
        """
        self.select_media()
        media_path = self.media_path
        print(f"[App] media_path{media_path}")
        if self.media_path:
            filename = Path(media_path).stem + ".json"
            self.json_path = Path("./App/JSON_files") / filename
            # Load annotation data from JSON file
            try:
                with self.json_path.open(mode='r') as file:
                    self.frames_annotations = json.load(file)

                self.redraw_boxes(media_path,self.frames_annotations)

                if media_path.lower().endswith(('.mp4', '.avi', '.mov')):
                    self.prev_frame_button.grid(row=0, column=4, padx=10, pady=10, sticky='w')
                    self.play_all.grid(row=0, column=3, padx=10, pady=10, sticky='w')
                    self.next_frame_button.grid(row=0, column=5, padx=10, pady=10, sticky='w')

                self.display_frame(self.current_frames[0])
                self.sort_annotations(self.frames_annotations[0])

            except FileNotFoundError:
                print("[App] No annotations found")
    
    def play(self):
        self.play_processed_video(self.current_frames) 
    
    def filter(self):
        """
        Apply filters to the displayed annotations based on user selection.

        This method retrieves the selected classes and objects, applies the necessary 
        filters to the annotations, and updates the displayed bounding boxes accordingly. 
        It also manages UI elements for editing if a specific object is selected.

        Preconditions:
            - The `frames_annotations` must be initialized and contain valid data.
            - The `get_selected`, `objMan`, and `redraw_boxes` methods must be properly defined.
        """
        print("[App] filter() called...")
        selected_classes, selected_objects = self.get_selected()
        print(selected_classes,selected_objects)  
        self.objMan = ObjManager(self.frames_annotations)
        self.objMan.clear()
        filteredBoxes=[]
        
        # Apply filter
        if selected_classes == []:
            filteredBoxes = self.objMan.data
        elif selected_objects==[]:
            print(f"[App] in if sel_obj")
            filteredBoxes = self.objMan.filterClass(selected_classes[0])
            self.remove_edit_UI()
        else:
            print(f"[App] in else sel_obj")
            print(f"[App] {selected_objects[0]}")
            
            index=self.current_frame_IDs.index(int(selected_objects[0][1]))
            OGID = self.current_frame_OGIDs[index]
            filteredBoxes = self.objMan.filterObjectID(OGID)
            
            if len(selected_objects) == 1:      #The user selects a box from a frame by filtering for that specific box
                self.filteredAnno = filteredBoxes
                entries = self.get_coords(filteredBoxes)
                
                if entries == [] or entries == None:
                    print('[App] No tracking for the selcted object.')
                else:
                    print('[App] Display edit')
                    self.display_coords(entries)
                    
                print(f"[App] Frame {self.current_frame_index} filtered:")
            else:
                self.remove_edit_UI()
        self.redraw_boxes(self.media_path,filteredBoxes)
        self.display_frame(self.current_frames[self.current_frame_index])
        self.sort_annotations(self.frames_annotations[self.current_frame_index])
    
    def editBox_GiveIndexes(self):
        print('[App] frame ID',self.current_frame_index)
        print('[App] object ID whose box is changing',self.filteredAnno[self.current_frame_index][0]["objectID"])
        indexF = self.current_frame_index
        objID = self.filteredAnno[self.current_frame_index][0]["objectID"]
        indexB = self.objMan.getObjIndexInFrame(indexF, objID)
        return indexF, indexB
    
    def editRedisplayFrame(self):
        self.redraw_boxes(self.media_path,self.filteredAnno)
        self.display_frame(self.current_frames[self.current_frame_index])
    
    def editSaveEdits(self):
        print("[App] Saving changes")
        # Hide all movement buttons
        self.move_up_button.grid_remove()
        self.move_down_button.grid_remove()
        self.move_left_button.grid_remove()
        self.move_right_button.grid_remove()
        # Hide stretching buttons
        self.stretch_horizontalally.grid_remove()
        self.stretch_vertically.grid_remove()
        self.squeeze_horizontalally.grid_remove()
        self.squeeze_vertically.grid_remove()
        # Hide text fields and buttons
        self.class_entry.grid_remove()
        self.class_button.grid_remove()
        self.id_entry.grid_remove()
        self.id_button.grid_remove()
        # Optionally hide the Save Changes button itself
        self.save_changes_button.grid_remove()
        self.objMan.writeChanges(self.json_path)

    def editMoveUp(self):
        print("[App] moving up")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editMoveBoundingBoxVerticle(indexF, indexB, -10)
        self.editRedisplayFrame()
        return
    def editMoveDown(self):
        print("[App] moving down")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editMoveBoundingBoxVerticle(indexF, indexB, 10)
        self.editRedisplayFrame()
        return
    def editMoveLeft(self):
        print("[App] moving left")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editMoveBoundingBoxHorizontal(indexF, indexB, -10)
        self.editRedisplayFrame()
        return
    def editMoveRight(self):
        print("[App] moving right")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editMoveBoundingBoxHorizontal(indexF, indexB, 10)
        self.editRedisplayFrame()
        return
    def editClass(self):
        text = self.class_entry.get()
        print(f"[App] editing class {text}")
        if text != "" :
            indexF, indexB = self.editBox_GiveIndexes()
            self.objMan.editLabel(indexF, indexB, text)
            self.editRedisplayFrame()
        return
    def editObjID(self):
        text = self.id_entry.get()
        print(f"[App] editing objID {text}")
        if text != "" :
            indexF, indexB = self.editBox_GiveIndexes()
            self.objMan.editID(indexF, indexB, text)
            self.editRedisplayFrame()
        return
    def editStretchBoxHorz(self):
        print(f"[App] stretching box horz")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editBoundingBoxShape(indexF, indexB, "x1", -5)
        self.objMan.editBoundingBoxShape(indexF, indexB, "x2", 5)
        self.editRedisplayFrame()
        return
    def editStretchBoxVert(self):
        print(f"[App] stretching box vert")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editBoundingBoxShape(indexF, indexB, "y1", -5)
        self.objMan.editBoundingBoxShape(indexF, indexB, "y2", 5)
        self.editRedisplayFrame()
        return
    def editSqueezeBoxHorz(self):
        print(f"[App] squeeze box horz")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editBoundingBoxShape(indexF, indexB, "x1", 5)
        self.objMan.editBoundingBoxShape(indexF, indexB, "x2", -5)
        self.editRedisplayFrame()
        return
    def editSqueezeBoxVert(self):
        print(f"[App] squeeze box vert")
        indexF, indexB = self.editBox_GiveIndexes()
        self.objMan.editBoundingBoxShape(indexF, indexB, "y1", 5)
        self.objMan.editBoundingBoxShape(indexF, indexB, "y2", -5)
        self.editRedisplayFrame()
        return
            
    def move_forward(self):
        """
        Move to the next frame in the current video or image sequence.

        This method increments the `current_frame_index` and updates the displayed frame
        and its associated annotations. If there are filtered entries, it retrieves and
        displays their coordinates. If the end of the frames is reached, it prints a message.

        Returns:
            None

        Preconditions:
            - The `current_frames` list must be populated with frames.
            - The `frames_annotations` list must be properly initialized.
        """
        if self.current_frame_index < len(self.current_frames) - 1:
            self.current_frame_index += 1
            self.display_frame(self.current_frames[self.current_frame_index])
            self.sort_annotations(self.frames_annotations[self.current_frame_index])
            
            if self.entries != []:
                entries = self.get_coords(self.filteredAnno)
                self.display_coords(entries)        
        else:
            print("[App] End of video frames")
    
    def move_back(self):        
        """
        Move to the previous frame in the current video or image sequence.

        This method decrements the `current_frame_index` and updates the displayed frame
        and its associated annotations. If there are filtered entries, it retrieves and
        displays their coordinates. If the beginning of the frames is reached, it prints a message.

        Preconditions:
            - The `current_frames` list must be populated with frames.
            - The `frames_annotations` list must be properly initialized.
        """
        if self.current_frame_index > 0 and self.current_frame_index < len(self.current_frames) - 1:
            self.current_frame_index -= 1
            self.display_frame(self.current_frames[self.current_frame_index])
            self.sort_annotations(self.frames_annotations[self.current_frame_index])
            
            if self.entries != []:
                entries = self.get_coords(self.filteredAnno)
                self.display_coords(entries)        
        else:
            print("[App] Start of video frames")
      
if __name__ == "__main__":
    app=MediaPlayer()
    app.mainloop()