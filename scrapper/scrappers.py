import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2 import service_account
import scrapper.constants as const


# Setup logging configuration
logging.basicConfig(
    filename='scrappers.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = const.FOLDER_ID


def authenticate():
    """
        Authenticates the application using a Google service account.

        Returns:
            Credentials object for Google APIs.
    """
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return creds


def upload_to_drive(file_name, content):
    """
        Uploads a file to Google Drive in the specified folder.

        Args:
            file_name (str): The name of the file to upload.
            content (str): The content of the file.
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # File metadata for Google Drive
    file_metadata = {
        'name': file_name,
        'parents': [PARENT_FOLDER_ID]
    }

    # Convert the content into a file-like object for upload
    from io import BytesIO
    from googleapiclient.http import MediaIoBaseUpload

    file_io = BytesIO(content.encode('utf-8'))
    media = MediaIoBaseUpload(file_io, mimetype='text/plain')

    # Upload the file to Google Drive
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    logging.info(f"File uploaded to Google Drive with ID: {file.get('id')}")
    print(f"File successfully uploaded to Google Drive: {file.get('id')}")


class Linkedin(webdriver.Chrome):
    """
        A class for automating LinkedIn tasks using Selenium.

        Args:
            driver_path (str): Path to the Selenium Chrome driver.
            teardown (bool): Whether to quit the driver upon object deletion.
    """
    def __init__(self, driver_path=r"C:\selenium-chrome-driver", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Linkedin, self).__init__()
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            Ensures proper cleanup of resources when exiting the context.
        """
        if self.teardown:
            self.quit()

    def login_page(self):
        """
            Navigates to the LinkedIn login page.
        """
        if hasattr(const, 'BASE_URL'):
            self.get(const.BASE_URL)
        else:
            raise AttributeError("BASE_URL is not defined in the constants module.")

    def perform_login(self, username, password):
        """
            Logs into LinkedIn using the provided credentials.

            Args:
                username (str): LinkedIn username.
                password (str): LinkedIn password.
        """
        try:
            username_input = self.find_element(By.ID, "username")
            password_input = self.find_element(By.ID, "password")

            username_input.send_keys(username)
            password_input.send_keys(password)

            login_button = self.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.implicitly_wait(15)
            print("Login successful.")
        except Exception as e:
            print(f"Error during login: {e}")

    def navigate_to_profile(self, profile_url):
        """
            Navigates to a specific LinkedIn profile.

            Args:
                profile_url (str): URL of the LinkedIn profile.
        """
        if hasattr(const, 'PROFILE_URL'):
            self.get(const.PROFILE_URL)
            print(f"Redirected to profile: {const.PROFILE_URL}")
        else:
            raise AttributeError("PROFILE_URL is not defined in the constants module.")

    def wait(self, duration=10):
        """
            Pauses execution for a specified duration.

            Args:
                duration (int): Time to wait in seconds. Default is 10 seconds.
        """
        print(f"Waiting for {duration} seconds...")
        time.sleep(duration)

    def navigate_to_feed(self):
        """
            Navigates to the LinkedIn feed page and waits for it to load.
        """
        self.get(const.FEED_URL)

        # Wait for the feed to load
        WebDriverWait(self, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2")))

    def scrape_single_feed(self):
        """
            Scrapes and displays a single LinkedIn feed post.
        """
        post_element = WebDriverWait(self, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".update-components-text.relative.update-components-update-v2__commentary"))
        )

        # Extract text content
        post_content = post_element.text
        print("Post Content:")
        print(post_content)

    def scroll_and_collect_feeds(self, target_feed_count=100, max_scroll_attempts=100, scroll_step=3000):
        """
            Scrolls the LinkedIn feed and collects posts until a target count is reached.

            Args:
                target_feed_count (int): Number of feeds to collect.
                max_scroll_attempts (int): Maximum number of scroll attempts.
                scroll_step (int): Number of pixels to scroll per attempt.

            Returns:
                list: A list of collected feed content.
        """
        initialScroll = 0
        finalScroll = scroll_step
        feeds = []
        scroll_attempts = 0

        while len(feeds) < target_feed_count:
            # Scroll the page by the scroll_step amount
            self.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
            initialScroll = finalScroll
            finalScroll += scroll_step

            # Wait for new content to load
            print(f"Scrolled to position: {initialScroll}. Waiting for new content...")
            time.sleep(20)

            # Wait for new content to load (or time out if no new content appears)
            try:
                WebDriverWait(self, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2"))
                )
            except Exception as e:
                print("No new content loaded or timeout occurred.")
                break

            # Get the updated page source and parse with BeautifulSoup
            src = self.page_source
            soup = BeautifulSoup(src, 'lxml')

            # Extract feed items
            feed_items = soup.find_all('div', {'class': 'feed-shared-update-v2'})
            for item in feed_items:
                # Look for the main post content
                post_content = item.find('div', class_='update-components-text')  # Main feed content
                if post_content:
                    # Exclude social activity by removing "update-v2-social-activity" content
                    social_activity = post_content.find('div', class_='update-v2-social-activity')
                    if social_activity:
                        social_activity.extract()  # Remove the social activity content

                    # Extract the main post text
                    main_post_text = post_content.find('span', class_='break-words tvm-parent-container')
                    if main_post_text:
                        text_content = main_post_text.get_text(strip=True)

                        # Ensure the content is unique before adding
                        if text_content and text_content not in [feed['text'] for feed in feeds]:
                            feeds.append({'text': text_content})

            # Stop if the number of feeds has reached the target
            if len(feeds) >= target_feed_count:
                print(f"Collected {len(feeds)} feeds, stopping.")
                break

            # Stop if no new content appears after max scroll attempts
            scroll_attempts += 1
            if scroll_attempts >= max_scroll_attempts:
                print("Reached maximum scroll attempts.")
                break

        return feeds

    def extract_feed(self, soup):
        feeds = []

        # Find all feed containers
        feed_elements = soup.find_all('div', class_='update-components-text')

        for feed in feed_elements:
            # Extract the main feed text
            text_content = feed.find('span', class_='break-words tvm-parent-container')
            if text_content:
                feed_text = text_content.get_text(separator=' ').strip()

                # Check for and exclude "update-v2-social-activity" content
                social_activity = feed.find('div', class_='update-v2-social-activity')
                if social_activity:
                    social_activity_text = social_activity.get_text(separator=' ').strip()
                    feed_text = feed_text.replace(social_activity_text, '')  # Remove the social activity content

                # Append the cleaned feed text if it’s not empty
                if feed_text:
                    feeds.append(feed_text)

        return feeds

    def scroll_and_collect_feeds_txt(self, target_feed_count=10):
        feeds = []
        scroll_attempts = 0
        max_scroll_attempts = 20  # Failsafe to prevent infinite scrolling

        logging.info("Starting scroll and collect feeds process.")
        logging.info(f"Target feed count: {target_feed_count}. Max scroll attempts: {max_scroll_attempts}.")

        while len(feeds) < target_feed_count:
            # Measure page height and dynamically adjust scroll step
            page_height = self.execute_script("return document.body.scrollHeight")
            scroll_step = page_height // 3  # Adjust scroll step dynamically

            # Log current scroll position and number of feeds collected
            logging.info(
                f"Scroll attempt {scroll_attempts + 1}: Scrolling to position {scroll_step * scroll_attempts}.")
            logging.info(f"Feeds collected so far: {len(feeds)} / {target_feed_count}.")

            # Scroll and wait
            self.execute_script(f"window.scrollTo(0, {scroll_step * scroll_attempts})")
            time.sleep(20)  # Wait for new content to load

            # Extract feed data
            page_source = self.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            new_feeds = self.extract_feed(soup)  # Custom extraction logic

            # Log the number of new feeds found in the current scroll
            feeds_before = len(feeds)
            feeds.extend(feed for feed in new_feeds if feed not in feeds)  # Avoid duplicates
            feeds_after = len(feeds)
            new_feed_count = feeds_after - feeds_before
            logging.info(f"New feeds collected in this scroll: {new_feed_count}.")

            if len(feeds) >= target_feed_count:
                logging.info(f"Target feed count reached: {len(feeds)} feeds collected. Stopping scrolling.")
                break

            # Stop if no new content is loaded for multiple scrolls
            if new_feed_count == 0:
                logging.warning("No new content found. Stopping scrolling.")
                break

            scroll_attempts += 1
            if scroll_attempts >= max_scroll_attempts:
                logging.warning("Reached maximum scroll attempts. Stopping.")
                break

        # Log final result
        logging.info(f"Scrolling completed. Total feeds collected: {len(feeds)}.")

        # Save collected feeds to a separate file
        with open('feeds_output.txt', 'w', encoding='utf-8') as file:
            for index, feed in enumerate(feeds, start=1):
                file.write(f"Feed {index}: {feed}\n")

        logging.info("Feeds saved to 'feeds_output.txt'.")
        return feeds

    def scrap_company_posts(self, target_post_count=5, max_scroll_attempts=10):
        posts = []
        scroll_attempts = 0

        logging.info("Starting the company posts page scrolling and feed collection process.")
        logging.info(f"Target feed count: {target_post_count}. Max scroll attempts: {max_scroll_attempts}.")

        while len(posts) < target_post_count and scroll_attempts < max_scroll_attempts:
            logging.info(f"Scroll attempt {scroll_attempts + 1}: Current feed count is {len(posts)}.")

            # Parse the current page source
            page_source = self.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            # Find all post containers
            contents = soup.find_all('div', class_='feed-shared-update-v2')

            for post in contents:
                content = []

                # Extract main post text
                text_element = post.find('div', class_='update-components-text')
                if text_element:
                    content.append(text_element.get_text(strip=True))

                # Extract all links
                links = [a['href'] for a in post.find_all('a', href=True)]
                if links:
                    content.extend(links)

                # Extract hashtags
                hashtags = [word for word in " ".join(content).split() if word.startswith("#")]
                if hashtags:
                    content.extend(hashtags)

                # Combine all content
                combined_content = " ".join(content)

                # Avoid duplicates
                if combined_content not in posts:
                    posts.append(combined_content)
                    logging.info(f"New feed collected: {combined_content[:100]}...")

            scroll_attempts += 1

            if len(posts) >= target_post_count:
                logging.info(f"Target feed count reached: {len(posts)} feeds collected.")
                break

        logging.info("Feed collection completed.")

        # Save collected posts to a file
        output_file = 'company_posts.txt'
        with open(output_file, 'w', encoding='utf-8') as file:
            for index, post in enumerate(posts, start=1):
                file.write(f"Post {index}: {post}\n")

        logging.info(f"Posts saved to '{output_file}'.")
        print(f"Posts have been successfully saved to '{output_file}'.")
        return posts

    def company_posts_gdrive(self, target_post_count=5, max_scroll_attempts=15):
        posts = []
        scroll_attempts = 0

        logging.info("Starting the company posts page scrolling and feed collection process.")
        logging.info(f"Target feed count: {target_post_count}. Max scroll attempts: {max_scroll_attempts}.")

        while len(posts) < target_post_count and scroll_attempts < max_scroll_attempts:
            logging.info(f"Scroll attempt {scroll_attempts + 1}: Current feed count is {len(posts)}.")

            # Parse the current page source
            page_source = self.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            # Find all post containers
            contents = soup.find_all('div', class_='feed-shared-update-v2')

            for post in contents:
                content = []

                # Extract main post text
                text_element = post.find('div', class_='update-components-text')
                if text_element:
                    content.append(text_element.get_text(strip=True))

                # Extract all links
                links = [a['href'] for a in post.find_all('a', href=True)]
                if links:
                    content.extend(links)

                # Extract hashtags
                hashtags = [word for word in " ".join(content).split() if word.startswith("#")]
                if hashtags:
                    content.extend(hashtags)

                # Combine all content
                combined_content = " ".join(content)

                # Avoid duplicates
                if combined_content not in posts:
                    posts.append(combined_content)
                    logging.info(f"New feed collected: {combined_content[:100]}...")

            scroll_attempts += 1

            if len(posts) >= target_post_count:
                logging.info(f"Target feed count reached: {len(posts)} feeds collected.")
                break

        logging.info("Feed collection completed.")
        # Prepare content to upload
        posts_content = "\n".join([f"Post {index}: {post}" for index, post in enumerate(posts, start=1)])
        upload_to_drive("company_posts.txt", posts_content)

        return posts



