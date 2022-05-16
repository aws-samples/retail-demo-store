
FROM public.ecr.aws/s5z3t2n9/nginx:1.21-alpine
WORKDIR /app

COPY offers/openapi/spec.yaml /usr/share/nginx/html/specs/offers/spec.yaml
COPY location/openapi/spec.yaml /usr/share/nginx/html/specs/location/spec.yaml
COPY carts/openapi/spec.yaml /usr/share/nginx/html/specs/carts/spec.yaml
COPY orders/openapi/spec.yaml /usr/share/nginx/html/specs/orders/spec.yaml
COPY products/openapi/spec.yaml /usr/share/nginx/html/specs/products/spec.yaml
COPY users/openapi/spec.yaml /usr/share/nginx/html/specs/users/spec.yaml
COPY videos/openapi/spec.yaml /usr/share/nginx/html/specs/videos/spec.yaml
COPY search/openapi/spec.yaml /usr/share/nginx/html/specs/search/spec.yaml
COPY recommendations/openapi/spec.yaml /usr/share/nginx/html/specs/recommendations/spec.yaml

COPY swagger-ui/index.html /usr/share/nginx/html
COPY swagger-ui/services.json /usr/share/nginx/html

RUN chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]