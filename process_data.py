# coding: utf-8

# Imports
import pandas as pd
import json
import numpy as np

# Read in data
data = []
with open('talk_data.json') as f:
    for line in f:
        data.append(json.loads(line))

# Extract data by column from JSONs
titles = []
upload_dates = []
links = []
topics = []
transcripts = []
views = []
durations = []
speakers = []
descriptions = []
unique_topics = set()

for talk_data in data:
    title = str([x for x in talk_data.keys()][0])
    titles.append(title)
    metadata = talk_data[title]
    upload_dates.append(str(metadata['posted_date']))
    links.append(str(metadata['talk_link']))
    topics.append(metadata['talk_topics'])
    for topic in metadata['talk_topics']:
        unique_topics.add(topic)
    transcript_raw = metadata['transcript']
    transcript = ''
    for section in transcript_raw:
        transcript += section
        transcript += ' '
    transcripts.append(str(transcript))
    views.append(int(metadata['view_count']))
    durations.append(float(metadata['duration'])/60)
    speakers.append(str(metadata['speaker']))
    descriptions.append(str(metadata['description']))

# Create and populate DataFrame with talk metadata
df = pd.DataFrame()
df['title'] = titles
df['upload_date'] = upload_dates
df['link'] = links
df['topics'] = topics
df['transcript'] = transcripts
df['views'] = views
df['log_views'] = np.log(1 + df['views'])
df['duration'] = durations
df['speaker'] = speakers
df['description'] = descriptions

# Save DataFrame to csv for later use
df.to_csv('og_dataset.csv')

# Explode topics column into a binary variable for each of the listed topics
topics_list = list(unique_topics)
topics_list.sort()
topics_matrix = np.zeros((df.shape[0], len(topics_list)))

for i, talk_topics in enumerate(topics):
    for topic in talk_topics:
        col_index = topics_list.index(topic)
        topics_matrix[i, col_index] = 1

for i in range(df.shape[0]):
    assert(len(topics[i]) == np.sum(topics_matrix[i,:]))

for i, topic in enumerate(topics_list):
    df[topic] = topics_matrix[:, i]

# Save DataFrame for later use
df.to_csv('dataset_exploded_topics.csv')


# Prepare and save DataFrame for recommendation task
df.drop(labels = ['topics', 'views', 'log_views', 'upload_date', 'transcript', 'speaker', 'description'], axis = 1, inplace = True)
df.to_csv('recommend_dataset.csv')



