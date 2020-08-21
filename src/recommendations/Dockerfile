FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y g++
COPY /src/recommendations-service/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY /src/recommendations-service /app

ENTRYPOINT ["python"]
CMD ["app.py"]
