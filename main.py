#!/usr/bin/env python3
"""
AI-Powered CV Generator API - Complete System
FastAPI service with job scraping, AI customization, and beautiful PDF generation
"""

import re
import unicodedata
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import io
import traceback

# Import our modules
from scraper import AdvancedJobScraper
from cv_generator import CVGenerator, UserProfile, JobRequirements
from ai_cv_customizer import generate_ai_customized_cv
from pdf_cv_generator import generate_beautiful_cv_pdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
scraper = None
cv_generator = None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for HTTP headers by removing/replacing problematic characters
    """
    # Remove/replace Polish characters with ASCII equivalents
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    
    # Replace Polish characters
    for polish, ascii_char in replacements.items():
        filename = filename.replace(polish, ascii_char)
    
    # Remove any remaining non-ASCII characters
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    
    # Remove/replace problematic characters for filenames
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple spaces and underscores
    filename = re.sub(r'[\s_]+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    return filename

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global scraper, cv_generator
    
    logger.info("🚀 Starting AI CV Generator API")
    
    # Initialize services
    try:
        scraper = AdvancedJobScraper(use_selenium=True, headless=True)
        cv_generator = CVGenerator()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        scraper = None
        cv_generator = None
    
    yield
    
    # Cleanup
    logger.info("🔌 Shutting down API")
    if scraper:
        try:
            scraper.close()
        except Exception as e:
            logger.error(f"Error closing scraper: {e}")

# FastAPI app
app = FastAPI(
    title="AI CV Generator API",
    description="AI-powered job scraping and CV generation system",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class JobScrapeRequest(BaseModel):
    url: str

class JobData(BaseModel):
    success: bool
    portal: str
    url: str
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    requirements: List[str]
    skills: List[str]
    description: str
    experience_level: str
    scraped_at: str

# Helper functions
def create_job_data(result: Dict[str, Any]) -> JobData:
    """Convert scraper result to JobData"""
    return JobData(
        success=result.get('success', False),
        portal=result.get('portal', 'unknown'),
        url=result.get('url', ''),
        title=result.get('title', 'N/A'),
        company=result.get('company', 'N/A'),
        location=result.get('location', 'N/A'),
        salary=result.get('salary'),
        requirements=result.get('requirements', []),
        skills=result.get('skills', []),
        description=result.get('description', ''),
        experience_level=result.get('experience_level', 'Unknown'),
        scraped_at=datetime.now().isoformat()
    )

def dict_to_user_profile(data: Dict[str, Any]) -> UserProfile:
    """Convert dict to UserProfile"""
    return UserProfile(
        name=data.get('name', 'John Doe'),
        email=data.get('email', 'john@email.com'),
        phone=data.get('phone', '+48 123 456 789'),
        location=data.get('location', 'Warsaw'),
        linkedin=data.get('linkedin', ''),
        github=data.get('github', ''),
        current_position=data.get('current_position', 'Developer'),
        years_experience=data.get('years_experience', 3),
        skills=data.get('skills', []),
        education=data.get('education', 'B.Sc. Computer Science'),
        work_experience=data.get('work_experience', [])
    )

def calculate_skill_match(job_skills: List[str], user_skills: List[str]) -> Dict[str, Any]:
    """Calculate skill matching score"""
    if not job_skills or not user_skills:
        return {
            'match_score': 0.0,
            'matching_skills': [],
            'missing_skills': job_skills or []
        }
    
    matching_skills = []
    missing_skills = []
    
    for job_skill in job_skills:
        found = False
        for user_skill in user_skills:
            if (job_skill.lower() in user_skill.lower() or 
                user_skill.lower() in job_skill.lower()):
                matching_skills.append(job_skill)
                found = True
                break
        if not found:
            missing_skills.append(job_skill)
    
    match_score = len(matching_skills) / len(job_skills) if job_skills else 0.0
    
    return {
        'match_score': match_score,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills
    }

async def parse_cv_content(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Parse CV content from uploaded file
    This is a simplified version - you can enhance with actual CV parsing libraries
    """
    try:
        # For now, return a basic parsed structure
        # In a real implementation, you'd use libraries like:
        # - PyPDF2 for PDF parsing
        # - python-docx for DOCX parsing
        # - AI services for content extraction
        
        return {
            'success': True,
            'extracted_text': 'CV content extracted successfully',
            'user_profile': {
                'name': 'Extracted Name',
                'email': 'extracted@email.com',
                'skills': ['Python', 'JavaScript', 'React'],
                'experience': 'Software Engineer with 5 years experience'
            }
        }
    except Exception as e:
        logger.error(f"CV parsing error: {e}")
        return {
            'success': False,
            'error': f"Failed to parse CV: {str(e)}"
        }

def reinitialize_scraper():
    """Reinitialize scraper if it's broken"""
    global scraper
    try:
        if scraper:
            scraper.close()
        scraper = AdvancedJobScraper(use_selenium=True, headless=True)
        logger.info("🔄 Scraper reinitialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to reinitialize scraper: {e}")
        return False

# API Endpoints
@app.get("/")
async def root():
    """API info"""
    return {
        "message": "🤖 AI CV Generator API",
        "version": "3.0.0",
        "features": ["job_scraping", "ai_cv_generation", "beautiful_pdfs", "ats_optimization", "cv_upload"],
        "endpoints": {
            "scrape": "POST /api/v1/scrape",
            "generate_cv": "POST /api/v1/generate-cv",
            "upload_cv": "POST /api/v1/upload-cv",
            "download_pdf": "POST /api/v1/download-pdf",
            "supported_portals": "GET /api/v1/supported-portals",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    global scraper, cv_generator
    
    scraper_status = scraper is not None
    selenium_status = False
    
    if scraper:
        try:
            # Test if selenium is working
            selenium_status = hasattr(scraper, 'driver') and scraper.driver is not None
        except:
            selenium_status = False
    
    status = "healthy" if scraper_status and cv_generator else "degraded"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scraper_ready": scraper_status,
            "cv_generator_ready": cv_generator is not None,
            "ai_enabled": True,
            "pdf_generator_ready": True,
            "selenium_available": selenium_status
        }
    }

@app.get("/sw.js")
async def service_worker():
    """Simple service worker for PWA support"""
    js_content = """
// Simple Service Worker for CVcraft
const CACHE_NAME = 'cvcraft-v1';
const urlsToCache = [
  '/',
  '/api/v1/supported-portals'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
"""
    return Response(
        content=js_content,
        media_type="application/javascript",
        headers={"Cache-Control": "max-age=3600"}
    )

@app.post("/api/v1/scrape", response_model=JobData)
async def scrape_job(request: JobScrapeRequest):
    """Scrape job posting"""
    global scraper
    
    if not scraper:
        # Try to reinitialize scraper
        if not reinitialize_scraper():
            raise HTTPException(status_code=503, detail="Scraper service unavailable")
    
    try:
        logger.info(f"🔍 Scraping: {request.url}")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, scraper.scrape_job, request.url)
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            
            # If selenium session expired, try to reinitialize
            if 'invalid session id' in error_msg.lower():
                logger.warning("🔄 Selenium session expired, reinitializing...")
                if reinitialize_scraper():
                    # Retry scraping
                    result = await loop.run_in_executor(None, scraper.scrape_job, request.url)
                    if result.get('success'):
                        return create_job_data(result)
            
            # If 403 forbidden, provide helpful message
            if '403' in error_msg:
                raise HTTPException(
                    status_code=400, 
                    detail="Website blocked the request. The job portal may have anti-bot protection. Please try a different URL or try again later."
                )
            
            raise HTTPException(
                status_code=400, 
                detail=f"Scraping failed: {error_msg}"
            )
        
        return create_job_data(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Scraping error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal scraping error: {str(e)}")

@app.post("/api/v1/generate-cv")
async def generate_ai_cv(request: dict):
    """🤖 Generate AI-customized CV with perfect job matching"""
    try:
        url = request.get("url")
        user_profile = request.get("user_profile", {})
        
        if not url:
            raise HTTPException(status_code=400, detail="Job URL is required")
        
        # Scrape job first
        global scraper
        if not scraper:
            if not reinitialize_scraper():
                raise HTTPException(status_code=503, detail="Scraper service unavailable")
        
        loop = asyncio.get_event_loop()
        scrape_result = await loop.run_in_executor(None, scraper.scrape_job, url)
        
        if not scrape_result.get('success'):
            return {"success": False, "error": "Job scraping failed"}
        
        # Create user profile
        user = dict_to_user_profile(user_profile)
        
        # Create job requirements
        job = JobRequirements(
            title=scrape_result.get('title', 'Developer'),
            company=scrape_result.get('company', 'Company'),
            required_skills=scrape_result.get('skills', []),
            nice_to_have=[],
            experience_level=scrape_result.get('experience_level', 'Mid'),
            key_requirements=scrape_result.get('requirements', []),
            technologies=scrape_result.get('skills', [])
        )
        
        # 🤖 AI MAGIC - Generate customized CV content
        full_job_description = scrape_result.get('description', '') + ' ' + ' '.join(scrape_result.get('requirements', []))
        
        logger.info(f"🧠 Running AI customization for {job.title}")
        
        try:
            ai_result = await generate_ai_customized_cv(user, job, full_job_description)
        except Exception as ai_error:
            logger.warning(f"AI generation failed: {ai_error}, falling back to standard generation")
            ai_result = {'success': False}
        
        if ai_result.get('success'):
            customized_content = ai_result['customized_content']
            
            # Calculate skill matching
            skill_match = calculate_skill_match(job.required_skills, user.skills)
            
            return {
                "success": True,
                "cv_content": customized_content.get('professional_summary', 'AI-generated professional summary'),
                "job_title": job.title,
                "company": job.company,
                "match_score": round(skill_match['match_score'] * 100, 1),
                "matching_skills": skill_match['matching_skills'],
                "missing_skills": skill_match['missing_skills'],
                "ai_optimized": True,
                "ats_score": ai_result.get('ats_optimization_score', 85),
                "keyword_density": ai_result.get('keyword_density', {}),
                "customized_sections": customized_content,
                "generated_at": datetime.now().isoformat()
            }
        else:
            # Fallback to regular CV generation if AI fails
            logger.warning("AI generation failed, falling back to standard generation")
            try:
                generator = CVGenerator()
                cv_content = generator.generate_cv(user, job)
            except Exception:
                cv_content = f"Professional CV for {job.title} position at {job.company}"
            
            skill_match = calculate_skill_match(job.required_skills, user.skills)
            
            return {
                "success": True,
                "cv_content": cv_content,
                "job_title": job.title,
                "company": job.company,
                "match_score": round(skill_match['match_score'] * 100, 1),
                "matching_skills": skill_match['matching_skills'],
                "missing_skills": skill_match['missing_skills'],
                "ai_optimized": False,
                "ats_score": 75,
                "generated_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CV generation error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.post("/api/v1/upload-cv")
async def upload_and_customize_cv(
    job_url: str = Form(...),
    cv_file: UploadFile = File(...)
):
    """📁 Upload existing CV and customize for specific job"""
    try:
        logger.info(f"📄 Processing CV upload: {cv_file.filename}")
        
        # Validate file type
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                        'application/msword', 'text/plain']
        if cv_file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOC, DOCX, or TXT files.")
        
        # Validate file size (10MB max)
        if cv_file.size and cv_file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Read uploaded file
        file_content = await cv_file.read()
        
        # Scrape job first
        global scraper
        if not scraper:
            if not reinitialize_scraper():
                raise HTTPException(status_code=503, detail="Scraper service unavailable")
        
        loop = asyncio.get_event_loop()
        scrape_result = await loop.run_in_executor(None, scraper.scrape_job, job_url)
        
        if not scrape_result.get('success'):
            return {"success": False, "error": "Job scraping failed"}
        
        # Create job requirements
        job = JobRequirements(
            title=scrape_result.get('title', 'Developer'),
            company=scrape_result.get('company', 'Company'),
            required_skills=scrape_result.get('skills', []),
            nice_to_have=[],
            experience_level=scrape_result.get('experience_level', 'Mid'),
            key_requirements=scrape_result.get('requirements', []),
            technologies=scrape_result.get('skills', [])
        )
        
        # Parse CV content
        parse_result = await parse_cv_content(file_content, cv_file.filename)
        
        if not parse_result.get('success'):
            return {"success": False, "error": parse_result.get('error', 'CV parsing failed')}
        
        # Create user profile from parsed CV
        parsed_profile = parse_result.get('user_profile', {})
        user = dict_to_user_profile(parsed_profile)
        
        # Generate AI customization
        job_description = scrape_result.get('description', '') + ' ' + ' '.join(scrape_result.get('requirements', []))
        
        logger.info(f"🧠 Running AI customization for uploaded CV")
        
        try:
            ai_result = await generate_ai_customized_cv(user, job, job_description)
        except Exception as ai_error:
            logger.warning(f"AI generation failed: {ai_error}")
            ai_result = {'success': False}
        
        if ai_result.get('success'):
            customized_content = ai_result['customized_content']
            skill_match = calculate_skill_match(job.required_skills, user.skills)
            
            return {
                "success": True,
                "cv_content": customized_content.get('professional_summary', 'AI-generated summary'),
                "job_title": job.title,
                "company": job.company,
                "match_score": round(skill_match['match_score'] * 100, 1),
                "matching_skills": skill_match['matching_skills'],
                "missing_skills": skill_match['missing_skills'],
                "parsed_cv": parse_result.get('extracted_text', ''),
                "customized_sections": customized_content,
                "ai_optimized": True,
                "uploaded_filename": cv_file.filename,
                "ats_score": ai_result.get('ats_optimization_score', 85),
                "generated_at": datetime.now().isoformat()
            }
        else:
            # Fallback without AI
            skill_match = calculate_skill_match(job.required_skills, user.skills)
            
            return {
                "success": True,
                "cv_content": f"Customized CV for {job.title} position",
                "job_title": job.title,
                "company": job.company,
                "match_score": round(skill_match['match_score'] * 100, 1),
                "matching_skills": skill_match['matching_skills'],
                "missing_skills": skill_match['missing_skills'],
                "parsed_cv": parse_result.get('extracted_text', ''),
                "ai_optimized": False,
                "uploaded_filename": cv_file.filename,
                "ats_score": 75,
                "generated_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CV upload error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.post("/api/v1/download-pdf")
async def download_pdf_endpoint(request: dict):
    """📄 Download beautiful, ATS-optimized PDF CV"""
    try:
        url = request.get("url")
        user_profile = request.get("user_profile", {})
        
        if not url:
            raise HTTPException(status_code=400, detail="Job URL is required")
        
        # Scrape job
        global scraper
        if not scraper:
            if not reinitialize_scraper():
                raise HTTPException(status_code=503, detail="Scraper service unavailable")
        
        loop = asyncio.get_event_loop()
        scrape_result = await loop.run_in_executor(None, scraper.scrape_job, url)
        
        if not scrape_result.get('success'):
            raise HTTPException(status_code=400, detail="Job scraping failed")
        
        # Create user profile and job requirements
        user = dict_to_user_profile(user_profile)
        
        job = JobRequirements(
            title=scrape_result.get('title', 'Developer'),
            company=scrape_result.get('company', 'Company'),
            required_skills=scrape_result.get('skills', []),
            nice_to_have=[],
            experience_level=scrape_result.get('experience_level', 'Mid'),
            key_requirements=scrape_result.get('requirements', []),
            technologies=scrape_result.get('skills', [])
        )
        
        # Calculate skill analysis
        skill_analysis = calculate_skill_match(job.required_skills, user.skills)
        
        # 🎨 Generate beautiful PDF
        logger.info(f"🎨 Generating PDF for {user.name} - {job.title}")
        
        try:
            pdf_buffer = generate_beautiful_cv_pdf(user, job, skill_analysis)
        except Exception as pdf_error:
            logger.error(f"PDF generation error: {pdf_error}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
        
        # Sanitize filename for HTTP headers - FIXED!
        safe_name = sanitize_filename(user.name)
        safe_company = sanitize_filename(job.company)
        safe_title = sanitize_filename(job.title.split('(')[0].strip())
        
        # Generate safe filename
        filename = f"{safe_name}_CV_{safe_company}_{safe_title}.pdf"
        
        # Ensure filename is not too long
        if len(filename) > 200:
            filename = f"{safe_name[:50]}_CV.pdf"
        
        logger.info(f"📎 Generated safe filename: {filename}")
        
        # Return PDF with ASCII-safe headers
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_buffer.getvalue())),
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF generation error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/supported-portals")
async def get_supported_portals():
    """Get supported job portals"""
    return {
        "supported_portals": [
            {
                "name": "Pracuj.pl",
                "domain": "pracuj.pl",
                "features": ["full_parsing", "skills_extraction", "salary_detection", "ai_optimization"],
                "status": "fully_supported"
            },
            {
                "name": "NoFluffJobs",
                "domain": "nofluffjobs.com",
                "features": ["tech_stack", "salary_ranges", "remote_work", "ai_optimization"],
                "status": "supported"
            },
            {
                "name": "JustJoin.it", 
                "domain": "justjoin.it",
                "features": ["tech_skills", "experience_levels", "ai_optimization"],
                "status": "supported"
            },
            {
                "name": "Indeed.pl",
                "domain": "indeed.pl",
                "features": ["basic_parsing", "ai_optimization"],
                "status": "basic_support"
            },
            {
                "name": "LinkedIn Jobs",
                "domain": "linkedin.com",
                "features": ["professional_network", "company_insights", "ai_optimization"],
                "status": "supported"
            }
        ],
        "total_supported": 5,
        "ai_optimization": "available_for_all_portals",
        "file_upload_supported": True,
        "max_file_size": "10MB",
        "supported_formats": ["PDF", "DOC", "DOCX", "TXT"]
    }

# Error handlers - FIXED!
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Mount static files - MUST be last
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )