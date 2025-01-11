"""
Module Name: UI_Media_Components.py

Description:
    This module implements a graphical user interface (GUI) for media display and editing 
    using Tkinter. It allows users to manage and annotate media files, such as videos, 
    with features for playback, annotation viewing, and object tracking.

Usage:
    To run the application, create an instance of the UI_Media_Components class and call 
    the mainloop method:
    
    app = UI_Media_Components()
    app.mainloop()

Dependencies:
    - tkinter: For GUI components.
    - threading: For handling video playback in a separate thread.
    - cv2: For video frame handling.
    - PIL (Pillow): For image processing.

Author: team 120
Date: 19/09/2024
"""
import sys
import os
#Used for testing:
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import ttk
import threading

class UI_Media_Components(tk.Tk):
    """
    UI_Media_Components inherits from tkinter.Tk and serves as the main GUI application window. 
    It provides components for displaying and editing media (like videos) with interaction options.
    """
    def __init__(self):
        """
        Initialize the main window, configure window settings, and set up UI elements.
        """
        super().__init__()
        self.title("YOAT Team TJM")
        self.geometry("1920x1080")
        self.configure(bg="#ECECEC")
        self.grid_rowconfigure(1, weight=1)  # Make row 1 (content_frame) expandable
        self.grid_columnconfigure(0, weight=1)  # Ensure column 0 expands to full width

        self.media_path = ""
        self.video_reader = None
        self.current_frame = None
        self.is_paused = False
        self.replay = False
        self.entries_widgets = {}
        self.array_of_classes=['Person','Car','Backpack','Dog']
        self.condition = threading.Condition()
        self.entries = []
        self.current_frame_IDs = []
        self.current_frame_OGIDs = []

        # Create Notebook (tab container)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))  # Fill horizontally (no vertical expansion)
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Helvetica', 18, 'bold'))

        # Create frames for each tab
        self.view = ttk.Frame(self.notebook)
        self.edit = ttk.Frame(self.notebook)

        self.notebook.add(self.view, text='View', padding=(10, 5))
        self.notebook.add(self.edit, text='Edit', padding=(10, 5))

        # Create a frame to hold the canvas and side panel, shared between view and edit modes
        self.content_frame = tk.Frame(self, bg="#ECECEC")
        #self.content_frame.pack(fill='both', expand=True)

        # Configure grid layout for content_frame
        self.content_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)  # This will expand vertically and horizontally
        self.content_frame.grid_columnconfigure(0, weight=8)  # 70% for the canvas
        self.content_frame.grid_columnconfigure(1, weight=2)  # 30% for the side panel
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Shared canvas between View and Edit tabs
        self.canvas = tk.Canvas(self.content_frame, bg="black")
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')  # Canvas on the left side (70%)

        # Side panel (30% width), it will be shared by both View and Edit modes
        self.side_panel = tk.Frame(self.content_frame, bg="#ECECEC")
        self.side_panel.grid(row=0, column=1, sticky='nsew')

        # Add heading to side panel
        self.side_panel_label = tk.Label(self.side_panel, text="Side Panel", font=("Helvetica", 18, "bold"), bg="#ECECEC")
        self.side_panel_label.pack(pady=20)

        # View mode control frame (inside side panel)
        self.view_frame = tk.Frame(self.side_panel, bg="#ECECEC")
        self.view_frame.pack(fill='both')

        # Edit mode control frame (inside side panel)
        self.edit_frame = tk.Frame(self.side_panel, bg="#ECECEC")
        self.edit_frame.pack(fill='both')

        # Define buttons for the Edit tab
        self.review_button = tk.Button(
        self.edit, text="Open existing annotation", command=self.open_existing,
        fg="black", font=("Helvetica", 16, "bold")
        )
        self.review_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.next_frame_button = tk.Button(
            self.edit, text="\u23E9", command=self.move_forward,
            fg="black", font=("Helvetica", 25, "bold")
        )

        self.prev_frame_button = tk.Button(
            self.edit, text="\u23EA", command=self.move_back,
            fg="black", font=("Helvetica", 25, "bold")
        )
        self.play_all = tk.Button(
            self.edit, text="Play", command=self.play,
            fg="black", font=("Helvetica", 16, "bold")
        )
        # Validation for integer entry
        vcmd = (self.register(self.validate_integer), '%P')
        # Define buttons for movement
        self.move_up_button = tk.Button(self.edit, text="\u2191", font=("Helvetica", 25, "bold"), bg="#ECECEC", command=self.editMoveUp)
        self.move_down_button = tk.Button(self.edit, text="\u2193", font=("Helvetica", 25, "bold"), bg="#ECECEC", command=self.editMoveDown)
        self.move_left_button = tk.Button(self.edit, text="\u2190", font=("Helvetica", 25, "bold"), bg="#ECECEC", command=self.editMoveLeft)
        self.move_right_button = tk.Button(self.edit, text="\u2192", font=("Helvetica", 25, "bold"), bg="#ECECEC", command=self.editMoveRight)
        # Define buttons for stretching
        self.stretch_horizontalally = tk.Button(self.edit, text="Stretch Box Horixontally", font=("Helvetica", 16, "bold"), bg="#ECECEC", command=self.editStretchBoxHorz)
        self.stretch_vertically = tk.Button(self.edit, text="Stretch Box Vertically", font=("Helvetica", 16, "bold"), bg="#ECECEC", command=self.editStretchBoxVert)
        self.squeeze_horizontalally = tk.Button(self.edit, text="Squeeze Box Horixontally", font=("Helvetica", 16, "bold"), bg="#ECECEC", command=self.editSqueezeBoxHorz)
        self.squeeze_vertically = tk.Button(self.edit, text="Squeeze Box Vertically", font=("Helvetica", 16, "bold"), bg="#ECECEC", command=self.editSqueezeBoxVert)
        # Define buttons and text fields for class & ID
        self.class_entry = tk.Entry(self.edit, font=("Helvetica", 14))
        self.class_button = tk.Button(self.edit, text="Submit Class", font=("Helvetica", 14), command=self.editClass)
        self.id_entry = tk.Entry(self.edit, font=("Helvetica", 14), validate="key", validatecommand=vcmd)
        self.id_button = tk.Button(self.edit, text="Submit ID", font=("Helvetica", 14), command=self.editObjID)
        
        # Define button for saving changes
        self.save_changes_button = tk.Button(self.edit, text="Save Changes", font=("Helvetica", 16, "bold"), bg="#ECECEC", command=self.editSaveEdits)
        
        # Define buttons for the View tab
        self.select_button = tk.Button(
            self.view, text="Select Media", command=self.manage_media,
            fg="black",font=("Helvetica", 16, "bold")
        )
        self.select_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.pause_button = tk.Button(
            self.view, text="\u23F8", command=self.toggle_pause,
            fg="black", font=("Helvetica", 25, "bold")
        )
        self.pause_button.grid_forget()
        
        self.replay_button = tk.Button(
            self.view, text="\u21BA", command=self.start_replay,
            fg="black", font=("Helvetica", 25, "bold")
        )
        self.replay_button.grid_forget()
        
        self.YOLO_button = tk.Button(
            self.view, text="Let's YOLO", command=self.start_YOLO,
            fg="black",font=("Helvetica", 16, "bold")
        )
        self.YOLO_button.grid_forget()

        #Sizing and spcing configuration
        self.edit.grid_columnconfigure(0, weight=1)
        self.edit.grid_columnconfigure(1, weight=1)
        self.edit.grid_columnconfigure(2, weight=1)
        self.edit.grid_columnconfigure(3, weight=1)
        self.edit.grid_columnconfigure(4, weight=1)
        self.edit.grid_columnconfigure(5, weight=1)

        self.view.grid_columnconfigure(0, weight=1)
        self.view.grid_columnconfigure(1, weight=1)
        self.view.grid_columnconfigure(2, weight=1)
        self.view.grid_columnconfigure(3, weight=1)
        self.view.grid_columnconfigure(4, weight=1)
        self.view.grid_columnconfigure(5, weight=1)

        self.view_frame.update_idletasks()
        self.edit_frame.update_idletasks()
        self.video_thread = None

        # Bind window resize event to handle resizing elements
        self.bind("<Configure>", self.on_resize)
        # Bind to listen for tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_resize(self, event):
        """
        Handle resizing of the canvas and side panel when the window size changes.
        """
        self.canvas.config(width=self.content_frame.winfo_width() * 0.78, height=self.content_frame.winfo_height())
        self.side_panel.config(width=self.content_frame.winfo_width() * 0.22, height=self.content_frame.winfo_height())
    
    def class_display(self):
        """
        Constructs and displays a user interface for selecting classes with associated checkboxes and dropdown menus.
        """
        for widget in self.edit_frame.winfo_children():
            widget.destroy()

        # Create a dictionary to hold the checkboxes' state
        self.check_vars = {}
        self.dropdown_vars = {}  # Dictionary to hold dropdown variable references

        # Create a frame to hold the title and checkboxes
        self.checkbox_frame = tk.Frame(self.edit_frame, bg="#ECECEC")
        self.checkbox_frame.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        
        # Create a frame to hold the checkboxes and dropdown menus
        self.checkbox_list_frame = tk.Frame(self.checkbox_frame, bg="#ECECEC")
        self.checkbox_list_frame.pack(side='top', fill='both', expand=True)

        # Create a checkbox and dropdown menu for each class
        for index, item in enumerate(self.get_array_of_classes()):
            # Frame to contain the checkbox and dropdown
            item_frame = tk.Frame(self.checkbox_list_frame,bg="#ECECEC")
            item_frame.pack(side='top', fill='x', pady=5, padx=10)

            # Create the checkbox
            var = tk.BooleanVar()
            self.check_vars[item] = var
            checkbox = tk.Checkbutton(item_frame, text=item.capitalize(), variable=var, font=("Helvetica", 14), bg="#ECECEC")
            checkbox.pack(side='left', anchor='w')

            # Create a dropdown menu
            dropdown_var = tk.StringVar(value='ID')  # Default value
            self.dropdown_vars[item] = dropdown_var
            dropdown = tk.OptionMenu(item_frame, dropdown_var, *(self.objects[self.get_array_of_classes().index(item)]))
            dropdown.pack(side='left', padx=10)

            # Bind the dropdown to watch for changes and tick checkbox if a value is selected
            def on_dropdown_change(*args, item=item):
                if self.dropdown_vars[item].get() != 'ID':  # Only tick if something other than 'ID' is selected
                    self.check_vars[item].set(True)
                else:
                    self.check_vars[item].set(False)  # Optionally untick if 'ID' is selected again

            # Add trace to the dropdown variable
            dropdown_var.trace_add('write', on_dropdown_change)

        # Create the submit button to capture selected checkboxes
        self.submit_button = tk.Button(self.edit_frame, text="Submit", command=self.filter, bg="#ECECEC",font=("Helvetica", 14, "bold"))
        self.submit_button.pack(side='top', anchor='w', padx=10, pady=10)
        
        # Ensure the edit_frame expands and fills the available space
        self.edit_frame.grid_rowconfigure(0, weight=1)
        self.edit_frame.grid_columnconfigure(0, weight=1)
        
        # Update the layout
        self.edit_frame.update_idletasks()

    def get_selected(self):
        """
        Retrieve the currently selected classes and associated dropdown values.

        Returns:
            tuple: A tuple containing:
                - A list of selected class names.
                - A list of lists, each containing a class name and its corresponding selected dropdown value.
        """
        selected_classes = []
        selected_objects = []
        # Print ticked checkboxes
        print("Selected checkboxes:")
        for class_name, var in self.check_vars.items():
            if var.get():  # If the checkbox is ticked
                selected_classes.append(class_name)

                # Print selected dropdowns
                print("\nSelected dropdowns:")
                for class_name, dropdown_var in self.dropdown_vars.items():
                    selected_value = dropdown_var.get()
                    if selected_value != 'ID':  # If any item is selected from the dropdown
                        selected_objects.append([class_name,selected_value])
        
        return selected_classes,selected_objects
            
    def on_tab_change(self, event):
        """
        Handle the change of tabs in a notebook widget and update the interface accordingly.
        """
        # Get the index of the current tab
        current_tab = self.notebook.index(self.notebook.select())
        
        # Check if the current tab is "View" or "Edit" and update the label
        if current_tab == 0:  # View tab
            # If the listbox exists, destroy it before creating a new one
            if hasattr(self, 'edit_frame'):
                self.edit_frame.forget()
                self.view_frame.pack()
            # Messaging space
            self.side_panel_label.config(text="Welcome to our \nYOAT Application!",font=("Helvetica", 18, "bold"),bg="#ECECEC")
            msg='You are currently in view mode: \na video and image player you can \nuse to preview any media on your \ndevice before processing it with \nYOLO to identify and track unique \nobjects in your media. After \nloading, the annotated media is \nsaved. To look at your product \nnavigate to the edit tab and open \nthe file anytime you run the application!'
            self.side_panel_message = tk.Label(self.view_frame, text=msg,fg="black", font=("Helvetica", 14), bg="#ECECEC", bd=0, highlightthickness=0, relief="flat")
            self.side_panel_message.pack()
        elif current_tab == 1:  # Edit tab
            if hasattr(self, 'view_frame'):
                self.view_frame.forget()
                self.side_panel_message.forget()
                self.edit_frame.pack()
            self.side_panel_label.config(text="Class based object \ntracker")
        
        self.view_frame.update_idletasks()
        self.edit_frame.update_idletasks()

    def set_array_of_classes(self,array_of_classes):
        self.array_of_classes = array_of_classes
    
    def get_array_of_classes(self):
        return self.array_of_classes

    def sort_annotations(self,single_frame_annotations):
        """
        Process a list of annotations and categorize them by class.

        Args:
            single_frame_annotations (list): A list of dictionaries, each representing an annotation with keys "objectID" and "class".
       """    
        all_classes = []
        class_objects = []
        i=1
        for annotation in single_frame_annotations:
            ID = annotation["objectID"]
            self.current_frame_OGIDs.append(ID)
            try:
                ID = int(ID)
            except ValueError:
                ID=i
            self.current_frame_IDs.append(ID)
            i+=1
            class_name=annotation["class"]
            if class_name not in all_classes:
                all_classes.append(class_name)
                class_objects.append([str(ID)])
            else:
                index = all_classes.index(class_name)
                class_objects[index].append(str(ID))
                
        self.array_of_classes = all_classes
        self.objects = class_objects
        self.class_display()
    
    def display_coords(self, entries):
        """
        Arrange and display UI elements for movement controls and data entry fields.

        Args:
            entries (list): A list of entries that might contain button configurations or related data.
        """
        # put the buttons on the UI
        # Movement Buttons in a 3x3 grid (center the movement buttons)
        self.move_up_button.grid(row=1, column=0, padx=5, pady=5,sticky='w')       # Up button
        self.move_left_button.grid(row=1, column=1, padx=5, pady=5,sticky='w')     # Left button
        self.move_down_button.grid(row=2, column=0, padx=5, pady=5,sticky='w')     # Down button
        self.move_right_button.grid(row=2, column=1, padx=5, pady=5,sticky='w')    # Right button

        # Text fields and buttons for functionA and functionB
        self.class_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        self.class_button.grid(row=3, column=1, padx=5, pady=5,sticky='w')

        self.id_entry.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        self.id_button.grid(row=4, column=1, padx=5, pady=5,sticky='w')

        # Stretch and squeeze buttons in a separate row
        self.stretch_horizontalally.grid(row=3, column=2, padx=5, pady=5)
        self.stretch_vertically.grid(row=4, column=2, padx=5, pady=5)
        self.squeeze_horizontalally.grid(row=3, column=3, padx=5, pady=5)
        self.squeeze_vertically.grid(row=4, column=3, padx=5, pady=5)

        # Save changes button at the bottom
        self.save_changes_button.grid(row=0, column=1, columnspan=3, padx=5, pady=10)

        self.edit_frame.update_idletasks()
        
    def validate_integer(self, P):
        if P.isdigit() or "": return True  # Allow digits
        return False

    def remove_edit_UI(self):
        """
        Hide and remove all edit-related UI elements from the interface.
        """
        self.move_up_button.grid_forget()
        self.move_down_button.grid_forget()
        self.move_left_button.grid_forget()
        self.move_right_button.grid_forget()
        self.stretch_horizontalally.grid_forget()
        self.stretch_vertically.grid_forget()
        self.squeeze_horizontalally.grid_forget()
        self.squeeze_vertically.grid_forget()
        self.stretch_horizontalally.grid_forget()
        self.stretch_vertically.grid_forget()
        self.squeeze_horizontalally.grid_forget()
        self.squeeze_vertically.grid_forget()
        self.class_entry.grid_forget()
        self.class_button.grid_forget()
        self.id_entry.grid_forget()
        self.id_button.grid_forget()
        self.save_changes_button.grid_forget()
        
        self.edit_frame.update_idletasks()   
    
    def retrieve_values(self):
        """
        Retrieve updated values from entry widgets.

        This method accesses a dictionary of entry widgets stored in `self.entries_widgets` and retrieves 
        the current values for the keys "x1", "x2", "y1", and "y2". It then returns these values as a list.

        Returns:
            list: A list containing the updated values from the entry widgets in the order [x1, x2, y1, y2].
        """
        x1 = self.entries_widgets["x1"].get()
        x2 = self.entries_widgets["x2"].get()
        y1 = self.entries_widgets["y1"].get()
        y2 = self.entries_widgets["y2"].get()

        return [x1,x2,y1,y2]        