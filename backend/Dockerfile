FROM python:3.11-slim

# Stel werk directory in
WORKDIR /app

# Installeer systeem dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Kopieer requirements
COPY requirements.txt .

# Installeer Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer project bestanden
COPY . .

# Expose poort
EXPOSE 8000