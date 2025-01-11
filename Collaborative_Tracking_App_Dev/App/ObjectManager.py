"""
Module Name: ObjectManager.py

Description:
    This module provides the ObjManager class, which is designed to filter 
    and edit object annotations in a series of frames. It allows users to 
    modify bounding boxes: their shapes, positions, class labels, and 
    object IDs. It can save the modified annotations to a JSON file.

Usage:
    To use the ObjManager, instantiate it with a reference array of annotations 
    and utilize its methods for editing and saving data.

Dependencies:
    - json

Author: team 120
Date: 19/09/2024
"""

import json

class ObjManager():
    """
    A class to manage and edit object annotations in a series of frames.

    This class facilitates the editing of annotations associated with objects,
    which are represented as bounding boxes sharing a common ID. Edits can be made
    to specific boxes at designated frames, and changes can be flushed to a JSON file.

    Attributes:
        data (list): A reference array containing the annotations for objects.
        changedAnnotations (list): A list to keep track of any modified annotations.
        OGIDs (list): A list of original IDs for tracking purposes.

    Methods:
        __init__(arrRef): Initializes the ObjManager with a reference array.
    """

    def __init__(self, arrRef):
        """
        Initialize the ObjManager with a reference array of annotations.

        Args:
            arrRef (list): The initial list of annotations to manage.

        Preconditions:
            - The input `arrRef` must be a list of annotations in the expected format.
        """
        self.data  = arrRef
        self.changedAnnotations=[]
        self.OGIDs = []
        print("[ObjectManager] O.M. created")

    def clear(self):
        self.changedAnnotations = []
    
    def editBoundingBoxShape(self,indexF,indexB, coord, change_amount):
        """
        Stretch or squeeze a bounding box by modifying its coordinates.

        Args:
            indexF (int): The index of the frame containing the bounding box to be edited.
            indexB (int): The index of the bounding box within the specified frame.
            coord (str): The coordinate to change ('x1', 'y1', 'x2', 'y2').
            change_amount (int or float): The amount to adjust the specified coordinate.

        Preconditions:
            - The specified indices must be valid for the `data` structure.
            - The `coord` argument must be one of 'x1', 'y1', 'x2', or 'y2'.
        """
        self.data[indexF][indexB]["bounding_box"][coord] += change_amount
        print(f"[ObjectManager] edit: F{indexF} B{indexB}  {coord} += {change_amount}")

    def editMoveBoundingBoxVerticle(self,indexF,indexB, move_amount):
        """
        Move a bounding box vertically by adjusting its Y coordinates.

        Args:
            indexF (int): The index of the frame containing the bounding box to be edited.
            indexB (int): The index of the bounding box within the specified frame.
            move_amount (int or float): The amount to move the bounding box vertically.

        Preconditions:
            - The specified indices must be valid for the `data` structure.
        """
        y1 = self.data[indexF][indexB]["bounding_box"]["y1"]
        y2 = self.data[indexF][indexB]["bounding_box"]["y2"]
        self.data[indexF][indexB]["bounding_box"]["y1"] = y1 + move_amount
        self.data[indexF][indexB]["bounding_box"]["y2"] = y2 + move_amount
        print(f"[ObjectManager] edit: {indexF};{indexB}   yshifted by  {move_amount}")

    def editMoveBoundingBoxHorizontal(self,indexF,indexB, move_amount):
        """
        Move a bounding box horizontally by adjusting its X coordinates.

        Args:
            indexF (int): The index of the frame containing the bounding box to be edited.
            indexB (int): The index of the bounding box within the specified frame.
            move_amount (int or float): The amount to move the bounding box horizontally.

        Preconditions:
            - The specified indices must be valid for the `data` structure.
        """
        x1 = self.data[indexF][indexB]["bounding_box"]["x1"]
        x2 = self.data[indexF][indexB]["bounding_box"]["x2"]
        self.data[indexF][indexB]["bounding_box"]["x1"] = x1 + move_amount
        self.data[indexF][indexB]["bounding_box"]["x2"] = x2 + move_amount
        print(f"[ObjectManager] edit: {indexF};{indexB}   xshifted by  {move_amount}")

    def editLabel(self,indexF,indexB,new_val):
        """
        Edit the label of a bounding box.

        Args:
            indexF (int): The index of the frame containing the bounding box to be edited.
            indexB (int): The index of the bounding box within the specified frame.
            new_val (str): The new class label to assign to the bounding box.

        Preconditions:
            - The specified indices must be valid for the `data` structure.
            - The `new_val` should be a valid string representing the class label.
        """
        self.data[indexF][indexB]["class"] = new_val
        print(f"[ObjectManager] edit: {indexF};{indexB}   label   {new_val}")

    def editID(self, indexF, indexB, new_val):
        """
        Edit the object ID of a bounding box.

        Args:
            indexF (int): The index of the frame containing the bounding box to be edited.
            indexB (int): The index of the bounding box within the specified frame.
            new_val (int or str): The new object ID to assign to the bounding box.

        Preconditions:
            - The specified indices must be valid for the `data` structure.
            - The `new_val` should be a valid identifier (int or string) for the object.
        """
        self.data[indexF][indexB]["objectID"] = new_val
        print(f"[ObjectManager] edit: {indexF};{indexB}   ID   {new_val}")

    def writeChanges(self, file_path):
        """
        Write the current data to a JSON file.

        Args:
            file_path (str): The path to the JSON file where the data will be saved.

        Preconditions:
            - The `file_path` must be a valid writable path.
            - The `data` structure must be properly populated with the annotations.
        """
        with open(file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)
        print(f"[ObjectManager] overwritten {file_path}")

    def filterClass(self,filter_value): 
        """
        Filter bounding boxes by class label.

        This method creates a new array of bounding boxes from the current data,
        retaining only those that match the specified class label. The resulting 
        array may contain empty entries for boxes that do not match the filter, 
        allowing for preservation of indices for future edits.

        Args:
            filter_value (str): The class label to filter by.

        Returns:
            list: A list of filtered bounding boxes, with empty entries where 
                the class did not match.

        Preconditions:
            - The `filter_value` must be a valid class label present in the data.
        """
        print("[Objectmanager] filterClass() running")
        arrFiltered = []
        
        for frame in self.data:
            for box in frame:
                if box["class"] == filter_value:
                    arrFiltered.append(box)
            self.changedAnnotations.append(arrFiltered)
            arrFiltered = []
        print(f"[ObjectManager] filtered frame for '{filter_value}' ")
        return self.changedAnnotations
    
    def filterObjectID(self,filter_value): 
        """
        Filter bounding boxes by object ID.

        This method creates a new array of bounding boxes from the current data,
        retaining only those that match the specified object ID. The resulting 
        array may contain empty entries for boxes that do not match the filter, 
        allowing for preservation of indices for future edits.

        Args:
            filter_value (int or str): The object ID to filter by.

        Returns:
            list: A list of filtered bounding boxes, with empty entries where 
                the object ID did not match.

        Preconditions:
            - The `filter_value` must be a valid object ID present in the data.
        """
        arrFiltered = []
        for frame in self.data:
            for box in frame:
                if box["objectID"] == filter_value:
                    arrFiltered.append(box)
            self.changedAnnotations.append(arrFiltered)
            arrFiltered = []
        print(f"[ObjectManager] filtered frames for '{filter_value}' ")
        return self.changedAnnotations

    def getBox(box):
        bbox = box["bounding_box"]
        x1, y1 = bbox["x1"], bbox["y1"]
        x2, y2 = bbox["x2"], bbox["y2"]
        return [x1,x2,y1,y2]

    def getOGIDs(self):
        for frame in self.data:
            for annotation in frame:
                ID = annotation["objectID"]
                self.OGIDs.append(ID)

    def getObjIndexInFrame(self,indexF, objID):
        """
        Retrieve the index of a bounding box by its object ID in a specific frame.

        This method searches for a bounding box with the specified object ID
        within a given frame and returns its index. If the object ID is not found,
        it returns -1.

        Args:
            indexF (int): The index of the frame to search in.
            objID (int or str): The object ID to search for.

        Returns:
            int: The index of the bounding box with the specified object ID, or -1 
                if not found.

        Preconditions:
            - The specified indexF must be valid for the `data` structure.
        """
        indexB = 0
        for box in self.data[indexF]:
            if box["objectID"] == objID: return indexB
            else: indexB +=1
        return -1