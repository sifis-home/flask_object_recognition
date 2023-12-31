import datetime
import hashlib
import platform
from unittest.mock import Mock, patch

import cv2
import numpy as np

from app import (
    add_noise,
    get_analysis_id,
    get_coco,
    get_data,
    get_scale,
    iterate,
    load_yolo,
    on_close,
    on_error,
    on_open,
)


def test_on_error():
    error = "WebSocket error occurred"

    with patch("builtins.print") as mock_print:
        on_error(None, error)

    mock_print.assert_called_once_with(error)


def test_on_close():
    close_status_code = 1000
    close_msg = "Connection closed"

    with patch("builtins.print") as mock_print:
        on_close(None, close_status_code, close_msg)

    mock_print.assert_called_once_with("### Connection closed ###")


def test_on_open():
    with patch("builtins.print") as mock_print:
        on_open(None)

    mock_print.assert_called_once_with("### Connection established ###")


def test_get_data():
    analyzer_id = platform.node()

    result = get_data()
    expected_result = analyzer_id

    assert result == expected_result


def test_load_yolo():
    # Mock cv2.dnn.readNet
    mocked_readNet = Mock(spec=cv2.dnn.readNet)
    with patch("cv2.dnn.readNet", mocked_readNet):
        # Call the function
        net = load_yolo()

    # Check if cv2.dnn.readNet was called with the expected arguments
    mocked_readNet.assert_called_once_with("yolov3.weights", "yolov3.cfg")

    # Check if the returned 'net' object matches the mocked result
    assert net == mocked_readNet.return_value


def test_get_coco():
    with open("coco.names", "r") as f:
        expected_classes = [line.strip() for line in f.readlines()]
    classes = get_coco()

    assert classes == expected_classes


def test_get_scale():
    sensitivity = 1
    epsilon = 0.3

    expected_scale_factor = float(sensitivity) / float(epsilon)
    scale_factor = get_scale(sensitivity, epsilon)

    assert scale_factor == expected_scale_factor


def test_get_analysis_id():
    analyzer_id = get_data()
    now = datetime.datetime.now()

    hash_object = hashlib.sha256()
    hash_object.update(bytes(str(now), "utf-8"))
    hash_value = hash_object.hexdigest()

    expected_analysis_id = str(analyzer_id) + str(now) + hash_value
    analysis_id = get_analysis_id(analyzer_id, now, hash_value)

    assert analysis_id == expected_analysis_id


def test_iterate():
    items_list = [5, 3.2]
    types = iterate(items_list)

    expected_types = []
    for item in items_list:
        if type(item) is int:
            item_type = "Integer"
        elif type(item) is float:
            item_type = "Float"
        elif type(item) is str:
            item_type = "String"
        else:
            item_type = "Other"
        expected_types.append(item_type)

    assert types == expected_types


def test_add_noise():
    items = np.asarray([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    sensitivity = 1
    epsilon = 0.3
    img_size = items.shape
    print(img_size)

    scale_factor = get_scale(sensitivity, epsilon)
    expected_noise = np.random.laplace(scale=scale_factor, size=img_size)
    noise = add_noise(sensitivity, epsilon, img_size)

    assert noise.shape == expected_noise.shape
