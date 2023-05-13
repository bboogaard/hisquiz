FROM nginx:stable-alpine

COPY ./src/manage /usr/share/nginx/html
COPY ./src/manage/nginx /etc/nginx/conf.d

WORKDIR /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]