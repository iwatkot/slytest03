import logging
import os
import sys

from enum import Enum

absolute_path = os.path.dirname(__file__)

os.makedirs(os.path.join(absolute_path, 'logs'), exist_ok=True)

LOG_FORMATTER = "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
LOG_FILE = os.path.join(absolute_path, 'logs/main_log.txt')


class Logger(logging.getLoggerClass()):
    """Handles logging to the file and stroudt with timestamps."""
    def __init__(self, name: str):
        super().__init__(name)
        self.setLevel(logging.DEBUG)
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.file_handler = logging.FileHandler(
            filename=LOG_FILE, mode='a')
        self.fmt = LOG_FORMATTER
        self.stdout_handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        self.file_handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        self.addHandler(self.stdout_handler)
        self.addHandler(self.file_handler)


class LogTemplates(Enum):
    """Storing log templates for the split_image.py"""
    LOADING_SCENE = "Preparing to load the scene with ID: {}."
    LOADING_SCENE_DATA = "Loading scene data with scene token: {}."
    LOADING_LIDAR_DATA = "Loading lidar data with lidar token: {}."
    TRANSLATION = "Loaded translation data: {}."
    LOADING_FROM_FILE = "Loading lidar data from file: {}."
    LOADED_POINTS_ARRAY = "Loaded points array with total number of: "\
        "points: {}."
    LOADED_BOXES = "Loaded {} boxes."
    FOUND_BOX = "Found target box type: {}."
    BOX_CENTER = "Coordinates of the center of the box: {}."
    BOX_SIZES = "Dimensions of of the box (W, L, H): {}."
    WRITED_FILE = "Writed a file with {} points."
    NO_POINTS = "The box contains no points."
    WRONG_SCENE = "The wrong scene number was entered."
    FINISHED = "The script is finished extarcting clouds of points from "\
        "the scene. Total number of files: {}. List of files: {}."

    def format(self, *args, **kwargs):
        return self.value.format(*args, **kwargs)

    def __str__(self):
        return self.value
