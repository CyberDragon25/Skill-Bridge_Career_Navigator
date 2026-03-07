from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Get absolute path to data directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

# Load job requirements
with open(DATA_DIR / 'jobs.json', 'r') as f:
    JOB_REQUIREMENTS = json.load(f)

# Comprehensive skills taxonomy
KNOWN_SKILLS = [
    # Languages
    "Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Kotlin", "C#", "Ruby", "PHP",
    # Frontend
    "React", "Angular", "Vue", "HTML", "CSS", "Redux", "Next.js",
    # Backend
    "Node.js", "Express", "Flask", "Django", "Spring Boot", "FastAPI",
    # Databases
    "SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "DynamoDB",
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "CI/CD", "Jenkins",
    # Tools & Others
    "Git", "Linux", "Bash", "REST APIs", "GraphQL", "Microservices",
    # Data & ML
    "Spark", "Kafka", "Airflow", "Machine Learning", "TensorFlow", "PyTorch",
    # Mobile
    "Android", "iOS", "Swift", "Jetpack Compose",
    # Other
    "Agile", "Scrum", "JIRA", "Testing", "JUnit"
]

# Learning resources mapping
LEARNING_RESOURCES = {
    "docker": {
        "time": "2 weeks",
        "resource": "Docker Official Tutorial",
        "url": "https://docs.docker.com/get-started/",
        "priority": 1
    },
    "kubernetes": {
        "time": "3 weeks", 
        "resource": "Kubernetes Basics",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "priority": 1
    },
    "aws": {
        "time": "4 weeks",
        "resource": "AWS Free Tier Tutorials",
        "url": "https://aws.amazon.com/getting-started/",
        "priority": 1
    },
    "terraform": {
        "time": "2 weeks",
        "resource": "Terraform Getting Started",
        "url": "https://developer.hashicorp.com/terraform/tutorials",
        "priority": 2
    },
    "react": {
        "time": "3 weeks",
        "resource": "React Official Documentation",
        "url": "https://react.dev/learn",
        "priority": 1
    },
    "node.js": {
        "time": "2 weeks",
        "resource": "Node.js Guide",
        "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs",
        "priority": 1
    },
    "typescript": {
        "time": "2 weeks",
        "resource": "TypeScript Handbook",
        "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "priority": 2
    },
    "graphql": {
        "time": "2 weeks",
        "resource": "GraphQL Tutorial",
        "url": "https://graphql.org/learn/",
        "priority": 2
    },
    "ci/cd": {
        "time": "2 weeks",
        "resource": "GitHub Actions Guide",
        "url": "https://docs.github.com/en/actions/learn-github-actions",
        "priority": 1
    },
    "linux": {
        "time": "3 weeks",
        "resource": "Linux Command Line Basics",
        "url": "https://www.freecodecamp.org/news/the-linux-commands-handbook/",
        "priority": 1
    },
    "sql": {
        "time": "3 weeks",
        "resource": "SQL Tutorial",
        "url": "https://www.w3schools.com/sql/",
        "priority": 1
    },
    "mongodb": {
        "time": "2 weeks",
        "resource": "MongoDB University",
        "url": "https://learn.mongodb.com/",
        "priority": 2
    },
    "spring boot": {
        "time": "4 weeks",
        "resource": "Spring Boot Guide",
        "url": "https://spring.io/guides",
        "priority": 2
    },
}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Skill-Bridge API is running"
    }), 200

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """Parse resume and extract skills"""
    try:
        # Check if file is in request
        if 'resume' not in request.files:
            return jsonify({"error": "No resume file provided"}), 400
        
        file = request.files['resume']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file content
        text = file.read().decode('utf-8', errors='ignore')
        
        # Validate content
        if len(text.strip()) < 20:
            return jsonify({"error": "Resume appears to be empty or too short"}), 400
        
        # Extract skills
        found_skills = extract_skills(text)
        
        if len(found_skills) == 0:
            return jsonify({
                "warning": "No recognized skills found. Make sure your resume includes technical skills.",
                "skills": [],
                "total_skills": 0
            }), 200
        
        return jsonify({
            "skills": found_skills,
            "total_skills": len(found_skills),
            "message": f"Successfully extracted {len(found_skills)} skills"
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error processing resume: {str(e)}"}), 500

def extract_skills(text):
    """Extract skills using keyword matching (FALLBACK - always works)"""
    found = []
    text_lower = text.lower()
    
    # Convert text to set of words for more accurate matching
    words = set(text_lower.split())
    
    for skill in KNOWN_SKILLS:
        skill_lower = skill.lower()
        # Check if skill appears in text (whole word or phrase)
        if skill_lower in text_lower:
            # Avoid duplicates
            if skill not in found:
                found.append(skill)
    
    return found

@app.route('/api/roles', methods=['GET'])
def get_roles():
    """Get available job roles"""
    roles = [
        {"value": role, "label": role, "description": JOB_REQUIREMENTS[role]["description"]}
        for role in JOB_REQUIREMENTS.keys()
    ]
    return jsonify({"roles": roles}), 200

@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    """Analyze skills gap between resume and job requirements"""
    try:
        data = request.json
        
        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        resume_skills = data.get('skills', [])
        target_role = data.get('role', '')
        
        if not resume_skills:
            return jsonify({"error": "No skills provided"}), 400
        
        if not target_role:
            return jsonify({"error": "No role specified"}), 400
        
        if target_role not in JOB_REQUIREMENTS:
            return jsonify({"error": f"Invalid role: {target_role}"}), 400
        
        # Get required skills for role
        job_data = JOB_REQUIREMENTS[target_role]
        required_skills = job_data['required_skills']
        nice_to_have = job_data.get('nice_to_have', [])
        
        # Perform gap analysis using fallback method
        result = analyze_gap_fallback(resume_skills, required_skills, nice_to_have)
        result['role'] = target_role
        result['description'] = job_data['description']
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": f"Error analyzing gap: {str(e)}"}), 500

def analyze_gap_fallback(resume_skills, required_skills, nice_to_have):
    """
    Rule-based gap analysis (FALLBACK - always works)
    This is the core algorithm that ensures the app works without AI
    """
    # Normalize to lowercase for comparison
    resume_set = set(s.lower().strip() for s in resume_skills)
    required_set = set(s.lower().strip() for s in required_skills)
    nice_set = set(s.lower().strip() for s in nice_to_have)
    
    # Find matches and gaps
    matching_required = [s for s in required_skills if s.lower() in resume_set]
    missing_required = [s for s in required_skills if s.lower() not in resume_set]
    matching_nice = [s for s in nice_to_have if s.lower() in resume_set]
    extra_skills = [s for s in resume_skills if s.lower() not in required_set and s.lower() not in nice_set]
    
    # Calculate match percentage (based on required skills only)
    match_pct = (len(matching_required) / len(required_skills)) * 100 if required_skills else 0
    
    # Determine recommendation
    if match_pct >= 80:
        recommendation = "Excellent match! You're ready to apply."
    elif match_pct >= 60:
        recommendation = "Good match! Focus on the missing required skills."
    elif match_pct >= 40:
        recommendation = "Moderate match. Plan 1-2 months of focused learning."
    else:
        recommendation = "Significant gap. Consider 2-3 months of preparation."
    
    return {
        "matching_skills": matching_required,
        "missing_skills": missing_required,
        "matching_nice_to_have": matching_nice,
        "extra_skills": extra_skills[:10],  # Limit to 10
        "match_percentage": round(match_pct, 1),
        "total_required": len(required_skills),
        "total_matching": len(matching_required),
        "total_missing": len(missing_required),
        "recommendation": recommendation,
        "ai_used": False,  # Fallback mode indicator
    }

@app.route('/api/generate-roadmap', methods=['POST'])
def generate_roadmap():
    """Generate personalized learning roadmap for missing skills"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        missing_skills = data.get('missing_skills', [])
        
        if not missing_skills:
            return jsonify({
                "roadmap": [],
                "message": "No missing skills - you're ready to apply!",
                "total_weeks": 0
            }), 200
        
        roadmap = []
        total_weeks = 0
        
        for skill in missing_skills:
            key = skill.lower().strip()
            
            if key in LEARNING_RESOURCES:
                # Use predefined resource
                resource_info = LEARNING_RESOURCES[key].copy()
                resource_info['skill'] = skill
                roadmap.append(resource_info)
                
                # Extract weeks for total calculation
                time_str = resource_info['time']
                weeks = int(time_str.split()[0])
                total_weeks += weeks
            else:
                # Generic resource for skills not in mapping
                roadmap.append({
                    "skill": skill,
                    "time": "2-3 weeks",
                    "resource": f"Online tutorials for {skill}",
                    "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial",
                    "priority": 2
                })
                total_weeks += 2
        
        # Sort by priority (1 = high, 2 = medium)
        roadmap.sort(key=lambda x: (x.get('priority', 3), x['time']))
        
        return jsonify({
            "roadmap": roadmap,
            "total_items": len(roadmap),
            "estimated_total_time": f"{total_weeks} weeks",
            "message": f"Learning plan for {len(roadmap)} skills"
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error generating roadmap: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')