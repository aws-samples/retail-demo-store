FROM public.ecr.aws/s5z3t2n9/golang:1.15-alpine AS build
WORKDIR /src/
COPY src/orders-service/*.* /src/
RUN apk add --no-cache git
RUN go get -u github.com/gorilla/mux
RUN go get -u gopkg.in/yaml.v2
RUN CGO_ENABLED=0 go build -o /bin/orders-service
RUN apk add ca-certificates
FROM scratch
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /bin/orders-service /bin/orders-service
EXPOSE 80
ENTRYPOINT ["/bin/orders-service"]