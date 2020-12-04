import urllib.request
import urllib.error
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


class Scrapper:

    def __init__(self, base_url, questions_filename, chrome_driver, max_results=20):
        self.base_url = base_url
        self.web_driver = self.__create_web_driver(chrome_driver)
        self.questions = self.__read_query_file(questions_filename)
        self.query_urls = self.__create_query_urls(self.questions)
        self.max_results = max_results
        self.current_anchor = 1

    def __create_web_driver(self, chrome_driver):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(
            executable_path=chrome_driver, chrome_options=options)
        driver.maximize_window()

        return driver

    def __read_query_file(self, questions_filename):
        f = open(questions_filename, "r")
        lines = f.read().split("\n")

        return lines

    def __create_query_urls(self, questions):
        query_urls = []

        for question in questions:
            words = question.split(' ')
            cached_base_url = self.base_url

            for word in words:
                cached_base_url += word + '+'

            query_urls.append(cached_base_url)

        return query_urls

    def __generate_result_files(self, anchors):
        #current_anchor = 1

        for anchor in anchors:
            anchor_content = self.__driver_navigate_and_get_content(
                anchor['href'])
            soup_html_content = BeautifulSoup(anchor_content, 'html.parser')
            html_content = str.encode(soup_html_content.prettify())

            file_name = 'htmlFile' + str(self.current_anchor) + ".html"
            open_file = open(file_name, 'wb')
            open_file.write(html_content)
            open_file.close()

            self.current_anchor += 1

    def __driver_navigate_and_get_content(self, query_url):
        self.web_driver.get(query_url)
        results_page_content = self.web_driver.page_source.encode(
            'utf-8').strip()

        return results_page_content

    def __bs4_find_all_by_selector(self, content, selector, target_class):
        soup = BeautifulSoup(content, 'html.parser')
        match_results_titles = soup.find_all(selector, class_=target_class)

        return match_results_titles

    def start_parsing(self):

        print('Starting scrapper')
        print(self.query_urls)
        for query_url in self.query_urls:
            print('Starting parsing URL =', query_url, '\n')

            results_page_content = self.__driver_navigate_and_get_content(
                query_url)

            # match with all the titles of the results
            match_results = self.__bs4_find_all_by_selector(
                results_page_content, 'div', 'yuRUbf')
            print('Found ', len(match_results), ' results', '\n')

            # if we got less than 20 results, let's start getting the next pages
            while len(match_results) < 20:
                print('Getting the next page because we only got',
                      len(match_results),  "results.\n")

                query_url += "%3F&sxsrf=ALeKk01tCospBkxy4U9JkFz8FUaS2bDZew:1602565806114&ei=rjaFX_6xBoOvggePwKzYBw&start=10&sa=N&ved=2ahUKEwj-wOjs5rDsAhWDl-AKHQ8gC3sQ8tMDegQIHxAw&cshid=1602565979594464&biw=1536&bih=760&dpr=1.25"

                results_page_content = self.__driver_navigate_and_get_content(
                    query_url)

                next_page_match_results = self.__bs4_find_all_by_selector(
                    results_page_content, 'div', 'yuRUbf')

                for result in next_page_match_results:
                    match_results.append(result)

            print('We were able to get', len(
                match_results), 'thus, we will proceed.\n')

            # get the anchor of all the results
            anchors = []
            for i in range(0, self.max_results):
                anchors.append(match_results[i].find('a'))

            self.__generate_result_files(anchors)

            print(
                'Finished parsing the results for the question. Proceeded with the next one if available.\n')


def main():
    base_url = "https://www.google.com/search?sxsrf=ALeKk03eeKzuL_neAS01Osqly2UC8uFlOA%3A1602483071935&source=hp&ei=f_ODX9zqNrKl_QaLyo_4Cw&q="
    scrapper = Scrapper(base_url, 'Query.txt', 'chromedriver.exe')

    scrapper.start_parsing()


if __name__ == "__main__":
    main()
