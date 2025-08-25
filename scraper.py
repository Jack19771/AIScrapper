#!/usr/bin/env python3
"""
Advanced Job Scraper with Selenium
Scrapes job listings from Polish job portals with JavaScript support
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedJobScraper:
    def __init__(self, use_selenium=True, headless=True):
        self.use_selenium = use_selenium
        self.headless = headless
        
        # Setup requests session
        self.session = requests.Session()
        self.headers = self._get_random_headers()
        self.session.headers.update(self.headers)
        
        # Setup Selenium if needed
        self.driver = None
        if use_selenium:
            self._setup_selenium()
    
    def _get_random_headers(self):
        """Get random headers to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with anti-detection"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Anti-detection options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins-discovery')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Selenium WebDriver initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Selenium setup failed: {e}")
            logger.warning("📝 Make sure ChromeDriver is installed: pip install chromedriver-autoinstaller")
            self.use_selenium = False
    
    def detect_portal(self, url):
        """Detect which job portal we're scraping"""
        domain = urlparse(url).netloc.lower()
        
        portals = {
            'pracuj.pl': 'pracuj',
            'indeed.pl': 'indeed',
            'indeed.com': 'indeed',
            'nofluffjobs.com': 'nofluff',
            'justjoin.it': 'justjoin',
            'theprotocol.it': 'protocol',
            'bulldogjob.pl': 'bulldog'
        }
        
        for domain_key, portal in portals.items():
            if domain_key in domain:
                return portal
        
        return 'unknown'
    
    def scrape_with_selenium(self, url, portal):
        """Scrape using Selenium for JavaScript-heavy sites"""
        if not self.driver:
            return {'success': False, 'error': 'Selenium not available'}
        
        try:
            logger.info(f"🌐 Loading {url} with Selenium")
            self.driver.get(url)
            
            # Wait for page load
            time.sleep(random.uniform(2, 4))
            
            if portal == 'pracuj':
                return self._scrape_pracuj_selenium()
            elif portal == 'nofluff':
                return self._scrape_nofluff_selenium()
            elif portal == 'justjoin':
                return self._scrape_justjoin_selenium()
            
            # Fallback - extract from page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return self._extract_generic_info(soup, url, portal)
            
        except Exception as e:
            logger.error(f"❌ Selenium scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _scrape_pracuj_selenium(self):
        """Enhanced Pracuj.pl scraping with Selenium"""
        try:
            # Wait for main content to load
            wait = WebDriverWait(self.driver, 10)
            
            # Job title
            title = "N/A"
            try:
                title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="text-offerTitle"], h1')))
                title = title_elem.text.strip()
            except TimeoutException:
                title_selectors = ['h1', '.offer-title', '[data-test*="title"]']
                title = self._try_selectors(title_selectors) or "N/A"
            
            # Company
            company = "N/A"
            company_selectors = ['[data-test="text-employer"]', '.company-name', '[data-test*="company"]', 'h2']
            company = self._try_selectors(company_selectors) or "N/A"
            
            # Location
            location = "N/A"
            location_selectors = ['[data-test="text-workingPlace"]', '.location', '[data-test*="location"]']
            location = self._try_selectors(location_selectors) or "N/A"
            
            # Requirements
            requirements = []
            req_selectors = [
                '[data-test="section-requirements"] li',
                '.requirements li',
                '.requirement-item',
                '[data-test*="requirement"] li'
            ]
            requirements = self._extract_list_items(req_selectors)
            
            # Skills
            skills = []
            skill_selectors = [
                '[data-test="chip-item"]',
                '.skill-tag',
                '.technology-tag',
                '.badge'
            ]
            skills = self._extract_skills(skill_selectors)
            
            # Description
            description = ""
            desc_selectors = [
                '[data-test="section-responsibilities"]',
                '.job-description',
                '.offer-description',
                '[data-test*="description"]'
            ]
            description = self._try_selectors(desc_selectors) or ""
            
            # Salary
            salary = "N/A"
            salary_selectors = [
                '[data-test*="salary"]',
                '.salary',
                '.wage',
                '[data-test*="wage"]'
            ]
            salary = self._try_selectors(salary_selectors) or "N/A"
            
            experience = self._extract_experience_level(title + " " + " ".join(requirements))
            
            return {
                'success': True,
                'portal': 'pracuj',
                'url': self.driver.current_url,
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'requirements': requirements[:10],
                'skills': skills[:15],
                'description': description[:1500],
                'experience_level': experience,
                'raw_requirements': " ".join(requirements)
            }
            
        except Exception as e:
            logger.error(f"❌ Pracuj.pl selenium scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _scrape_nofluff_selenium(self):
        """NoFluffJobs scraping with Selenium"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Job title
            title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, .posting-details-title')))
            title = title_elem.text.strip()
            
            # Company
            company_elem = self.driver.find_element(By.CSS_SELECTOR, '.company-name, .posting-details-company')
            company = company_elem.text.strip() if company_elem else "N/A"
            
            # Technologies
            tech_elements = self.driver.find_elements(By.CSS_SELECTOR, '.posting-technologies .technology')
            skills = [elem.text.strip() for elem in tech_elements if elem.text.strip()]
            
            # Requirements
            req_elements = self.driver.find_elements(By.CSS_SELECTOR, '.posting-requirements li')
            requirements = [elem.text.strip() for elem in req_elements if elem.text.strip()]
            
            # Salary
            salary_elem = self.driver.find_element(By.CSS_SELECTOR, '.posting-salary, .salary-range')
            salary = salary_elem.text.strip() if salary_elem else "N/A"
            
            experience = self._extract_experience_level(title)
            
            return {
                'success': True,
                'portal': 'nofluff',
                'url': self.driver.current_url,
                'title': title,
                'company': company,
                'location': "Remote/Warsaw",
                'salary': salary,
                'requirements': requirements,
                'skills': skills,
                'description': " ".join(requirements),
                'experience_level': experience
            }
            
        except Exception as e:
            logger.error(f"❌ NoFluffJobs selenium scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _try_selectors(self, selectors):
        """Try multiple CSS selectors until one works"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except (NoSuchElementException, Exception):
                continue
        return None
    
    def _extract_list_items(self, selectors):
        """Extract list items from multiple selectors"""
        items = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) > 5 and len(text) < 200:
                        items.append(text)
                if items:  # If we found items with this selector, break
                    break
            except Exception:
                continue
        return items[:10]  # Limit results
    
    def _extract_skills(self, selectors):
        """Extract skills/technologies from multiple selectors"""
        skills = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) < 50 and not any(char.isdigit() for char in text):
                        skills.append(text)
                if skills:
                    break
            except Exception:
                continue
        
        # Also extract from text using keywords
        page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
        tech_keywords = self._get_tech_keywords()
        
        for keyword in tech_keywords:
            if keyword.lower() in page_text and keyword not in skills:
                skills.append(keyword)
        
        return list(set(skills))[:15]  # Remove duplicates and limit
    
    def _get_tech_keywords(self):
        """Common technology keywords to look for"""
        return [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C#', 'C++', 'PHP', 'Ruby', 'Go', 'Rust', 'Kotlin',
            'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js', 'Express', 'FastAPI',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'ElasticSearch', 'SQLite',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Jenkins', 'GitLab', 'GitHub',
            'Git', 'CI/CD', 'Linux', 'Ubuntu', 'Nginx', 'Apache',
            'Scrum', 'Agile', 'REST', 'API', 'GraphQL', 'Microservices',
            'HTML', 'CSS', 'SASS', 'Bootstrap', 'Tailwind', 'jQuery', 'Webpack'
        ]
    
    def scrape_job(self, url):
        """Main scraping method"""
        portal = self.detect_portal(url)
        logger.info(f"🔍 Scraping {portal} job: {url}")
        
        # Try Selenium first for better results
        if self.use_selenium and portal in ['pracuj', 'nofluff', 'justjoin']:
            result = self.scrape_with_selenium(url, portal)
            if result.get('success'):
                return result
        
        # Fallback to requests
        return self._scrape_with_requests(url, portal)
    
    def _scrape_with_requests(self, url, portal):
        """Fallback scraping with requests"""
        try:
            # Random delay
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_generic_info(soup, url, portal)
            
        except Exception as e:
            logger.error(f"❌ Requests scraping failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'portal': portal,
                'url': url
            }
    
    def _extract_generic_info(self, soup, url, portal):
        """Generic information extraction from any job site"""
        try:
            # Try to find title
            title_tags = ['h1', '[data-test*="title"]', '.job-title', '.offer-title']
            title = "N/A"
            for tag in title_tags:
                elem = soup.select_one(tag)
                if elem and elem.text.strip():
                    title = elem.text.strip()
                    break
            
            # Extract all text for analysis
            page_text = soup.get_text()
            
            # Extract skills using keywords
            skills = self._extract_skills_from_text(page_text)
            requirements = self._extract_requirements_from_text(page_text)
            experience = self._extract_experience_level(title + " " + page_text[:1000])
            
            return {
                'success': True,
                'portal': portal,
                'url': url,
                'title': title,
                'company': "N/A",
                'location': "N/A",
                'salary': "N/A",
                'requirements': requirements,
                'skills': skills,
                'description': page_text[:1000],
                'experience_level': experience,
                'raw_requirements': " ".join(requirements)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'portal': portal,
                'url': url
            }
    
    def _extract_skills_from_text(self, text):
        """Extract technical skills from job description"""
        if not text:
            return []
        
        tech_skills = self._get_tech_keywords()
        found_skills = []
        text_lower = text.lower()
        
        for skill in tech_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills[:15]
    
    def _extract_requirements_from_text(self, text):
        """Extract requirements from job description"""
        if not text:
            return []
        
        patterns = [
            r'(?:wymagania|requirements?|must have|essential):?\s*(.+?)(?:\n\n|\n[A-Z]|oferujemy|we offer|benefits)',
            r'(?:potrzebne|needed|required):?\s*(.+?)(?:\n\n|\n[A-Z]|oferujemy)',
            r'(?:oczekujemy|expect|looking for):?\s*(.+?)(?:\n\n|\n[A-Z]|oferujemy)'
        ]
        
        requirements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                reqs = re.split(r'[,;•\-\n]\s*', match)
                for req in reqs:
                    req = req.strip()
                    if req and len(req) > 10 and len(req) < 150:
                        requirements.append(req)
        
        return requirements[:10]
    
    def _extract_experience_level(self, text):
        """Extract experience level from text"""
        if not text:
            return "Unknown"
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect', '5+ lat', '5+ years', 'starszy']):
            return "Senior"
        elif any(word in text_lower for word in ['junior', 'intern', 'trainee', 'entry', 'początkuj', 'młodszy']):
            return "Junior"
        elif any(word in text_lower for word in ['mid', 'regular', 'specjalista', '2-4 lat', '2-4 years']):
            return "Mid"
        else:
            return "Mid"  # Default assumption
    
    def batch_scrape(self, urls):
        """Scrape multiple URLs"""
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"📋 Processing {i+1}/{len(urls)}: {url}")
            result = self.scrape_job(url)
            results.append(result)
            
            # Delay between requests
            if i < len(urls) - 1:
                delay = random.uniform(3, 7)
                logger.info(f"⏱️ Waiting {delay:.1f}s...")
                time.sleep(delay)
        
        return results
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("🔌 Selenium WebDriver closed")

def test_advanced_scraper():
    """Test the advanced scraper"""
    scraper = AdvancedJobScraper(use_selenium=True, headless=True)
    
    try:
        # Test URLs - add real ones here
        test_urls = [
            # "https://pracuj.pl/praca/python-developer-warszawa,oferta,12345",
            # "https://nofluffjobs.com/job/python-developer-xyz",
        ]
        
        if not test_urls:
            logger.info("📝 No test URLs provided. Example output:")
            return {
                'example_output': {
                    'success': True,
                    'portal': 'pracuj',
                    'title': 'Senior Python Developer',
                    'company': 'Tech Company Sp. z o.o.',
                    'location': 'Warszawa (hybrydowo)',
                    'salary': '15,000 - 20,000 PLN',
                    'requirements': [
                        'Min. 4 lata doświadczenia w Python',
                        'Znajomość Django lub FastAPI',
                        'Doświadczenie z PostgreSQL/MySQL',
                        'Znajomość Docker i CI/CD'
                    ],
                    'skills': ['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS', 'Git', 'REST API'],
                    'experience_level': 'Senior'
                }
            }
        
        # Scrape all URLs
        results = scraper.batch_scrape(test_urls)
        
        for result in results:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return results
        
    finally:
        scraper.close()

if __name__ == "__main__":
    print("🚀 Advanced Job Scraper with Selenium")
    print("=" * 60)
    
    # Example usage:
    # scraper = AdvancedJobScraper()
    # result = scraper.scrape_job("https://pracuj.pl/praca/...")
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    # scraper.close()
    
    # Run test
    test_results = test_advanced_scraper()
    print("\n✅ Advanced scraper ready!")
    print("📝 Usage: scraper.scrape_job('job-url')")
    print("🔧 Features: Selenium, anti-detection, multiple portals")