# Recommendation Engine using Instagram API.

## DISCLAIMER:

For this project, I have used an unofficial Instagram API from Lev Pasha through GitHub. Hence, the names of the functions provided are different from Facebook’s documentation of Instagram API but they are similar in functionality. I used this version of API as I found that Facebook’s version of API was not actively maintained on GitHub or any forums.
The following link redirects to the GitHub page of unofficial Instagram API. Please go through the relevant steps for installation of this API if required.

Link: https://github.com/LevPasha/Instagram-API-python

Moreover, before running the source code, please make sure all the libraries are installed on the local computer
and change the “login” and “password” to relevant username and password for logging purposes.

## DATA AND TOOLS:

The data used for this project is received from user’s Instagram profile. The recommendation engine is built on python 3.7.1 and uses libraries such as InstagramAPI, pandas, numpy, network and tqdm etc.

## EVALUATION METRICS:

The evaluation metrics I used for the first part takes the natural logarithm of each of the values number of likes, number of comments and the rank calculated. The product of these three values is found and then multiply with negative exponential value of when the photo was taken to get the present value factor for the photo.

The second part of this project uses a simpler evaluation metrics. We multiply the natural logarithms of number of likes and number of comments to provide the relative score to the user and display the recommended hashtags.

## PROGRAM FLOW:
• The first step is to enter the user credentials and login to user’s Instagram page
• Next I get the user’s personal information i.e.: unique id and full name displayed on Instagram.
• A list of all the people that the user follows is generated and I create a data frame out of it that serves as our dataset.
• I got the most recent posts like by the user, expand the network of followers to friends of friends and then see who among those also like the photo
• I create a graph from photos list, the user ID and followers ID to get the page rank using network library
• Now I move towards calculating the relative score of each photo and then provide the top 10 photos with their unqiue ID.
• The next part of this project provides us with a recommendation of hashtags from users activity. I capture the hashtags from the photos that the user has recently liked and make a data frame. Every time the hashtag appears on the caption, the number of likes and comments on that picture are added to the number of likes and comments for the hashtag
• The score for each hashtag is found out, sorted in descending order and a recommendation of top 10 hashtags is provided.

## RESULTS:
The results of this project will be in form of two .png files: 1) "hashtag.png" 2) "photo.png". Also, the urls on x-axis of "photo.png" will be shown on the terminal.

