#!/usr/bin/env python3
"""
FastAPI Job Scraper Service
RESTful API for job scraping with async support
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
import logging
from datetime import datetime
import json
import os
from contextlib import asynccontextmanager

# Import our scraper
from scraper import AdvancedJobScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scraper instance
scraper_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage scraper lifecycle"""
    global scraper_instance
    logger.info("🚀 Starting Job Scraper API")
    scraper_instance = AdvancedJobScraper(use_selenium=True, headless=True)
    yield
    logger.info("🔌 Shutting down Job Scraper API")
    if scraper_instance:
        scraper_instance.close()

# FastAPI app
app = FastAPI(
    title="AI Job Scraper API",
    description="Scrape job postings for AI CV generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class JobScrapeRequest(BaseModel):
    url: str
    extract_salary: bool = True
    extract_benefits: bool = False

class BatchScrapeRequest(BaseModel):
    urls: List[str]
    max_concurrent: int = 3

class JobAnalysisRequest(BaseModel):
    url: str
    user_skills: List[str]
    target_position: str

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

class AnalysisResult(BaseModel):
    job_data: JobData
    skill_match_score: float
    missing_skills: List[str]
    matching_skills: List[str]
    recommendations: List[str]

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    timestamp: str

# Helper functions
def create_job_data(scraper_result: Dict[str, Any]) -> JobData:
    """Convert scraper result to JobData model"""
    return JobData(
        success=scraper_result.get('success', False),
        portal=scraper_result.get('portal', 'unknown'),
        url=scraper_result.get('url', ''),
        title=scraper_result.get('title', 'N/A'),
        company=scraper_result.get('company', 'N/A'),
        location=scraper_result.get('location', 'N/A'),
        salary=scraper_result.get('salary'),
        requirements=scraper_result.get('requirements', []),
        skills=scraper_result.get('skills', []),
        description=scraper_result.get('description', ''),
        experience_level=scraper_result.get('experience_level', 'Unknown'),
        scraped_at=datetime.now().isoformat()
    )

def analyze_skill_match(job_skills: List[str], user_skills: List[str]) -> Dict[str, Any]:
    """Analyze skill matching between job and user"""
    job_skills_lower = [skill.lower() for skill in job_skills]
    user_skills_lower = [skill.lower() for skill in user_skills]
    
    matching_skills = []
    for user_skill in user_skills_lower:
        for job_skill in job_skills_lower:
            if user_skill in job_skill or job_skill in user_skill:
                matching_skills.append(user_skill)
                break
    
    missing_skills = [skill for skill in job_skills if skill.lower() not in user_skills_lower]
    
    match_score = len(matching_skills) / len(job_skills) if job_skills else 0.0
    
    return {
        'match_score': round(match_score * 100, 2),
        'matching_skills': list(set(matching_skills)),
        'missing_skills': missing_skills[:10],  # Limit to top 10
        'total_job_skills': len(job_skills),
        'user_skills_count': len(user_skills)
    }

# API Endpoints
@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "AI Job Scraper API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "scrape": "POST /api/v1/scrape",
            "batch": "POST /api/v1/batch-scrape", 
            "analyze": "POST /api/v1/analyze",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    global scraper_instance
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scraper_ready": scraper_instance is not None,
        "selenium_available": scraper_instance.use_selenium if scraper_instance else False
    }

@app.post("/api/v1/scrape", response_model=JobData)
async def scrape_job(request: JobScrapeRequest):
    """Scrape a single job posting"""
    global scraper_instance
    
    if not scraper_instance:
        raise HTTPException(status_code=503, detail="Scraper not initialized")
    
    try:
        logger.info(f"🔍 Scraping job: {request.url}")
        
        # Run scraping in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            scraper_instance.scrape_job, 
            request.url
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400, 
                detail=f"Scraping failed: {result.get('error', 'Unknown error')}"
            )
        
        return create_job_data(result)
        
    except Exception as e:
        logger.error(f"❌ Scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/batch-scrape")
async def batch_scrape_jobs(request: BatchScrapeRequest):
    """Scrape multiple job postings"""
    global scraper_instance
    
    if not scraper_instance:
        raise HTTPException(status_code=503, detail="Scraper not initialized")
    
    if len(request.urls) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 URLs per batch")
    
    try:
        logger.info(f"📋 Batch scraping {len(request.urls)} jobs")
        
        # Limit concurrent requests
        semaphore = asyncio.Semaphore(request.max_concurrent)
        
        async def scrape_single(url: str):
            async with semaphore:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    scraper_instance.scrape_job, 
                    url
                )
                return create_job_data(result)
        
        # Process all URLs concurrently
        tasks = [scrape_single(url) for url in request.urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "url": request.urls[i],
                    "error": str(result),
                    "scraped_at": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        return {
            "total_requested": len(request.urls),
            "successful": sum(1 for r in processed_results if r.get('success', False)),
            "failed": sum(1 for r in processed_results if not r.get('success', True)),
            "results": processed_results
        }
        
    except Exception as e:
        logger.error(f"❌ Batch scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_job_fit(request: JobAnalysisRequest):
    """Analyze job fit for user skills"""
    global scraper_instance
    
    if not scraper_instance:
        raise HTTPException(status_code=503, detail="Scraper not initialized")
    
    try:
        logger.info(f"🎯 Analyzing job fit: {request.url}")
        
        # Scrape job first
        loop = asyncio.get_event_loop()
        scrape_result = await loop.run_in_executor(
            None, 
            scraper_instance.scrape_job, 
            request.url
        )
        
        if not scrape_result.get('success'):
            raise HTTPException(
                status_code=400, 
                detail=f"Scraping failed: {scrape_result.get('error')}"
            )
        
        job_data = create_job_data(scrape_result)
        
        # Analyze skill match
        analysis = analyze_skill_match(job_data.skills, request.user_skills)
        
        # Generate recommendations
        recommendations = []
        if analysis['match_score'] < 70:
            recommendations.append("Consider gaining experience in missing key skills")
        if len(analysis['missing_skills']) > 5:
            recommendations.append("Focus on the top 3-5 most important missing skills")
        if analysis['match_score'] > 80:
            recommendations.append("Great match! Highlight your matching skills in CV")
        
        recommendations.append(f"Your skill match score: {analysis['match_score']}%")
        
        return AnalysisResult(
            job_data=job_data,
            skill_match_score=analysis['match_score'],
            missing_skills=analysis['missing_skills'],
            matching_skills=analysis['matching_skills'],
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/supported-portals")
async def get_supported_portals():
    """Get list of supported job portals"""
    return {
        "supported_portals": [
            {
                "name": "Pracuj.pl",
                "domain": "pracuj.pl",
                "selenium_required": True,
                "features": ["full_parsing", "skills_extraction", "salary_detection"]
            },
            {
                "name": "NoFluffJobs",
                "domain": "nofluffjobs.com", 
                "selenium_required": True,
                "features": ["tech_stack", "salary_ranges", "remote_work"]
            },
            {
                "name": "JustJoin.it",
                "domain": "justjoin.it",
                "selenium_required": True,
                "features": ["tech_skills", "experience_levels"]
            },
            {
                "name": "Indeed.pl",
                "domain": "indeed.pl",
                "selenium_required": False,
                "features": ["basic_parsing"]
            }
        ]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return ErrorResponse(
        error=exc.detail,
        timestamp=datetime.now().isoformat()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"❌ Unhandled exception: {exc}")
    return ErrorResponse(
        error="Internal server error",
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )