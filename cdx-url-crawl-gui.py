import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import signal
import sys
import pandas as pd
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from tqdm import tqdm
import threading

class CrawlerThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)

    def __init__(self, base_url, delay=1):
        super().__init__()
        self.base_url = base_url
        self.delay = delay
        self.visited_urls = []
        self.paused = False
        self.running = True

    def run(self):
        urls_to_visit = [self.base_url]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

        while urls_to_visit and self.running:
            while self.paused:
                time.sleep(0.1)

            current_url = urls_to_visit.pop(0)

            if any(url['url'] == current_url for url in self.visited_urls):
                continue

            try:
                # Send a GET request to the current URL
                response = requests.get(current_url, headers=headers, timeout=10)
                response.raise_for_status()  # Raise an error for bad status codes
            except requests.exceptions.RequestException as e:
                self.status_signal.emit(f"Error fetching the URL: {e}")
                continue

            # Get the page title
            soup = BeautifulSoup(response.text, 'html.parser')
            page_title = soup.title.string.strip() if soup.title else 'No Title'

            # Mark the current URL as visited with its title
            self.visited_urls.append({'url': current_url, 'title': page_title})
            self.progress_signal.emit(len(self.visited_urls))
            self.status_signal.emit(f"Crawling: {current_url}")

            # Find all anchor tags and extract the href attribute
            for anchor in soup.find_all('a', href=True):
                # Resolve relative URLs using urljoin
                url = urljoin(current_url, anchor['href'])

                # Only keep URLs within the same domain, avoid fragments, mailto links, and already visited URLs
                parsed_url = urlparse(url)
                if parsed_url.netloc == urlparse(self.base_url).netloc and parsed_url.scheme in ["http", "https"] and not any(url_entry['url'] == url for url_entry in self.visited_urls) and url not in urls_to_visit:
                    urls_to_visit.append(url)

            # Respectful crawling: delay between requests
            time.sleep(self.delay)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False

def save_urls_to_file(urls, file_name, delimiter):
    if urls:
        with open(file_name, 'w', encoding='utf-8') as file:
            for index, url_entry in enumerate(urls, start=1):
                file.write(f'"{index}"{delimiter}"{url_entry["url"]}"{delimiter}"{url_entry["title"]}"\n')
    else:
        print("No URLs found.")

def save_urls_to_excel(urls, file_name):
    if urls:
        data = [{'Increment Number': index + 1, 'URL': url_entry['url'], 'Page Title': url_entry['title']} for index, url_entry in enumerate(urls)]
        df = pd.DataFrame(data)
        df.to_excel(file_name, index=False)
    else:
        print("No URLs found.")

class WebScraperApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Web Scraper")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QtWidgets.QVBoxLayout()

        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setPlaceholderText("Enter the base URL")
        self.url_input.setStyleSheet("padding: 10px; border-radius: 10px; background-color: #ffffff;")
        layout.addWidget(self.url_input)

        self.format_label = QtWidgets.QLabel("Choose the format to save the URLs:")
        layout.addWidget(self.format_label)

        self.format_combo = QtWidgets.QComboBox(self)
        self.format_combo.addItem("Text")
        self.format_combo.addItem("Excel")
        layout.addWidget(self.format_combo)

        self.delimiter_label = QtWidgets.QLabel("Choose a delimiter (for text format):")
        layout.addWidget(self.delimiter_label)

        self.delimiter_combo = QtWidgets.QComboBox(self)
        self.delimiter_combo.addItem(", (Comma)")
        self.delimiter_combo.addItem("; (Semicolon)")
        layout.addWidget(self.delimiter_combo)

        self.file_name_input = QtWidgets.QLineEdit(self)
        self.file_name_input.setPlaceholderText("Enter the file name without extension")
        self.file_name_input.setStyleSheet("padding: 10px; border-radius: 10px; background-color: #ffffff;")
        layout.addWidget(self.file_name_input)

        self.start_button = QtWidgets.QPushButton("Start Crawling", self)
        self.start_button.setStyleSheet("padding: 10px; border-radius: 10px; background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_crawling)
        layout.addWidget(self.start_button)

        self.pause_button = QtWidgets.QPushButton("Pause", self)
        self.pause_button.setStyleSheet("padding: 10px; border-radius: 10px; background-color: #FFA500; color: white;")
        self.pause_button.clicked.connect(self.pause_crawling)
        self.pause_button.setEnabled(False)
        layout.addWidget(self.pause_button)

        self.stop_button = QtWidgets.QPushButton("Stop", self)
        self.stop_button.setStyleSheet("padding: 10px; border-radius: 10px; background-color: #FF0000; color: white;")
        self.stop_button.clicked.connect(self.stop_crawling)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QtWidgets.QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def start_crawling(self):
        base_url = self.url_input.text().strip()
        save_format_choice = self.format_combo.currentIndex()
        file_name = self.file_name_input.text().strip()

        if not base_url or not file_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please provide both URL and file name.")
            return

        if save_format_choice == 0:  # Text
            self.save_format = 'text'
            delimiter_choice = self.delimiter_combo.currentIndex()
            self.delimiter = ',' if delimiter_choice == 0 else ';'
            self.file_name = file_name + ".txt"
        elif save_format_choice == 1:  # Excel
            self.save_format = 'excel'
            self.file_name = file_name + ".xlsx"
        else:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Invalid format selected.")
            return

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        self.crawler_thread = CrawlerThread(base_url)
        self.crawler_thread.progress_signal.connect(self.update_progress)
        self.crawler_thread.status_signal.connect(self.update_status)
        self.crawler_thread.start()

    def pause_crawling(self):
        if self.crawler_thread.paused:
            self.crawler_thread.resume()
            self.pause_button.setText("Pause")
        else:
            self.crawler_thread.pause()
            self.pause_button.setText("Resume")

    def stop_crawling(self):
        self.crawler_thread.stop()
        self.crawler_thread.wait()
        if self.save_format == 'text':
            save_urls_to_file(self.crawler_thread.visited_urls, self.file_name, self.delimiter)
        elif self.save_format == 'excel':
            save_urls_to_excel(self.crawler_thread.visited_urls, self.file_name)
        self.reset_ui()

    def reset_ui(self):
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Idle")

    def update_progress(self, count):
        self.progress_bar.setValue(min(100, count))

    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WebScraperApp()
    window.show()
    sys.exit(app.exec_())
