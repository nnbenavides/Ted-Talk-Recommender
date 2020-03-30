# Ted-Talk-Recommender
Web Scraper + Recommendation Engine for TED Talks. The recommendation system uses k-nearest neighbors (KNN) to identify similar talks to a provided one and recommends the most similar talks to the user. Because the data lacked user ratings for various talks, more complex collaborative filtering methods were not applicable.

## Required Packages/Software
* Python 3
* pandas
* numpy
* scikit-learn
* BeautifulSoup

## Running Code
Once the required packages have been installed, run the following commands to set up your Ted Talk recommendation system.

1. Scrape TED Talk metadata.
```
Run python scrape_ted_talks.py. This will take several hours.
```

2. Process the scraped metadata.

```
Run python process_data.py.
```

3. Run the recommendation system.
```
Run python recommend_talks.py and follow the instructions provided by the program.
```

## Author

* **Nicholas Benavides**

## Acknowledgments

* Thanks to [shunk031](https://github.com/shunk031/TedScraper/blob/master/ted_talks/scraper.py) for the original scraper code, which was modified and updated for this project.
