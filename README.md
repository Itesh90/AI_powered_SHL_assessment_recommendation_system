# SHL Assessment Recommendation System

An AI-powered web application that recommends the most relevant SHL assessments based on natural language hiring queries or job descriptions.

## 🚀 Features

- **Intelligent Matching**: Uses advanced embeddings and semantic search to match job requirements with assessments
- **Balanced Recommendations**: Automatically balances technical and behavioral assessments when needed
- **Multiple Input Types**: Accepts plain text queries, job descriptions, or URLs
- **Real-time API**: Fast RESTful API with comprehensive endpoints
- **User-friendly Interface**: Clean, responsive web interface with export functionality
- **Evaluation Metrics**: Built-in evaluation system with Mean Recall@10 calculation

## 📁 Project Structure

```
shl_recommender/
│
├── backend/
│   ├── main.py              # FastAPI application
│   ├── crawler.py           # SHL catalog crawler
│   ├── embeddings.py        # Embedding engine for semantic search
│   ├── recommender.py       # Recommendation logic
│   └── data/
│       ├── assessments.json # Assessment database
│       └── assessments.csv  # CSV format database
│
├── frontend/
│   └── index.html           # Web interface
│
├── evaluation/
│   └── compute_recall.py    # Evaluation metrics
│
├── requirements.txt         # Python dependencies
├── README.md               # Documentation
└── .env                    # Environment variables
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Embeddings**: text-embedding-3-large (OpenAI) with fallback to sentence-transformers
- **Frontend**: HTML5 + TailwindCSS + Vanilla JavaScript
- **Database**: JSON/CSV file storage (easily upgradeable to vector DB)
- **Deployment**: 
  - Backend: Render/Railway/Heroku
  - Frontend: Vercel/Netlify/GitHub Pages

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+ (optional, for frontend development)
- OpenAI API key (optional, for enhanced embeddings)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/shl-recommender.git
cd shl-recommender
```

### 2. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_api_key_here  # Optional
PORT=8000
```

### 4. Generate assessment data

```bash
cd backend
python crawler.py
```

This will create the assessment database in `backend/data/`.

### 5. Run the backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### 6. Open the frontend

Open `frontend/index.html` in a web browser, or serve it with:

```bash
cd frontend
python -m http.server 3000
```

Then navigate to `http://localhost:3000`.

## 📊 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

#### Get Recommendations
```http
POST /recommend
```

Request body:
```json
{
  "query": "I am hiring for Java developers who can collaborate with teams"
}
```

Response:
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Java Programming Test",
      "adaptive_support": "No",
      "description": "Technical assessment...",
      "duration": 45,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}
```

#### List Assessments
```http
GET /assessments?limit=10
```

#### Analyze Query Intent
```http
GET /analyze?query=your_query_here
```

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Evaluation

### Running Evaluation

```bash
cd evaluation
python compute_recall.py
```

This will:
1. Create sample train and test sets
2. Generate predictions for test queries
3. Calculate Mean Recall@10
4. Save predictions to CSV

### Metrics

The system uses **Mean Recall@10** as the primary evaluation metric:

```
Recall@K = (Relevant items in top K) / (Total relevant items)
Mean Recall@K = Average of Recall@K across all queries
```

## 🔄 How It Works

### 1. Data Pipeline
- **Crawler**: Scrapes/loads SHL assessment catalog
- **Processing**: Extracts features (name, description, category, test types)
- **Storage**: Saves to JSON/CSV for quick access

### 2. Embedding Generation
- Creates semantic embeddings for each assessment
- Combines multiple fields for richer representation
- Supports OpenAI embeddings with fallback options

### 3. Query Processing
- Extracts text from URLs if provided
- Analyzes query intent (technical vs behavioral needs)
- Enhances short queries with context

### 4. Recommendation Engine
- Performs semantic search using cosine similarity
- Balances categories when query suggests multiple needs
- Returns top 5-10 most relevant assessments

### 5. Result Presentation
- Formats results with all required attributes
- Provides both API and web interface access
- Supports CSV export for further analysis

## 🚀 Deployment

### Backend Deployment (Render)

1. Create a `render.yaml`:

```yaml
services:
  - type: web
    name: shl-recommender-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && python main.py
    envVars:
      - key: PORT
        value: 8000
```

2. Push to GitHub and connect to Render

### Frontend Deployment (Vercel)

1. Update API URL in `frontend/index.html`
2. Deploy to Vercel:

```bash
cd frontend
vercel --prod
```

### Alternative: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

WORKDIR /app/backend
CMD ["python", "main.py"]
```

## 📈 Performance Optimization

### Current Optimizations
- Caching of embeddings
- Batch processing for multiple queries
- Efficient cosine similarity computation
- Balanced category selection algorithm

### Future Improvements
- Vector database integration (Pinecone/Weaviate)
- LLM reranking with GPT-4
- Fine-tuned embeddings for HR domain
- Real-time learning from user feedback
- A/B testing framework

## 🔍 Sample Queries

1. **Technical + Behavioral**: 
   "I am hiring for Java developers who can also collaborate effectively with my business teams."

2. **Multi-skill Technical**: 
   "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript."

3. **Analyst Role**: 
   "Need a data analyst who wants applications to screen using Cognitive and personality tests."

4. **URL Input**: 
   "https://example.com/job-description.html"

## 📝 Submission Checklist

- [x] API endpoint URL (deployed and functional)
- [x] GitHub repository (public/shared access)
- [x] Web application frontend URL
- [x] 2-page approach document
- [x] CSV file with test set predictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- SHL for assessment catalog structure
- OpenAI for embedding models
- FastAPI community for excellent documentation

## 📞 Support

For issues or questions, please open a GitHub issue or contact [your-email@example.com].
