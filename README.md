# Asynchronous Webcrawler for Keyword Extraction

An asynchronous webcrawler that extracts keywords from each discovered website and writes them to a PostgreSQL database.

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Description

This project is an asynchronous webcrawler built with Python, using `undetected-chromedriver` and `Selenium` for web scraping. The crawler navigates through web pages, extracts keywords, and stores them in a PostgreSQL database. The main goal is to collect keywords for SEO purposes.

## Features

- Asynchronous crawling using `asyncio`.
- Keyword extraction from web pages.
- Storage of extracted keywords in a PostgreSQL database.
- Handling of dynamic web pages using `undetected-chromedriver`.
- Ability to change database configuration on the fly.
- Multithreading for handling user input and error management.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/async-webcrawler.git
    cd async-webcrawler
    ```

2. **Install dependencies:**

    Make sure you have Python 3.7 or higher and `pip` installed.

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up ChromeDriver:**

    Download ChromeDriver and place it in `/usr/local/bin`.

    ```bash
    # Example for macOS/Linux
    wget -O /usr/local/bin/chromedriver https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip
    chmod +x /usr/local/bin/chromedriver
    ```

4. **Set up Google Chrome:**

    Make sure Google Chrome is installed at `/usr/local/bin/chrome`.

    ```bash
    # Example for macOS/Linux
    wget -O /usr/local/bin/chrome https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    chmod +x /usr/local/bin/chrome
    ```

5. **Set up PostgreSQL:**

    Ensure you have a PostgreSQL database running and accessible.

## Usage

1. **Run the webcrawler:**

    ```bash
    python webcrawler.py
    ```

2. **Provide initial inputs:**

    You will be prompted to enter the initial URL, database name, username, password, host, and port.

3. **Monitor and interact:**

    - Type `changedata` to change the database configuration.
    - Type `info` to get information about the last error encountered.

## Configuration

The configuration for the PostgreSQL database is set dynamically via user input. The `db_config` dictionary is populated with the database name, user, password, host, and port.

```python
db_config = {
    'dbname': 'your_db_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': 'your_port'
}
```
## Contributing

To contribute, follow these steps:

1. **Fork the repository**: Click the "Fork" button at the top right of the repository page to create a copy of the repository in your own GitHub account.

2. **Clone the repository**: Clone your forked repository to your local machine.

    ```bash
    git clone https://github.com/yourusername/async-webcrawler.git
    cd async-webcrawler
    ```

3. **Create a new branch**: Create a new branch for your feature or bugfix.

    ```bash
    git checkout -b feature/your-feature
    ```

4. **Make your changes**: Implement your feature or bugfix.

5. **Commit your changes**: Commit your changes with a descriptive commit message.

    ```bash
    git add .
    git commit -m 'Add some feature'
    ```

6. **Push to your branch**: Push your changes to your forked repository.

    ```bash
    git push origin feature/your-feature
    ```

7. **Open a pull request**: Go to the original repository and open a pull request. Provide a clear description of your changes and why they are necessary.
