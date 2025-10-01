FROM rasa/rasa:3.6.16

WORKDIR /app

# Copy project files
COPY . /app

# Expose Rasa HTTP port
EXPOSE 5005

# Default command: run Rasa server
CMD ["run", "--enable-api", "--cors", "*", "--debug"]
