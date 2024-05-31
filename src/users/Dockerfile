FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm

WORKDIR /src

RUN apt-get update && apt-get install -y  && rm -rf /var/lib/apt/lists/*

COPY src/users-service/data/*.* /src/data/
COPY src/users-service/requirements.txt .
RUN python3 -m pip install --upgrade pip && python3 -m pip install --no-cache-dir -r requirements.txt

COPY src/users-service/*.* /src/



ENV PYTHONUNBUFFERED 1
EXPOSE 80
CMD ["python3", "/src/users-service/main.py"]