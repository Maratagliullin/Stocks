FROM node:lts-alpine

WORKDIR /app
ADD package*.json ./

RUN npm install

ADD . .

EXPOSE 8080
CMD npm run serve