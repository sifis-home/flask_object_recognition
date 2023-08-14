import datetime
import hashlib
import platform
from tempfile import NamedTemporaryFile

import cv2
import numpy as np
import rel
import websocket
from flask import Flask, abort, json, request

app = Flask(__name__)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")


def get_data():
    analyzer_id = platform.node()
    print(analyzer_id)

    return analyzer_id


def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

    return net


def get_coco():
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    return classes


def get_scale(sensitivity, epsilon):
    scale_factor = float(sensitivity) / float(epsilon)

    return scale_factor


def get_analysis_id(analyzer_id, now, hash_value):
    analysis_id = str(analyzer_id) + str(now) + hash_value

    return analysis_id


@app.route(
    "/cam_object/<cam_link>/<epsilon>/<sensitivity>/<requestor_id>/<requestor_type>/<request_id>"
)
def cam_object_recognition(
    cam_link, epsilon, sensitivity, requestor_id, requestor_type, request_id
):
    analyzer_id = get_data()

    # Get current date and time
    now = datetime.datetime.now()

    # Generate a random hash using SHA-256 algorithm
    hash_object = hashlib.sha256()
    hash_object.update(bytes(str(now), "utf-8"))
    hash_value = hash_object.hexdigest()

    # Concatenate the time and the hash
    analysis_id = get_analysis_id(analyzer_id, now, hash_value)

    # Load YOLOv3 network
    net = load_yolo()

    # Load COCO dataset class names
    classes = get_coco()

    # Generate random colors for each class
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    labels = []
    labels_dict = {}

    # Compute the scale factor for Laplacian noise
    scale_factor = get_scale(sensitivity, epsilon)

    # for object detection
    cap = cv2.VideoCapture(cam_link)

    frame_id = 0

    while True:
        # Read a frame from the video
        ret, frame = cap.read()
        if not ret:
            break

        img = np.asarray(frame)

        frame_id += 1

        # Generate Laplacian noise
        noise = np.random.laplace(scale=scale_factor, size=img.shape)

        # Add the noise to the image
        noisy_img = img + noise

        noisy_img = cv2.convertScaleAbs(noisy_img)
        frame = noisy_img

        # Convert the frame to a blob and pass it through the network
        blob = cv2.dnn.blobFromImage(
            frame, 1 / 255, (416, 416), swapRB=True, crop=False
        )
        net.setInput(blob)
        outs = net.forward(net.getUnconnectedOutLayersNames())

        # Parse the network output and draw the detections on the frame
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * frame.shape[1])
                    center_y = int(detection[1] * frame.shape[0])
                    w = int(detection[2] * frame.shape[1])
                    h = int(detection[3] * frame.shape[0])
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        # Apply non-maximum suppression to remove overlapping detections
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Draw the detections on the frame
        for i in indices:
            i = i[0]
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            labels.append(label)
            color = colors[class_ids[i]]

        # print(labels)

        ws_req = {
            "RequestPostTopicUUID": {
                "topic_name": "SIFIS:Object_Recognition_Frame_Results",
                "topic_uuid": "Object_Recognition_Frame_Results",
                "value": {
                    "description": "Object Recognition Frame Results",
                    "requestor_id": str(requestor_id),
                    "requestor_type": str(requestor_type),
                    "analyzer_id": str(analyzer_id),
                    "analysis_id": str(analysis_id),
                    "Type": "CAM",
                    "file_name": "Empty",
                    "epsilon": float(epsilon),
                    "sensitivity": float(sensitivity),
                    "scale_factor": float(scale_factor),
                    "frame_id": int(frame_id),
                    "labels": labels,
                },
            }
        }
        ws.send(json.dumps(ws_req))

        labels_dict[frame_id] = labels
        labels = []
        if cv2.waitKey(1) == ord("q"):
            break

    # Release the video file and close all windows
    cap.release()
    cv2.destroyAllWindows()

    ws_req_final = {
        "RequestPostTopicUUID": {
            "topic_name": "SIFIS:Object_Recognition_Results",
            "topic_uuid": "Object_Recognition_Results",
            "value": {
                "description": "Object Recognition Results",
                "requestor_id": str(requestor_id),
                "requestor_type": str(requestor_type),
                "request_id": str(request_id),
                "analyzer_id": str(analyzer_id),
                "analysis_id": str(analysis_id),
                "Type": "CAM",
                "file_name": "Empty",
                "epsilon": float(epsilon),
                "sensitivity": float(sensitivity),
                "scale_factor": float(scale_factor),
                "labels dictionary": labels_dict,
            },
        }
    }

    ws.send(json.dumps(ws_req_final))
    return ws_req_final


@app.route(
    "/file_object/<file_name>/<epsilon>/<sensitivity>/<requestor_id>/<requestor_type>/<request_id>",
    methods=["POST"],
)
def file_object_recognition(
    file_name, epsilon, sensitivity, requestor_id, requestor_type, request_id
):
    analyzer_id = get_data()

    # Get current date and time
    now = datetime.datetime.now()

    # Generate a random hash using SHA-256 algorithm
    hash_object = hashlib.sha256()
    hash_object.update(bytes(str(now), "utf-8"))
    hash_value = hash_object.hexdigest()

    # Concatenate the time and the hash
    analysis_id = get_analysis_id(analyzer_id, now, hash_value)

    # Load YOLOv3 network
    net = load_yolo()

    # Load COCO dataset class names
    classes = get_coco()

    # Generate random colors for each class
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    labels = []
    labels_dict = {}

    # Compute the scale factor for Laplacian noise
    scale_factor = get_scale(sensitivity, epsilon)

    if not request.files:
        # If the user didn't submit any files, return a 400 (Bad Request) error.
        abort(400)

    # Loop over every file that the user submitted.
    for filename, handle in request.files.items():
        # Create a temporary file.
        # The location of the temporary file is available in `temp.name`.
        temp = NamedTemporaryFile()
        # Write the user's uploaded file to the temporary file.
        # The file will get deleted when it drops out of scope.
        handle.save(temp)

        video_link = temp.name

        # for object detection
        cap = cv2.VideoCapture(video_link)

        frame_id = 0

        while True:
            # Read a frame from the video
            ret, frame = cap.read()
            if not ret:
                break

            img = np.asarray(frame)

            frame_id += 1

            # Generate Laplacian noise
            noise = np.random.laplace(scale=scale_factor, size=img.shape)

            # Add the noise to the image
            noisy_img = img + noise

            noisy_img = cv2.convertScaleAbs(noisy_img)
            frame = noisy_img

            # Convert the frame to a blob and pass it through the network
            blob = cv2.dnn.blobFromImage(
                frame, 1 / 255, (416, 416), swapRB=True, crop=False
            )
            net.setInput(blob)
            outs = net.forward(net.getUnconnectedOutLayersNames())

            # Parse the network output and draw the detections on the frame
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * frame.shape[1])
                        center_y = int(detection[1] * frame.shape[0])
                        w = int(detection[2] * frame.shape[1])
                        h = int(detection[3] * frame.shape[0])
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        class_ids.append(class_id)
                        confidences.append(float(confidence))
                        boxes.append([x, y, w, h])

            # Apply non-maximum suppression to remove overlapping detections
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # Draw the detections on the frame
            for i in indices:
                i = i[0]
                x, y, w, h = boxes[i]
                label = classes[class_ids[i]]
                labels.append(label)

            # print(labels)

            ws_req = {
                "RequestPostTopicUUID": {
                    "topic_name": "SIFIS:Object_Recognition_Frame_Results",
                    "topic_uuid": "Object_Recognition_Frame_Results",
                    "value": {
                        "description": "Object Recognition Frame Results",
                        "requestor_id": str(requestor_id),
                        "requestor_type": str(requestor_type),
                        "analyzer_id": str(analyzer_id),
                        "analysis_id": str(analysis_id),
                        "Type": "File",
                        "file_name": str(file_name),
                        "epsilon": float(epsilon),
                        "sensitivity": float(sensitivity),
                        "scale_factor": float(scale_factor),
                        "frame_id": int(frame_id),
                        "labels": labels,
                    },
                }
            }

            ws.send(json.dumps(ws_req))

            labels_dict[frame_id] = labels
            labels = []
            if cv2.waitKey(1) == ord("q"):
                break

        # Release the video file and close all windows
        cap.release()
        cv2.destroyAllWindows()

    ws_req_final = {
        "RequestPostTopicUUID": {
            "topic_name": "SIFIS:Object_Recognition_Results",
            "topic_uuid": "Object_Recognition_Results",
            "value": {
                "description": "Object Recognition Results",
                "requestor_id": str(requestor_id),
                "requestor_type": str(requestor_type),
                "request_id": str(request_id),
                "analyzer_id": str(analyzer_id),
                "analysis_id": str(analysis_id),
                "Type": "File",
                "file_name": str(file_name),
                "epsilon": float(epsilon),
                "sensitivity": float(sensitivity),
                "scale_factor": float(scale_factor),
                "labels dictionary": labels_dict,
            },
        }
    }

    ws.send(json.dumps(ws_req_final))
    return ws_req_final


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt

    app.run(debug=True, host="0.0.0.0", port=8080)
