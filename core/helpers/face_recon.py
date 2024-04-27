
import cv2
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
    def __init__(self) -> None:
        logger.info("Running facial recognition")
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        try:
            for image in os.listdir("test-images"):
                face_image = face_recognition.load_image_file(f"test-images/{image}")
                face_encodings = face_recognition.face_encodings(face_image)

                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(image)
                else:
                    logger.warning(f"No face found in image: {image}")
                    self.known_face_encodings.append(None)
                    self.known_face_names.append(image)
        except FileNotFoundError as e:
            logger.error(f"Error loading image file: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def run_recognition(self, frame):
        try:
            if frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rbg_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rbg_small_frame)
                face_encodings = face_recognition.face_encodings(rbg_small_frame, face_locations)
                face_names = []

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Not Registered"
                    confidence = "Not Registered"

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_matches_matrix = np.argmin(face_distances)

                    if matches[best_matches_matrix]:
                        name = self.known_face_names[best_matches_matrix].split(".")[0]
                        confidence = face_confidence(face_distances[best_matches_matrix])

                    face_names.append(f"{name} - {confidence}")

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom), (right, bottom), (0, 0, 255), -1)
                    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

                cv2.imshow("Face Recognition", frame)
                if cv2.waitKey(1) == ord("q"):
                    logger.info('Exiting facial recognition...')
        except cv2.error as e:
            logger.error(f"OpenCV Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def cleanup(self):
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            logger.error(f"An error occurred during cleanup: {e}")

if __name__ == "__main__":
    try:
        face_recon = FaceRecognition()
        face_recon.run_recognition()
    finally:
        face_recon.cleanup()
