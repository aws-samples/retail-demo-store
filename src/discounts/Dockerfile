FROM python:3.8-slim

COPY /src/discounts-service /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]