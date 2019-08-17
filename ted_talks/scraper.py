# -*- coding: utf-8 -*-
# Scraper code modifies https://github.com/shunk031/TedScraper/blob/master/ted_talks/scraper.py
import time
import re
import datetime
import json
import os

from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup


class TEDScraper:

    BASE_URL = "https://www.ted.com/talks"
    LANG_URL = "https://www.ted.com/participate/translate/our-languages"

    def __init__(self, lang="en"):
        """
        :param str url:
        :param str lang="en":
        """
        self.lang = lang
        self.target_url = TEDScraper.BASE_URL  # target url
        self.target_page_list_url = ""
        self.target_page_list = 0     # number of pages in the talk list
        self.target_page_num = 0      # number of talk pages
        self.target_talk = ""         # talk title
        self.all_page_list = 0
        self.all_talk_page_num = 0    # total number of talk pages
        self.start_time = 0
        self.end_time = 0
        self.all_processing_time = 0  # executtion time

    @staticmethod
    def make_soup(url):
        """
        Return BeautifulSoup instance from URL

        :param str url:
        :rtype: bs4.BeautifulSoup
        """
        try:
            with urlopen(url) as res:
                # print("[DEBUG] in make_soup() : Found: {}".format(url))
                html = res.read()

        except HTTPError as e:
            print("[DEBUG] in make_soup() : Raise HTTPError exception:")
            print("[DEBUG] URL: {} {}".format(url, e))
            return None

        return BeautifulSoup(html, "lxml")

    @staticmethod
    def get_languages():
        """
        Return available language, the symbol and number of talk

        :rtype list
        """
        soup = TEDScraper.make_soup(TEDScraper.LANG_URL)
        languages = soup.find_all('a')
        #print(languages[100].attrs['href'])
        lang_div = soup.find_all("div", {"class": "col"})

        lang_info = []
        for ld in lang_div:
            lang_type = ld.find("a").get_text()
            lang_symbol = ld.find("a").attrs['href'].replace(
                "/talks?language=", "")
            lang_talks = ld.get_text().strip().replace(lang_type, "").split()[0]
            lang_info.append(
                {"lang_type": lang_type, "lang_symbol": lang_symbol, "lang_talks": lang_talks})

        return lang_info

    def get_talk_title(self, ta_soup):
        title = ta_soup.select('meta[property$="og:title"]')[0].attrs['content']
        return title

    def get_talk_blurb(self, ta_soup):
        blurb = ta_soup.select('meta[name$="description"]')[0].attrs['content']
        return blurb

    def get_talk_speaker(self, ta_soup):
        speaker = ta_soup.select('meta[name$="author"]')[0].attrs['content']
        return speaker

    def get_talk_duration(self, ta_soup):
        duration = ta_soup.select('meta[property$="og:video:duration"]')[0].attrs['content']
        return duration

    def get_view_count(self, ta_soup):
        data_spec = str(ta_soup.select('script[data-spec]')[0])
        view_count_start = data_spec.find('"viewed_count":')
        view_count_end = data_spec[view_count_start:].find(',')
        view_count = data_spec[view_count_start+15:view_count_start + view_count_end] 
        return view_count

    def get_talk_topics(self, ta_soup):
        topics = []
        topics_tags = ta_soup.select('meta[property$="og:video:tag"]')
        for tag in topics_tags:
            topic = tag.attrs['content']
            topics.append(topic)
        return topics

    def get_talk_posted_date(self, ta_soup):
        posted_date = str(ta_soup.select('meta[itemprop$="uploadDate"]')[0].attrs['content'])[:10]
        return posted_date

    def get_talk_links(self, ta_soup):
        """
        Get the link to each talk from the current talk list,
        and return a list of the link

        :param bs4.BeautifulSoup soup:
        :rtype: List
        """
        talk_links = ta_soup.find_all("div", {"class": "talk-link"})
        talk_addresses = [self._find_talk_a(tl) for tl in talk_links]
        talk_addresses = [urljoin(TEDScraper.BASE_URL, ta)
                          for ta in talk_addresses]
        return talk_addresses

    def get_all_talk_links(self):
        """
        Get all the links to each talk

        :rtype: list
        """
        all_talk_links = []
        page_counter = 1
        target_url = TEDScraper.BASE_URL

        while True:
            soup = TEDScraper.make_soup(target_url)
            talk_links = self.get_talk_links(soup)
            print("Found ", len(talk_links), " links.")
            all_talk_links.append(talk_links)
            next_link = self.get_next_talk_list_a(soup)

            if next_link is None:
                break

            page_counter += 1
            print("[ FIND ] Now page: {}".format(page_counter))
            print("         {}".format(next_link))

            target_url = next_link
            time.sleep(5)

        return all_talk_links

    def get_next_talk_list_a(self, soup):
        """
        Get a link to the next talk list

        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        pagination_div = soup.find("div", {"class": "pagination"})
        next_link_a = pagination_div.find("a", {"class", "pagination__next"})

        if next_link_a is None:
            return None

        next_link = next_link_a.attrs['href']
        next_link = urljoin(TEDScraper.BASE_URL, next_link)

        # print("next page url: {}".format(next_link))

        return next_link

    def get_talk_transcript(self, ta_url):
        transcript = []
        transcript_url = ta_url + '/transcript?language=' + self.lang
        soup = self.make_soup(transcript_url)
        if soup is None:
            return []
        transcript_blocks = soup.select('p')
        for i, block in enumerate(transcript_blocks):
            if i == len(transcript_blocks) - 1:
                break
            text = block.contents[0]
            text = text.replace('\n', '')
            text = text.replace('\t', '')
            transcript.append(text)
        return transcript

    def get_talk_info(self, ta_url):
        self.target_url = ta_url
        ta_soup = TEDScraper.make_soup(ta_url)

        print("[ GET ] get scrape date ...")
        update_date = self._get_scrape_date()
        print(update_date)
        print("[ GET ] get talk posted date ...")
        talk_date = self.get_talk_posted_date(ta_soup)
        print(talk_date)
        print("[ GET ] get talk title ...")
        talk_title = self.get_talk_title(ta_soup)
        print(talk_title)
        talk_lang = self.lang
        print("[ GET ] get talk description ...")
        talk_blurb = self.get_talk_blurb(ta_soup)
        print(talk_blurb)
        print("[ GET ] get talk speaker ...")
        speaker = self.get_talk_speaker(ta_soup)
        print(speaker)
        print("[ GET ] get talk duration ...")
        duration = self.get_talk_duration(ta_soup)
        print(duration)
        print("[ GET ] get view count ...")
        view_count = self.get_view_count(ta_soup)
        print(view_count)
        print("[ GET ] get talk topics ...")
        topics = self.get_talk_topics(ta_soup)
        print(topics)
        print("[ GET ] get talk transcript ...")
        transcript = self.get_talk_transcript(ta_url)
        print(transcript)

        talk_info = {
            "posted_date": talk_date,
            "update_date": update_date,
            "talk_title": talk_title,
            "talk_link": ta_url,
            "talk_lang": talk_lang,
            "talk_topics": topics,
            "transcript": transcript,
            "view_count": view_count,
            "duration": duration,
            "speaker": speaker,
            "description": talk_blurb
        }
        return talk_info

    def _find_talk_a(self, soup):
        """
        Find the talk link address from talk page

        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        link = soup.find('a').attrs['href']
        return link

        #return soup.find(data-ga-context="talks").find("a").attrs['href']

    def _format_filename(self, s):
        """
        Convert spaces in filenames to underscores

        :param str s:
        :rtype: str
        """
        return s.replace(" ", "_")

    def _get_scrape_date(self):
        """
        Return the date on which scraping was performed

        :rtype: datetime.date
        """
        today = datetime.date.today()
        return today.strftime('%Y-%m-%d')