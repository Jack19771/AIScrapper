#!/usr/bin/env python3
"""
AI CV Customization Engine
Uses LLM to create perfectly tailored CVs that match job requirements
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from cv_generator import UserProfile, JobRequirements

logger = logging.getLogger(__name__)

class AICVCustomizer:
    def __init__(self):
        """Initialize AI CV Customizer"""
        # We'll use the Claude API that's available in artifacts
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 2000
    
    async def customize_cv_content(self, user_profile: UserProfile, job_requirements: JobRequirements, 
                                 job_description: str) -> Dict[str, Any]:
        """
        Use AI to create customized CV content that perfectly matches the job
        """
        try:
            # Prepare comprehensive context for AI
            context = self._prepare_ai_context(user_profile, job_requirements, job_description)
            
            # Generate AI-customized sections
            customized_sections = {}
            
            # 1. Professional Summary
            customized_sections['professional_summary'] = await self._generate_professional_summary(context)
            
            # 2. Customized Experience
            customized_sections['experience'] = await self._customize_experience(context)
            
            # 3. Optimized Skills
            customized_sections['skills'] = await self._optimize_skills(context)
            
            # 4. Key Achievements
            customized_sections['achievements'] = await self._generate_achievements(context)
            
            return {
                'success': True,
                'customized_content': customized_sections,
                'ats_optimization_score': await self._calculate_ats_score(customized_sections, job_requirements),
                'keyword_density': self._analyze_keyword_density(customized_sections, job_requirements)
            }
            
        except Exception as e:
            logger.error(f"AI customization error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_ai_context(self, user_profile: UserProfile, job_requirements: JobRequirements, 
                          job_description: str) -> Dict[str, Any]:
        """Prepare comprehensive context for AI processing"""
        
        return {
            'job_info': {
                'title': job_requirements.title,
                'company': job_requirements.company,
                'description': job_description,
                'required_skills': job_requirements.required_skills,
                'key_requirements': job_requirements.key_requirements,
                'experience_level': job_requirements.experience_level,
                'technologies': job_requirements.technologies
            },
            'user_info': {
                'name': user_profile.name,
                'current_position': user_profile.current_position,
                'years_experience': user_profile.years_experience,
                'skills': user_profile.skills,
                'education': user_profile.education,
                'work_experience': user_profile.work_experience
            },
            'customization_goals': [
                'Maximize ATS keyword matching',
                'Create compelling narrative that shows perfect fit',
                'Use specific metrics and quantifiable achievements',
                'Incorporate exact terminology from job posting',
                'Maintain authenticity while optimizing for role'
            ]
        }
    
    async def _generate_professional_summary(self, context: Dict[str, Any]) -> str:
        """Generate AI-powered professional summary tailored to the job"""
        
        prompt = f"""
        You are an expert CV writer who creates compelling professional summaries that get candidates hired.
        
        JOB POSTING ANALYSIS:
        - Company: {context['job_info']['company']}
        - Position: {context['job_info']['title']}
        - Experience Level: {context['job_info']['experience_level']}
        - Key Requirements: {', '.join(context['job_info']['key_requirements'][:5])}
        - Required Skills: {', '.join(context['job_info']['required_skills'][:8])}
        
        CANDIDATE PROFILE:
        - Current Role: {context['user_info']['current_position']}
        - Experience: {context['user_info']['years_experience']} years
        - Skills: {', '.join(context['user_info']['skills'][:10])}
        - Education: {context['user_info']['education']}
        
        TASK: Write a 3-4 sentence professional summary that:
        1. Uses EXACT keywords from the job posting naturally
        2. Positions the candidate as the perfect fit
        3. Includes quantifiable achievements (use realistic metrics)
        4. Shows progression and expertise alignment
        5. Is ATS-optimized but reads naturally
        
        Write ONLY the professional summary text. Make it compelling and specific.
        """
        
        return await self._call_ai_api(prompt)
    
    async def _customize_experience(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AI-customize work experience to match job requirements"""
        
        user_experience = context['user_info']['work_experience']
        job_skills = context['job_info']['required_skills']
        job_title = context['job_info']['title']
        
        if not user_experience:
            # Generate professional experience if none provided
            prompt = f"""
            Create a realistic work experience entry for someone applying to: {job_title}
            
            Required skills to incorporate: {', '.join(job_skills[:6])}
            Experience level: {context['job_info']['experience_level']}
            
            Generate a JSON object with:
            {{
                "title": "appropriate job title",
                "company": "realistic company name",
                "period": "realistic time period",
                "responsibilities": [
                    "3-4 bullet points with specific achievements",
                    "Include metrics and quantifiable results",
                    "Use keywords from required skills naturally",
                    "Show progression and impact"
                ]
            }}
            
            Make it realistic and impressive. Use EXACT keywords from required skills.
            Return ONLY valid JSON.
            """
            
            experience_json = await self._call_ai_api(prompt)
            try:
                generated_exp = json.loads(experience_json)
                return [generated_exp]
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._create_fallback_experience(context)
        
        # Customize existing experience
        customized_exp = []
        for exp in user_experience:
            
            prompt = f"""
            Rewrite this work experience to perfectly match the job requirements:
            
            ORIGINAL EXPERIENCE:
            - Title: {exp.get('title', 'Software Engineer')}
            - Company: {exp.get('company', 'Tech Company')}
            - Period: {exp.get('period', '2020-Present')}
            - Original responsibilities: {exp.get('responsibilities', [])}
            
            TARGET JOB:
            - Position: {job_title}
            - Required skills: {', '.join(job_skills[:8])}
            - Key requirements: {', '.join(context['job_info']['key_requirements'][:5])}
            
            TASK: Rewrite the responsibilities to:
            1. Include EXACT keywords from required skills
            2. Add quantifiable metrics (realistic numbers)
            3. Show direct relevance to target role  
            4. Maintain truthfulness but optimize presentation
            5. Use action verbs and show impact
            
            Return JSON format:
            {{
                "title": "optimized title",
                "company": "keep original company",
                "period": "keep original period", 
                "responsibilities": [
                    "4-5 optimized bullet points with metrics",
                    "Each incorporating job keywords naturally"
                ]
            }}
            
            Return ONLY valid JSON.
            """
            
            exp_json = await self._call_ai_api(prompt)
            try:
                customized_exp.append(json.loads(exp_json))
            except json.JSONDecodeError:
                # Keep original if AI fails
                customized_exp.append(exp)
        
        return customized_exp
    
    async def _optimize_skills(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """AI-optimize skills section for maximum ATS impact"""
        
        user_skills = context['user_info']['skills']
        required_skills = context['job_info']['required_skills']
        job_description = context['job_info']['description']
        
        prompt = f"""
        You are an ATS optimization expert. Analyze and optimize this skills section:
        
        USER'S CURRENT SKILLS: {', '.join(user_skills)}
        
        JOB REQUIREMENTS: {', '.join(required_skills)}
        
        TASK: Create optimized skill categories that:
        1. Prioritize skills that match job requirements EXACTLY
        2. Group related skills professionally  
        3. Use EXACT terminology from job posting
        4. Add relevant skills the user likely has based on their background
        5. Optimize for ATS keyword matching
        
        Return JSON format:
        {{
            "Programming Languages": ["exact matches first", "then related"],
            "Frameworks & Libraries": ["prioritize job matches"],
            "Cloud & DevOps": ["include if relevant"],
            "Databases": ["matching database technologies"],
            "Tools & Methodologies": ["agile, scrum, etc if mentioned"]
        }}
        
        Only include categories with skills. Prioritize job-matching skills first in each category.
        Return ONLY valid JSON.
        """
        
        skills_json = await self._call_ai_api(prompt)
        try:
            return json.loads(skills_json)
        except json.JSONDecodeError:
            # Fallback to basic categorization
            return self._create_fallback_skills(user_skills, required_skills)
    
    async def _generate_achievements(self, context: Dict[str, Any]) -> List[str]:
        """Generate compelling, quantified achievements"""
        
        prompt = f"""
        Create 4-5 impressive key achievements for someone applying to: {context['job_info']['title']}
        
        Context:
        - Experience level: {context['job_info']['experience_level']}
        - Required skills: {', '.join(context['job_info']['required_skills'][:6])}
        - User background: {context['user_info']['current_position']}, {context['user_info']['years_experience']} years experience
        
        Each achievement should:
        1. Include specific, realistic metrics (percentages, numbers, timelines)
        2. Use keywords from job requirements
        3. Show business impact and technical expertise
        4. Be impressive but believable
        5. Demonstrate skills relevant to target role
        
        Return as JSON array of strings:
        ["Achievement with 40% improvement metric", "Led team of X delivering Y results", ...]
        
        Return ONLY valid JSON array.
        """
        
        achievements_json = await self._call_ai_api(prompt)
        try:
            return json.loads(achievements_json)
        except json.JSONDecodeError:
            # Fallback achievements
            return [
                f"Successfully delivered {context['job_info']['experience_level'].lower()}-level projects using industry best practices",
                f"Demonstrated expertise in {', '.join(context['job_info']['required_skills'][:3])} with measurable business impact",
                "Proven track record of optimizing performance and delivering high-quality solutions",
                "Strong collaboration skills with cross-functional teams and stakeholders"
            ]
    
    async def _call_ai_api(self, prompt: str) -> str:
        """Make API call to Claude for content generation"""
        try:
            import aiohttp
            
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Note: In real implementation, you'd need proper API key handling
            # For now, we'll use a fallback approach
            
            # Simulate AI response for development
            return await self._simulate_ai_response(prompt)
            
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return await self._simulate_ai_response(prompt)
    
    async def _simulate_ai_response(self, prompt: str) -> str:
        """Simulate AI response for development/testing"""
        
        if "professional summary" in prompt.lower():
            return f"Experienced software professional with proven expertise in modern technologies and delivering scalable solutions. Strong background in full-stack development with focus on performance optimization and code quality. Passionate about leveraging innovative technologies to drive business impact and user satisfaction."
        
        elif "experience" in prompt.lower() and "{" in prompt:
            return json.dumps({
                "title": "Senior Software Engineer",
                "company": "TechCorp Solutions",
                "period": "2020 - Present",
                "responsibilities": [
                    "Developed and maintained scalable applications using Python and React, serving 50K+ users",
                    "Implemented CI/CD pipelines reducing deployment time by 60% and improving code quality",
                    "Led cross-functional team of 4 developers delivering 12+ features quarterly",
                    "Optimized database performance and caching strategies, improving response times by 40%"
                ]
            })
        
        elif "skills" in prompt.lower() and "{" in prompt:
            return json.dumps({
                "Programming Languages": ["Python", "JavaScript", "TypeScript"],
                "Frameworks & Libraries": ["React", "Django", "FastAPI"],
                "Cloud & DevOps": ["AWS", "Docker", "CI/CD"],
                "Databases": ["PostgreSQL", "Redis"],
                "Tools & Methodologies": ["Git", "Agile", "REST API"]
            })
        
        elif "achievements" in prompt.lower() and "[" in prompt:
            return json.dumps([
                "Successfully delivered 15+ enterprise-level projects using modern development practices",
                "Improved system performance by 45% through optimization and architectural improvements",
                "Led technical initiatives resulting in 30% reduction in bug reports and improved user satisfaction",
                "Mentored 6+ junior developers while maintaining 98% on-time project delivery rate"
            ])
        
        return "AI-generated content placeholder"
    
    def _create_fallback_experience(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fallback experience if AI fails"""
        return [{
            "title": "Software Engineer",
            "company": "Technology Solutions",
            "period": "2020 - Present",
            "responsibilities": [
                f"Developed applications using {', '.join(context['job_info']['required_skills'][:3])}",
                "Collaborated with cross-functional teams in agile environment",
                "Implemented best practices for code quality and testing",
                "Participated in technical decision-making processes"
            ]
        }]
    
    def _create_fallback_skills(self, user_skills: List[str], required_skills: List[str]) -> Dict[str, List[str]]:
        """Create fallback skills categorization"""
        
        # Prioritize matching skills
        matching = [skill for skill in user_skills if skill in required_skills]
        others = [skill for skill in user_skills if skill not in required_skills]
        
        return {
            "Programming Languages": matching[:4] + others[:2],
            "Tools & Technologies": others[2:6] if len(others) > 2 else others
        }
    
    async def _calculate_ats_score(self, customized_content: Dict[str, Any], 
                                 job_requirements: JobRequirements) -> int:
        """Calculate ATS optimization score"""
        
        # Simple scoring based on keyword matches
        score = 0
        total_possible = 100
        
        # Check keyword presence in different sections
        all_content = str(customized_content).lower()
        
        for skill in job_requirements.required_skills:
            if skill.lower() in all_content:
                score += 8  # Each matching skill worth 8 points
        
        return min(score, total_possible)
    
    def _analyze_keyword_density(self, customized_content: Dict[str, Any], 
                               job_requirements: JobRequirements) -> Dict[str, int]:
        """Analyze keyword density for ATS optimization"""
        
        all_content = str(customized_content).lower()
        keyword_counts = {}
        
        for skill in job_requirements.required_skills:
            keyword_counts[skill] = all_content.count(skill.lower())
        
        return keyword_counts

# Integration function for the main API
async def generate_ai_customized_cv(user_profile: UserProfile, job_requirements: JobRequirements, 
                                  job_description: str) -> Dict[str, Any]:
    """
    Main function to generate AI-customized CV content
    """
    customizer = AICVCustomizer()
    return await customizer.customize_cv_content(user_profile, job_requirements, job_description)

# Test function
async def test_ai_customization():
    """Test AI CV customization"""
    from cv_generator import UserProfile, JobRequirements
    
    # Sample user profile
    user = UserProfile(
        name="Sarah Johnson",
        email="sarah.johnson@email.com",
        phone="+1 555-123-4567",
        location="San Francisco, CA",
        current_position="Software Developer",
        years_experience=4,
        skills=["Python", "JavaScript", "React", "PostgreSQL", "Git"],
        education="B.S. Computer Science, UC Berkeley"
    )
    
    # Sample job requirements
    job = JobRequirements(
        title="Senior Full Stack Developer",
        company="TechCorp",
        required_skills=["Python", "React", "AWS", "Docker", "PostgreSQL", "REST API"],
        nice_to_have=["Kubernetes", "TypeScript", "GraphQL"],
        experience_level="Senior",
        key_requirements=["5+ years experience", "Full stack development", "Cloud platforms"],
        technologies=["Python", "React", "AWS", "Docker"]
    )
    
    job_description = """
    We are looking for a Senior Full Stack Developer with expertise in Python and React.
    The ideal candidate will have experience with AWS cloud services, Docker containerization,
    and building scalable REST APIs. Must have 5+ years of software development experience.
    """
    
    # Test AI customization
    result = await generate_ai_customized_cv(user, job, job_description)
    
    print("🤖 AI CV Customization Result:")
    print("=" * 50)
    print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    print("🧠 AI CV Customization Engine")
    print("=" * 40)
    
    # Run test
    asyncio.run(test_ai_customization())