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
        items = response.css('li.newsletter_pagination_item')

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
        title = response.meta.get('title', '')
        link = response.meta.get('link', '')
        description = response.meta.get('description', '')

        content_blocks = []

        # Select all elements inside the table with class 'hse-body-wrapper-table'
        elements = response.css('table.hse-body-wrapper-table tbody tr td div div *')

        for element in elements:
            tag = element.root.tag.lower()

            if tag in ['p', 'div', 'td']:
                text = element.xpath('normalize-space()').get()
                if text:
                    content_blocks.append({'type': 'text', 'content': text})

            elif tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                heading = element.xpath('normalize-space()').get()
                if heading:
                    content_blocks.append({'type': 'header', 'content': heading})

            elif tag == 'img':
                img_src = element.xpath('@src').get()
                if img_src:
                    content_blocks.append({'type': 'image', 'src': response.urljoin(img_src)})

            elif tag == 'li':
                li_text = element.xpath('normalize-space()').get()
                if li_text:
                    content_blocks.append({'type': 'list_item', 'content': li_text})

        yield {
            'title': title,
            'link': link,
            'description': description,
            'content_blocks': content_blocks
        }

        self.logger.info(f"✅ Parsed {len(content_blocks)} blocks from: {link}")
