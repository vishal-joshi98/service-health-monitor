FROM python:3.11-slim

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    curl gnupg2 unixodbc-dev gcc g++ \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list \
       > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean

# Copy requirements first (better Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

CMD ["python", "app.py"]
