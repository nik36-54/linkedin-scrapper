from scrapper.scrappers import Linkedin
import scrapper.constants as const
from bs4 import BeautifulSoup

USERNAME = const.USERNAME
PASSWORD = const.PASSWORD


def main():
    # Create an instance of the Profile class with explicit teardown control
    bot = Linkedin(teardown=False)  # Browser won't close automatically
    try:
        # Call the desired method (e.g., youtube)
        # bot.youtube()

        bot.login_page()
        bot.perform_login(username=USERNAME, password=PASSWORD)
        # bot.navigate_to_profile(const.PROFILE_URL)
        # # bot.wait(duration=15)
        #
        # # Keep the browser open
        # profile_data = {}
        # print(bot.title)
        #
        # page_source = bot.page_source
        # soup = BeautifulSoup(page_source, 'lxml')
        #
        # name = soup.find('h1', {'class': 'qYVRLPCjyOKnAgQzmXUbsDZgrcLSSOFihfKs inline t-24 v-align-middle break-words'})
        # name = name.get_text().strip()
        #
        # profile_data['name'] = name
        # profile_data['url'] = const.PROFILE_URL
        # headline = soup.find('div', {'class': 'text-body-medium break-words'})
        # headline = headline.get_text().strip()
        # profile_data['headline'] = headline
        #
        # location = soup.find('span', {'class': 'text-body-small inline t-black--light break-words'})
        # if location:
        #     location = location.get_text().strip()
        # profile_data['location'] = location
        #
        # about = soup.find('div', {'class': 'display-flex ph5 pv3'})
        # about = about.get_text().strip()
        # profile_data['about'] = about
        #
        # print(profile_data)

        bot.navigate_to_feed()
        bot.scrape_single_feed()

        input("Press Enter to quit...")
    finally:
        # Manually close the browser
        bot.quit()


if __name__ == "__main__":
    main()
