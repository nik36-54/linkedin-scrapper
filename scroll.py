from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def scroll_and_collect_feeds(driver, target_feed_count=10, max_scroll_attempts=10, scroll_step=1000):
    """
    Scrolls through a webpage and collects unique feed items using Selenium and BeautifulSoup.

    Args:
        driver: Selenium WebDriver instance.
        target_feed_count (int): Number of unique feed items to collect.
        max_scroll_attempts (int): Maximum number of scrolls to attempt before stopping.
        scroll_step (int): Pixels to scroll on each attempt.

    Returns:
        list: A list of unique feed items collected from the page.
    """
    initialScroll = 0
    finalScroll = scroll_step
    feeds = []  # To store unique feed content
    scroll_attempts = 0  # To track the number of scrolls

    while len(feeds) < target_feed_count:
        # Scroll the page
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        initialScroll = finalScroll
        finalScroll += scroll_step

        # Use WebDriverWait to wait until new content appears
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'feed-shared-update-v2'))
            )
        except Exception as e:
            print("No new content loaded or timeout occurred.")
            break

        # Get updated page source and parse with BeautifulSoup
        src = driver.page_source
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


# Example usage
if __name__ == "__main__":
    # Initialize WebDriver
    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/feed/')

    # Ensure login is completed before proceeding
    input("Log in to LinkedIn and press Enter to continue...")

    # Collect feeds
    collected_feeds = scroll_and_collect_feeds(driver)

    # Print the collected feeds
    for i, feed in enumerate(collected_feeds, 1):
        print(f"Feed {i}: {feed}")

    # Close the driver
    driver.quit()
