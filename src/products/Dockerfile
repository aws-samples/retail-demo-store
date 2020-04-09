FROM golang:1.11-alpine AS build
WORKDIR /src/
RUN apk add --no-cache git bash
RUN go get -u github.com/gorilla/mux
RUN go get -u gopkg.in/yaml.v2
RUN go get -u github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute
COPY src/products-service/*.* /src/
COPY src/products-service/data/*.* /src/data/
RUN CGO_ENABLED=0 go build -o /bin/products-service
RUN apk add ca-certificates
FROM scratch
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /bin/products-service /bin/products-service
COPY --from=build /src/data/*.* /bin/data/
EXPOSE 80
ENTRYPOINT ["/bin/products-service"]