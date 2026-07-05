#!/bin/bash
# DO NOT HARDCODE API KEYS HERE.
# Create a .env file in this directory with NVIDIA_API_KEY=your_key_here
uvicorn api:app --host 0.0.0.0 --port 8000
