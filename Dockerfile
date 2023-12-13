# Use your custom base image from the private repo
FROM your-private-repo/custom-base-image:latest

# Install any required certificates (replace /path/to/certificates with the actual path)
COPY /path/to/certificates /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Create a new user
RUN useradd -ms /bin/bash newuser

# Set the working directory
WORKDIR /app

# Copy your Python script into the container
COPY main.py .

# Change to the new user
USER newuser

# Run the Python script
CMD ["python", "main.py"]
