from scraper import AdvancedJobScraper

scraper = AdvancedJobScraper(use_selenium=True, headless=False)  # headless=False żeby zobaczyć co się dzieje

url = "https://www.pracuj.pl/praca/analityk-it-python-pyspark-warszawa,oferta,1004282517?sug=list_top_cr_bd_6_tname_252_tgroup_A&s=1f7c2c91&searchId=MTc1NjExOTMzMDc1NC40Njk1"
result = scraper.scrape_job(url)

print("🎯 Wyniki:")
print(f"Title: {result.get('title')}")
print(f"Skills: {result.get('skills')}")
print(f"Requirements: {result.get('requirements')}")

scraper.close()