# Webweaver-Node

![Development Status](https://img.shields.io/badge/status-in_development-orange)

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

## 🚧 Project Status

This project is currently under development