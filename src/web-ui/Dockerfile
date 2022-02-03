FROM public.ecr.aws/s5z3t2n9/node:14.17-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci 
COPY . .

RUN npm run build

FROM public.ecr.aws/s5z3t2n9/nginx:1.21-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]