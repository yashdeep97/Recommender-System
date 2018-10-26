import numpy as np
from data_parser import *
from scipy import spatial
from operator import itemgetter
from array import *
from collaborative_baseline import *

neighbourhood_size = 2

def find_similarity_scores(movie1_ratinglist, movie2_ratinglist):
	movie1_ratinglist=np.asarray(movie1_ratinglist)
	movie2_ratinglist=np.asarray(movie2_ratinglist)
	N1 = np.count_nonzero(movie1_ratinglist)
	N2 = np.count_nonzero(movie2_ratinglist)

	mean1 = np.sum(movie1_ratinglist)*1.0/N1
	mean2 = np.sum(movie2_ratinglist)*1.0/N2

	maskedMean1 = (movie1_ratinglist>0)*mean1
	maskedMean2 = (movie2_ratinglist>0)*mean2

	centered_movie1_list = movie1_ratinglist - maskedMean1
	centered_movie2_list = movie2_ratinglist - maskedMean2

	score = 1 - spatial.distance.cosine(centered_movie1_list,centered_movie2_list)

	return score



def predict_rating(user_id, movie_id,rating_matrix,flag):
	movie_list_for_userid = rating_matrix[user_id,:]

	non_zero_ratings_indices_tuple = np.nonzero(movie_list_for_userid)
	non_zero_ratings_indices_array =  non_zero_ratings_indices_tuple[0]
	non_zero_ratings = movie_list_for_userid[non_zero_ratings_indices_tuple]
	non_zero_ratings = [value for value in non_zero_ratings]


	if(flag==1):
		local_baseline_list = []
		for index in non_zero_ratings_indices_array:
			local_baseline = find_baseline(user_id,index,rating_matrix)
			local_baseline_list.append(local_baseline)
		local_baseline_list = np.asarray(local_baseline_list)
		non_zero_ratings = np.subtract(non_zero_ratings,local_baseline_list)

	similarityScore_list=[]
	temp=[]

	for movie2_id in non_zero_ratings_indices_array:

		movie2_ratinglist = rating_matrix[:,movie2_id]
		movie1_ratinglist = rating_matrix[:,movie_id]
		score = find_similarity_scores(movie1_ratinglist, movie2_ratinglist)
		similarityScore_list.append(score)

	d = dict((key, value) for (key, value) in zip(similarityScore_list,non_zero_ratings))
	#print(d)
	#print(zip(similarityScore_list,non_zero_ratings))
	key = d.keys()
	key = sorted(key,reverse=True)
	values = [d[k] for k in key]
	
	
	top_similarityScore_list = [key[i] for i in range(1,neighbourhood_size+1)]
	neighbourhoodRating_list = [values[i] for i in range(1,neighbourhood_size+1)]

	#print(temp)
	predictedRating = weighted_avg(top_similarityScore_list, neighbourhoodRating_list)
	return predictedRating

def weighted_avg(top_similarityScore_list, neighbourhoodRating_list):
	top_similarityScore_list = np.asarray(top_similarityScore_list)
	neighbourhoodRating_list = np.asarray(neighbourhoodRating_list)
	numerator = np.sum(np.multiply(top_similarityScore_list, neighbourhoodRating_list))
	denominator =  np.sum(top_similarityScore_list)

	if(denominator!=0):
		weightedAvg = numerator*1.0/denominator

	return weightedAvg


if __name__=='__main__':
    filepath='ml-1m/'
    rating_matrix,validation_matrix = load_rating_matrix(filepath)
  
    predictedRating = predict_rating(0,1192,rating_matrix,0)
    print(predictedRating)
    #print(validation_matrix)
