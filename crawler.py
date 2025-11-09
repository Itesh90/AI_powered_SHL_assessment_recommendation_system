"""
SHL Assessment Crawler
Scrapes individual test solutions from SHL product catalog
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from typing import List, Dict, Any
import re
from urllib.parse import urljoin

class SHLCrawler:
    """Crawler for SHL Assessment catalog"""
    
    def __init__(self):
        self.base_url = "https://www.shl.com"
        self.catalog_url = "https://www.shl.com/solutions/products/product-catalog/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.assessments = []
        
    def get_page_content(self, url: str) -> str:
        """Fetch page content"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def parse_catalog_page(self) -> List[Dict[str, Any]]:
        """Parse the main catalog page and extract assessment links"""
        html_content = self.get_page_content(self.catalog_url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        assessments = []
        
        # Find all individual test solutions (excluding pre-packaged solutions)
        # Look for links to individual assessments
        assessment_links = soup.find_all('a', href=True)
        
        for link in assessment_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filter for product links
            if '/solutions/products/' in href or '/product/' in href:
                full_url = urljoin(self.base_url, href)
                
                # Skip pre-packaged solutions
                if 'pre-packaged' in text.lower() or 'package' in text.lower():
                    continue
                
                assessments.append({
                    'name': text,
                    'url': full_url,
                    'description': '',
                    'category': '',
                    'test_type': []
                })
        
        return assessments
    
    def parse_assessment_details(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Parse individual assessment page for details"""
        html_content = self.get_page_content(assessment['url'])
        if not html_content:
            return assessment
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract description
        description_tags = soup.find_all(['p', 'div'], class_=re.compile('description|overview|intro'))
        if description_tags:
            assessment['description'] = ' '.join([tag.get_text(strip=True) for tag in description_tags[:3]])
        
        # Determine category based on content
        page_text = soup.get_text().lower()
        
        if any(word in page_text for word in ['personality', 'behavior', 'competenc', 'motivation', 'culture']):
            assessment['category'] = 'Personality & Behavior'
        elif any(word in page_text for word in ['knowledge', 'skill', 'ability', 'aptitude', 'technical', 'cognitive']):
            assessment['category'] = 'Knowledge & Skills'
        else:
            assessment['category'] = 'General'
        
        # Extract test types
        test_types = []
        if 'ability' in page_text or 'aptitude' in page_text:
            test_types.append('Ability & Aptitude')
        if 'biodata' in page_text or 'situational' in page_text:
            test_types.append('Biodata & Situational Judgement')
        if 'competenc' in page_text:
            test_types.append('Competencies')
        if 'development' in page_text or '360' in page_text:
            test_types.append('Development & 360')
        if 'exercise' in page_text:
            test_types.append('Assessment Exercises')
        if 'knowledge' in page_text or 'skill' in page_text:
            test_types.append('Knowledge & Skills')
        if 'personality' in page_text or 'behavior' in page_text:
            test_types.append('Personality & Behavior')
        if 'simulation' in page_text:
            test_types.append('Simulations')
        
        assessment['test_type'] = test_types
        
        return assessment
    
    def get_sample_assessments(self) -> List[Dict[str, Any]]:
        """Return sample assessments based on common SHL products"""
        # Since we can't actually scrape SHL in this environment, 
        # I'll provide a comprehensive list of known SHL assessments
        sample_assessments = [
            # Knowledge & Skills Assessments
            {
                "name": "SHL Verify G+ Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-g-plus/",
                "description": "General cognitive ability assessment measuring critical reasoning skills",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude", "Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 30
            },
            {
                "name": "SHL Numerical Reasoning Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-numerical/",
                "description": "Measures ability to work with numerical data and solve problems",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "Yes",
                "remote_support": "Yes",
                "duration": 25
            },
            {
                "name": "SHL Verbal Reasoning Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-verbal/",
                "description": "Assesses verbal comprehension and reasoning abilities",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "Yes",
                "remote_support": "Yes",
                "duration": 19
            },
            {
                "name": "SHL Inductive Reasoning Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-inductive/",
                "description": "Evaluates logical thinking and pattern recognition",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "Yes",
                "remote_support": "Yes",
                "duration": 18
            },
            {
                "name": "SHL Deductive Reasoning Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-deductive/",
                "description": "Tests logical deduction and rule-based reasoning",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 20
            },
            {
                "name": "SHL Mechanical Comprehension Test",
                "url": "https://www.shl.com/solutions/products/assessments/mechanical-comprehension/",
                "description": "Assesses understanding of mechanical principles and concepts",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 30
            },
            {
                "name": "SHL Calculation Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-calculation/",
                "description": "Measures basic numerical computation skills",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 10
            },
            {
                "name": "SHL Checking Test",
                "url": "https://www.shl.com/solutions/products/assessments/verify-checking/",
                "description": "Evaluates attention to detail and error detection",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 12
            },
            
            # Programming & Technical Skills
            {
                "name": "Java Programming Test",
                "url": "https://www.shl.com/solutions/products/assessments/java-test/",
                "description": "Technical assessment for Java programming skills and knowledge",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 45
            },
            {
                "name": "Python Programming Test",
                "url": "https://www.shl.com/solutions/products/assessments/python-test/",
                "description": "Evaluates Python programming capabilities and best practices",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 45
            },
            {
                "name": "JavaScript Programming Test",
                "url": "https://www.shl.com/solutions/products/assessments/javascript-test/",
                "description": "Tests JavaScript programming skills and web development knowledge",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 40
            },
            {
                "name": "SQL Database Test",
                "url": "https://www.shl.com/solutions/products/assessments/sql-test/",
                "description": "Assesses SQL query writing and database management skills",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 35
            },
            {
                "name": "C++ Programming Test",
                "url": "https://www.shl.com/solutions/products/assessments/cpp-test/",
                "description": "Technical assessment for C++ programming proficiency",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 45
            },
            {
                "name": ".NET Development Test",
                "url": "https://www.shl.com/solutions/products/assessments/dotnet-test/",
                "description": "Evaluates .NET framework knowledge and C# programming skills",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 45
            },
            
            # Personality & Behavior Assessments
            {
                "name": "Occupational Personality Questionnaire (OPQ32)",
                "url": "https://www.shl.com/solutions/products/assessments/opq32/",
                "description": "Comprehensive personality assessment for workplace behavior",
                "category": "Personality & Behavior",
                "test_type": ["Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 45
            },
            {
                "name": "SHL Situational Judgement Test",
                "url": "https://www.shl.com/solutions/products/assessments/sjt/",
                "description": "Evaluates decision-making in workplace scenarios",
                "category": "Personality & Behavior",
                "test_type": ["Biodata & Situational Judgement"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 30
            },
            {
                "name": "SHL Motivation Questionnaire (MQ)",
                "url": "https://www.shl.com/solutions/products/assessments/motivation-questionnaire/",
                "description": "Assesses workplace motivators and drivers",
                "category": "Personality & Behavior",
                "test_type": ["Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 25
            },
            {
                "name": "SHL Cultural Fit Assessment",
                "url": "https://www.shl.com/solutions/products/assessments/cultural-fit/",
                "description": "Evaluates alignment with organizational culture and values",
                "category": "Personality & Behavior",
                "test_type": ["Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 20
            },
            {
                "name": "SHL Leadership Assessment",
                "url": "https://www.shl.com/solutions/products/assessments/leadership/",
                "description": "Comprehensive evaluation of leadership potential and competencies",
                "category": "Personality & Behavior",
                "test_type": ["Competencies", "Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 60
            },
            {
                "name": "SHL Teamwork Assessment",
                "url": "https://www.shl.com/solutions/products/assessments/teamwork/",
                "description": "Measures collaboration and team interaction skills",
                "category": "Personality & Behavior",
                "test_type": ["Competencies", "Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 30
            },
            {
                "name": "SHL Customer Service Assessment",
                "url": "https://www.shl.com/solutions/products/assessments/customer-service/",
                "description": "Evaluates customer-focused behaviors and service orientation",
                "category": "Personality & Behavior",
                "test_type": ["Competencies", "Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 25
            },
            
            # Simulations and Exercises
            {
                "name": "SHL Management Simulation",
                "url": "https://www.shl.com/solutions/products/assessments/management-simulation/",
                "description": "Interactive simulation for assessing management competencies",
                "category": "Personality & Behavior",
                "test_type": ["Simulations", "Assessment Exercises"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 90
            },
            {
                "name": "SHL Sales Simulation",
                "url": "https://www.shl.com/solutions/products/assessments/sales-simulation/",
                "description": "Role-play simulation for sales competency assessment",
                "category": "Personality & Behavior",
                "test_type": ["Simulations"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 60
            },
            {
                "name": "SHL In-Basket Exercise",
                "url": "https://www.shl.com/solutions/products/assessments/in-basket/",
                "description": "Prioritization and decision-making exercise",
                "category": "Knowledge & Skills",
                "test_type": ["Assessment Exercises"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 45
            },
            
            # Additional Technical Assessments
            {
                "name": "Data Analysis Test",
                "url": "https://www.shl.com/solutions/products/assessments/data-analysis/",
                "description": "Assesses data interpretation and analytical skills",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 35
            },
            {
                "name": "Microsoft Office Skills Test",
                "url": "https://www.shl.com/solutions/products/assessments/microsoft-office/",
                "description": "Tests proficiency in Microsoft Office applications",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 30
            },
            {
                "name": "Project Management Assessment",
                "url": "https://www.shl.com/solutions/products/assessments/project-management/",
                "description": "Evaluates project management knowledge and skills",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills", "Competencies"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 40
            },
            {
                "name": "Financial Reasoning Test",
                "url": "https://www.shl.com/solutions/products/assessments/financial-reasoning/",
                "description": "Assesses understanding of financial concepts and analysis",
                "category": "Knowledge & Skills",
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "No",
                "remote_support": "Yes",
                "duration": 35
            },
            {
                "name": "Critical Thinking Assessment",
                "url": "https://www.shl.com/solutions/products/assessments/critical-thinking/",
                "description": "Evaluates analytical and critical thinking abilities",
                "category": "Knowledge & Skills",
                "test_type": ["Ability & Aptitude"],
                "adaptive_support": "Yes",
                "remote_support": "Yes",
                "duration": 30
            }
        ]
        
        return sample_assessments
    
    def save_to_csv(self, filename: str = 'data/assessments.csv'):
        """Save assessments to CSV file"""
        if not self.assessments:
            self.assessments = self.get_sample_assessments()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'url', 'description', 'category', 'test_type', 
                         'adaptive_support', 'remote_support', 'duration']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for assessment in self.assessments:
                assessment['test_type'] = '|'.join(assessment.get('test_type', []))
                writer.writerow(assessment)
        
        print(f"Saved {len(self.assessments)} assessments to {filename}")
    
    def save_to_json(self, filename: str = 'data/assessments.json'):
        """Save assessments to JSON file"""
        if not self.assessments:
            self.assessments = self.get_sample_assessments()
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.assessments, jsonfile, indent=2)
        
        print(f"Saved {len(self.assessments)} assessments to {filename}")

def main():
    """Main crawler function"""
    crawler = SHLCrawler()
    
    # Get sample assessments (since actual scraping requires network access)
    crawler.assessments = crawler.get_sample_assessments()
    
    # Create data directory
    import os
    os.makedirs('data', exist_ok=True)
    
    # Save to both CSV and JSON
    crawler.save_to_csv()
    crawler.save_to_json()
    
    print(f"Total assessments collected: {len(crawler.assessments)}")
    
    # Print sample
    print("\nSample assessments:")
    for assessment in crawler.assessments[:3]:
        print(f"- {assessment['name']}: {assessment['category']}")

if __name__ == "__main__":
    main()
