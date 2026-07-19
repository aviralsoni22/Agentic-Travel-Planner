# HuggingFace Docker Space: build the Vite app, then serve the static bundle on :7860.
# VITE_API_BASE is a build-time value (Vite bakes it into the bundle). On HF, set it as a
# Space "Variable"; HF passes Space variables as build args, which this ARG picks up.
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

# Serve stage: tiny static server with SPA fallback (serve -s), on the HF default port.
FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 7860
CMD ["serve", "-s", "dist", "-l", "7860"]
