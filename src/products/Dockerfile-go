FROM public.ecr.aws/s5z3t2n9/golang:1.15-alpine AS build
ARG GOPROXY_OVERRIDE=https://proxy.golang.org
WORKDIR /src/
RUN apk add --no-cache git bash
RUN go get -u github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute
COPY src/products-service/*.* /src/
COPY src/products-service/data/*.* /src/data/
RUN echo "Setting GOPROXY to $GOPROXY_OVERRIDE"
RUN go env -w GOPROXY=$GOPROXY_OVERRIDE
RUN CGO_ENABLED=0 go build -o /bin/products-service
RUN apk add ca-certificates
FROM scratch
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /bin/products-service /bin/products-service
COPY --from=build /src/data/*.* /bin/data/
EXPOSE 80
ENTRYPOINT ["/bin/products-service"]