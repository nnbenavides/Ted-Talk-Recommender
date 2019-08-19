# Imports
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors as nn

'''
Fits a k-nearest-neighbors model to identify the 10 most similar talks to the target.
	Arguments:
		data - pandas DataFrame of numeric values, each talk represented by a row
		target - list of feature values corresponding to the target talk
	Output:
		list of indices corresponding to the 10 nearest neighbors of target
'''
def get_recommendations(data, target):
	print('------------------ Processing ------------------')
	knn_model = nn(n_neighbors = 10, metric = 'cosine')
	knn_model.fit(data)
	k_neighbors = knn_model.kneighbors(np.asarray(target).reshape(1, -1))
	return k_neighbors[1][0]

'''
Gets a TED talk from the user to find recommendations for. The user can input either the title of the talk 
or a link to the talk. The method continues to ask for input until a recognized input is provided by the user.
	Arguments:
		titles - list of TED talk titles
		links - list of TED talk links
	Output:
		index of the talk provided by the user, corresponding to a row in the pandas DataFrame
'''
def get_input(titles, links):
	while(True):
		user_talk = input("Share the name of a Ted Talk you like or a link to the video, and I'll recommend some other TED Talks for you.\n")
		user_talk = user_talk.lower()
		if user_talk in titles:
			talk_index = titles.index(user_talk)
			print("Thank you. Let me go find you some other talks.")
			return talk_index
		elif ".com" in user_talk:
			language_ind = user_talk.find('language=')
			if language_ind != -1:
				user_talk = user_talk[:language_ind - 1]
		if user_talk in links:
			talk_index = links.index(user_talk)
			print("Thank you. Let me go find you some other talks.")
			return talk_index
		print("I don't seem to have any data on that talk. Can you try another one?")

'''
Displays 5 recommended TED talks for the talk provided by the user. The relevant information for each talk is
the speaker, title of the talk, and a link so the user can easily view any of the recommendations
	Arguments:
		df - pandas DataFrame containing TED talk metadata; each talk is represented by a row
		rec_indices - list of indices for recommended talks, corresponding to rows in the DataFrame
		target_index - index of the TED talk provided by the user
		max_recs - maximum number of recommendations to display to the user
	Output:
		None, but the information for each recommended talk is printed to the console
'''
def display_recs(df, rec_indices, target_index, max_recs = 5):
	print('Here are your recommendations:\n')
	recs_displayed = 0
	for rec_ind in rec_indices:
		if rec_ind == target_index:
			continue
		if recs_displayed >= max_recs:
			return
		
		rec_vector = df.iloc[rec_ind]
		speaker = str(rec_vector['speaker'])
		if speaker == 'nan':
			speaker = 'Unknown'
		title = str(rec_vector['title']).title()
		link = str(rec_vector['link'])
		recs_displayed += 1

		print('Recommendation ' + str(recs_displayed) + ':')
		print(speaker + ': ' + title)
		print('Link:', link)
		print('\n')

'''
Receives a TED talk that the user likes, finds the 10 nearest neighbors using a K-nearest-neighbors
model from scikit-learn, and displays the speaker, title, and link for the top 5 recommended talks 
to the user.
'''
def main():
	talk_data = pd.read_csv('recommend_dataset.csv', index_col = 0)
	numeric_data = talk_data.drop(labels = ['title', 'link', 'speaker'], axis = 1)
	titles = list(talk_data['title'])
	links = list(talk_data['link'])
	user_talk_index = get_input(titles, links)
	user_talk_vector = numeric_data.iloc[user_talk_index]
	rec_indices = get_recommendations(numeric_data, user_talk_vector)
	display_recs(talk_data, rec_indices, user_talk_index)

if __name__ == "__main__":
	main()