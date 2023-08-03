FROM python:3.10
RUN python -m pip install --upgrade pip
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install poetry


COPY . /app
WORKDIR /app
COPY pyproject.toml /app
copy app.py /app
copy dog.jpg /app

COPY yolov3.weights /app
COPY yolov3.cfg /app
COPY coco.names /app

RUN poetry config virtualenvs.create false
RUN poetry install

EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app.py"]
