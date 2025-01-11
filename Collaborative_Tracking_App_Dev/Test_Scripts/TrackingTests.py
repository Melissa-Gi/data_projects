import sys
import os

# Add the TeamTJM directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import modules as if running from the TeamTJM directory
from App import ObjectTracking
from App.YOLO.YOLO_API import YOLO_model
import cv2
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
import time
import unittest

# Add the TeamTJM directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestObjectTracking(unittest.TestCase):
    
    # Unit: Test color conversion
    def test_color_conversion(self):
        srgb = sRGBColor(0.5, 0.5, 0.5)
        lab = convert_color(srgb, LabColor)
        self.assertAlmostEqual(lab.lab_l, 53.231, places=0)
        self.assertAlmostEqual(lab.lab_a, 0.000, places=0)
        self.assertAlmostEqual(lab.lab_b, 0.000, places=0)

    # Unit:Test overlap calculation
    def test_calculate_overlap_area(self):
        box1 = (0, 0, 100, 100)
        box2 = (50, 50, 150, 150)
        self.assertAlmostEqual(ObjectTracking.calculate_overlap_area(box1, box2), 14.29, places=2)  # Expected overlap percentage

    # Unit:Test bounding box parsing
    def test_parse_results(self):
        class_labels = {0: "person"}
        class_colours = {0: (255, 0, 0)}
        result = ObjectTracking.parse_results(0, [0.9], [10, 10, 50, 50], [255, 0, 0], class_labels, class_colours)
        self.assertEqual(result[6], "person")
        self.assertEqual(result[11], 0.9)

    # Integration test: YOLO integration
    def test_yolo_integration(self):
        sample_frame = cv2.imread('Test_Scripts/Test_resources/test_image.jpg')
        model = YOLO_model()
        class_ids, scores, boxes, average_colours = model.detect_frame(sample_frame)
        self.assertGreater(len(class_ids), 0)

    # Integration test: tracking across frames
    def test_object_tracking(self):
        processed_frames, annotations = ObjectTracking.media_capture('Test_Scripts/Test_resources/test_video.mp4')
        self.assertGreater(len(processed_frames), 0)
        self.assertGreater(len(annotations), 0)

    # End-to-End test: full pipeline
    def test_full_pipeline(self):
        video_path = 'Test_Scripts/Test_resources/test_video.mp4'
        processed_frames, annotations = ObjectTracking.media_capture(video_path)
        self.assertGreater(len(processed_frames), 0)
        self.assertGreater(len(annotations), 0)
        self.assertIn('class', annotations[0][0])

    # Performance test: processing time
    def test_performance(self):
        start_time = time.time()
        ObjectTracking.media_capture('Test_Scripts/Test_resources/test_video.mp4')
        end_time = time.time()
        processing_time = end_time - start_time
        self.assertLess(processing_time, 30)  # Ensure processing time is under 60 seconds

if __name__ == "__main__":
    unittest.main()