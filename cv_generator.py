#!/usr/bin/env python3
"""
AI CV Generator - Prototype
Generates tailored CVs based on job requirements
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class UserProfile:
    """User profile data"""
    name: str
    email: str
    phone: str
    location: str
    linkedin: str = ""
    github: str = ""
    
    # Professional data
    current_position: str = ""
    years_experience: int = 0
    skills: List[str] = None
    education: str = ""
    
    # Work experience (simplified)
    work_experience: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.work_experience is None:
            self.work_experience = []

@dataclass
class JobRequirements:
    """Parsed job requirements"""
    title: str
    company: str
    required_skills: List[str]
    nice_to_have: List[str]
    experience_level: str
    key_requirements: List[str]
    technologies: List[str]

class CVGenerator:
    def __init__(self):
        self.templates = {
            'ats_friendly': self._create_ats_template,
            'modern': self._create_modern_template,
            'tech': self._create_tech_template
        }
    
    def generate_cv(self, user_profile: UserProfile, job_requirements: JobRequirements, 
                   template_type: str = 'ats_friendly') -> str:
        """Generate tailored CV"""
        
        if template_type not in self.templates:
            template_type = 'ats_friendly'
        
        # Analyze skill match
        skill_analysis = self._analyze_skills(user_profile.skills, job_requirements.required_skills)
        
        # Tailor user profile to job
        tailored_profile = self._tailor_profile(user_profile, job_requirements, skill_analysis)
        
        # Generate CV content
        cv_content = self.templates[template_type](tailored_profile, job_requirements, skill_analysis)
        
        return cv_content
    
    def _analyze_skills(self, user_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        """Analyze skill matching"""
        user_lower = [s.lower() for s in user_skills]
        required_lower = [s.lower() for s in required_skills]
        
        matching = []
        missing = []
        
        for req_skill in required_skills:
            found = False
            for user_skill in user_skills:
                if req_skill.lower() in user_skill.lower() or user_skill.lower() in req_skill.lower():
                    matching.append(req_skill)
                    found = True
                    break
            if not found:
                missing.append(req_skill)
        
        return {
            'matching_skills': matching,
            'missing_skills': missing,
            'match_score': len(matching) / len(required_skills) if required_skills else 0,
            'priority_skills': required_skills[:8]  # Top 8 most important
        }
    
    def _tailor_profile(self, profile: UserProfile, job_req: JobRequirements, 
                       skill_analysis: Dict[str, Any]) -> UserProfile:
        """Tailor user profile for specific job"""
        
        # Create tailored copy
        tailored = UserProfile(
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            location=profile.location,
            linkedin=profile.linkedin,
            github=profile.github,
            current_position=profile.current_position,
            years_experience=profile.years_experience,
            skills=profile.skills.copy(),
            education=profile.education,
            work_experience=profile.work_experience.copy()
        )
        
        # Reorder skills to match job requirements
        priority_skills = []
        other_skills = []
        
        for skill in tailored.skills:
            if any(req_skill.lower() in skill.lower() for req_skill in job_req.required_skills):
                priority_skills.append(skill)
            else:
                other_skills.append(skill)
        
        tailored.skills = priority_skills + other_skills
        
        return tailored
    
    def _create_ats_template(self, profile: UserProfile, job_req: JobRequirements, 
                            skill_analysis: Dict[str, Any]) -> str:
        """Create ATS-friendly CV template"""
        
        cv_content = f"""
{profile.name.upper()}
{profile.email} | {profile.phone} | {profile.location}
{profile.linkedin + " | " if profile.linkedin else ""}{profile.github if profile.github else ""}

PROFESSIONAL SUMMARY
{self._generate_professional_summary(profile, job_req, skill_analysis)}

TECHNICAL SKILLS
{self._format_skills_for_ats(profile.skills, skill_analysis['priority_skills'])}

PROFESSIONAL EXPERIENCE
{self._format_experience_for_ats(profile.work_experience, job_req)}

EDUCATION
{profile.education}

KEY ACHIEVEMENTS
{self._generate_key_achievements(profile, job_req)}
"""
        
        return cv_content.strip()
    
    def _generate_professional_summary(self, profile: UserProfile, job_req: JobRequirements,
                                     skill_analysis: Dict[str, Any]) -> str:
        """Generate tailored professional summary"""
        
        experience_text = f"{profile.years_experience}+ years" if profile.years_experience > 0 else "Experienced"
        
        # Use job-specific keywords
        key_technologies = ", ".join(skill_analysis['matching_skills'][:5])
        
        summary = f"""
{experience_text} {job_req.title.replace('Senior ', '').replace('Junior ', '')} with proven expertise in {key_technologies}. 
Demonstrated success in {job_req.experience_level.lower()}-level projects with focus on scalable solutions and best practices.
Strong background in software development lifecycle, agile methodologies, and cross-functional team collaboration.
Passionate about leveraging cutting-edge technologies to deliver high-impact business solutions.
""".strip()
        
        return summary
    
    def _format_skills_for_ats(self, user_skills: List[str], priority_skills: List[str]) -> str:
        """Format skills section for ATS optimization"""
        
        # Group skills by category
        programming = []
        frameworks = []
        tools = []
        cloud = []
        databases = []
        other = []
        
        programming_keywords = ['python', 'java', 'javascript', 'c#', 'go', 'rust', 'kotlin']
        framework_keywords = ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'spring']
        tool_keywords = ['docker', 'kubernetes', 'jenkins', 'git', 'gitlab', 'ci/cd']
        cloud_keywords = ['aws', 'azure', 'gcp', 'cloud']
        db_keywords = ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch']
        
        for skill in user_skills:
            skill_lower = skill.lower()
            
            if any(kw in skill_lower for kw in programming_keywords):
                programming.append(skill)
            elif any(kw in skill_lower for kw in framework_keywords):
                frameworks.append(skill)
            elif any(kw in skill_lower for kw in tool_keywords):
                tools.append(skill)
            elif any(kw in skill_lower for kw in cloud_keywords):
                cloud.append(skill)
            elif any(kw in skill_lower for kw in db_keywords):
                databases.append(skill)
            else:
                other.append(skill)
        
        skill_sections = []
        
        if programming:
            skill_sections.append(f"Programming Languages: {', '.join(programming)}")
        if frameworks:
            skill_sections.append(f"Frameworks & Libraries: {', '.join(frameworks)}")
        if cloud:
            skill_sections.append(f"Cloud Platforms: {', '.join(cloud)}")
        if databases:
            skill_sections.append(f"Databases: {', '.join(databases)}")
        if tools:
            skill_sections.append(f"Tools & Technologies: {', '.join(tools)}")
        if other:
            skill_sections.append(f"Additional Skills: {', '.join(other)}")
        
        return "\n".join(skill_sections)
    
    def _format_experience_for_ats(self, work_experience: List[Dict], job_req: JobRequirements) -> str:
        """Format work experience with job-relevant keywords"""
        
        if not work_experience:
            return f"""
SOFTWARE ENGINEER | Various Companies | 2020 - Present
- Developed and maintained scalable applications using {', '.join(job_req.technologies[:3])}
- Collaborated with cross-functional teams in Agile/Scrum environment
- Implemented CI/CD pipelines and automated testing procedures
- Optimized application performance and resolved technical challenges
- Participated in code reviews and mentored junior developers
"""
        
        formatted_experience = []
        
        for exp in work_experience:
            title = exp.get('title', 'Software Engineer')
            company = exp.get('company', 'Technology Company')
            period = exp.get('period', '2020 - Present')
            responsibilities = exp.get('responsibilities', [])
            
            # Enhance responsibilities with job keywords
            enhanced_responsibilities = []
            for resp in responsibilities:
                # Add relevant keywords to existing responsibilities
                enhanced_resp = self._enhance_responsibility_with_keywords(resp, job_req)
                enhanced_responsibilities.append(f"• {enhanced_resp}")
            
            if not enhanced_responsibilities:
                # Generate default responsibilities
                enhanced_responsibilities = [
                    f"• Developed and maintained applications using {', '.join(job_req.technologies[:2])}",
                    f"• Implemented {job_req.experience_level.lower()}-level architecture patterns and best practices",
                    "• Collaborated with product managers and stakeholders to deliver business solutions",
                    "• Participated in agile development cycles and code review processes"
                ]
            
            exp_text = f"{title.upper()} | {company} | {period}\n" + "\n".join(enhanced_responsibilities)
            formatted_experience.append(exp_text)
        
        return "\n\n".join(formatted_experience)
    
    def _enhance_responsibility_with_keywords(self, responsibility: str, job_req: JobRequirements) -> str:
        """Enhance responsibility with job-relevant keywords"""
        
        # Simple keyword injection
        tech_keywords = job_req.technologies[:3]
        
        if not any(tech in responsibility.lower() for tech in [t.lower() for t in tech_keywords]):
            if 'develop' in responsibility.lower():
                responsibility += f" using {tech_keywords[0]}"
            elif 'implement' in responsibility.lower():
                responsibility += f" with {', '.join(tech_keywords[:2])}"
        
        return responsibility
    
    def _generate_key_achievements(self, profile: UserProfile, job_req: JobRequirements) -> str:
        """Generate key achievements relevant to the job"""
        
        achievements = [
            f"Successfully delivered {job_req.experience_level.lower()}-level projects using modern development practices",
            f"Expertise in {', '.join(job_req.technologies[:3])} with proven track record of scalable solutions",
            "Strong problem-solving skills with focus on performance optimization and code quality",
            "Experience with full software development lifecycle from requirements to deployment"
        ]
        
        return "\n".join(f"• {achievement}" for achievement in achievements)
    
    def _create_modern_template(self, profile: UserProfile, job_req: JobRequirements, 
                               skill_analysis: Dict[str, Any]) -> str:
        """Create modern-looking CV template"""
        # Implementation for modern template
        return self._create_ats_template(profile, job_req, skill_analysis)
    
    def _create_tech_template(self, profile: UserProfile, job_req: JobRequirements,
                             skill_analysis: Dict[str, Any]) -> str:
        """Create tech-focused CV template"""
        # Implementation for tech template  
        return self._create_ats_template(profile, job_req, skill_analysis)

# Example usage and testing
def test_cv_generator():
    """Test the CV generator with ALGOTEQUE data"""
    
    # User profile example
    user = UserProfile(
        name="Jan Kowalski",
        email="jan.kowalski@email.com",
        phone="+48 123 456 789",
        location="Warszawa, Poland",
        linkedin="linkedin.com/in/jankowalski",
        github="github.com/jankowalski",
        current_position="Python Developer",
        years_experience=4,
        skills=[
            "Python", "Django", "Flask", "FastAPI", "PostgreSQL", "Docker", 
            "AWS", "Git", "REST API", "Jenkins", "Kubernetes", "Agile"
        ],
        education="M.Sc. Computer Science, Warsaw University of Technology",
        work_experience=[
            {
                "title": "Python Developer",
                "company": "Tech Solutions Sp. z o.o.",
                "period": "2022 - Present",
                "responsibilities": [
                    "Developed web applications using Django and PostgreSQL",
                    "Implemented microservices architecture with Docker",
                    "Collaborated with team using Agile methodology"
                ]
            }
        ]
    )
    
    # Job requirements from ALGOTEQUE scraping
    job = JobRequirements(
        title="Senior Solutions Architect",
        company="ALGOTEQUE SERVICES sp. z o.o.",
        required_skills=[
            "Python", "ML", "AI", "scikit-learn", "PyTorch", "TensorFlow",
            "Pandas", "NumPy", "NLP", "Hugging Face", "PySpark", "REST API"
        ],
        nice_to_have=["AWS", "Docker", "Kubernetes", "Jenkins"],
        experience_level="Senior",
        key_requirements=[
            "5+ years Python/ML/AI experience",
            "3+ years ML libraries experience",
            "NLP experience required",
            "Big Data experience with PySpark"
        ],
        technologies=[
            "Python", "scikit-learn", "PyTorch", "TensorFlow", "Pandas", 
            "NumPy", "Hugging Face", "PySpark", "REST API", "Docker"
        ]
    )
    
    # Generate CV
    generator = CVGenerator()
    cv_content = generator.generate_cv(user, job, template_type='ats_friendly')
    
    print("🎯 Generated CV for ALGOTEQUE Senior Solutions Architect:")
    print("=" * 60)
    print(cv_content)
    print("\n" + "=" * 60)
    
    return cv_content

if __name__ == "__main__":
    print("🚀 AI CV Generator - Prototype")
    print("=" * 50)
    
    # Run test
    test_cv = test_cv_generator()
    
    print("\n✅ CV Generator ready!")
    print("📝 Features: ATS-optimized, keyword-matched, tailored content")