# Use an official Nginx base image
FROM nginx:latest

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# Expose only the HTTPS port
EXPOSE 443

# Run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]