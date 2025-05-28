import scrapy
import logging

class NewsletterSpider(scrapy.Spider):
    name = "cbnewsinner"
    start_urls = ['https://www.cbinsights.com/newsletter/']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                meta={'playwright': True},
                callback=self.parse
            )

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")
        items = response.css('li.newsletter_pagination_item')
        self.logger.info(f"Found {len(items)} newsletter items")

        for item in items:
            title = item.css('h4 a::text').get(default='').strip()
            link = item.css('h4 a::attr(href)').get(default='')
            description = item.css('p.description::text').get(default='').strip()

            if link:
                full_link = response.urljoin(link)
                yield scrapy.Request(
                    url=full_link,
                    callback=self.parse_inner,
                    meta={
                        'playwright': True,
                        'title': title,
                        'link': full_link,
                        'description': description
                    },
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                    }
                )

        # Handle pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                },
                meta={'playwright': True},
                callback=self.parse
            )

    def parse_inner(self, response):
        content_blocks = response.css('article p::text, article li::text').getall()
        full_content = ' '.join([text.strip() for text in content_blocks if text.strip() and len(text.strip()) > 10])

        yield {
            'title': response.meta.get('title', ''),
            'link': response.meta.get('link', ''),
            'description': response.meta.get('description', ''),
            'full_content': full_content or 'No content found'
        }