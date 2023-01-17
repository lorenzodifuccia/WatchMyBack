import sys
import time
import logging
import argparse

import cv2

from src import face_detection, utils


def configure_logging(debug=False):
    main_logger = logging.getLogger("watchmyback")
    main_logger.setLevel(logging.DEBUG if debug else logging.WARNING)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)

    main_logger.addHandler(stdout_handler)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    face_detection_instance = face_detection.FaceDetection(debug=args.debug)
    face_detection_thread = utils.ThreadWatchdog(name="watchmyback.face", instance=face_detection_instance)
    face_detection_thread.start_with_watchdog()

    while face_detection_thread.running:
        try:
            if args.debug:
                if face_detection_thread.running and face_detection_instance.debug_frame is not None:
                    cv2.imshow('WatchMyBack Face Detection', cv2.flip(face_detection_instance.debug_frame, 1))
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC
                        face_detection_thread.kill()
                        cv2.destroyAllWindows()
                        break

                    continue

            time.sleep(1)

        except KeyboardInterrupt:
            face_detection_thread.kill()


if __name__ == "__main__":
    main()
