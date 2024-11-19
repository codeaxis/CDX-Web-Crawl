# Web Scraper with PyQt5 GUI

This project is a web scraper with a modern GUI built using PyQt5. It allows users to scrape URLs from a given website, save the results to either a text or Excel file, and manage the crawling process through a user-friendly interface. The application supports pausing, resuming, and stopping the crawl process, with results saved automatically when stopped.

## Features

- Crawl a website starting from a base URL.
- GUI with PyQt5 for easy user interaction.
- Save results as a text file or Excel file.
- Pause, resume, and stop the crawling process.
- Progress bar and status updates.

## Prerequisites

- Python 3.7+
- Virtual environment (`venv`) to manage dependencies

## Installation

### Setting up the Virtual Environment

#### Linux

1. **Install Python and Virtual Environment**
   
   Open a terminal and ensure Python 3 is installed:
   ```sh
   sudo apt-get update
   sudo apt-get install python3 python3-venv python3-pip
   ```

2. **Create a Virtual Environment**
   
   Navigate to your project directory and create a virtual environment:
   ```sh
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**
   ```sh
   source venv/bin/activate
   ```

4. **Install Dependencies**
   
   Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

#### Windows

1. **Install Python and Virtual Environment**

   Download and install Python from [python.org](https://www.python.org/downloads/). Ensure you select "Add Python to PATH" during installation.

2. **Create a Virtual Environment**

   Open Command Prompt and navigate to your project directory. Then create a virtual environment:
   ```cmd
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   ```cmd
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   
   Install the required packages:
   ```cmd
   pip install -r requirements.txt
   ```

### Required Python Packages

Create a `requirements.txt` file in the root directory with the following content:

```
requests
beautifulsoup4
pandas
PyQt5
tqdm
openpyxl
```

## Running the Web Scraper

1. **Activate the Virtual Environment**
   - On Linux:
     ```sh
     source venv/bin/activate
     ```
   - On Windows:
     ```cmd
     venv\Scripts\activate
     ```

2. **Run the Application**
   
   To start the web scraper GUI, run the following command:
   ```sh
   python web_scraper.py
   ```

## Usage

1. **Enter the Base URL**: Provide the starting point for the web scraper.
2. **Choose the Save Format**: Select either "Text" or "Excel" to save the results.
3. **Select Delimiter (for Text)**: If "Text" is selected, choose the delimiter (comma or semicolon).
4. **Enter File Name**: Provide a name for the output file (without extension).
5. **Control the Scraper**:
   - Click **Start Crawling** to begin.
   - Click **Pause** to pause and **Resume** to continue.
   - Click **Stop** to stop the scraper and save the current progress.

## Notes

- The scraper respects the domain of the provided base URL and does not crawl external domains.
- The application saves progress to the specified file when the stop button is pressed.
- A progress bar and status label provide real-time feedback on the scraping process.

## Troubleshooting

- **PyQt5 Installation Issues**: Ensure your Python version is 3.7 or higher, as some versions may face compatibility issues with PyQt5.
- **Permission Errors**: Run the terminal as administrator or use `sudo` if you encounter permission issues when installing packages.

## License

This project is licensed under the MIT License.

