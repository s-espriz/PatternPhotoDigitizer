FROM python:3.11

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y


WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

