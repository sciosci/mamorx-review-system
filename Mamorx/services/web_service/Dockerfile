FROM node:20.9-alpine3.17 AS dependencies
WORKDIR /my-project
COPY services/web_service/package*.json ./
RUN npm install

FROM node:20.9-alpine3.17 AS builder
WORKDIR /my-project
COPY services/web_service .
COPY --from=dependencies /my-project/node_modules ./node_modules

RUN npm run build

FROM node:20.9-alpine3.17 AS runner
WORKDIR /my-project
ENV NODE_ENV=production
# If you are using a custom next.config.js file, uncomment this line.
# # COPY --from=builder /my-project/next.config.js ./
# COPY --from=builder /my-project/public ./public
COPY --from=builder /my-project/.next ./.next
COPY --from=builder /my-project/node_modules ./node_modules
COPY --from=builder /my-project/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]