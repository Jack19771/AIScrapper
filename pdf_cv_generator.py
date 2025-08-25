#!/usr/bin/env python3
"""
Modern Beautiful CV Generator
Creates stunning, professional CVs like premium design templates
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Frame, PageTemplate
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus.doctemplate import BaseDocTemplate
from io import BytesIO
from typing import Dict, List, Any
from cv_generator import UserProfile, JobRequirements

class ModernCVGenerator:
    def __init__(self):
        # Modern, elegant colors - like your examples
        self.colors = {
            'primary': HexColor('#2c3e50'),        # Dark blue-gray
            'secondary': HexColor('#34495e'),      # Medium gray
            'accent': HexColor('#3498db'),         # Modern blue
            'text_primary': HexColor('#2c3e50'),   # Dark text
            'text_secondary': HexColor('#7f8c8d'), # Light gray text
            'text_light': HexColor('#95a5a6'),     # Very light gray
            'sidebar_bg': HexColor('#2c3e50'),     # Dark sidebar
            'white': HexColor('#ffffff'),
            'light_bg': HexColor('#ecf0f1'),       # Very light background
            'divider': HexColor('#bdc3c7'),        # Light divider
        }
        
        # Professional fonts
        self.fonts = {
            'heading': 'Helvetica-Bold',
            'subheading': 'Helvetica-Bold',
            'body': 'Helvetica',
            'body_bold': 'Helvetica-Bold',
            'light': 'Helvetica',
        }
        
        self.setup_styles()
    
    def setup_styles(self):
        """Setup modern, beautiful styles"""
        self.styles = getSampleStyleSheet()
        
        # Large name header - like Taylor Cook example
        self.styles.add(ParagraphStyle(
            name='LargeName',
            fontSize=32,
            textColor=self.colors['primary'],
            fontName=self.fonts['heading'],
            spaceAfter=4,
            alignment=TA_LEFT,
            leading=36,
        ))
        
        # Professional title under name
        self.styles.add(ParagraphStyle(
            name='ProfTitle',
            fontSize=14,
            textColor=self.colors['text_secondary'],
            fontName=self.fonts['body'],
            spaceAfter=20,
            alignment=TA_LEFT,
        ))
        
        # Contact info - clean and minimal
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            fontSize=10,
            textColor=self.colors['text_secondary'],
            fontName=self.fonts['body'],
            spaceAfter=4,
            alignment=TA_LEFT,
        ))
        
        # Section headers - bold and prominent
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=14,
            textColor=self.colors['primary'],
            fontName=self.fonts['heading'],
            spaceBefore=20,
            spaceAfter=12,
            alignment=TA_LEFT,
        ))
        
        # Subsection headers (like job titles)
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            fontSize=12,
            textColor=self.colors['text_primary'],
            fontName=self.fonts['body_bold'],
            spaceBefore=8,
            spaceAfter=4,
            alignment=TA_LEFT,
        ))
        
        # Company and dates
        self.styles.add(ParagraphStyle(
            name='CompanyDate',
            fontSize=10,
            textColor=self.colors['text_secondary'],
            fontName=self.fonts['body'],
            spaceAfter=8,
            alignment=TA_LEFT,
        ))
        
        # Body text - clean and readable
        self.styles.add(ParagraphStyle(
            name='ModernBody',
            fontSize=10,
            textColor=self.colors['text_primary'],
            fontName=self.fonts['body'],
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14,
        ))
        
        # Bullet points
        self.styles.add(ParagraphStyle(
            name='BulletModern',
            fontSize=10,
            textColor=self.colors['text_primary'],
            fontName=self.fonts['body'],
            spaceAfter=4,
            leftIndent=12,
            bulletIndent=0,
            alignment=TA_LEFT,
            leading=14,
        ))
        
        # Skills section
        self.styles.add(ParagraphStyle(
            name='SkillCategory',
            fontSize=10,
            textColor=self.colors['text_primary'],
            fontName=self.fonts['body_bold'],
            spaceAfter=4,
            alignment=TA_LEFT,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SkillItems',
            fontSize=10,
            textColor=self.colors['text_primary'],
            fontName=self.fonts['body'],
            spaceAfter=8,
            alignment=TA_LEFT,
        ))
    
    def generate_pdf(self, user_profile: UserProfile, job_requirements: JobRequirements, 
                    skill_analysis: Dict[str, Any]) -> BytesIO:
        """Generate modern, beautiful PDF CV"""
        
        buffer = BytesIO()
        
        # Create document with professional margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=25*mm,
            rightMargin=25*mm,
            topMargin=25*mm,
            bottomMargin=25*mm,
        )
        
        # Build content
        story = []
        
        # Header with large name - like your examples
        story.extend(self._build_modern_header(user_profile, job_requirements))
        
        # Professional summary
        story.extend(self._build_profile_section(user_profile, job_requirements, skill_analysis))
        
        # Skills in clean categories
        story.extend(self._build_skills_section(user_profile, skill_analysis))
        
        # Experience section - clean and impactful
        story.extend(self._build_experience_section(user_profile, job_requirements))
        
        # Education
        story.extend(self._build_education_section(user_profile))
        
        # Build the PDF
        doc.build(story, onFirstPage=self._add_modern_styling, onLaterPages=self._add_modern_styling)
        
        buffer.seek(0)
        return buffer
    
    def _add_modern_styling(self, canvas, doc):
        """Add modern styling elements"""
        # Clean line under header
        canvas.setStrokeColor(self.colors['divider'])
        canvas.setLineWidth(0.5)
        canvas.line(25*mm, A4[1] - 80*mm, A4[0] - 25*mm, A4[1] - 80*mm)
    
    def _build_modern_header(self, profile: UserProfile, job_req: JobRequirements) -> List:
        """Build large, impactful header like the examples"""
        story = []
        
        # Large name - like "TAYLOR COOK"
        story.append(Paragraph(profile.name.upper(), self.styles['LargeName']))
        
        # Professional title
        prof_title = profile.current_position or job_req.title or "Software Professional"
        story.append(Paragraph(prof_title, self.styles['ProfTitle']))
        
        # Contact info in clean format
        contact_items = []
        if profile.email:
            contact_items.append(profile.email)
        if profile.phone:
            contact_items.append(profile.phone)
        if profile.location:
            contact_items.append(profile.location)
        
        if contact_items:
            contact_line = " | ".join(contact_items)
            story.append(Paragraph(contact_line, self.styles['ContactInfo']))
        
        # Professional links
        if profile.linkedin:
            linkedin_clean = profile.linkedin.replace('https://', '').replace('http://', '')
            story.append(Paragraph(f"LinkedIn: {linkedin_clean}", self.styles['ContactInfo']))
        
        if profile.github:
            github_clean = profile.github.replace('https://', '').replace('http://', '')
            story.append(Paragraph(f"GitHub: {github_clean}", self.styles['ContactInfo']))
        
        story.append(Spacer(1, 15))
        return story
    
    def _build_profile_section(self, profile: UserProfile, job_req: JobRequirements, 
                             skill_analysis: Dict[str, Any]) -> List:
        """Build profile/summary section"""
        story = []
        
        story.append(Paragraph("PROFILE", self.styles['SectionHeader']))
        
        # Craft compelling summary
        experience_text = f"{profile.years_experience}+ years" if profile.years_experience > 0 else "Experienced"
        position = job_req.title or "Software Professional"
        
        # Get matching skills for keyword optimization
        key_skills = skill_analysis.get('matching_skills', [])[:4]
        if not key_skills:
            key_skills = job_req.technologies[:4] if job_req.technologies else []
        
        skills_text = ", ".join(key_skills) if key_skills else "modern technologies"
        
        # Professional, engaging summary
        summary = f"""{experience_text} {position} with proven expertise in {skills_text}. Demonstrated success in delivering scalable, high-performance solutions in {job_req.experience_level.lower()}-level environments. Strong technical background combined with excellent problem-solving skills and commitment to code quality. Passionate about leveraging innovative technologies to drive business impact and user satisfaction."""
        
        story.append(Paragraph(summary, self.styles['ModernBody']))
        story.append(Spacer(1, 15))
        
        return story
    
    def _build_skills_section(self, profile: UserProfile, skill_analysis: Dict[str, Any]) -> List:
        """Build clean, organized skills section"""
        story = []
        
        story.append(Paragraph("CORE COMPETENCIES", self.styles['SectionHeader']))
        
        # Prioritize matching skills
        all_skills = profile.skills.copy()
        matching_skills = skill_analysis.get('matching_skills', [])
        
        # Reorder: matching skills first
        priority_skills = []
        other_skills = []
        
        for skill in all_skills:
            if any(match.lower() in skill.lower() or skill.lower() in match.lower() 
                   for match in matching_skills):
                priority_skills.append(skill)
            else:
                other_skills.append(skill)
        
        ordered_skills = priority_skills + other_skills
        
        # Group skills professionally
        categories = self._categorize_skills_modern(ordered_skills)
        
        # Create clean skills layout
        for category, skills in categories.items():
            if skills:
                # Category header
                story.append(Paragraph(category, self.styles['SkillCategory']))
                
                # Skills as clean text
                skills_text = " • ".join(skills[:6])  # Max 6 per category for clean look
                story.append(Paragraph(skills_text, self.styles['SkillItems']))
        
        return story
    
    def _categorize_skills_modern(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills for modern presentation"""
        categories = {
            'Programming Languages': [],
            'Frameworks & Libraries': [],
            'Cloud & DevOps': [],
            'Databases': [],
            'Tools & Methodologies': []
        }
        
        # Enhanced categorization
        prog_kw = ['python', 'java', 'javascript', 'typescript', 'c#', 'c++', 'go', 'rust', 'php', 'ruby']
        framework_kw = ['react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express', 'node']
        cloud_kw = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform']
        db_kw = ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'elasticsearch']
        tools_kw = ['git', 'jira', 'agile', 'scrum', 'rest', 'api', 'graphql', 'microservices']
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized = False
            
            if any(kw in skill_lower for kw in prog_kw):
                categories['Programming Languages'].append(skill)
                categorized = True
            elif any(kw in skill_lower for kw in framework_kw):
                categories['Frameworks & Libraries'].append(skill)
                categorized = True
            elif any(kw in skill_lower for kw in cloud_kw):
                categories['Cloud & DevOps'].append(skill)
                categorized = True
            elif any(kw in skill_lower for kw in db_kw):
                categories['Databases'].append(skill)
                categorized = True
            
            if not categorized:
                categories['Tools & Methodologies'].append(skill)
        
        return categories
    
    def _build_experience_section(self, profile: UserProfile, job_req: JobRequirements) -> List:
        """Build clean, impactful experience section"""
        story = []
        
        story.append(Paragraph("EMPLOYMENT HISTORY", self.styles['SectionHeader']))
        
        if profile.work_experience:
            for exp in profile.work_experience:
                story.extend(self._format_job_entry(exp, job_req))
        else:
            # Create professional default experience
            default_job = {
                "title": "Software Engineer",
                "company": "Tech Solutions Inc.",
                "period": "2020 - Present",
                "responsibilities": [
                    f"Developed and maintained scalable applications using {', '.join(job_req.technologies[:3]) if job_req.technologies else 'modern technologies'}",
                    "Collaborated with cross-functional teams to deliver high-quality software solutions",
                    "Implemented best practices for code quality, testing, and deployment processes",
                    "Participated in agile development cycles and technical decision-making processes"
                ]
            }
            story.extend(self._format_job_entry(default_job, job_req))
        
        return story
    
    def _format_job_entry(self, exp: Dict, job_req: JobRequirements) -> List:
        """Format individual job entry beautifully"""
        entry = []
        
        # Job title - prominent
        title = exp.get('title', 'Software Engineer')
        company = exp.get('company', 'Technology Company')
        period = exp.get('period', '2020 - Present')
        
        # Job header - like the examples
        job_line = f"{title}, {company}"
        entry.append(Paragraph(job_line, self.styles['JobTitle']))
        entry.append(Paragraph(period, self.styles['CompanyDate']))
        
        # Responsibilities as clean bullets
        responsibilities = exp.get('responsibilities', [])
        for resp in responsibilities:
            enhanced_resp = self._enhance_responsibility(resp, job_req)
            entry.append(Paragraph(f"• {enhanced_resp}", self.styles['BulletModern']))
        
        entry.append(Spacer(1, 12))
        return entry
    
    def _enhance_responsibility(self, responsibility: str, job_req: JobRequirements) -> str:
        """Enhance responsibility with job keywords"""
        enhanced = responsibility
        
        # Add relevant technologies if missing
        if job_req.technologies:
            relevant_tech = job_req.technologies[0]
            if relevant_tech.lower() not in enhanced.lower() and 'develop' in enhanced.lower():
                enhanced = enhanced.replace('applications', f'applications using {relevant_tech}')
        
        return enhanced
    
    def _build_education_section(self, profile: UserProfile) -> List:
        """Build clean education section"""
        story = []
        
        if profile.education:
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            story.append(Paragraph(profile.education, self.styles['ModernBody']))
            story.append(Spacer(1, 12))
        
        return story

def generate_beautiful_cv_pdf(user_profile: UserProfile, job_requirements: JobRequirements, 
                             skill_analysis: Dict[str, Any]) -> BytesIO:
    """Generate beautiful, modern CV PDF"""
    generator = ModernCVGenerator()
    return generator.generate_pdf(user_profile, job_requirements, skill_analysis)

def test_modern_cv():
    """Test modern CV generation"""
    from cv_generator import UserProfile, JobRequirements
    
    # Test user
    user = UserProfile(
        name="Taylor Cook",
        email="taylor.cook@gmail.com",
        phone="(555) 123-4567",
        location="San Francisco, CA",
        linkedin="linkedin.com/in/taylorcook",
        github="github.com/taylorcook",
        current_position="Senior Software Engineer",
        years_experience=5,
        skills=[
            "Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker", 
            "AWS", "Git", "REST API", "Agile", "Scrum", "TypeScript"
        ],
        education="Master of Computer Science, Stanford University",
        work_experience=[
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp",
                "period": "2021 - Present",
                "responsibilities": [
                    "Developed scalable web applications serving 50K+ users using React and Python",
                    "Led team of 3 developers implementing microservices architecture",
                    "Optimized application performance reducing load times by 40%",
                    "Collaborated with product team to deliver 10+ features quarterly"
                ]
            }
        ]
    )
    
    # Job requirements
    job = JobRequirements(
        title="Senior Full Stack Developer",
        company="Google",
        required_skills=["Python", "JavaScript", "React", "AWS"],
        nice_to_have=["Docker", "TypeScript"],
        experience_level="Senior",
        key_requirements=["5+ years experience"],
        technologies=["Python", "JavaScript", "React", "AWS", "Docker"]
    )
    
    # Skill analysis
    skill_analysis = {
        'matching_skills': ["Python", "JavaScript", "React", "AWS", "Docker"],
        'missing_skills': ["Kubernetes"],
        'match_score': 0.9
    }
    
    # Generate PDF
    pdf_buffer = generate_beautiful_cv_pdf(user, job, skill_analysis)
    
    # Save test file
    with open('modern_beautiful_cv.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("✅ Modern beautiful CV generated: modern_beautiful_cv.pdf")

if __name__ == "__main__":
    print("🎨 Modern Beautiful CV Generator")
    print("=" * 40)
    
    try:
        test_modern_cv()
        print("🎉 Success! Check modern_beautiful_cv.pdf")
    except Exception as e:
        print(f"❌ Error: {e}")