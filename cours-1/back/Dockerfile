# INSTRUCTION 1: Base Image
FROM python:3.11-slim

# INSTRUCTION 2: Metadata
LABEL maintainer="dev@example.com"
LABEL description="Example web application demonstrating Docker image concepts"

# INSTRUCTION 3: Working Directory
WORKDIR /app

# INSTRUCTION 4: Copy Dependencies File
COPY requirements.txt .

# INSTRUCTION 5: Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# INSTRUCTION 6: Copy Application Code
COPY . .

# INSTRUCTION 7: Environment Variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5000

# INSTRUCTION 8: Expose Port
EXPOSE 5000

# INSTRUCTION 9: Runtime Command
CMD ["python", "app.py"]
