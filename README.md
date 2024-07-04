# Async WebCrawler

An asynchronous web crawler written in Python that simulates user actions using Selenium and bypasses anti-bot systems with undetected_chromedriver. Unlike web crawlers using requests, it can handle any web page, store keywords in a PostgreSQL database, and process links of any type. This web crawler identifies the keywords that users search for in order to find a specific website, helping to understand how people are led to the site through search engines.

## Features
- Asynchronous crawling
- User action simulation using Selenium
- Bypasses anti-bot systems with `undetected_chromedriver`
- Stores keywords in a PostgreSQL database
- Skips processing of the following file extensions for increased security and relevance: .exe, .bat, .msi, .sh, .bin, .jar, .zip, .rar, .7z, .tar, .gz, .iso, .img, .dll, .so, .mp4, .avi, .mov, .wmv, .mp3, .wav, .flac, .jpg, .jpeg, .png, .gif, .bmp, .pdf, .doc etc...
- Retrieves all links from a page, even if the page requires scrolling to load all the links.

## Versions
The repository contains four versions of the web crawler:
1. **webcrawler.py (ignores robots.txt)**: Designed to run on your main computer and ignores `robots.txt` directives. **Warning: web crawler can get to unsafe links so that can be dangerous.**
2. **webcrawler-respectful.py (respects robots.txt)**: Designed to run on your main computer and respects `robots.txt` directives. **Warning: web crawler can get to unsafe links so that can be dangerous.**
3. **webcrawler-docker.py (ignores robots.txt)**: Designed to run in a Docker container and ignores `robots.txt` directives. **This version is safe because of running in isolated docker-container.**
4. **webcrawler-docker-respectful.py (respects robots.txt)**: Designed to run in a Docker container and respects `robots.txt` directives. **This version is safe because of running in isolated docker-container.**

## Installation

### Recommended: Docker Installation
It is recommended to run this web crawler in a Docker container or any other isolated environment to ensure safety and prevent potential security risks.

#### Docker installation

1. **Clone the repository:**
  ```cmd
  git clone https://github.com/yourusername/async-webcrawler.git
  cd async-webcrawler
  ```

2. **Build the Docker image:**
    ```cmd
    docker build -t async-webcrawler .
    ```

3. **Run the Docker container:**
    ```cmd
    docker run -it --name webcrawler async-webcrawler /bin/bash
    ```
4. **Run webcrawler:**
   ```cmd
   python webcrawler_docker.py
   ```
   
### Alternative: Local Installation
You can also install and run this web crawler locally. However, please note that this is at your own risk as the program may visit potentially harmful websites.

#### Step-by-Step Local Installation

1. **Clone the repository:**
    ```cmd
    git clone https://github.com/yourusername/async-webcrawler.git
    cd async-webcrawler
    ```

2. **Create a virtual environment and activate it:**
    ```cmd
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required packages:**
    ```cmd
    pip install -r requirements.txt
    ```

4. **Set up the PostgreSQL database:**
    Ensure you have PostgreSQL installed and running. Create a database and configure the connection settings in your application.

5. **Run the web crawler:**
    ```cmd
    python main.py
    ```

## In programm commands:
```cmd
help
```
