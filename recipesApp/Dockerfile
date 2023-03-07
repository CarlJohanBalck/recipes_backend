# Set the base image to use for this container
FROM python:3.9

# Set the working directory within the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Set the command to run when the container starts
CMD ["python3", "recipes.py"]
