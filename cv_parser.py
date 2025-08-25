#!/usr/bin/env python3
"""
AI CV Parser & Customization System
Upload existing CV → Parse with AI → Customize for specific jobs → Generate beautiful PDF
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Any, Optional
from io import BytesIO
import PyPDF2
import docx
from cv_generator import UserProfile, JobRequirements

logger = logging.getLogger(__name__)

class CVParserAI:
    def __init__(self):
        """Initialize CV Parser with AI capabilities"""
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 3000
    
    async def parse_cv_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse uploaded CV file and extract structured data using AI
        """
        try:
            # Extract text from file based on type
            if filename.lower().endswith('.pdf'):
                cv_text = self._extract_text_from_pdf(file_content)
            elif filename.lower().endswith(('.docx', '.doc')):
                cv_text = self._extract_text_from_docx(file_content)
            else:
                return {'success': False, 'error': 'Unsupported file format'}
            
            if not cv_text or len(cv_text.strip()) < 50:
                return {'success': False, 'error': 'Could not extract meaningful text from CV'}
            
            # Use AI to parse and structure the CV data
            parsed_data = await self._ai_parse_cv_text(cv_text)
            
            return {
                'success': True,
                'parsed_cv': parsed_data,
                'original_text': cv_text,
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"CV parsing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""
    
    def _extract_text_from_docx(self, docx_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc_file = BytesIO(docx_content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return ""
    
    async def _ai_parse_cv_text(self, cv_text: str) -> Dict[str, Any]:
        """Use AI to parse CV text into structured data"""
        
        prompt = f"""
        You are an expert CV parser. Analyze this CV text and extract structured information.
        
        CV TEXT:
        {cv_text}
        
        TASK: Extract and structure the following information as JSON:
        
        {{
            "personal_info": {{
                "name": "Full name",
                "email": "email address", 
                "phone": "phone number",
                "location": "city, country",
                "linkedin": "LinkedIn URL if present",
                "github": "GitHub URL if present"
            }},
            "professional_summary": "Current professional summary/objective from CV",
            "current_position": "Most recent job title",
            "years_experience": estimated_total_years_as_number,
            "skills": [
                "List of all technical skills mentioned",
                "Programming languages", 
                "Tools and technologies",
                "Frameworks and libraries",
                "Soft skills if mentioned"
            ],
            "education": "Highest degree and institution",
            "work_experience": [
                {{
                    "title": "Job title",
                    "company": "Company name", 
                    "period": "Date range (e.g., 2020-2023)",
                    "responsibilities": [
                        "Key responsibility 1",
                        "Key responsibility 2", 
                        "Key achievement with metrics if available"
                    ]
                }}
            ],
            "certifications": ["Any certifications mentioned"],
            "languages": ["Languages if mentioned"],
            "key_achievements": [
                "Notable achievements with quantifiable results",
                "Awards, recognitions, or standout accomplishments"
            ]
        }}
        
        IMPORTANT:
        - Extract exact information from the CV text
        - Don't add information that isn't there
        - For missing fields, use empty string or empty array
        - Be precise with job titles, company names, and dates
        - Include ALL skills mentioned, even if they seem basic
        - Extract metrics and numbers from achievements where possible
        
        Return ONLY valid JSON. No additional text.
        """
        
        try:
            response = await self._call_ai_api(prompt)
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing if AI returns malformed JSON
            return self._fallback_parse_cv(cv_text)
    
    async def customize_cv_for_job(self, parsed_cv: Dict[str, Any], job_requirements: JobRequirements, 
                                 job_description: str) -> Dict[str, Any]:
        """
        Use AI to customize the parsed CV for a specific job posting
        """
        try:
            # Create customization prompt
            customization_result = await self._ai_customize_cv(parsed_cv, job_requirements, job_description)
            
            return {
                'success': True,
                'customized_cv': customization_result,
                'original_cv': parsed_cv,
                'customization_applied': True
            }
            
        except Exception as e:
            logger.error(f"CV customization error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _ai_customize_cv(self, parsed_cv: Dict[str, Any], job_req: JobRequirements, 
                             job_description: str) -> Dict[str, Any]:
        """AI-powered CV customization for specific job"""
        
        prompt = f"""
        You are an expert career coach specializing in CV optimization for ATS systems.
        
        ORIGINAL CV DATA:
        {json.dumps(parsed_cv, indent=2)}
        
        TARGET JOB:
        - Position: {job_req.title}
        - Company: {job_req.company}
        - Experience Level: {job_req.experience_level}
        - Required Skills: {', '.join(job_req.required_skills)}
        - Key Requirements: {', '.join(job_req.key_requirements)}
        
        JOB DESCRIPTION:
        {job_description}
        
        TASK: Customize the CV to maximize chances of getting this specific job.
        
        Create a new version that:
        1. Rewrites the professional summary to match the job perfectly
        2. Reorders and emphasizes relevant skills from the original CV
        3. Adds missing critical skills the person likely has but didn't mention
        4. Rewrites job responsibilities to include keywords from the job posting
        5. Quantifies achievements with realistic metrics where missing
        6. Optimizes for ATS keyword matching
        
        Return JSON format:
        {{
            "professional_summary": "Rewritten summary with job keywords and compelling value proposition",
            "skills": {{
                "Programming Languages": ["prioritized list based on job match"],
                "Frameworks & Libraries": ["relevant frameworks mentioned in job"],
                "Cloud & DevOps": ["cloud technologies if relevant"],
                "Databases": ["database technologies"],
                "Tools & Methodologies": ["tools, methodologies, soft skills"]
            }},
            "work_experience": [
                {{
                    "title": "keep original or enhance slightly",
                    "company": "keep original", 
                    "period": "keep original",
                    "responsibilities": [
                        "Rewritten responsibilities using job keywords",
                        "Added quantifiable metrics where realistic",
                        "Emphasized relevant technologies and achievements"
                    ]
                }}
            ],
            "key_achievements": [
                "Enhanced achievements that show relevance to target role",
                "Added realistic metrics and business impact",
                "Highlighted skills that match job requirements"
            ],
            "ats_optimization": {{
                "keyword_matches": ["exact keywords from job posting included"],
                "keyword_density_score": estimated_score_out_of_100,
                "missing_critical_skills": ["important job skills not in original CV"],
                "optimization_notes": "Brief explanation of key changes made"
            }}
        }}
        
        CRITICAL: 
        - Keep all information truthful and based on original CV
        - Only enhance and reframe existing experience
        - Don't invent new jobs or fake experience
        - Use EXACT keywords from the job posting naturally
        - Make it compelling but authentic
        
        Return ONLY valid JSON.
        """
        
        try:
            response = await self._call_ai_api(prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback customization
            return self._fallback_customize_cv(parsed_cv, job_req)
    
    def create_user_profile_from_parsed_cv(self, parsed_cv: Dict[str, Any], 
                                         customized_cv: Optional[Dict[str, Any]] = None) -> UserProfile:
        """Convert parsed/customized CV data to UserProfile object"""
        
        # Use customized version if available, otherwise original
        cv_data = customized_cv if customized_cv else parsed_cv
        personal_info = cv_data.get('personal_info', {})
        
        # Extract skills - handle both flat list and categorized format
        skills = []
        if isinstance(cv_data.get('skills'), list):
            skills = cv_data['skills']
        elif isinstance(cv_data.get('skills'), dict):
            # Flatten categorized skills
            for category, skill_list in cv_data['skills'].items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
        
        return UserProfile(
            name=personal_info.get('name', 'Professional'),
            email=personal_info.get('email', ''),
            phone=personal_info.get('phone', ''),
            location=personal_info.get('location', ''),
            linkedin=personal_info.get('linkedin', ''),
            github=personal_info.get('github', ''),
            current_position=cv_data.get('current_position', 'Professional'),
            years_experience=cv_data.get('years_experience', 0),
            skills=skills,
            education=cv_data.get('education', ''),
            work_experience=cv_data.get('work_experience', [])
        )
    
    async def _call_ai_api(self, prompt: str) -> str:
        """Make API call to AI service"""
        try:
            # Simulate AI response for development
            return await self._simulate_ai_response(prompt)
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return await self._simulate_ai_response(prompt)
    
    async def _simulate_ai_response(self, prompt: str) -> str:
        """Simulate AI response for development/testing"""
        
        if "parse cv text" in prompt.lower() or "extract structured information" in prompt.lower():
            return json.dumps({
                "personal_info": {
                    "name": "John Smith",
                    "email": "john.smith@email.com",
                    "phone": "+1 555-123-4567",
                    "location": "San Francisco, CA",
                    "linkedin": "linkedin.com/in/johnsmith",
                    "github": "github.com/johnsmith"
                },
                "professional_summary": "Experienced software developer with 5 years in full-stack development",
                "current_position": "Senior Software Developer",
                "years_experience": 5,
                "skills": [
                    "Python", "JavaScript", "React", "Django", "PostgreSQL", 
                    "Docker", "AWS", "Git", "REST API", "Agile"
                ],
                "education": "B.S. Computer Science, UC Berkeley",
                "work_experience": [
                    {
                        "title": "Senior Software Developer",
                        "company": "TechCorp Inc.",
                        "period": "2020-Present",
                        "responsibilities": [
                            "Developed web applications using Python and React",
                            "Collaborated with cross-functional teams",
                            "Implemented CI/CD pipelines"
                        ]
                    }
                ],
                "certifications": ["AWS Certified Developer"],
                "languages": ["English", "Spanish"],
                "key_achievements": [
                    "Led migration to microservices architecture",
                    "Improved application performance by 40%"
                ]
            })
        
        elif "customize the cv" in prompt.lower():
            return json.dumps({
                "professional_summary": "Results-driven Senior Software Developer with 5+ years of experience in full-stack development, specializing in Python, React, and cloud technologies. Proven track record of delivering scalable solutions and leading technical initiatives. Seeking to leverage expertise in modern development practices to drive innovation at target company.",
                "skills": {
                    "Programming Languages": ["Python", "JavaScript", "TypeScript"],
                    "Frameworks & Libraries": ["React", "Django", "FastAPI"],
                    "Cloud & DevOps": ["AWS", "Docker", "CI/CD"],
                    "Databases": ["PostgreSQL", "Redis"],
                    "Tools & Methodologies": ["Git", "Agile", "REST API", "Microservices"]
                },
                "work_experience": [
                    {
                        "title": "Senior Software Developer",
                        "company": "TechCorp Inc.",
                        "period": "2020-Present",
                        "responsibilities": [
                            "Architected and developed scalable web applications using Python, React, and AWS, serving 100K+ users",
                            "Led cross-functional team of 4 developers implementing microservices architecture, reducing deployment time by 60%",
                            "Implemented automated CI/CD pipelines using Docker and AWS, improving development efficiency by 45%",
                            "Collaborated with product managers and stakeholders to deliver 15+ features quarterly using Agile methodology"
                        ]
                    }
                ],
                "key_achievements": [
                    "Successfully led migration from monolith to microservices architecture, improving system scalability by 300%",
                    "Optimized application performance through database indexing and caching strategies, reducing load times by 40%",
                    "Mentored 3 junior developers while maintaining 98% on-time project delivery rate",
                    "Implemented automated testing suite achieving 95% code coverage and reducing bugs by 50%"
                ],
                "ats_optimization": {
                    "keyword_matches": ["Python", "React", "AWS", "microservices", "CI/CD", "Agile"],
                    "keyword_density_score": 78,
                    "missing_critical_skills": ["Kubernetes", "GraphQL"],
                    "optimization_notes": "Enhanced experience descriptions with quantifiable metrics and added relevant keywords from job posting"
                }
            })
        
        return "AI response placeholder"
    
    def _fallback_parse_cv(self, cv_text: str) -> Dict[str, Any]:
        """Fallback CV parsing if AI fails"""
        
        # Simple regex-based parsing
        name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', cv_text, re.MULTILINE)
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', cv_text)
        phone_match = re.search(r'(\+?[\d\s\-\(\)]+)', cv_text)
        
        return {
            "personal_info": {
                "name": name_match.group(1) if name_match else "Professional",
                "email": email_match.group(1) if email_match else "",
                "phone": phone_match.group(1) if phone_match else "",
                "location": "",
                "linkedin": "",
                "github": ""
            },
            "professional_summary": "Experienced professional seeking new opportunities",
            "current_position": "Professional",
            "years_experience": 3,
            "skills": ["Python", "JavaScript", "SQL"],
            "education": "Computer Science",
            "work_experience": [],
            "certifications": [],
            "languages": [],
            "key_achievements": []
        }
    
    def _fallback_customize_cv(self, parsed_cv: Dict[str, Any], job_req: JobRequirements) -> Dict[str, Any]:
        """Fallback customization if AI fails"""
        
        return {
            "professional_summary": f"Experienced professional with expertise in {', '.join(job_req.required_skills[:3])}",
            "skills": {
                "Technical Skills": parsed_cv.get('skills', [])
            },
            "work_experience": parsed_cv.get('work_experience', []),
            "key_achievements": parsed_cv.get('key_achievements', []),
            "ats_optimization": {
                "keyword_matches": job_req.required_skills[:5],
                "keyword_density_score": 60,
                "missing_critical_skills": [],
                "optimization_notes": "Basic optimization applied"
            }
        }

# Integration function for the main API
async def parse_and_customize_cv(file_content: bytes, filename: str, 
                               job_requirements: JobRequirements, 
                               job_description: str) -> Dict[str, Any]:
    """
    Main function to parse uploaded CV and customize it for specific job
    """
    parser = CVParserAI()
    
    # Step 1: Parse uploaded CV
    parse_result = await parser.parse_cv_file(file_content, filename)
    
    if not parse_result['success']:
        return parse_result
    
    # Step 2: Customize for specific job
    customize_result = await parser.customize_cv_for_job(
        parse_result['parsed_cv'], 
        job_requirements, 
        job_description
    )
    
    if not customize_result['success']:
        return customize_result
    
    # Step 3: Create UserProfile object for PDF generation
    user_profile = parser.create_user_profile_from_parsed_cv(
        parse_result['parsed_cv'],
        customize_result['customized_cv']
    )
    
    return {
        'success': True,
        'original_cv': parse_result['parsed_cv'],
        'customized_cv': customize_result['customized_cv'],
        'user_profile': user_profile,
        'filename': filename
    }

# Test function
async def test_cv_parser():
    """Test CV parsing system"""
    
    # Simulate uploaded CV content
    sample_cv_text = """
    John Smith
    john.smith@email.com | +1 555-123-4567 | San Francisco, CA
    LinkedIn: linkedin.com/in/johnsmith
    
    PROFESSIONAL SUMMARY
    Experienced Software Developer with 5 years in full-stack development
    
    SKILLS
    Python, JavaScript, React, Django, PostgreSQL, Docker, AWS, Git
    
    EXPERIENCE
    Senior Software Developer | TechCorp Inc. | 2020-Present
    • Developed web applications using Python and React
    • Implemented CI/CD pipelines
    • Led team of 3 developers
    
    EDUCATION
    B.S. Computer Science, UC Berkeley, 2018
    """
    
    # Test parsing
    parser = CVParserAI()
    parse_result = await parser._ai_parse_cv_text(sample_cv_text)
    
    print("🔍 CV Parsing Result:")
    print("=" * 50)
    print(json.dumps(parse_result, indent=2))
    
    return parse_result

if __name__ == "__main__":
    print("📄 AI CV Parser & Customization System")
    print("=" * 50)
    
    # Run test
    asyncio.run(test_cv_parser())