FROM python:3.7
RUN python -m pip install --upgrade pip
RUN pip install opencv-python-headless==4.5.3.56
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python
RUN pip install poetry
RUN pip install websocket-client
RUN pip install rel
RUN pip install requests

#COPY requirements.txt requirements.txt
#RUN apt-get update && apt-get install git -y
#RUN pip3 install -r requirements.txt
COPY . /app
WORKDIR /app
COPY pyproject.toml /app
copy app.py /app

COPY yolov3.weights /app
COPY yolov3.cfg /app
COPY coco.names /app

RUN poetry config virtualenvs.create false
RUN poetry install

# RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app.py"]
