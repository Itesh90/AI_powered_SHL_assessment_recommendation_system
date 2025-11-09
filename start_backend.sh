#!/bin/bash

echo "Starting SHL Assessment Recommendation System..."

# Change to backend directory
cd backend

# Check if data exists
if [ ! -f "data/assessments.json" ]; then
    echo "Generating assessment data..."
    python crawler.py
fi

# Start the FastAPI server
echo "Starting API server on port 8000..."
python main.py