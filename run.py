from scrapper.scrappers import Linkedin
import scrapper.constants as const
from bs4 import BeautifulSoup
import time
from supabase_src import store_company_posts
# from supabase_config import supabase
from datetime import datetime
USERNAME = const.USERNAME
PASSWORD = const.PASSWORD


def main():
    bot = Linkedin(teardown=False)
    try:
        # Call the desired method (e.g., youtube)
        # bot.youtube()

        bot.login_page()
        bot.perform_login(username=USERNAME, password=PASSWORD)
        # bot.get(const.FEED_URL)
        bot.get(const.POST_URL)
        time.sleep(5)
        # page_source = bot.page_source
        # print(page_source)

        # soup = BeautifulSoup(page_source, 'html.parser')

        # # List to store the feed data (text, links, hashtags)
        # feeds_list = []
        #
        # # Extract all feed containers (the divs that hold each feed)
        # feeds = soup.find_all('div', class_='update-components-text')
        #
        # # Iterate through the first 10 feeds and extract relevant content
        # for i, feed in enumerate(feeds[:10]):  # Limit to first 10 feeds
        #     # Extract the main text content (using the span with the class 'break-words tvm-parent-container')
        #     text_content = feed.find('span', class_='break-words tvm-parent-container')
        #     if text_content:
        #         text_content = text_content.get_text(separator=' ').strip()
        #     else:
        #         text_content = ""  # If no text is found, set it to an empty string
        #
        #     # # Extract links (href attributes within <a> tags)
        #     # links = [a['href'] for a in feed.find_all('a', href=True)]
        #     #
        #     # # Extract hashtags (only if text_content is not empty)
        #     # hashtags = []
        #     # if text_content:  # Check if there's any text content to extract hashtags from
        #     #     hashtags = [word for word in text_content.split() if word.startswith('#')]
        #     #
        #     # # Clean the hashtags by removing the word "hashtag" and keeping only the '#' symbol
        #     # hashtags = [hashtag.replace("hashtag", "#") for hashtag in hashtags]
        #
        #     # Store the extracted data as a dictionary
        #     feed_data = {
        #         'text': text_content,
        #         # 'links': links,
        #         # 'hashtags': hashtags
        #     }
        #
        #     # Append to the list
        #     feeds_list.append(feed_data)
        #
        # # Print the extracted feed data (text, links, hashtags)
        # for index, data in enumerate(feeds_list, start=1):
        #     print(f"Feed {index}:")
        #     print(f"Text: {data['text']}")
        #     # print(f"Links: {data['links']}")
        #     # print(f"Hashtags: {data['hashtags']}")
        #     print('-' * 40)

        # bot.navigate_to_feed()
        # bot.scrape_single_feed()

        # collected_feeds = bot.scroll_and_collect_feeds(target_feed_count=10, max_scroll_attempts=10, scroll_step=1000)
        # for i, feed in enumerate(collected_feeds, 1):
        #     print(f"Feed {i}: {feed}")

        # Scroll and collect the first 10 feeds
        # feeds = bot.scroll_and_collect_feeds(target_feed_count=10, max_scroll_attempts=9, scroll_step=1000)

        # Print the extracted feed data (text content)
        # for index, data in enumerate(feeds, start=1):
        #     print(f"Feed {index}:")
        #     print(f"Text: {data['text']}")
        #     print('-' * 40)
        # feeds = bot.scroll_and_collect_feeds_txt(target_feed_count=50)
        posts = bot.scrap_company_posts(target_post_count=5, max_scroll_attempts=10)
        # posts = bot.company_posts_gdrive(target_post_count=5, max_scroll_attempts=15)
        with open("company_posts.txt", "r", encoding="utf-8") as file:
            document_content = file.read()
        post_db = store_company_posts(datetime.now(), document_content)
        if post_db:
            print("Uploaded data:", post_db)
        else:
            print("Failed to upload data.")
        input("Press Enter to quit...")
    finally:
        bot.quit()


if __name__ == "__main__":
    main()
