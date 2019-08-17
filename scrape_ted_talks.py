from ted_talks.scraper import TEDScraper
from itertools import chain
import csv
import pandas as pd
import time
import json


languages = TEDScraper.get_languages()
ts = TEDScraper(lang="en")


# Get Talk URLs
all_talk_links = ts.get_all_talk_links()
all_talk_links = list(chain(*all_talk_links))
print('Total links scraped: ', len(all_talk_links))

# Save talk links to avoid re-scraping if there are issues later on
df = pd.DataFrame()
df['link'] = all_talk_links
df.to_csv('talk-links.csv')

# Read talk links in
df = pd.read_csv('talk-links.csv', index_col = 0)
links = list(df['link'])

# Scrape talk metadata and write to json
filename = 'talk_data.json'
with open(filename, "w") as f:
	for url in links:
		talk_data_dict = {}
		talk_data = ts.get_talk_info(url)
		talk_title = talk_data['talk_title']
		talk_data_dict[talk_title] = talk_data
		json.dump(talk_data_dict, f)
		f.write('\n')
		time.sleep(10)


