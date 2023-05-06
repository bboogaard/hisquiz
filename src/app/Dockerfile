FROM nginx:stable-alpine

COPY ./src/app /usr/share/nginx/html
COPY ./src/app/nginx /etc/nginx/conf.d

WORKDIR /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]