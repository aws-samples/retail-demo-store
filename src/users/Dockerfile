FROM golang:1.11-alpine AS build
WORKDIR /src/
COPY src/users-service/*.* /src/
COPY src/users-service/data/*.* /src/data/
RUN apk add --no-cache git
RUN go get -u github.com/gorilla/mux
RUN go get -u gopkg.in/yaml.v2
RUN CGO_ENABLED=0 go build -o /bin/users-service

FROM scratch
COPY --from=build /bin/users-service /bin/users-service
COPY --from=build /src/data/*.* /bin/data/
EXPOSE 80
ENTRYPOINT ["/bin/users-service"]