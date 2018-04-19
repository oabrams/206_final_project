Orly Abrams
Final Project README

This project processes data taken from the Yelp Fusion API and generates specific outputs based on the user input. To begin, the user is prompted to enter in a term (related to food ie. "italian", "breakfast", "tacos") and a location. This will automatically generate the database with the received data (if it is not already in the database). The user will then be prompted to select if they want the first 10 restaurants sorted alphabetically or the top 10 restaurants based on ratings according to their original search parameters. Based on this selection they will have the option to generate either a map or a bar graph for the corresponding restaurants. Following, they will be prompted to select one of the listed restaurants for more information, or input "next" for the next 10 restaurants (if they input "next", they will then be prompted to select one of the 20 listed restaurants). At this point they will be prompted to input "tweets" if they want to see the top tweets about the selected restaurant. If they agree, the top tweets based on popularity will be displayed and then the user will be able to exit the program or begin again.

The required keys/secrets for the project include:
YELP API KEY
TWITTER API KEY
TWITTER API SECRET
TWITTER ACCESS TOKEN
TWITTER ACCESS TOKEN SECRET
MAPBOX ACCESS TOKEN (to create the map on plotly)

All of the keys listed above can be generated via the documentation on their given websites (YELP, TWITTER, PLOTLY) and used in a secrets.py file.

The major function involved in my code is make_yelp_request_using_db(). It handles the majority of the user input and determines through a sequence of if/else statements what select statements to create using the database to produce the proper output.
