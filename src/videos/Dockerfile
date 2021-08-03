FROM public.ecr.aws/s5z3t2n9/python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y g++ ffmpeg procps
COPY /src/videos-service/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app/video-files/

COPY /src/videos-service /app

ENTRYPOINT ["python"]
CMD ["app.py"]
