# WP4 Analytic: Privacy-Aware Object Recognition

[![Actions Status][actions badge]][actions]
[![CodeCov][codecov badge]][codecov]
[![LICENSE][license badge]][license]

<!-- Links -->
[actions]: https://github.com/sifis-home/flask_object_recognition/actions
[codecov]: https://codecov.io/gh/sifis-home/flask_object_recognition
[license]: LICENSES/MIT.txt

<!-- Badges -->
[actions badge]: https://github.com/sifis-home/flask_object_recognition/workflows/flask_object_recognition/badge.svg
[codecov badge]: https://codecov.io/gh/sifis-home/flask_object_recognition/branch/master/graph/badge.svg
[license badge]: https://img.shields.io/badge/license-MIT-blue.svg

A crucial aspect of a smart home system is its ability to detect and recognize potentially dangerous objects that may not be easily identifiable by humans alone. This process involves object recognition, where suspicious objects are identified within captured images or videos and their locations within the frame are determined. These suspicious objects can range from intruders to fire incidents, elderly or vulnerable individuals in risky situations, or misplaced hazardous items like sharp tools. To achieve this, the system utilizes cameras to capture images or record videos, which are then transmitted for analysis. During the analysis phase, the system performs object recognition by identifying and classifying the objects present in the images, along with their precise locations. If any suspicious objects are detected, the user is promptly alerted, ensuring timely response and appropriate action. By integrating object recognition capabilities into the smart home system, it becomes capable of effectively identifying potential threats and alerting users to take necessary measures. This enhances the safety and security of the home environment by leveraging advanced image analysis techniques and automation. 
The object recognition algorithm employed in the system, YOLOv3, leverages images or video frames obtained from cameras positioned throughout the controlled environment. This encompasses both the camera integrated within the controlled device and external surveillance cameras placed in the smart home environment. Moreover, recorded videos and individual images can also be utilized as input data for analysis. Through the processing of this input data, the object recognition system identifies and classifies objects based on the patterns and features learned by the underlying model during training. By comparing the detected objects to the known objects, the system can recognize and categorize the objects present in the captured frames. 

In order to preserve the privacy of data, Differential privacy mechanism is used. Differential Privacy is a powerful privacy-preserving technique widely used to add noise to data, including images. We use it to add random Laplacian noise to the pixel values of images and ensure that privacy is protected while still allowing valuable insights to be extracted from the data. The amount of noise added is determined by the sensitivity and privacy budget parameters, where sensitivity measures the impact of input data changes on algorithm output, and the privacy budget controls the level of noise added to protect privacy. 

## Deploying

### Privacy-Aware Object Recognition in a container

Privacy-Aware Object Recognition is intended to run in a docker container on port 8080. The Dockerfile at the root of this repo describes the container. To build and run it execute the following commands:

`docker build -t flask_object_recognition .`

`docker-compose up`

## REST API of Privacy-Aware Object Recognition

Description of the REST endpoint available while Privacy-Aware Object Recognition is running.

---

#### GET /file_object

Description: Returns the classification of objects in an image or video frame.

Command: 

`curl -F "file=@file_location" http://localhost:8080/file_object/<file_name.mp4>/<epsilon>/<sensitivity>/<requestor_id>/<requestor_type>/<request_id>`

Sample: 

`curl -F "file=@file_location" http://localhost:8080/file_object/sample.mp4/0.03/1.0/33466553786f48cb72faad7b2fb9d0952c97/NSSD/2023061906001633466553786f48cb72faad7b2fb9d0952c97`


---
## License

Released under the [MIT License](LICENSE).

## Acknowledgements

This software has been developed in the scope of the H2020 project SIFIS-Home with GA n. 952652.
