import math
import time
import logging

import cv2
import mediapipe as mp

from . import utils

module_logger = logging.getLogger("watchmyback.face")

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class FaceDetection:
    def __init__(self, camera=0, debug=False):
        self.camera = camera
        self.debug = debug
        self.debug_frame = None

        self.capture = None

        self.user_face = None
        self.last_safe_face = None

        self.detection_threshold_count = 0
        self.detection_notification_timer = 0

        self.error_counter = 0

        self.mp_face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6)
        # model_selection=1 -> full-range model best for faces within 5 meter

    def start(self):
        module_logger.warning("Starting Face Detection and VideoCapture")
        self.capture = cv2.VideoCapture(self.camera)

        if not self.capture or not self.capture.isOpened():
            module_logger.warning("Reset Camera Permission")
            utils.reset_camera_permission()
            return

        # TODO:
        #  - Security permission on Windows, Mac, Linux (?)
        #  - It's not possible to get the list of cameras, using only built-in.
        #  - If no camera is available?

        while self.capture.isOpened():
            success, image = self.capture.read()
            if not success:
                module_logger.debug("Skipping empty frame...")
                self.error_counter += 1

                if self.error_counter > 5:
                    module_logger.warning("Too many errors. Killing...")
                    self.stop()
                    break

                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.mp_face_detection.process(image)

            if self.debug:
                self.debug_frame = self._draw_frame_debug(image, results.detections)

            if not results.detections:
                self.detection_threshold_count = min(self.detection_threshold_count, 0) - 1

                if self.detection_threshold_count == -30:
                    module_logger.warning("Showing notification...")
                    utils.show_notification("WatchMyBack :)", "About to lock...")

                elif self.detection_threshold_count < -100:  # TODO: calculate best threshold
                    module_logger.warning("Locking...")
                    self.detection_threshold_count = 0
                    utils.lock_screen()

            elif len(results.detections) == 1:
                self.user_face = self.last_safe_face = results.detections[0]
                self.detection_threshold_count = 0

            else:  # len(results.detections) > 1
                if not self.user_face:
                    self.user_face = self.last_safe_face = order_detection_by_box_area(results.detections, True)[0]

                detections = order_detections_by_distance(results.detections, self.user_face)
                self.user_face = detections[0]

                if self.debug:
                    self.debug_frame = self._draw_frame_debug(image, detections)

                self.detection_threshold_count = max(self.detection_threshold_count, 0) + 1
                if self.detection_threshold_count > 20:  # TODO: calculate best threshold
                    module_logger.info("Detected two or more faces!")

                    if time.time() > self.detection_notification_timer + 5:
                        module_logger.warning("Showing notification...")
                        utils.show_notification("WatchMyBack :)", "Nose down to lock the screen!")
                        self.detection_notification_timer = time.time()
                        self.last_safe_face = self.user_face

                    if is_nose_down(self.last_safe_face, self.user_face):
                        module_logger.warning("Locking...")
                        self.detection_threshold_count = 0
                        utils.lock_screen()

    def stop(self):
        module_logger.warning("Stopping Face Detection")
        self.error_counter = 0
        self.detection_threshold_count = 0

        if self.capture:
            self.capture.release()
            self.capture = None

    @staticmethod
    def _draw_frame_debug(image, detections):
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        color_map = {0: (0, 0, 255), 1: (255, 0, 0), 2: (0, 255, 0)}
        color_index = 0
        for detection in detections if detections else []:
            mp_drawing.draw_detection(image,
                                      detection,
                                      keypoint_drawing_spec=
                                      mp_drawing_styles.DrawingSpec(color=color_map[min(color_index, 2)]))
            color_index += 1

        return image


# Utils
def relative_keypoints_nose(detection):
    return detection.location_data.relative_keypoints[2].x, detection.location_data.relative_keypoints[2].y


def is_nose_down(prev_face, current_face):
    return abs(relative_keypoints_nose(prev_face)[1] - relative_keypoints_nose(current_face)[1]) > 0.08


def relative_bounding_box(detection):
    return detection.location_data.relative_bounding_box.width, detection.location_data.relative_bounding_box.height


def euclidean_distance(p, q):
    x, y = p
    x1, y1 = q
    return math.sqrt((x1 - x)**2 + (y1 - y)**2)


def order_detections_by_distance(detections, target, reverse=False):
    return sorted(detections,
                  key=lambda detection: euclidean_distance(relative_keypoints_nose(detection),
                                                           relative_keypoints_nose(target)),
                  reverse=reverse)


def order_detection_by_box_area(detections, reverse=False):
    return sorted(detections, key=lambda detection: math.prod(relative_bounding_box(detection)), reverse=reverse)
