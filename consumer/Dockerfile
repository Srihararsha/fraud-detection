# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the Streamlit app and model
COPY ./consumer /app
COPY ./model /app/model

# Install dependencies
RUN pip install -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "fraud_stream_kafka.py"] 