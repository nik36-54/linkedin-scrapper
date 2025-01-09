import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scrapper.constants as const
from bs4 import BeautifulSoup


class Feed(webdriver.Chrome):
    def __init__(self, driver_path=r"C:\selenium-chrome-driver", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Feed, self).__init__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

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

    def scroll_and_collect_feeds(self, target_feed_count=10, max_scroll_attempts=10, scroll_step=1000):
        initialScroll = 0
        finalScroll = scroll_step
        feeds = []
        scroll_attempts = 0

        while len(feeds) < target_feed_count:
            self.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
            initialScroll = finalScroll
            finalScroll += scroll_step

            # Use WebDriverWait to wait until new content appears
            try:
                WebDriverWait(self, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".update-components-text.relative.update-components-update-v2__commentary"))
                )
            except Exception as e:
                print("No new content loaded or timeout occurred.")
                break

            # Get updated page source and parse with BeautifulSoup
            src = self.page_source
            soup = BeautifulSoup(src, 'lxml')

            # Extract feed items
            feed_items = soup.find_all('div', {'class': 'feed-shared-update-v2'})  # Update class name if necessary
            for item in feed_items:
                text = item.get_text(strip=True)
                if text not in feeds:  # Ensure uniqueness
                    feeds.append(text)

            # Stop if no new content appears after max scroll attempts
            scroll_attempts += 1
            if scroll_attempts > max_scroll_attempts:
                print("Reached maximum scroll attempts.")
                break

        return feeds




    def scroll_and_collect_feeds(self, target_feed_count=100, max_scroll_attempts=45, scroll_step=1000):
        initialScroll = 0
        finalScroll = scroll_step
        feeds = []
        scroll_attempts = 0

        while len(feeds) < target_feed_count:
            # Scroll the page by the scroll_step amount
            self.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
            initialScroll = finalScroll
            finalScroll += scroll_step

            # Wait for 10 seconds to allow content to load quickly
            print(f"Scrolled to position: {initialScroll}. Waiting for new content...")
            time.sleep(10)

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
                text_content = item.get_text(strip=True)
                if text_content and text_content not in [feed['text'] for feed in feeds]:  # Ensure uniqueness
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
