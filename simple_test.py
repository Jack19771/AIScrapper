from scraper import AdvancedJobScraper

print("🧪 Testing scraper...")

scraper = AdvancedJobScraper(use_selenium=True, headless=True)

url = "https://www.pracuj.pl/praca/python-django-developer-warszawa,oferta,1004294341?sug=list_top_cr_bd_21_tname_252_tgroup_A&s=1f7c2c91&searchId=MTc1NjExOTMzMDc1NC40Njk1"

result = scraper.scrape_job(url)

print(f"Success: {result.get('success')}")
print(f"Title: {result.get('title')}")
print(f"Skills: {result.get('skills', [])[:5]}")  # First 5 skills

scraper.close()
print("✅ Test done")