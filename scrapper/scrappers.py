import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scrapper.constants as const
import time


class Profile(webdriver.Chrome):
    def __init__(self, driver_path=r"C:\selenium-chrome-driver",
                 teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Profile, self).__init__()

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
        """
        Navigate to the LinkedIn homepage/feed.
        """
        self.get("https://www.linkedin.com/feed/")

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
