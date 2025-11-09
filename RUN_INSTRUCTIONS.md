# How to Run the SHL Assessment Recommendation System

## Prerequisites
- Python 3.8+ (✅ You have Python 3.10.11)
- pip (Python package manager)

## Quick Start (Windows PowerShell)

### Step 1: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: (Optional) Set Environment Variables

Create a `.env` file in the root directory (optional, only if you have an OpenAI API key):

```env
OPENAI_API_KEY=your_api_key_here
PORT=8000
```

**Note:** The system works without an OpenAI API key - it will use sentence-transformers as a fallback.

### Step 3: Generate Assessment Data (First Time Only)

If `assessments.json` doesn't exist or you want to regenerate it:

```powershell
python crawler.py
```

### Step 4: Start the Backend Server

```powershell
python main.py
```

The API will start at: **http://localhost:8000**

You should see:
- API documentation at: http://localhost:8000/docs
- Health check at: http://localhost:8000/health

### Step 5: Open the Frontend

**Option A:** Open `index.html` directly in your browser (double-click the file)

**Option B:** Serve it with a simple HTTP server:

```powershell
# In a new terminal window
python -m http.server 3000
```

Then open: **http://localhost:3000**

## Alternative: Using Docker

If you have Docker installed:

```powershell
docker-compose up
```

This will:
- Build the backend container
- Start the API on port 8000
- Serve the frontend on port 3000

## Testing the System

### Test via API (PowerShell)

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

```powershell
$body = @{
    query = "I am hiring for Java developers who can collaborate with teams"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/recommend" -Method Post -Body $body -ContentType "application/json"
```

### Test via Web Interface

1. Open the frontend (index.html or http://localhost:3000)
2. Enter a query like: "I need a Python developer with good communication skills"
3. Click "Get Recommendations"

## Running Evaluation

To run the evaluation script:

```powershell
python compute_recall.py
```

This will:
- Generate test predictions
- Calculate Mean Recall@10
- Create submission.csv

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, set a different port:

```powershell
$env:PORT=8001
python main.py
```

### Module Not Found
Make sure all dependencies are installed:

```powershell
pip install -r requirements.txt
```

### No Assessments Found
Generate the assessment data:

```powershell
python crawler.py
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /recommend` - Get recommendations
- `GET /assessments?limit=10` - List assessments
- `GET /analyze?query=your_query` - Analyze query intent
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Project Structure

```
files/
├── main.py              # FastAPI backend server
├── recommender.py       # Recommendation logic
├── embeddings.py        # Embedding engine
├── crawler.py           # Assessment data crawler
├── index.html           # Frontend web interface
├── assessments.json     # Assessment database
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (optional)
```

