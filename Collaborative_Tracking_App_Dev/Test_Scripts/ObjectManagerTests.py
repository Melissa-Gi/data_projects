import sys
import os
import unittest
import json
from io import StringIO
from unittest.mock import patch

# Add the TeamTJM directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.ObjectManager import ObjManager

class TestObjManager(unittest.TestCase):
    
    #Collapse this for convinence if one can
    def setUp(self):
        # Set up initial data for testing
        self.initial_data = [
    [
        {
            "class": "person",
            "confidence": "0.92",
            "objectID": 0,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 131,
                "y1": 356,
                "x2": 298,
                "y2": 854
            }
        },
        {
            "class": "person",
            "confidence": "0.91",
            "objectID": 1,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 329,
                "y1": 366,
                "x2": 496,
                "y2": 849
            }
        },
        {
            "class": "person",
            "confidence": "0.9",
            "objectID": 2,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 719,
                "y1": 404,
                "x2": 887,
                "y2": 782
            }
        },
        {
            "class": "person",
            "confidence": "0.9",
            "objectID": 3,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 1661,
                "y1": 105,
                "x2": 1919,
                "y2": 1066
            }
        },
        {
            "class": "handbag",
            "confidence": "0.88",
            "objectID": 4,
            "colours": {
                "B": 123,
                "G": 155,
                "R": 218
            },
            "bounding_box": {
                "x1": 1591,
                "y1": 277,
                "x2": 1920,
                "y2": 644
            }
        },
        {
            "class": "person",
            "confidence": "0.87",
            "objectID": 5,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 514,
                "y1": 346,
                "x2": 670,
                "y2": 834
            }
        },
        {
            "class": "person",
            "confidence": "0.85",
            "objectID": 6,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 1418,
                "y1": 450,
                "x2": 1515,
                "y2": 732
            }
        },
        {
            "class": "backpack",
            "confidence": "0.76",
            "objectID": 7,
            "colours": {
                "B": 248,
                "G": 5,
                "R": 192
            },
            "bounding_box": {
                "x1": 1052,
                "y1": 325,
                "x2": 1247,
                "y2": 629
            }
        },
        {
            "class": "person",
            "confidence": "0.75",
            "objectID": 8,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 631,
                "y1": 438,
                "x2": 715,
                "y2": 747
            }
        },
        {
            "class": "backpack",
            "confidence": "0.67",
            "objectID": 9,
            "colours": {
                "B": 248,
                "G": 5,
                "R": 192
            },
            "bounding_box": {
                "x1": 724,
                "y1": 453,
                "x2": 817,
                "y2": 557
            }
        },
        {
            "class": "person",
            "confidence": "0.59",
            "objectID": 10,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 870,
                "y1": 203,
                "x2": 1136,
                "y2": 1077
            }
        },
        {
            "class": "person",
            "confidence": "0.59",
            "objectID": 11,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 1344,
                "y1": 434,
                "x2": 1406,
                "y2": 645
            }
        },
        {
            "class": "backpack",
            "confidence": "0.3",
            "objectID": 12,
            "colours": {
                "B": 248,
                "G": 5,
                "R": 192
            },
            "bounding_box": {
                "x1": 725,
                "y1": 451,
                "x2": 803,
                "y2": 556
            }
        },
        {
            "class": "person",
            "confidence": "0.27",
            "objectID": 13,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 484,
                "y1": 412,
                "x2": 544,
                "y2": 763
            }
        },
        {
            "class": "handbag",
            "confidence": "0.26",
            "objectID": 14,
            "colours": {
                "B": 123,
                "G": 155,
                "R": 218
            },
            "bounding_box": {
                "x1": 456,
                "y1": 622,
                "x2": 490,
                "y2": 728
            }
        }
    ],
    [
        {
            "class": "person",
            "confidence": "0.92",
            "objectID": 0,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 131,
                "y1": 356,
                "x2": 298,
                "y2": 854
            }
        },
        {
            "class": "person",
            "confidence": "0.91",
            "objectID": 1,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 329,
                "y1": 366,
                "x2": 496,
                "y2": 849
            }
        },
        {
            "class": "person",
            "confidence": "0.9",
            "objectID": 2,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 719,
                "y1": 404,
                "x2": 887,
                "y2": 782
            }
        },
        {
            "class": "person",
            "confidence": "0.9",
            "objectID": 3,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 1661,
                "y1": 105,
                "x2": 1919,
                "y2": 1066
            }
        },
        {
            "class": "handbag",
            "confidence": "0.88",
            "objectID": 4,
            "colours": {
                "B": 123,
                "G": 155,
                "R": 218
            },
            "bounding_box": {
                "x1": 1591,
                "y1": 277,
                "x2": 1920,
                "y2": 644
            }
        },
        {
            "class": "person",
            "confidence": "0.87",
            "objectID": 5,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 514,
                "y1": 346,
                "x2": 670,
                "y2": 834
            }
        },
        {
            "class": "person",
            "confidence": "0.85",
            "objectID": 6,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 1418,
                "y1": 450,
                "x2": 1515,
                "y2": 732
            }
        },
        {
            "class": "backpack",
            "confidence": "0.76",
            "objectID": 7,
            "colours": {
                "B": 248,
                "G": 5,
                "R": 192
            },
            "bounding_box": {
                "x1": 1052,
                "y1": 325,
                "x2": 1247,
                "y2": 629
            }
        },
        {
            "class": "person",
            "confidence": "0.75",
            "objectID": 8,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 631,
                "y1": 438,
                "x2": 715,
                "y2": 747
            }
        },
        {
            "class": "backpack",
            "confidence": "0.67",
            "objectID": 12,
            "colours": {
                "B": 248,
                "G": 5,
                "R": 192
            },
            "bounding_box": {
                "x1": 724,
                "y1": 453,
                "x2": 817,
                "y2": 557
            }
        },
        {
            "class": "person",
            "confidence": "0.59",
            "objectID": 11,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 1344,
                "y1": 434,
                "x2": 1406,
                "y2": 645
            }
        },
        {
            "class": "person",
            "confidence": "0.59",
            "objectID": 10,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 870,
                "y1": 203,
                "x2": 1136,
                "y2": 1077
            }
        },
        {
            "class": "backpack",
            "confidence": "0.3",
            "objectID": 15,
            "colours": {
                "B": 248,
                "G": 5,
                "R": 192
            },
            "bounding_box": {
                "x1": 725,
                "y1": 451,
                "x2": 803,
                "y2": 556
            }
        },
        {
            "class": "person",
            "confidence": "0.27",
            "objectID": 13,
            "colours": {
                "B": 237,
                "G": 133,
                "R": 135
            },
            "bounding_box": {
                "x1": 484,
                "y1": 412,
                "x2": 544,
                "y2": 763
            }
        },
        {
            "class": "handbag",
            "confidence": "0.26",
            "objectID": 14,
            "colours": {
                "B": 123,
                "G": 155,
                "R": 218
            },
            "bounding_box": {
                "x1": 456,
                "y1": 622,
                "x2": 490,
                "y2": 728
            }
        }
    ]]
        self.obj_manager = ObjManager(self.initial_data)
    
    #All functionality unit test
    
    def test_editBoundingBoxShape(self):
        self.obj_manager.editBoundingBoxShape(0, 0, "x1", 5)
        self.assertEqual(self.initial_data[0][0]["bounding_box"]["x1"], 136)
    
    def test_editMoveBoundingBoxVerticle(self):
        self.obj_manager.editMoveBoundingBoxVerticle(0, 0, 10)
        self.assertEqual(self.initial_data[0][0]["bounding_box"]["y1"], 366)
        self.assertEqual(self.initial_data[0][0]["bounding_box"]["y2"], 864)
    
    def test_editMoveBoundingBoxHorizontal(self):
        self.obj_manager.editMoveBoundingBoxHorizontal(0, 0, -5)
        self.assertEqual(self.initial_data[0][0]["bounding_box"]["x1"], 126)
        self.assertEqual(self.initial_data[0][0]["bounding_box"]["x2"], 293)
    
    def test_editLabel(self):
        self.obj_manager.editLabel(0, 1, "bus")
        self.assertEqual(self.initial_data[0][1]["class"], "bus")
    
    def test_editID(self):
        self.obj_manager.editID(1, 0, 3)
        self.assertEqual(self.initial_data[1][0]["objectID"], 3)
    
    def test_filterClass(self):
        filtered = self.obj_manager.filterClass("handbag")
        expected = [
            [{"class": "handbag","confidence": "0.88","objectID": 4,"colours": {"B": 123,"G": 155,"R": 218},
            "bounding_box": {"x1": 1591,"y1": 277,"x2": 1920,"y2": 644}},
            {"class": "handbag","confidence": "0.26","objectID": 14,"colours": {"B": 123,"G": 155,"R": 218},
            "bounding_box": {"x1": 456,"y1": 622,"x2": 490,"y2": 728}}],
            [{"class": "handbag","confidence": "0.88","objectID": 4,"colours": {"B": 123,"G": 155,"R": 218},
            "bounding_box": {"x1": 1591,"y1": 277,"x2": 1920,"y2": 644}},
            {"class": "handbag","confidence": "0.26","objectID": 14,"colours": {"B": 123,"G": 155,"R": 218},
            "bounding_box": {"x1": 456,"y1": 622,"x2": 490,"y2": 728}}]
        ]
        self.assertEqual(filtered, expected)
    
    def test_filterObjectID(self):
        filtered = self.obj_manager.filterObjectID(14)
        expected = [
            [{"class": "handbag","confidence": "0.26","objectID": 14,"colours": {"B": 123,"G": 155,"R": 218},
            "bounding_box": {"x1": 456,"y1": 622,"x2": 490,"y2": 728}}],
            [{"class": "handbag","confidence": "0.26","objectID": 14,"colours": {"B": 123,"G": 155,"R": 218},
            "bounding_box": {"x1": 456,"y1": 622,"x2": 490,"y2": 728}}]
        ]
        self.assertEqual(filtered, expected)
    
    def test_getBox(self):
        box = self.initial_data[0][0]
        result = ObjManager.getBox(box)
        self.assertEqual(result, [131, 298, 356, 854])
    
    def test_getObjIndexInFrame(self):
        index = self.obj_manager.getObjIndexInFrame(0, 2)
        self.assertEqual(index, 2)
        index_not_found = self.obj_manager.getObjIndexInFrame(0, 187)
        self.assertEqual(index_not_found, -1)

if __name__ == "__main__":
    unittest.main()