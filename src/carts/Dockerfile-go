FROM public.ecr.aws/s5z3t2n9/golang:1.11-alpine AS build
WORKDIR /src/
COPY src/carts-service/*.* /src/
RUN apk add --no-cache git
RUN CGO_ENABLED=0 go build -o /bin/carts-service
RUN apk add ca-certificates

FROM scratch
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /bin/carts-service /bin/carts-service
EXPOSE 80
ENTRYPOINT ["/bin/carts-service"]