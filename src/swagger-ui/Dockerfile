
FROM public.ecr.aws/s5z3t2n9/nginx:1.21-alpine
WORKDIR /app

COPY offers/openapi/spec.yaml /usr/share/nginx/html/specs/offers/spec.yaml
COPY location/openapi/spec.yaml /usr/share/nginx/html/specs/location/spec.yaml

COPY swagger-ui/index.html /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]