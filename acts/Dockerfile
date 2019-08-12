#base image for container
FROM python:3.7-alpine

# Set the working directory to /app
WORKDIR /acts

# Copy the current direcitory contents into the container at /app
COPY . /acts

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV TEAM_ID CC_304_305_306_17ECS707

# Run app.py when the container launches
CMD ["python", "act.py"]
