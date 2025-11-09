"""
Assessment Recommender Module
Handles the recommendation logic and LLM integration
"""

import json
import re
from typing import List, Dict, Any, Optional
from embeddings import EmbeddingEngine
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class AssessmentRecommender:
    """Main recommender class for SHL assessments"""
    
    def __init__(self, embeddings_engine: Optional[EmbeddingEngine] = None,
                 use_llm_reranking: bool = False, llm_api_key: Optional[str] = None):
        """
        Initialize recommender
        
        Args:
            embeddings_engine: Pre-initialized embedding engine
            use_llm_reranking: Whether to use LLM for reranking results
            llm_api_key: API key for LLM (OpenAI or Gemini)
        """
        self.engine = embeddings_engine or EmbeddingEngine()
        self.use_llm_reranking = use_llm_reranking
        self.llm_api_key = llm_api_key
        
        # Load assessments if not already loaded
        if not self.engine.assessments:
            try:
                self.engine.load_assessments('data/assessments.json')
                self.engine.build_assessment_embeddings()
            except FileNotFoundError:
                print("Assessments file not found. Please run crawler first.")
    
    def extract_text_from_url(self, url: str) -> str:
        """Extract text content from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit to first 5000 characters
            
        except Exception as e:
            print(f"Error extracting text from URL: {e}")
            return ""
    
    def process_query(self, query: str) -> str:
        """Process and enhance query"""
        # Check if query is a URL
        if self._is_url(query):
            extracted_text = self.extract_text_from_url(query)
            if extracted_text:
                query = f"Job description: {extracted_text}"
        
        # Enhance query with context if it's too short
        if len(query.split()) < 5:
            query = f"Find assessments for: {query}"
        
        return query
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a URL"""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _normalize_test_type(self, test_type) -> List[str]:
        """Normalize test_type to always be a list of strings"""
        if isinstance(test_type, list):
            return test_type
        elif isinstance(test_type, str):
            # Handle pipe-separated strings
            return [t.strip() for t in test_type.split('|') if t.strip()]
        else:
            return []
    
    def recommend(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get assessment recommendations
        
        Args:
            query: User query or job description
            top_k: Number of recommendations to return (min 5, max 10)
        
        Returns:
            List of recommended assessments
        """
        # Validate top_k
        top_k = max(5, min(10, top_k))
        
        # Process query
        processed_query = self.process_query(query)
        
        # Get initial results from embedding search
        results = self.engine.search(processed_query, top_k=top_k * 2)  # Get more for reranking
        
        # Optionally rerank with LLM
        if self.use_llm_reranking and self.llm_api_key:
            results = self._llm_rerank(processed_query, results, top_k)
        else:
            results = results[:top_k]
        
        # Format results
        formatted_results = []
        for assessment in results:
            formatted_results.append({
                "url": assessment.get("url", ""),
                "name": assessment.get("name", ""),
                "adaptive_support": assessment.get("adaptive_support", "No"),
                "description": assessment.get("description", ""),
                "duration": assessment.get("duration", 30),
                "remote_support": assessment.get("remote_support", "Yes"),
                "test_type": self._normalize_test_type(assessment.get("test_type", []))
            })
        
        return formatted_results
    
    def _llm_rerank(self, query: str, assessments: List[Dict], top_k: int) -> List[Dict]:
        """Use LLM to rerank assessments"""
        # This would integrate with OpenAI or Gemini for reranking
        # For now, return as-is
        return assessments[:top_k]
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the intent and requirements from the query"""
        query_lower = query.lower()
        
        intent = {
            "technical_skills": [],
            "soft_skills": [],
            "cognitive_abilities": [],
            "job_level": "general",
            "assessment_types": []
        }
        
        # Technical skills detection
        tech_patterns = {
            "java": ["java", "j2ee", "spring"],
            "python": ["python", "django", "flask"],
            "javascript": ["javascript", "js", "react", "angular", "vue"],
            "sql": ["sql", "database", "mysql", "postgresql"],
            "data": ["data", "analysis", "analytics", "scientist"],
            "cloud": ["cloud", "aws", "azure", "gcp"],
            ".net": [".net", "c#", "dotnet"],
            "cpp": ["c++", "cpp"]
        }
        
        for skill, patterns in tech_patterns.items():
            if any(p in query_lower for p in patterns):
                intent["technical_skills"].append(skill)
        
        # Soft skills detection
        soft_patterns = {
            "teamwork": ["team", "collaborat", "work together"],
            "leadership": ["lead", "manag", "supervis"],
            "communication": ["communicat", "present", "interact"],
            "customer_service": ["customer", "client", "service"],
            "problem_solving": ["problem", "solv", "analytical"]
        }
        
        for skill, patterns in soft_patterns.items():
            if any(p in query_lower for p in patterns):
                intent["soft_skills"].append(skill)
        
        # Cognitive abilities
        if any(word in query_lower for word in ["cognitive", "reasoning", "logical", "analytical"]):
            intent["cognitive_abilities"].append("general_cognitive")
        if any(word in query_lower for word in ["numerical", "math", "quantitative"]):
            intent["cognitive_abilities"].append("numerical")
        if any(word in query_lower for word in ["verbal", "language", "communication"]):
            intent["cognitive_abilities"].append("verbal")
        
        # Job level detection
        if any(word in query_lower for word in ["senior", "lead", "principal", "architect"]):
            intent["job_level"] = "senior"
        elif any(word in query_lower for word in ["junior", "entry", "graduate", "intern"]):
            intent["job_level"] = "junior"
        elif any(word in query_lower for word in ["mid", "intermediate"]):
            intent["job_level"] = "mid"
        
        # Assessment type preferences
        if any(word in query_lower for word in ["personality", "behavior", "culture"]):
            intent["assessment_types"].append("personality")
        if any(word in query_lower for word in ["technical", "coding", "programming"]):
            intent["assessment_types"].append("technical")
        if any(word in query_lower for word in ["cognitive", "ability", "aptitude"]):
            intent["assessment_types"].append("cognitive")
        
        return intent
    
    def get_balanced_recommendations(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get balanced recommendations based on query intent
        
        This method ensures a good mix of assessment types when the query
        suggests multiple competency areas
        """
        intent = self.analyze_query_intent(query)
        processed_query = self.process_query(query)
        
        # Determine if balancing is needed
        needs_technical = bool(intent["technical_skills"]) or "technical" in intent["assessment_types"]
        needs_behavioral = bool(intent["soft_skills"]) or "personality" in intent["assessment_types"]
        needs_cognitive = bool(intent["cognitive_abilities"]) or "cognitive" in intent["assessment_types"]
        
        # Get recommendations with balancing hint
        balance = needs_technical and (needs_behavioral or needs_cognitive)
        
        results = self.engine.search(
            processed_query, 
            top_k=top_k,
            balance_categories=balance
        )
        
        # Format and return
        formatted_results = []
        for assessment in results:
            formatted_results.append({
                "url": assessment.get("url", ""),
                "name": assessment.get("name", ""),
                "adaptive_support": assessment.get("adaptive_support", "No"),
                "description": assessment.get("description", ""),
                "duration": assessment.get("duration", 30),
                "remote_support": assessment.get("remote_support", "Yes"),
                "test_type": self._normalize_test_type(assessment.get("test_type", []))
            })
        
        return formatted_results

def create_sample_recommendations():
    """Create sample recommendations for testing"""
    recommender = AssessmentRecommender()
    
    # Test queries
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams.",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.",
        "Need assessments for a senior data analyst role requiring strong analytical and communication skills."
    ]
    
    print("Testing Assessment Recommender\n" + "="*50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        recommendations = recommender.get_balanced_recommendations(query, top_k=7)
        
        print(f"Found {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['name']}")
            print(f"   URL: {rec['url']}")
            print(f"   Duration: {rec['duration']} minutes")
        print()

if __name__ == "__main__":
    create_sample_recommendations()
