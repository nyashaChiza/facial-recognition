import cv2
import math
import os, sys
import numpy as np
import face_recognition
from loguru import logger

FACE_MATCH_THRESHOLD = 0.45

def face_confidence(face_distance, face_match_threshold=FACE_MATCH_THRESHOLD):
    range = 1.0 - face_match_threshold
    linear_value = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        value = round(linear_value * 100, 2)
        return f"{value}%"
    else:
        return f"confidence below threshold"


class FaceRecognition:
    face_locations: list = []
    face_encodings: list = []
    known_face_encodings: list = []
    known_face_names: list = []
    process_current_frame: bool = True
    
    video_capture = None
 

    def __init__(self) -> None:
        logger.info("Running facial recognition")
        self.face_names = None
        self.encode_faces()

    def encode_faces(self):
        try:
            for image in os.listdir("test-images"):
                face_image = face_recognition.load_image_file(f"test-images/{image}")
                face_encodings = face_recognition.face_encodings(face_image)

                if face_encodings:
                    # Assuming you want to use only the first face encoding if multiple faces are detected
                    face_encoding = face_encodings[0]

                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(image)
                else:
                    logger.warning(f"No face found in image: {image}")
                    self.known_face_encodings.append(None)  # Placeholder for images with no detected faces
                    self.known_face_names.append(image)
        except FileNotFoundError as e:
            logger.error(f"Error loading image file: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")



    def run_recognition(self, frame):
        try:
            if 1:  # Modify this condition based on your logic
                # video_capture = cv2.VideoCapture(0)
                # self.video_capture = video_capture

                # if not self.video_capture.isOpened():
                #     logger.error("Video Source not found ..!")

                # while True:
                #     status, frame = self.video_capture.read()

                    if frame:
                        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                        rbg_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                        self.face_locations = face_recognition.face_locations(
                            rbg_small_frame
                        )

                        self.face_encodings = face_recognition.face_encodings(
                            rbg_small_frame, self.face_locations
                        )

                        self.face_names = []

                        for face_encoding in self.face_encodings:
                            matches = face_recognition.compare_faces(
                                self.known_face_encodings, face_encoding
                            )
                            name = "Not Registered"
                            confidence = "Not Registered"

                            face_distances = face_recognition.face_distance(
                                self.known_face_encodings, face_encoding
                            )

                            best_matches_matrix = np.argmin(face_distances)

                            if matches[best_matches_matrix]:
                                name = self.known_face_names[best_matches_matrix]
                                if str(name).find("."):
                                    name = str(name).split(".")[0]

                                confidence = face_confidence(
                                    face_distances[best_matches_matrix]
                                )

                            self.face_names.append(f"{name} - {confidence}")

                    self.process_current_frame = not self.process_current_frame

                    for (top, right, bottom, left), name in zip(
                        self.face_locations, self.face_names
                    ):
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        cv2.rectangle(
                            frame, (left, bottom), (right, bottom), (0, 0, 255), -1
                        )
                        cv2.putText(
                            frame,
                            name,
                            (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_DUPLEX,
                            0.8,
                            (255, 255, 255),
                            1,
                        )

                    cv2.imshow("Face Recognition", frame)
                    if cv2.waitKey(1) == ord("q"):
                        logger.info('Exiting facial recognition...')
                      

        except cv2.error as e:
            logger.error(f"OpenCV Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            self.cleanup()


    def cleanup(self):
        try:
            if self.video_capture is not None:
                self.video_capture.release()
            cv2.destroyAllWindows()
        except Exception as e:
            logger.error(f"An error occurred during cleanup: {e}")


if __name__ == "__main__":
    try:
        face_recon = FaceRecognition()
        face_recon.run_recognition()
    finally:
        face_recon.cleanup()
