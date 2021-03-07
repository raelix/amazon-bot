from scraper_amazon import ScraperAmazon

class ScraperFactory:
  
  def get_scraper(self, scrape_provider='amazon'):
    if scrape_provider == 'amazon':
      scraper = ScraperAmazon()
    return scraper
          
