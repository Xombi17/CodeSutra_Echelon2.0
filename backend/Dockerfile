# Use Python 3.11 slim-bookworm for stability
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Hugging Face Spaces specific port
    PORT=7860

# Install system dependencies required for OpenCV and other tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Set Python to run in unbuffered mode (to see logs on HF immediately)
ENV PYTHONUNBUFFERED=1

# Create a non-root user (Hugging Face security best practice)
# Check if user 1000 exists, if not create it
RUN id -u 1000 &>/dev/null || useradd -m -u 1000 user

# Switch to user
USER user

# Copy application code with ownership (Crucial for SQLite write permissions)
COPY --chown=user . /code



# Expose the port
EXPOSE 7860

# Command to run the application
CMD ["python", "main.py"]
