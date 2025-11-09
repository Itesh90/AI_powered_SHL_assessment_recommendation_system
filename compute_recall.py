"""
Evaluation script for SHL Assessment Recommender
Computes Mean Recall@10 and other metrics
"""

import json
import csv
from typing import List, Dict, Any, Tuple
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from recommender import AssessmentRecommender
from embeddings import EmbeddingEngine

class EvaluationMetrics:
    """Compute evaluation metrics for recommendation system"""
    
    def __init__(self):
        self.recommender = None
        self.initialize_recommender()
    
    def initialize_recommender(self):
        """Initialize the recommender system"""
        # Initialize embedding engine
        engine = EmbeddingEngine()
        
        # Load assessments
        assessments_file = Path(__file__).parent.parent / "backend" / "data" / "assessments.json"
        if assessments_file.exists():
            with open(assessments_file, 'r') as f:
                assessments = json.load(f)
            engine.build_assessment_embeddings(assessments)
        
        # Initialize recommender
        self.recommender = AssessmentRecommender(embeddings_engine=engine)
    
    def recall_at_k(self, predicted: List[str], actual: List[str], k: int = 10) -> float:
        """
        Calculate Recall@K
        
        Args:
            predicted: List of predicted URLs
            actual: List of actual/ground truth URLs
            k: Top K predictions to consider
        
        Returns:
            Recall@K score
        """
        if not actual:
            return 0.0
        
        # Take top K predictions
        predicted_k = predicted[:k]
        
        # Count how many actual items are in predicted
        relevant_retrieved = len(set(predicted_k) & set(actual))
        
        # Calculate recall
        recall = relevant_retrieved / len(actual)
        
        return recall
    
    def mean_recall_at_k(self, predictions: List[Tuple[str, List[str]]], 
                        ground_truth: Dict[str, List[str]], k: int = 10) -> float:
        """
        Calculate Mean Recall@K across all queries
        
        Args:
            predictions: List of (query, predicted_urls) tuples
            ground_truth: Dict mapping query to actual URLs
            k: Top K predictions to consider
        
        Returns:
            Mean Recall@K score
        """
        recalls = []
        
        for query, predicted_urls in predictions:
            actual_urls = ground_truth.get(query, [])
            recall = self.recall_at_k(predicted_urls, actual_urls, k)
            recalls.append(recall)
            print(f"Query: {query[:50]}... | Recall@{k}: {recall:.3f}")
        
        mean_recall = np.mean(recalls) if recalls else 0.0
        
        return mean_recall
    
    def evaluate_test_set(self, test_file: str, output_file: str = "results.csv") -> Dict[str, Any]:
        """
        Evaluate on test set and save predictions
        
        Args:
            test_file: Path to test set file (CSV or JSON)
            output_file: Path to save predictions
        
        Returns:
            Evaluation results
        """
        # Load test queries
        test_queries = self.load_test_queries(test_file)
        
        # Generate predictions
        predictions = []
        predictions_for_csv = []
        
        for query in test_queries:
            # Get recommendations
            recommendations = self.recommender.get_balanced_recommendations(query, top_k=10)
            
            # Extract URLs
            predicted_urls = [rec["url"] for rec in recommendations]
            
            predictions.append((query, predicted_urls))
            
            # Format for CSV output
            for url in predicted_urls:
                predictions_for_csv.append({
                    "Query": query,
                    "Assessment_url": url
                })
        
        # Save predictions to CSV
        self.save_predictions_csv(predictions_for_csv, output_file)
        
        # If we have ground truth, calculate metrics
        ground_truth = self.load_ground_truth(test_file)
        
        results = {}
        if ground_truth:
            mean_recall = self.mean_recall_at_k(predictions, ground_truth, k=10)
            results["mean_recall@10"] = mean_recall
            print(f"\nMean Recall@10: {mean_recall:.3f}")
        
        results["num_queries"] = len(test_queries)
        results["predictions_saved_to"] = output_file
        
        return results
    
    def load_test_queries(self, filepath: str) -> List[str]:
        """Load test queries from file"""
        queries = []
        
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    queries = [item.get("query", item) if isinstance(item, dict) else item 
                              for item in data]
                elif isinstance(data, dict):
                    queries = data.get("queries", [])
        
        elif filepath.endswith('.csv'):
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    query = row.get("query") or row.get("Query")
                    if query and query not in queries:
                        queries.append(query)
        
        elif filepath.endswith('.txt'):
            with open(filepath, 'r') as f:
                queries = [line.strip() for line in f if line.strip()]
        
        return queries
    
    def load_ground_truth(self, filepath: str) -> Dict[str, List[str]]:
        """Load ground truth labels if available"""
        ground_truth = {}
        
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "ground_truth" in data:
                        ground_truth = data["ground_truth"]
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "query" in item and "urls" in item:
                                ground_truth[item["query"]] = item["urls"]
            
            elif filepath.endswith('.csv'):
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        query = row.get("query") or row.get("Query")
                        url = row.get("url") or row.get("Assessment_url")
                        if query and url:
                            if query not in ground_truth:
                                ground_truth[query] = []
                            ground_truth[query].append(url)
        
        except Exception as e:
            print(f"Could not load ground truth: {e}")
        
        return ground_truth
    
    def save_predictions_csv(self, predictions: List[Dict], filepath: str):
        """Save predictions in required CSV format"""
        with open(filepath, 'w', newline='') as f:
            fieldnames = ["Query", "Assessment_url"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(predictions)
        
        print(f"Predictions saved to {filepath}")
    
    def create_sample_test_set(self):
        """Create sample test set for evaluation"""
        # Labeled train set (sample)
        train_set = {
            "queries": [
                "I am hiring for Java developers who can also collaborate effectively with my business teams.",
                "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.",
                "Need a data analyst who can work with large datasets and communicate insights to stakeholders.",
                "Hiring for customer service representatives with strong problem-solving abilities.",
                "Looking for a project manager with technical background and leadership skills.",
                "Need software engineers with experience in cloud technologies and agile methodologies.",
                "Hiring sales professionals with strong negotiation and relationship building skills.",
                "Looking for financial analysts with strong numerical reasoning and attention to detail.",
                "Need HR professionals who can handle recruitment and employee relations.",
                "Hiring for entry-level positions requiring basic computer skills and teamwork."
            ],
            "ground_truth": {
                "I am hiring for Java developers who can also collaborate effectively with my business teams.": [
                    "https://www.shl.com/solutions/products/assessments/java-test/",
                    "https://www.shl.com/solutions/products/assessments/teamwork/",
                    "https://www.shl.com/solutions/products/assessments/opq32/"
                ]
            }
        }
        
        # Unlabeled test set
        test_set = [
            "Need a senior Python developer with strong analytical and problem-solving skills.",
            "Hiring for a data scientist role requiring SQL, Python, and machine learning expertise.",
            "Looking for a customer success manager with excellent communication and relationship management.",
            "Need a DevOps engineer familiar with cloud platforms and automation tools.",
            "Hiring for a business analyst position requiring data analysis and stakeholder management.",
            "Looking for a marketing manager with creative thinking and project management skills.",
            "Need a technical support specialist with troubleshooting abilities and customer service skills.",
            "Hiring for a software architect role requiring system design and leadership capabilities.",
            "Looking for an accounting professional with attention to detail and numerical reasoning."
        ]
        
        # Save train set
        with open("train_set.json", "w") as f:
            json.dump(train_set, f, indent=2)
        
        # Save test set
        with open("test_set.json", "w") as f:
            json.dump({"queries": test_set}, f, indent=2)
        
        print("Sample train and test sets created!")
        
        return train_set, test_set

def main():
    """Main evaluation function"""
    evaluator = EvaluationMetrics()
    
    # Create sample test sets
    print("Creating sample test sets...")
    evaluator.create_sample_test_set()
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    results = evaluator.evaluate_test_set("test_set.json", "predictions.csv")
    
    print("\n" + "="*50)
    print("Evaluation Complete!")
    print(f"Results: {results}")
    
    # Also create submission file in required format
    print("\nCreating submission file...")
    
    # Load predictions and format for submission
    submission_data = []
    with open("predictions.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            submission_data.append(row)
    
    # Save in exact submission format
    with open("submission.csv", "w", newline='') as f:
        fieldnames = ["Query", "Assessment_url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(submission_data)
    
    print("Submission file created: submission.csv")

if __name__ == "__main__":
    main()
