import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scrapper.constants as const
from bs4 import BeautifulSoup
import time


class Linkedin(webdriver.Chrome):
    def __init__(self, driver_path=r"C:\selenium-chrome-driver", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Linkedin, self).__init__()
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def login_page(self):
        if hasattr(const, 'BASE_URL'):
            self.get(const.BASE_URL)
        else:
            raise AttributeError("BASE_URL is not defined in the constants module.")

    def perform_login(self, username, password):
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
        if hasattr(const, 'PROFILE_URL'):
            self.get(const.PROFILE_URL)
            print(f"Redirected to profile: {const.PROFILE_URL}")
        else:
            raise AttributeError("PROFILE_URL is not defined in the constants module.")

    def wait(self, duration=10):
        print(f"Waiting for {duration} seconds...")
        time.sleep(duration)

    def navigate_to_feed(self):
        self.get(const.FEED_URL)

        # Wait for the feed to load
        WebDriverWait(self, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2")))

    def scrape_single_feed(self):
        post_element = WebDriverWait(self, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".update-components-text.relative.update-components-update-v2__commentary"))
        )

        # Extract text content
        post_content = post_element.text
        print("Post Content:")
        print(post_content)

    def scroll_and_collect_feeds(self, target_feed_count=100, max_scroll_attempts=100, scroll_step=3000):
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



