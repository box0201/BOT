# Koristi službeni Python image
FROM python:3.10-slim

# Postavi radni direktorijum u containera
WORKDIR /app

# Kopiraj sve fajlove u container
COPY . /app

# Instaliraj zavisnosti
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

# Pokreni Python fajl
CMD ["python", "pokret.py"]
