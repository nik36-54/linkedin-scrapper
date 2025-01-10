import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scrapper.constants as const
from bs4 import BeautifulSoup
import logging
import time

# Setup logging
logging.basicConfig(
    filename='scrappers.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Feed(webdriver.Chrome):
    def __init__(self, driver_path=r"C:\selenium-chrome-driver", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Feed, self).__init__()
        self.maximize_window()

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

    def scroll_and_collect_feeds(self, target_feed_count=10):
        """
        Scrolls through LinkedIn feed to collect post content.

        Parameters:
        target_feed_count (int): The desired number of feeds to collect.

        Returns:
        list: A list of extracted feeds.
        """
        feeds = []
        scroll_attempts = 0
        max_scroll_attempts = 9  # Failsafe to prevent infinite scrolling

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
            new_feeds = self.extract_feeds(soup)  # Custom extraction logic

            # Log the number of new feeds found in the current scroll
            feeds_before = len(feeds)
            feeds.extend(feed for feed in new_feeds if feed not in feeds)  # Avoid duplicates
            feeds_after = len(feeds)
            new_feed_count = feeds_after - feeds_before
            logging.info(f"New feeds collected in this scroll: {new_feed_count}.")

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
