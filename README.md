# Webweaver-Node

fully asynchronous web scraping microservice designed to handle dynamic and static content. Equipped with powerful tools for browser automation, HTML parsing, and flexible middleware, WebWeaver-Node efficiently extracts data from a wide range of websites with ease and reliability.

## 🚀 Features

- **Fully Asynchronous**: Enables concurrent task execution, enhancing speed and efficiency in scraping operations.
- **Built-In Browser Automation with Playwright**: Utilizes Playwright for scraping dynamic, JavaScript-heavy websites.
- **HTML Parsing with BeatifulSoup**: Provides enhanced HTML parsing capabilities using BeautifulSoup.
- **Enhanced Playwright and BeautifulSoup Integration**: Extends Playwright and BeautifulSoup with additional web scraping features, including DOM traversal tools, human-like interactions, and custom data extraction methods.
- **Rotating Proxy Support**: Integrates easily with rotating proxies to help manage IP bans and improve data collection stability.
- **Modular Request/Response Middleware System**: Includes built-in middleware for retry handling, status code checks, and more. Users can add/remove middleware as needed to fit their specific scraping needs.
- **Flexible Data Validation**: Uses Pydantic schemas for data validation, ensuring data quality before it is processed or stored.
- **Fuzzy String Matching**: Provides tools for fuzzy matching, keyword detection, and regex matching to categorize and organize scraped data.
- **Secure Authentication**: Client requests are authenticated using custom HTTP headers (API KEY and ACCESS ID) for enhanced security.

## 🛠️ Tech Stack

- **Server**: FastAPI and asyncio for asynchronous server operations.
- **Database**: Tortoise-ORM with Postgresql.
- **Web Scraping**: Spiders developed using aiohttp & playwright.
- **Data Parsing**: BeautifulSoup for parsing web content.

## 🕷️ How it Works

1. **Spiders**: Build spider objects by inheriting from the base Spider class.
2. **Pipelines**: Construct pipeline objects using the base Pipeline class.
3. **SpiderLauncher**: This class is responsible for launching the spiders, which asynchronously yield scraped data.
4. **Async Queue**: The yielded data is queued asynchronously, ready for pipelining.
5. **Pipeline Listener**: Processes queued data, invoking the appropriate pipeline module to handle data processing and storage.

## 🔒 Security

Authentication is managed using custom HTTP headers. Both API KEY and ACCESS ID are encrypted and stored in a PyNaCl "SecretBox" on the client side, accessed via the CLI app for enhanced security.

## 🚧 Project Status

This project is currently under development