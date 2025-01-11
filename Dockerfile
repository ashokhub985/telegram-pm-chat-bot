# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install any dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose the port the app runs on (if needed)
# EXPOSE 8080  # Uncomment if you're running on port 8080

# Step 6: Set environment variables (for .env)
COPY .env /app/.env

# Step 7: Run bot.py (main script) when the container starts
CMD ["python", "bot.py"]
