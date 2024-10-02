# Test task for EVOPLAY
___
## Overview
Python script for parsing search results on [GitHub](https://github.com) by keywords. And saving the data in json.

You can find the task requirements in this file. [assignment.pdf](assignment.pdf)
___
## Table of Contents
- [Features](#features)
- [Project structure](#project-structure-and-content)
- [Installation Git](#installation)

---
### Features:
1. **Random use of a proxy server from the specified list.**
2. **Generates a random User-Agent header**
3. **Use of logging.**
---
### Project structure and content:
```
.
├── managers                            # Manages proxies and User-Agent headers for the crawler.
│   └── proxy_manager.py            
├── parsers                             # The main logic of the script
│   ├── github_crawler.py
│   └── github_parser.py
├── utils                               # Utilities necessary for the project to work
│   └── file_loader.py
├── tests
│   ├── test_github_crawler.py
│   ├── test_github_parser.py
│   ├── test_json_functions.py
│   └── test_proxy_manager.py
├── README.md
├── assignment.pdf                      # Task conditions
├── config.py
├── data.json                           # Input data
├── main.py                             # Project startup file.
└── requirements.txt                    # Required dependencies.
```
---
## Installation

1. Python 3.x must be installed.

2. Clone the repository:
   ```
   https://github.com/bezhevets/EvoPlay.git
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:

   - On macOS and Linux:
   ```source venv/bin/activate```
   - On Windows:
   ```venv\Scripts\activate```
5. Install project dependencies:
   ```
    pip install -r requirements.txt
   ```
6. Write data to the `data.json` file or use the input data from the `data.json` file. [Go to data.json](data.json)
   - **IMPORTANT:** Proxy servers in the file are available until 02.10.24
7. Run the script using the following command::
    ```
   python main.py
    ```
---
**IMPORTANT**: The result is saved in a JSON file in the root folder.
