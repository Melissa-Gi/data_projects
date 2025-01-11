import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.App import MediaPlayer

class TestMediaPlayer(unittest.TestCase):
    def setUp(self):
        # Paths to your actual media files
        self.mp4_file = "Test_Scripts/Test_resources/test_video.mp4"
        self.jpg_file = "Test_Scripts/Test_resources/test_image.jpg"
        
        # Ensure the test media files exist
        self.assertTrue(os.path.exists(self.mp4_file), f"Video file not found: {self.mp4_file}")
        self.assertTrue(os.path.exists(self.jpg_file), f"Image file not found: {self.jpg_file}")

        # Initialize MediaPlayer instance
        self.player = MediaPlayer()

    def test_load_video(self):
        self.player.media_path = self.mp4_file
        self.player.manage_media()
        self.assertTrue(self.player.video_capture.isOpened())
        self.assertIsNotNone(self.player.video_thread)

    def test_load_image(self):
        self.player.media_path = self.jpg_file
        self.player.manage_media()
        self.assertTrue(os.path.exists(self.jpg_file))

if __name__ == "__main__":
    unittest.main()
