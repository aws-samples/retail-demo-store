FROM golang:1.11-alpine AS build
WORKDIR /src/
COPY src/carts-service/*.* /src/
RUN apk add --no-cache git
RUN go get -u github.com/gorilla/mux
RUN go get -u github.com/aws/aws-sdk-go
RUN go get -u gopkg.in/yaml.v2
RUN CGO_ENABLED=0 go build -o /bin/carts-service

EXPOSE 80
ENTRYPOINT ["/bin/carts-service"]