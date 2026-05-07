# Build Stage: Use Node to build the static React files
FROM node:18-alpine as build

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code and build the app
COPY . .
RUN npm run build

# Serve Stage: Use Nginx to serve the built static files
FROM nginx:alpine

# Copy the build output to Nginx's html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for the Nginx server
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]