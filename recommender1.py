from InstagramAPI import InstagramAPI
import pandas as pd
from tqdm import tqdm
import time 
import numpy as np
import datetime 
import networkx
import re
import matplotlib.pyplot as plt

def plot (xaxis, yaxis, xlabel, ylabel, title, filename):
   x = np.arange(len(xaxis))
   plt.bar(x, yaxis, color=['crimson', 'cadetblue', 'cyan', 'magenta', 'coral', 'darkcyan', 'blueviolet', 'burlywood', 'darkgreen', 'chocolate'])
   plt.xlabel(xlabel)
   plt.ylabel(ylabel)
   plt.xticks(x, xaxis, fontsize=5, rotation=20)
   plt.title(title)
   plt.savefig(filename, dpi=500)
   plt.clf()
   plt.cla()
   plt.close()

def hashtags(str):
   return re.findall(r'#(\w+)', str)

api = InstagramAPI("login", "password") # change login and password to relevant usernmae and password
time.sleep(2)
api.login()

# Get username info for your account
api.getSelfUsernameInfo()
user_info = api.LastJson
uid = user_info['user']['pk']
myname = user_info['user']['full_name']

# Get the list of people following
api.getSelfUsersFollowing()
following_info = api.LastJson
follow_list = []
for user in tqdm(following_info['users']):
   uid_followed = user['pk']
   fullname_followed = user['full_name']
   follow_list.append((uid, uid_followed, myname, fullname_followed))
   
   api.getUserFollowings(uid_followed)
   relationship = api.LastJson
   if relationship.get('users') is not None:
      for User in relationship['users']:
         follow_list.append((uid_followed, User['pk'], fullname_followed, User['full_name']))
   
   time.sleep(0.5)

# Create a dataframe of follow_list
follow_list_frame = pd.DataFrame(follow_list, columns=['Source ID', 'Destination ID', 'Source Name', 'Destination Name'])

# Grab the most recent images from everyone (friends of friends) and rate them by how how relevant they are to the user.
# Grab the number of likes, comments and time the photo was taken
# Get the photos that you've liked to be entered in dataset used for recommendations
api.getLikedMedia()
liked_photos = api.LastJson
users_liked = [item['user'] for item in liked_photos['items']]

# Build up a network from these liked photos
user_liked_relationship = []
for user in tqdm(users_liked):
   uid_followed = user['pk']
   fullname_followed = user['full_name']
   user_liked_relationship.append((uid, uid_followed, myname, fullname_followed))

   # Get the followings list for each followed user and append them
   api.getUserFollowings(uid_followed)
   user_secondary = api.LastJson
   for User in user_secondary['users']:
      user_liked_relationship.append((uid_followed, User['pk'], fullname_followed, User['full_name']))

   time.sleep(1)

# Create a dataframe from the liked photos list
liked_list_frame = pd.DataFrame(user_liked_relationship, columns=['Source ID', 'Destination ID', 'Source Name', 'Destination Nmae'])

#Change end index for a larger dataframe keeping in mind what's the maximum
liked_list_frame = liked_list_frame.iloc[0:500]
unique_user_id = np.unique(liked_list_frame[['Source ID', 'Destination ID']].values.reshape(1, -1))

# Create a graph to calculate relative score of pages
graph = networkx.from_pandas_edgelist(liked_list_frame, 'Source ID', 'Destination ID')
personalised_rank = dict(zip(graph.nodes(), [0] * len(graph.nodes())))
personalised_rank[uid] = 1
pg_rank = networkx.pagerank(graph, personalization=personalised_rank)

# Creating dataset for providing recommendations
total_urls = []
timetaken = []
number_of_likes = []
number_of_comments = []
pagerank = []
users = []

for id in tqdm(unique_user_id):
   api.getUserFeed(id)
   feed = api.LastJson

   if 'items' in feed.keys():
      for item in feed['items']:

         #Capture only images for this project
         if 'image_versions2' in item.keys():
            url = item['image_versions2']['candidates'][1]['url']
            taken_at = item['taken_at']

            # Check how many likes are provided with except block if 0 likes
            try:
               like = item['like_count']
            except KeyError:
               like = 0

            # Check the number of comments and provide an except block if zero comments are there
            try:
               comment = item['comment_count']
            except KeyError:
               comment = 0

            rank = pg_rank[item['user']['pk']]
            user = item['user']['full_name']

            # dont count oneself when appending
            if user != myname:
               total_urls.append(url)
               timetaken.append(taken_at)
               number_of_likes.append(like)
               number_of_comments.append(comment)
               pagerank.append(rank)
               users.append(user)
      
      time.sleep(1)

# With the dataset availbale, create a dataframe from it
relative_score = pd.DataFrame(
   {
      'URLS': total_urls,
      'Time taken': timetaken,
      'Number of likes': number_of_likes,
      'Number of comments': number_of_comments,
      'Rank': pagerank,
      'Users': users,
   }
)

# Specify from what time time data is required. This is optional
# I am doing it to simplify the data.
last_time = int((datetime.datetime.now() - datetime.timedelta(weeks=1)).strftime('%s'))
relative_score = relative_score[relative_score['Time taken'] > last_time]

# Find out the score
# A simple way to do it is just multiply to multiply parameters # of comments, # of likes, rank, weight and a negative exponent value of time to find its score in present terms when photo was taken
# This simple score is very big and therefore we can standardize it by taking the natural logarithm
relative_score['Total Score'] = np.log(relative_score['Number of likes']) * np.log(relative_score['Number of comments']) * relative_score['Rank'] * np.exp((relative_score['Time taken'] - int(time.time())) / 1e5)

# Get the top number of highest rated posts. I user 10 of these posts
relative_score = relative_score.sort_values(by='Total Score', ascending=False)
recommended_url = relative_score['URLS'].tolist()
recommended_post = relative_score['Total Score'].tolist()

recommended_url = recommended_url[0:10]
recommended_post = recommended_post[0:10]

# providing urls keys so that they can be easily shown on the bar chart
indexes = ['URL1', 'URL2', 'URL3', 'URL4', 'URL5', 'URL6', 'URL7', 'URL8', 'URL9', 'URL10']
url_dict = {}

for i in range(10):
   url_dict[indexes[i]] = recommended_url[i]

#prinitng dictionary
print("\n\nURLS of Top 10 recommended pictures")
print('-------------------------------------')
for key, values in url_dict.items():
   print(key + '-->' + values + "\n")
print("\n\n")

#Visualization
plot(indexes, recommended_post, "URL Address", "Scores", "Relative scores of Top 10 recommended photos", "photo.png")

# Find the images according to the hashtags a user mostly likes
# Very important when considering the tastes of travel enthusiasts 
total_hashtags = []

# Get recently liked photos
api.getLikedMedia()
liked_photos = api.LastJson
for item in tqdm(liked_photos['items']):
   if item['caption'] is not None:
      hashtag = hashtags(item['caption']['text'])
      [total_hashtags.append(i.lower()) for i in hashtag]
   
   time.sleep(1)

recommended_hashtags = pd.Series(total_hashtags).value_counts()[:10]
top_hashtag_images = {}

for hashtag in recommended_hashtags.index:
   api.getHashtagFeed(hashtag)
   feed = api.LastJson
   top_hashtag_images[hashtag] = feed 
   time.sleep(1)

total_urls = []
number_of_likes = []
tags = []
number_of_comments = []

for hashtag in top_hashtag_images.keys():
   images = top_hashtag_images[hashtag]['items']
   for item in images:
      if 'image_versions2' in item:
         total_urls.append(item['image_versions2']['candidates'][1]['url'])
            # Check how many likes are provided with except block if 0 likes
         try:
            number_of_likes.append(item['like_count'])
         except KeyError:
            number_of_likes.append(0)

            # Check the number of comments and provide an except block if zero comments are there
         try:
            number_of_comments.append(item['comment_count'])
         except KeyError:
            number_of_comments.append(0)

         tags.append(hashtag)
   
   time.sleep(1)

tag_frame = pd.DataFrame(
   {
      'Tags': tags,
      'Total urls': total_urls,
      'Number of likes': number_of_likes,
      'Number of comments': number_of_comments
   }
)

tag_frame['Score'] = np.log(tag_frame['Number of likes'] * tag_frame['Number of comments'])
popular_tags = tag_frame.groupby('Tags').max()
popular_tags = popular_tags.sort_values('Score', ascending=False)

count = 0
list_name = []
for a, b in popular_tags.iterrows():
   count = count + 1
   list_url = b.tolist()
   list_name.append(a)
   list_url = list_url[:len(list_url) - 3]
   print(f"Recommendation number {count} is: " + a)
   print(list_url)
   print("\n\n")
   
# Visualization
list_score = popular_tags['Score'].tolist()
plot(list_name, list_score, "Hashtag Names", "Scores", "Relative scores of Top 10 recommended hashtags", "hashtag.png")



