from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
import os
import json
from pathlib import Path

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent))

from recommender import AssessmentRecommender
from embeddings import EmbeddingEngine
from crawler import SHLCrawler
from contextlib import asynccontextmanager

# Request/Response models
class RecommendationRequest(BaseModel):
    query: str = Field(..., description="Job description text or URL")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Query must be at least 3 characters long")
        return v.strip()

class AssessmentResponse(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

class RecommendationResponse(BaseModel):
    recommended_assessments: List[AssessmentResponse]

class HealthResponse(BaseModel):
    status: str

# Global recommender instance
recommender = None
engine = None

def initialize_system():
    """Initialize the recommendation system"""
    global recommender, engine
    
    print("Initializing recommendation system...")
    
    # Check if data exists, if not create it
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    assessments_file = data_dir / "assessments.json"
    
    if not assessments_file.exists():
        print("Assessment data not found. Creating sample data...")
        crawler = SHLCrawler()
        crawler.assessments = crawler.get_sample_assessments()
        crawler.save_to_json(str(assessments_file))
        crawler.save_to_csv(str(data_dir / "assessments.csv"))
    
    # Initialize embedding engine
    api_key = os.getenv("OPENAI_API_KEY")
    engine = EmbeddingEngine(api_key=api_key)
    
    # Load assessments
    with open(assessments_file, 'r') as f:
        assessments = json.load(f)
    
    # Build embeddings
    engine.build_assessment_embeddings(assessments)
    
    # Initialize recommender
    recommender = AssessmentRecommender(
        embeddings_engine=engine,
        use_llm_reranking=False,  # Set to True if you have API key
        llm_api_key=api_key
    )
    
    print("System initialized successfully!")
    print(f"Loaded {len(assessments)} assessments")

# Lifespan event handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    initialize_system()
    yield
    # Shutdown (if needed)
    pass

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="AI-powered assessment recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "SHL Assessment Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(request: RecommendationRequest):
    """
    Get assessment recommendations for a given query
    
    - **query**: Job description text or URL containing job description
    
    Returns 5-10 most relevant assessments
    """
    global recommender
    
    if recommender is None:
        raise HTTPException(status_code=503, detail="Recommender not initialized")
    
    try:
        # Get recommendations
        recommendations = recommender.get_balanced_recommendations(
            query=request.query,
            top_k=10  # Return up to 10 recommendations
        )
        
        # Ensure we have at least 5 recommendations
        if len(recommendations) < 5:
            # If we have fewer than 5, try to get more
            recommendations = recommender.recommend(
                query=request.query,
                top_k=10
            )
        
        # Format response
        response = {
            "recommended_assessments": recommendations[:10]  # Max 10
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/assessments", tags=["Assessments"])
async def list_assessments(limit: int = 10):
    """List available assessments"""
    global engine
    
    if engine is None or not engine.assessments:
        raise HTTPException(status_code=503, detail="Assessments not loaded")
    
    return {
        "total": len(engine.assessments),
        "assessments": engine.assessments[:limit]
    }

@app.get("/analyze", tags=["Analysis"])
async def analyze_query(query: str):
    """Analyze query intent"""
    global recommender
    
    if recommender is None:
        raise HTTPException(status_code=503, detail="Recommender not initialized")
    
    intent = recommender.analyze_query_intent(query)
    return {"query": query, "intent": intent}

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return {"error": str(exc)}, 400

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return {"error": "An unexpected error occurred"}, 500

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    # Use PORT environment variable (required by Render) or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )
