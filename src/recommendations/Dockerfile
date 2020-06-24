FROM python:3.8-slim

COPY /src/recommendations-service /app

WORKDIR /app

# Needed for Optimizely SDK (git ref in req.txt)
RUN apt-get update && apt-get install -y g++ git
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]