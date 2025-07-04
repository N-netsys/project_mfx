# Stage 1: Use an official, slim Python runtime as a parent image
# Using a specific version like 3.11 is better for reproducibility.
# The '-slim' variant is smaller, making your final image more lightweight.
FROM python:3.11-slim

# Set environment variables to ensure best practices
# 1. Prevents Python from writing .pyc files to disc
# 2. Ensures that print statements and logs are sent straight to the container's log stream
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
# All subsequent commands (COPY, RUN, CMD) will be run from this directory
WORKDIR /app

# Install system dependencies if you have any (e.g., for certain database drivers)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# First, copy only the requirements file. This is a key optimization.
# Docker caches this layer. If requirements.txt doesn't change, Docker won't
# re-install all the packages on subsequent builds, making them much faster.
COPY ./requirements.txt .

# Install the Python dependencies
# --no-cache-dir reduces image size by not storing the download cache.
RUN pip install --no-cache-dir -r requirements.txt

# Now, copy the rest of your application's code into the container.
# This includes your 'app/' directory, 'alembic/' directory, etc.
COPY . .

# Expose the port that Uvicorn will run on.
# This tells Docker that the container listens on port 8000.
# Render will automatically map external traffic to this port.
EXPOSE 8000

# Define the command to run when the container starts.
# This starts the Uvicorn server, binding it to all network interfaces (0.0.0.0)
# so that it's accessible from outside the container.
# We do NOT use --reload in production.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]