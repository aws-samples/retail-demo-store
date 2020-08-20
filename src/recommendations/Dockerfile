FROM python:3.8-slim

WORKDIR /app

# Needed for Optimizely SDK (git ref in req.txt)
RUN apt-get update && apt-get install -y g++ git
COPY /src/recommendations-service/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY /src/recommendations-service /app

ENTRYPOINT ["python"]
CMD ["app.py"]