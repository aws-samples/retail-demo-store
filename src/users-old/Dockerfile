FROM public.ecr.aws/s5z3t2n9/golang:1.11-alpine AS build
WORKDIR /src/
COPY src/users-service/*.* /src/
COPY src/users-service/data/*.* /src/data/
RUN apk add --no-cache git
RUN CGO_ENABLED=0 go build -o /bin/users-service
RUN apk add ca-certificates
FROM scratch
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /bin/users-service /bin/users-service
COPY --from=build /src/data/*.* /bin/data/
EXPOSE 80
ENTRYPOINT ["/bin/users-service"]