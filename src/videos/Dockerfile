FROM public.ecr.aws/docker/library/python:3.11-slim-trixie

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends g++ ffmpeg procps && rm -rf /var/lib/apt/lists/*
COPY /src/videos-service/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app/video-files/

COPY /src/videos-service /app

ENTRYPOINT ["python"]
CMD ["app.py"]
