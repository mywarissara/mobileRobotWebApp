#!/usr/bin/python3

import time
import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import cv2
import copy
from threading import Thread, Lock
import numpy as np
from imutils.video import FPS

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Rectangle parameter
font = cv2.FONT_HERSHEY_PLAIN
text_color = (255, 255, 255)
rec_color = (0, 0, 255)

frame = np.zeros((480, 320, 3), dtype=np.uint8)
predictions = []

class WebcamVideoStream:
    def __init__(self, src=0, width=320, height=240):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self):
        if self.started:
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()

# Using threading to open camera

class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr", use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.seek(0)
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    """
    Trains a k-nearest neighbors classifier for face recognition.
    :param train_dir: directory that contains a sub-directory for each known person, with its name.
     (View in source code to see train_dir example tree structure)
     Structure:
        <train_dir>/
        ├── <person1>/
        │   ├── <somename1>.jpeg
        │   ├── <somename2>.jpeg
        │   ├── ...
        ├── <person2>/
        │   ├── <somename1>.jpeg
        │   └── <somename2>.jpeg
        └── ...
    :param model_save_path: (optional) path to save model on disk
    :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
    :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
    :param verbose: verbosity of training
    :return: returns knn classifier that was trained on the given data.
    """
    X = []
    y = []


    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                        face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(
                    image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)
                print(img_path)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(
        n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


def predict(X_img, model_path=None, knn_clf=None, distance_threshold=0.4):
    """
    Recognizes faces in given image using a trained KNN classifier
    :param X_img_path: path to image to be recognized
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """
    # print(distance_threshold)
    if knn_clf is None and model_path is None:
        raise Exception(
            "Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    X_face_locations = face_recognition.face_locations(X_img)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(
        X_img, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=3)
    are_matches = [closest_distances[0][i][0] <=
                   distance_threshold for i in range(len(X_face_locations))]

    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

# Function Create Model: Train the KNN classifier and save it to disk


def create_new_model(data):
    print("Training KNN classifier...")
    classifier = train(data,
                       model_save_path=data+"/trained_knn_model.clf", n_neighbors=3)
    print("Training complete!")


def take_pic(name, img_file):

    path_curr = os.getcwd()  # get current Dir
    path_pic = path_curr + "/knn_examples/train/" + name
    try:
        os.mkdir(path_pic)
    except:
        print("[Warning] The folder already existed!")

    # initialize the camera and grab a reference to the raw camera capture
    print("[INFO] `Camera` module...")

    # allow the camera to warmup
    time.sleep(1.0)

    initTime = time.time()
    currentTime = time.time()
    _no = 0
    _frame = img_file
    _frame = cv2.resize(
        _frame, (_frame.shape[1]//2, _frame.shape[0]//2), interpolation=cv2.INTER_AREA)
    _frame_copy = copy.deepcopy(_frame)
    centerX, centerY, _ = _frame.shape
    top = right = bottom = left = 0
    X_face_locations = face_recognition.face_locations(_frame_copy)
    try:
        (top, right, bottom, left) = X_face_locations[:][0]
        cv2.rectangle(_frame, (left, top), (right, bottom),
                      (0, 255, 0), 1)  # Draw rectangle
    except:
        pass
    
    return [_frame, top]


name = ''
def face_detection_main(frame):
    global name

    # initialize the camera and grab a reference to the raw camera capture
    print("[INFO] `Camera` module...")
    # vs = PiVideoStream().start()
    # vs = WebcamVideoStream(src=0).start()

    # allow the camera to warmup
    # time.sleep(1.0)

    while(True):
        # fps = FPS().start()

        # frame = vs.read()
        frame = cv2.resize(
            frame, (frame.shape[1]//2, frame.shape[0]//2), interpolation=cv2.INTER_AREA)

        # fps.update()

        # Using the trained classifier, make predictions for unknown images
        # Find all people in the image using a trained classifier model
        predictions = predict(
            frame, model_path="trained_knn_model.clf", distance_threshold=0.4)
        # print(predictions)
        # Print results on the console
        for name, (top, right, bottom, left) in predictions:

            cv2.rectangle(frame, (left, top), (right, bottom),
                          rec_color, 1)                  # Draw rectangle
            cv2.rectangle(frame, (left, bottom - 18), (right, bottom),
                          rec_color, cv2.FILLED)  # Put text in image

            if name != "unknown":
                print("- Found {} at ({}, {})".format(name, left, top))
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            font, 0.5, text_color, 1)
            else:
                cv2.putText(frame, "unknown", (left + 6, bottom - 6),
                            font, 0.5, text_color, 1)

        # # show the frame
        # cv2.imshow("Frame", frame)

        # # if the `q` key was pressed, break from the loop
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

        # fps.stop()
        # print(fps.elapsed())
        # print(fps.fps())
        return [frame,name]
    # do a bit of cleanup
    # cv2.destroyAllWindows()
    # vs.stop()


# if __name__ == "__main__":
#     create_new_model()
    #face_detection_main()
    # take_pic("test")
