"""
Embeddings module for semantic search
Uses OpenAI's text-embedding-3-large model
"""

import numpy as np
from typing import List, Dict, Any, Optional
import json
import os
import pickle

# Manual cosine similarity implementation to avoid scikit-learn dependency
def cosine_similarity(vectors1, vectors2):
    """
    Compute cosine similarity between two sets of vectors.
    Replaces sklearn.metrics.pairwise.cosine_similarity to reduce dependencies.
    
    Args:
        vectors1: Array of shape (n_samples1, n_features) or (n_features,)
        vectors2: Array of shape (n_samples2, n_features) or (n_features,)
    
    Returns:
        Similarity scores
    """
    # Handle 1D input
    if vectors1.ndim == 1:
        vectors1 = vectors1.reshape(1, -1)
    if vectors2.ndim == 1:
        vectors2 = vectors2.reshape(1, -1)
    
    # Normalize vectors
    norm1 = np.linalg.norm(vectors1, axis=1, keepdims=True)
    norm2 = np.linalg.norm(vectors2, axis=1, keepdims=True)
    
    # Avoid division by zero
    norm1 = np.where(norm1 == 0, 1, norm1)
    norm2 = np.where(norm2 == 0, 1, norm2)
    
    vectors1_norm = vectors1 / norm1
    vectors2_norm = vectors2 / norm2
    
    # Compute cosine similarity
    similarity = np.dot(vectors1_norm, vectors2_norm.T)
    
    return similarity

# For demo purposes, we'll use sentence-transformers if OpenAI API is not available
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available, using sentence-transformers as fallback")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Sentence transformers not available")

class EmbeddingEngine:
    """Handles text embeddings for semantic search"""
    
    def __init__(self, model_name: str = "text-embedding-3-large", api_key: Optional[str] = None):
        self.model_name = model_name
        self.embeddings_cache = {}
        self.assessment_embeddings = None
        self.assessments = []
        
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(api_key=api_key)
            self.use_openai = True
        elif SENTENCE_TRANSFORMERS_AVAILABLE:
            # Fallback to sentence-transformers
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_openai = False
        else:
            # Fallback to random embeddings for demo
            self.use_openai = False
            self.use_random = True
    
    def get_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Get embedding for a single text"""
        if use_cache and text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        if self.use_openai:
            try:
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=text
                )
                embedding = np.array(response.data[0].embedding)
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fallback to random
                embedding = self._get_fallback_embedding(text)
        elif SENTENCE_TRANSFORMERS_AVAILABLE:
            embedding = self.model.encode(text)
        else:
            embedding = self._get_fallback_embedding(text)
        
        if use_cache:
            self.embeddings_cache[text] = embedding
        
        return embedding
    
    def _get_fallback_embedding(self, text: str) -> np.ndarray:
        """Generate a deterministic pseudo-embedding based on text features"""
        # Create a feature vector based on text characteristics
        features = []
        
        # Word-based features
        words = text.lower().split()
        features.append(len(words))  # Word count
        features.append(len(text))  # Character count
        features.append(text.count(' '))  # Space count
        
        # Keyword presence features (important for our use case)
        tech_keywords = ['java', 'python', 'javascript', 'sql', 'programming', 'technical', 
                        'coding', 'software', 'data', 'analysis', 'database', 'development']
        behavior_keywords = ['personality', 'behavior', 'teamwork', 'leadership', 'communication',
                           'collaboration', 'motivation', 'culture', 'customer', 'service']
        cognitive_keywords = ['reasoning', 'logical', 'numerical', 'verbal', 'analytical',
                            'critical', 'problem', 'solving', 'cognitive', 'ability']
        
        for keyword_list in [tech_keywords, behavior_keywords, cognitive_keywords]:
            keyword_score = sum(1 for kw in keyword_list if kw in text.lower())
            features.append(keyword_score)
        
        # Character distribution features
        for char in 'abcdefghijklmnopqrstuvwxyz':
            features.append(text.lower().count(char))
        
        # Pad or truncate to fixed size (384 dimensions to match small models)
        target_size = 384
        features = features[:target_size] if len(features) > target_size else features + [0] * (target_size - len(features))
        
        # Normalize
        embedding = np.array(features, dtype=np.float32)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def get_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return np.array(embeddings)
    
    def load_assessments(self, filepath: str = 'data/assessments.json'):
        """Load assessments from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.assessments = json.load(f)
        return self.assessments
    
    def build_assessment_embeddings(self, assessments: Optional[List[Dict]] = None):
        """Build embeddings for all assessments"""
        if assessments:
            self.assessments = assessments
        
        if not self.assessments:
            raise ValueError("No assessments loaded")
        
        # Create rich text representation for each assessment
        assessment_texts = []
        for assessment in self.assessments:
            # Combine name, description, category, and test types for richer embedding
            text_parts = [
                assessment.get('name', ''),
                assessment.get('description', ''),
                assessment.get('category', ''),
                ' '.join(assessment.get('test_type', []) if isinstance(assessment.get('test_type'), list) 
                        else assessment.get('test_type', '').split('|'))
            ]
            combined_text = ' '.join(filter(None, text_parts))
            assessment_texts.append(combined_text)
        
        # Get embeddings
        self.assessment_embeddings = self.get_batch_embeddings(assessment_texts)
        
        return self.assessment_embeddings
    
    def search(self, query: str, top_k: int = 10, 
               balance_categories: bool = True) -> List[Dict[str, Any]]:
        """
        Search for most relevant assessments
        
        Args:
            query: Search query
            top_k: Number of results to return
            balance_categories: If True, try to balance between Knowledge & Skills 
                              and Personality & Behavior categories
        """
        if self.assessment_embeddings is None:
            raise ValueError("Assessment embeddings not built. Call build_assessment_embeddings first.")
        
        # Get query embedding
        query_embedding = self.get_embedding(query).reshape(1, -1)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.assessment_embeddings)[0]
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1]
        
        results = []
        if balance_categories and self._should_balance(query):
            # Try to balance between categories
            knowledge_results = []
            personality_results = []
            other_results = []
            
            for idx in top_indices:
                assessment = self.assessments[idx].copy()
                assessment['score'] = float(similarities[idx])
                
                category = assessment.get('category', '')
                if 'Knowledge' in category:
                    knowledge_results.append(assessment)
                elif 'Personality' in category or 'Behavior' in category:
                    personality_results.append(assessment)
                else:
                    other_results.append(assessment)
            
            # Balance results
            results = self._balance_results(
                knowledge_results, 
                personality_results, 
                other_results, 
                top_k
            )
        else:
            # Return top results without balancing
            for idx in top_indices[:top_k]:
                assessment = self.assessments[idx].copy()
                assessment['score'] = float(similarities[idx])
                results.append(assessment)
        
        return results
    
    def _should_balance(self, query: str) -> bool:
        """Determine if query requires balanced categories"""
        query_lower = query.lower()
        
        # Keywords suggesting need for both technical and behavioral assessment
        balance_keywords = [
            'collaborat', 'team', 'work with', 'stakeholder', 'communication',
            'culture', 'fit', 'soft skill', 'interpersonal', 'and', 'both',
            'well-rounded', 'holistic', 'comprehensive'
        ]
        
        # Check if query mentions both technical and behavioral aspects
        has_technical = any(kw in query_lower for kw in 
                           ['java', 'python', 'sql', 'technical', 'coding', 'programming',
                            'software', 'developer', 'engineer', 'data', 'database'])
        has_behavioral = any(kw in query_lower for kw in balance_keywords)
        
        return has_technical and has_behavioral
    
    def _balance_results(self, knowledge: List[Dict], personality: List[Dict], 
                        other: List[Dict], top_k: int) -> List[Dict]:
        """Balance results between categories"""
        results = []
        
        # Determine split
        if knowledge and personality:
            # Aim for 50-50 split if both categories present
            k_count = min(len(knowledge), top_k // 2 + 1)
            p_count = min(len(personality), top_k // 2 + 1)
            
            # Adjust if one category has fewer items
            if len(knowledge) < k_count:
                p_count = min(len(personality), top_k - len(knowledge))
            elif len(personality) < p_count:
                k_count = min(len(knowledge), top_k - len(personality))
            
            results.extend(knowledge[:k_count])
            results.extend(personality[:p_count])
        else:
            # Use what's available
            results.extend(knowledge[:top_k])
            results.extend(personality[:top_k])
        
        # Fill remaining slots with other results if needed
        remaining = top_k - len(results)
        if remaining > 0 and other:
            results.extend(other[:remaining])
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def save_embeddings(self, filepath: str = 'data/embeddings.pkl'):
        """Save embeddings to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'assessments': self.assessments,
                'embeddings': self.assessment_embeddings,
                'cache': self.embeddings_cache
            }, f)
    
    def load_embeddings(self, filepath: str = 'data/embeddings.pkl'):
        """Load embeddings from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.assessments = data['assessments']
            self.assessment_embeddings = data['embeddings']
            self.embeddings_cache = data['cache']

def test_embedding_engine():
    """Test the embedding engine"""
    engine = EmbeddingEngine()
    
    # Test with sample assessments
    sample_assessments = [
        {
            "name": "Java Programming Test",
            "description": "Technical assessment for Java skills",
            "category": "Knowledge & Skills",
            "test_type": ["Knowledge & Skills"]
        },
        {
            "name": "Teamwork Assessment",
            "description": "Evaluates collaboration and team skills",
            "category": "Personality & Behavior",
            "test_type": ["Personality & Behavior"]
        }
    ]
    
    engine.build_assessment_embeddings(sample_assessments)
    
    # Test search
    results = engine.search("Java developer who can collaborate with teams", top_k=2)
    
    print("Search Results:")
    for result in results:
        print(f"- {result['name']}: {result['score']:.3f}")

if __name__ == "__main__":
    test_embedding_engine()
