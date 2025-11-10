# Testing Guide for SHL Assessment Recommendation System

This guide covers various ways to test the project locally and in production.

## 🚀 Quick Start Testing

### 1. Start the Application Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`

## 📋 Testing Methods

### Method 1: Interactive API Documentation (Recommended)

FastAPI automatically generates interactive API documentation:

1. **Swagger UI** (Interactive): 
   - Open: `http://localhost:8000/docs`
   - Test all endpoints directly in the browser
   - See request/response schemas
   - Try different queries

2. **ReDoc** (Documentation):
   - Open: `http://localhost:8000/redoc`
   - Read detailed API documentation

### Method 2: Using cURL Commands

#### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

#### Root Endpoint
```bash
curl http://localhost:8000/
```

#### Get Recommendations
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "I need a Java developer with strong problem-solving skills"}'
```

#### List Available Assessments
```bash
curl "http://localhost:8000/assessments?limit=5"
```

#### Analyze Query Intent
```bash
curl "http://localhost:8000/analyze?query=Python%20developer%20with%20communication%20skills"
```

### Method 3: Using Python Requests

Create a test script `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Test health check
print("1. Testing Health Check...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test recommendations
print("2. Testing Recommendations...")
response = requests.post(
    f"{BASE_URL}/recommend",
    json={"query": "Java developer who can work in teams and solve complex problems"}
)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Found {len(data['recommended_assessments'])} recommendations")
for i, assessment in enumerate(data['recommended_assessments'][:3], 1):
    print(f"  {i}. {assessment['name']}")
print()

# Test list assessments
print("3. Testing List Assessments...")
response = requests.get(f"{BASE_URL}/assessments?limit=3")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Total assessments: {data['total']}")
print(f"Showing: {len(data['assessments'])} assessments\n")

# Test query analysis
print("4. Testing Query Analysis...")
response = requests.get(f"{BASE_URL}/analyze?query=technical%20skills%20assessment")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")
```

Run it:
```bash
python test_api.py
```

### Method 4: Using Postman or Insomnia

1. Import the API:
   - Base URL: `http://localhost:8000`
   - Or use the OpenAPI schema from `http://localhost:8000/openapi.json`

2. Test endpoints:
   - `GET /health`
   - `GET /`
   - `POST /recommend` (with JSON body)
   - `GET /assessments?limit=10`
   - `GET /analyze?query=your_query`

### Method 5: Frontend Testing

1. **Start the backend** (if not already running):
   ```bash
   python main.py
   ```

2. **Open the frontend**:
   - Open `index.html` in your browser
   - Or serve it:
     ```bash
     python -m http.server 3000
     ```
     Then open `http://localhost:3000`

3. **Test the UI**:
   - Enter a job description query
   - Click "Get Recommendations"
   - Verify results are displayed

## 🧪 Evaluation Testing

### Run the Evaluation Script

The project includes an evaluation script to test recommendation quality:

```bash
python compute_recall.py
```

This will:
- Create train and test sets
- Generate predictions for test queries
- Calculate Mean Recall@10 metric
- Save predictions to `predictions.csv`

## 📊 Test Cases

### Test Case 1: Technical Skills Query
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Java developer with Spring Boot experience"}'
```

**Expected**: Technical assessments related to Java/Spring

### Test Case 2: Soft Skills Query
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Team leader with communication and collaboration skills"}'
```

**Expected**: Behavioral/soft skills assessments

### Test Case 3: Mixed Query
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Full-stack developer with Python and JavaScript, good at problem-solving"}'
```

**Expected**: Mix of technical and behavioral assessments

### Test Case 4: Short Query
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "developer"}'
```

**Expected**: General assessments (system should handle short queries)

### Test Case 5: Invalid Query (Error Handling)
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "ab"}'
```

**Expected**: Validation error (query must be at least 3 characters)

## 🌐 Testing on Deployed Environment

### Render Deployment

If deployed on Render, replace `localhost:8000` with your Render URL:

```bash
# Example
curl https://your-app.onrender.com/health
curl -X POST https://your-app.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer"}'
```

### Vercel Deployment

If deployed on Vercel, use your Vercel URL:

```bash
# Example
curl https://your-app.vercel.app/health
curl -X POST https://your-app.vercel.app/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer"}'
```

## ✅ Verification Checklist

- [ ] Health check returns `{"status": "healthy"}`
- [ ] Root endpoint returns API information
- [ ] Recommendations endpoint returns 5-10 assessments
- [ ] Assessments list endpoint returns available assessments
- [ ] Query analysis endpoint returns intent classification
- [ ] Error handling works for invalid queries
- [ ] Frontend can connect to backend and display results
- [ ] Evaluation script runs successfully
- [ ] API documentation is accessible at `/docs`

## 🔍 Debugging Tips

1. **Check logs**: Look at console output when running `python main.py`
2. **Check initialization**: Verify "System initialized successfully!" appears
3. **Check data**: Ensure `data/assessments.json` exists
4. **Check API key**: If using OpenAI, verify `OPENAI_API_KEY` is set (optional)
5. **Check dependencies**: Ensure all packages are installed correctly

## 📝 Example Test Queries

Here are some example queries to test with:

1. **Technical**: "Python developer with machine learning experience"
2. **Behavioral**: "Manager with leadership and communication skills"
3. **Mixed**: "Software engineer who can collaborate and write clean code"
4. **Specific**: "Data scientist with SQL and Python skills"
5. **General**: "IT professional"

## 🐛 Troubleshooting

### Issue: "Recommender not initialized"
- **Solution**: Wait for startup to complete, check logs for initialization errors

### Issue: "No assessments found"
- **Solution**: Run the crawler first or check `data/assessments.json` exists

### Issue: Connection refused
- **Solution**: Ensure the server is running on the correct port

### Issue: Import errors
- **Solution**: Install all dependencies: `pip install -r requirements.txt`

