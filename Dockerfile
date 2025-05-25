FROM python:3.10

# Set working directory
WORKDIR /app

# Install Node.js for frontend building
RUN apt-get update && apt-get install -y nodejs npm

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Build frontend - Add --legacy-peer-deps flag
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps
RUN npm run build
WORKDIR /app

# Expose the port Flask will run on
EXPOSE 3001

# Set environment variables
ENV FLASK_APP=api/app.py
ENV LLM_TYPE=ollama 

# Start Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=3001"]