import os
import time
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Specify the path to your ChromeDriver executable
webdriver_path = 'C:/Users/sakin/Downloads/chromedriver.exe'

# Configure Chrome options
chrome_options = Options()

# Specify the URL
url = 'https://library.advocates.ke/'

# Specify the target directory to save the zip file
target_directory = 'C:\\Users\\sakin\\Downloads'

# Specify the target directory to save the downloaded files
download_directory = 'C:\\Users\\sakin\\Downloads'

# Create a new Chrome driver instance
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Set the download directory in Chrome options
prefs = {'download.default_directory': download_directory}
chrome_options.add_experimental_option('prefs', prefs)

# Navigate to the URL
driver.get(url)

# Wait for the page to load (adjust the sleep time as needed)
time.sleep(20)

# Find the table containing the documents
table = driver.find_element(By.CSS_SELECTOR, 'div.entry-content table.posts-data-table')

# Find the header row of the table
header_row = table.find_element(By.CSS_SELECTOR, 'thead tr')

# Extract the column indexes for title, category, summary, and link
column_indexes = {}
columns = header_row.find_elements(By.CSS_SELECTOR, 'th')
for i, column in enumerate(columns):
    column_name = column.get_attribute('data-name')
    if column_name:
        column_indexes[column_name] = i

# Create a list to store the document information
document_info = []

# Extract the document information from the table rows
def extract_document_info(rows):
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(cells) >= 4:
            title_index = column_indexes.get('title')
            category_index = column_indexes.get('doc_categories')
            summary_index = column_indexes.get('excerpt')
            link_index = column_indexes.get('link')
            title = cells[title_index].text
            category = cells[category_index].text
            summary = cells[summary_index].text
            link = cells[link_index].find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            document_info.append({'title': title, 'category': category, 'summary': summary, 'link': link})

# Extract the initial document information
rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
extract_document_info(rows)

# Check if there is a "Next" button
next_button = driver.find_element(By.CSS_SELECTOR, '.next')
while next_button:
    # Click the "Next" button
    next_button.click()

    # Wait for the page to load (adjust the sleep time as needed)
    time.sleep(20)

    # Find the table rows on the current page
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

    # Extract the document information from the current page
    extract_document_info(rows)

    # Check if there is another "Next" button
    next_button = driver.find_element(By.CSS_SELECTOR, '.next') if driver.find_elements(By.CSS_SELECTOR, '.next') else None

# Create a zip file
zip_file_path = os.path.join(target_directory, 'documents.zip')
zip_file = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)

# Download each document and add it to the zip file
for document in document_info:
    document_title = document['title']
    document_link = document['link']
    driver.get(document_link)
    # Wait for the download to complete (adjust the sleep time as needed)
    time.sleep(5)

    # Find the downloaded file in the download directory
    downloaded_file = os.listdir(download_directory)[0]
    downloaded_file_path = os.path.join(download_directory, downloaded_file)

    # Generate a unique file name by appending a counter if necessary
    counter = 1
    new_file_path = os.path.join(target_directory, document_title)
    while os.path.exists(new_file_path):
        new_file_path = os.path.join(target_directory, f"{document_title}_{counter}")
        counter += 1

    # Move the downloaded file to the zip file
    os.rename(downloaded_file_path, new_file_path)

    # Add the file to the zip file
    zip_file.write(new_file_path, os.path.basename(new_file_path))

# Close the browser and the zip file
driver.quit()
zip_file.close()

print('Download and zip process completed.')
