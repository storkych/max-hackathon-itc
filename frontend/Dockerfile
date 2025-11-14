FROM node:20-alpine AS builder

WORKDIR /app

COPY app/package.json package-lock.json* ./

RUN npm install

COPY app .

RUN npm run build

FROM nginx:alpine AS runner

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
