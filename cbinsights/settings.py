BOT_NAME = "cbinsights"

SPIDER_MODULES = ["cbinsights.spiders"]
NEWSPIDER_MODULE = "cbinsights.spiders"

ROBOTSTXT_OBEY = False

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False, 
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30 * 1000

CONCURRENT_REQUESTS = 5
DOWNLOAD_DELAY = 1.0

LOG_LEVEL = 'INFO'