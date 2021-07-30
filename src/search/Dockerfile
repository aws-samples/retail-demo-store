FROM public.ecr.aws/s5z3t2n9/python:3.8-slim

COPY /src/search-service /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]