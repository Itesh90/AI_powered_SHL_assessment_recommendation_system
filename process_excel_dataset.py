"""
Process the Gen_AI Dataset.xlsx file and generate submission.csv with predictions
"""
import pandas as pd
import csv
import json
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from recommender import AssessmentRecommender
from embeddings import EmbeddingEngine

def initialize_system():
    """Initialize the recommendation system"""
    print("Initializing recommendation system...")
    
    # Load assessments
    assessments_file = Path("data") / "assessments.json"
    if not assessments_file.exists():
        assessments_file = Path(__file__).parent / "data" / "assessments.json"
    
    if not assessments_file.exists():
        raise FileNotFoundError(f"Assessments file not found at {assessments_file}")
    
    print(f"Loading assessments from {assessments_file}")
    with open(assessments_file, 'r', encoding='utf-8') as f:
        assessments = json.load(f)
    
    # Initialize embedding engine
    api_key = os.getenv("OPENAI_API_KEY")
    engine = EmbeddingEngine(api_key=api_key)
    
    # Build embeddings
    print("Building embeddings...")
    engine.build_assessment_embeddings(assessments)
    
    # Initialize recommender
    recommender = AssessmentRecommender(
        embeddings_engine=engine,
        use_llm_reranking=False,
        llm_api_key=api_key
    )
    
    print(f"System initialized! Loaded {len(assessments)} assessments")
    return recommender

def process_excel_dataset(excel_file: str, output_file: str = "submission.csv"):
    """
    Process Excel file and generate predictions
    
    Args:
        excel_file: Path to Excel file with test queries
        output_file: Path to save submission CSV
    """
    # Read Excel file
    print(f"\nReading Excel file: {excel_file}")
    df = pd.read_excel(excel_file)
    
    # Get unique queries
    unique_queries = df['Query'].unique().tolist()
    print(f"Found {len(unique_queries)} unique queries")
    
    # Initialize recommender
    recommender = initialize_system()
    
    # Generate predictions
    print("\nGenerating predictions...")
    predictions = []
    
    for i, query in enumerate(unique_queries, 1):
        print(f"\n[{i}/{len(unique_queries)}] Processing: {query[:60]}...")
        
        try:
            # Get recommendations (top 10)
            recommendations = recommender.get_balanced_recommendations(query, top_k=10)
            
            # Extract URLs
            predicted_urls = [rec["url"] for rec in recommendations]
            
            print(f"  Generated {len(predicted_urls)} recommendations")
            
            # Format for CSV output (one row per query-assessment pair)
            for url in predicted_urls:
                predictions.append({
                    "Query": query,
                    "Assessment_url": url
                })
        
        except Exception as e:
            print(f"  Error processing query: {e}")
            import traceback
            traceback.print_exc()
            # Still add empty predictions to maintain format
            for _ in range(10):
                predictions.append({
                    "Query": query,
                    "Assessment_url": ""
                })
    
    # Save to CSV
    print(f"\nSaving predictions to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Query", "Assessment_url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(predictions)
    
    print(f"[OK] Submission file created: {output_file}")
    print(f"   Total rows: {len(predictions)}")
    print(f"   Unique queries: {len(unique_queries)}")
    print(f"   Average recommendations per query: {len(predictions) / len(unique_queries):.1f}")
    
    return output_file

if __name__ == "__main__":
    excel_file = "Gen_AI Dataset.xlsx"
    
    if not Path(excel_file).exists():
        print(f"Error: {excel_file} not found!")
        sys.exit(1)
    
    process_excel_dataset(excel_file, "submission.csv")
    print("\n[OK] Done! submission.csv is ready for submission.")

