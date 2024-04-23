# crawler.py
import scrapy
from scrapy.crawler import CrawlerProcess


class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://en.wikipedia.org']  # Seed URL
    max_pages = 2  # Max number of pages to crawl
    max_depth = 1  # Max depth to crawl

    def parse(self, response):
        # Your parsing logic here
        # Example: Extracting links and data
        links = response.css('a::attr(href)').getall()
        links = links[:min(5, len(links))]
        data = response.css('p::text').getall()
        data = data[:min(5, len(data))]
        print("\n\n\n\nTOTAL LINKS %d\n\n\n\n\n\n" % len(links))

        # Process extracted data as needed
        # Example: Store data or yield items
        yield {
            'url': response.url,
            'data': data
        }

        # Follow links if max pages and depth not reached
        item_count = self.crawler.stats.get_value('item_scraped_count', 0)
        if item_count < self.max_pages:
            for link in links:
                yield response.follow(link, callback=self.parse)

        depth = response.meta.get('depth', 1)
        if depth < self.max_depth:
            print(f'Current depth: {depth}')
            for link in links:
                yield response.follow(link, callback=self.parse, meta={'depth': depth + 1})
        else:
            print("Reached maximum depth. Stopping.")

        if item_count >= self.max_pages:
            print("Reached maximum pages. Stopping.")


# Instantiate a CrawlerProcess with concurrency settings
process = CrawlerProcess(settings={
    'CONCURRENT_REQUESTS': 4,  # Number of concurrent requests
    'DOWNLOAD_DELAY': 0.5,  # Delay between requests (in seconds)
    'AUTOTHROTTLE_ENABLED': True,  # Enable autothrottle
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 2,  # Target concurrency
})

# Add your spider to the process and start crawling
# process.crawl(MySpider)
# process.start()
print("Crawling completed.")
