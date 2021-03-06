#Orly Abrams

import requests
import json
import secrets
from requests_oauthlib import OAuth1
import certifi
import urllib3
import sqlite3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *

DBNAME = 'yelp_twitter.db'
YELPJSON = 'yelp.json'
TWITTERJSON = 'twitter.json'
API_KEY=secrets.yelp_api_key
HEADERS={'Authorization': 'Bearer {}'.format(API_KEY)}


def init_db():
    try:
        conn=sqlite3.connect(DBNAME)
        cur=conn.cursor()
    except Error in e:
        print(e)
    statement= """
            DROP TABLE IF EXISTS 'yelp';
            """
    cur.execute(statement)
    conn.commit()
    yelp="""
        CREATE TABLE IF NOT EXISTS 'yelp' (
        'Id' Integer primary key AUTOINCREMENT,
        'RestaurantName' TEXT Not Null,
        'City' TEXT,
        'State' TEXT,
        'Address' TEXT,
        'zipcode' Integer,
        'rating' Integer,
        'term' TEXT NOT NULL,
        'location' TEXT NOT NULL,
        'lat' Integer,
        'lng' Integer)
        """
    cur.execute(yelp)
    conn.commit()
    statement= """
            DROP TABLE IF EXISTS 'tweets';
            """
    cur.execute(statement)
    conn.commit()

    tweets="""
        CREATE TABLE IF NOT EXISTS 'tweets' (
        'Id' Integer primary key AUTOINCREMENT,
        'RestaurantName' Text,
        'Tweettext' Text,
        'Username' Text,
        'retweets' Integer,
        'favorites' Integer,
        'popularity_score' Integer
        )
        """

    cur.execute(tweets)
    conn.commit()
    statement= """
            DROP TABLE IF EXISTS 'url_link';
            """
    cur.execute(statement)
    conn.commit()

    url_link="""
        CREATE TABLE IF NOT EXISTS 'url_link' (
        'Id' Integer primary key AUTOINCREMENT,
        'Term' TEXT Not Null,
        'Location' Text Not Null)
        """
    cur.execute(url_link)
    conn.commit()
    statement= """
            DROP TABLE IF EXISTS 'tweet_check';
            """
    cur.execute(statement)
    conn.commit()
    tweet_check="""
        CREATE Table if not exists 'tweet_check' (
        'Id' Integer primary key Autoincrement,
        'RestaurantName' Text Not Null
        )"""
    cur.execute(tweet_check)
    conn.commit()

    conn.close()


def params_unique_combination(baseurl, params):
    alphabetized_keys=sorted(params.keys())
    res=[]
    for x in alphabetized_keys:
        res.append('{}-{}'.format(x, params[x]))
    return baseurl + '_'.join(res)

#twitter code
try:
    cache_file1=open(TWITTERJSON, 'r')
    cache_contents1=cache_file1.read()
    CACHE_DICT1=json.loads(cache_contents1)
    cache_file1.close()
except:
    CACHE_DICT1={}

#yelp cache
try:
    cache_file=open(YELPJSON, 'r')
    cache_contents=cache_file.read()
    CACHE_DICT=json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICT={}

#twitter cache request
def make_twitter_request_using_cache(url, params={}, auth=None):
    unique_ident=params_unique_combination(url, params)

    if unique_ident in CACHE_DICT1:
        #print('Getting cached data...')
        return CACHE_DICT1[unique_ident]
    else:
        #print('Making a request for new data...')
        resp=requests.get(url, params, auth=auth)
        CACHE_DICT1[unique_ident]=resp.text
        dumped_json_cache=json.dumps(CACHE_DICT1)
        fw=open(TWITTERJSON, 'w')
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICT1[unique_ident]

#yelp cache request
def make_yelp_request_using_cache(url, params, headers=HEADERS, verify=False):
    unique_ident=params_unique_combination(url, params)
    if unique_ident in CACHE_DICT:
        return CACHE_DICT[unique_ident]
    else:
        resp=requests.request('GET', url, headers=HEADERS, params=params)
        CACHE_DICT[unique_ident]=resp.text
        dumped_json_cache=json.dumps(CACHE_DICT)
        fw=open(YELPJSON, 'w')
        fw.write(dumped_json_cache)
        yelpinfo=json.loads(CACHE_DICT[unique_ident])
        # return(yelpinfo)
        fw.close()
        return(CACHE_DICT[unique_ident])

#yelp db request
def make_yelp_request_using_db(url, params, term, location, verify):

    response=make_yelp_request_using_cache(url, params)
    newresponse=json.loads(response)
    try:
        conn=sqlite3.connect(DBNAME)
        cur=conn.cursor()
    except Error in e:
        print(e)
#keeps track of terms/locations that have been entered
    insert=(None, term, location)
    statement1='INSERT INTO "url_link" '
    statement1+='Values(?, ?, ?)'
    cur.execute(statement1, insert)
    conn.commit()


    statement= 'SELECT * FROM url_link '
    statement+= 'WHERE term="{}" and location="{}"'.format(term, location)
    x=cur.execute(statement)
#only inputs data into database that isn't already in there
    if len(x.fetchall())==1:
        for x in newresponse['businesses']:
            insert=(None, x['name'], x['location']['city'], x['location']['state'], x['location']['address1'], x['location']['zip_code'], x['rating'], term, location, x['coordinates']['latitude'], x['coordinates']['longitude'])
            statement="INSERT INTO 'yelp' "
            statement+= 'Values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

            cur.execute(statement, insert)
            conn.commit()
    statement='SELECT * FROM yelp '
    statement+='WHERE term="{}" and location="{}"'.format(term, location)
    b=cur.execute(statement)
    if len(b.fetchall())==0:
        print('No information found with your search information. Try again.')
        return('No information found with your search information. Try again.')

    newinput=input('Enter "alpha" for a list of 10 restaurants sorted alphabetically, "top" for a list of the top 10 rated restaurants according to your query, or "exit" to return to the initial input: ')
#selecting/sorting restuarants alphabetically
    if newinput=="alpha":
        statement='SELECT RestaurantName, rating, lat, lng '
        statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
        statement+='ORDER By RestaurantName LIMIT 10'
        cur.execute(statement)
        count= 1
        names=[]
        ratings=[]
        latitude=[]
        longitude=[]
        for x in cur:
            names.append(x[0])
            ratings.append(x[1])
            latitude.append(x[2])
            longitude.append(x[3])
            print(count, x[0], 'Rating:', x[1])
            count+=1
#plotly input
        barinput=input('Enter "bar" to see a bar graph or "map" to see a map of corresponding restaurants: ')
#plotly bar code
        if barinput=='bar':
            trace0 = go.Bar(
            x=names,
            y=ratings,
            text=(names, ratings),
            marker=dict(
            color='rgb(158,202,225)',
            line=dict(
            color='rgb(8,48,107)',
            width=1.5,
            )
            ),
            opacity=0.6
            )

            data = [trace0]
            layout = go.Layout(
            title='Top 10 Restaurants for {} in {} (alpha sorted)'.format(term, location),
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='text-hover-bar')
#plotly map code
        elif barinput=='map':
            data = Data([
            Scattermapbox(
            lat=latitude,
            lon=longitude,
            mode='markers',
            marker=Marker(
            size=9
            ),
            text=names,
            )
            ])
            layout = Layout(
            title='Map of Top 10 Restaurants for {} in {} (alpha)'.format(term, location),
            autosize=True,
            hovermode='closest',
            mapbox=dict(
            accesstoken=secrets.mapbox_access_token,
            bearing=0,
            center=dict(lat=latitude[0], lon=longitude[0]),

            pitch=0,
            zoom=10
            ),
            )

            fig = dict(data=data, layout=layout)
            py.plot(fig, filename='Multiple Mapbox')
        else:
            print('Invalid input')

        number_next_input=input('Enter a number that corresponds with a restaurant from the list for more information or enter "next" and receive a list of the next 10 restaurants from the database: ')
#print another 10 restaurants
        if number_next_input=='next':
            statement='SELECT RestaurantName, rating '
            statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
            statement+='ORDER BY RestaurantName LIMIT 20'
            nextinfo=cur.execute(statement)
            countagain=11
            list1=[]
            for x in nextinfo:
                list1.append(x)
            updatedlist=list1[10:]
            for x in updatedlist:
                print(countagain, x[0], 'Rating:', x[1])
                countagain+=1
            finalinput=input('Enter a number that corresponds with a restaurant from the list for more information or enter "new query" to search a new term and location: ')
#print info based on selected restaurant
            if finalinput.isdigit() and int(finalinput)<= 20:
                statement='SELECT RestaurantName, rating, Address, City, State, zipcode '
                statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
                statement+='ORDER BY RestaurantName LIMIT 20'
                nextinfo=cur.execute(statement)
                list1=[]
                for x in nextinfo:
                    list1.append(x)
                print(list1[int(finalinput)-1][0],'\n', 'Rating:', list1[int(finalinput)-1][1], '\n', list1[int(finalinput)-1][2], list1[int(finalinput)-1][3], list1[int(finalinput)-1][4])
                tweetinput=input('Enter "tweets" for a list of tweets about the selected restaurant: ')
#print tweets
                if tweetinput=='tweets':
                    tweets=get_tweets_for_restaurant_from_db(list1[int(finalinput)-1][0])
                else:
                    print('Invalid input')
                return(list1)
#print info based on selected restaurant
        elif number_next_input.isdigit() and int(number_next_input)<= 10:
            statement='SELECT RestaurantName, rating, Address, City, State, zipcode '
            statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
            statement+='Order by RestaurantName LIMIT 10'
            moreinfo=cur.execute(statement)
            listagain=[]
            for x in moreinfo:
                listagain.append(x)
            print(listagain[int(number_next_input)-1][0], '\n', 'Rating:', listagain[int(number_next_input)-1][1], '\n', listagain[int(number_next_input)-1][2], listagain[int(number_next_input)-1][3], listagain[int(number_next_input)-1][4], listagain[int(number_next_input)-1][5])
            tweetinput=input('Enter "tweets" for a list of tweets about the selected restaurant: ')
#print tweets
            if tweetinput=='tweets':
                get_tweets_for_restaurant_from_db(listagain[int(number_next_input)-1][0])
            else:
                print('Invalid input')
            return(listagain)

#selecting/sorting restuarants based on ratings
    elif newinput=='top':
        statement='SELECT RestaurantName, rating, lat, lng '
        statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
        statement+='Order By rating Desc Limit 10'
        cur.execute(statement)
        count=1
        names=[]
        ratings=[]
        latitude=[]
        longitude=[]
        for x in cur:
            names.append(x[0])
            ratings.append(x[1])
            latitude.append(x[2])
            longitude.append(x[3])
            print(count, x[0], 'Rating:', x[1])
            count+=1
#plotly input
        barinput=input('Enter "bar" to see a bar graph or "map" to see a map of corresponding restaurants: ')
#plotly bar code
        if barinput=='bar':
            trace0 = go.Bar(
            x=names,
            y=ratings,
            text=(names, ratings),
            marker=dict(
            color='rgb(158,202,225)',
            line=dict(
            color='rgb(8,48,107)',
            width=1.5,
            )
            ),
            opacity=0.6
            )

            data = [trace0]
            layout = go.Layout(
            title='Top 10 Restaurants for {} in {} (by ratings)'.format(term, location),
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='text-hover-bar')
#plotly map code
        elif barinput=='map':
            data = Data([
            Scattermapbox(
            lat=latitude,
            lon=longitude,
            mode='markers',
            marker=Marker(
            size=9
            ),
            text=names,
            )
            ])
            layout = Layout(
            title='Map of Top 10 Restaurants for {} in {} (by ratings)'.format(term, location),
            autosize=True,
            hovermode='closest',
            mapbox=dict(
            accesstoken=secrets.mapbox_access_token,
            bearing=0,
            center=dict(lat=latitude[0], lon=longitude[0]),
            pitch=0,
            zoom=10
            ),
            )

            fig = dict(data=data, layout=layout)
            py.plot(fig, filename='Multiple Mapbox')
        else:
            print('Invalid input')
        number_next_input=input('Enter a number that corresponds with a restaurant from the list for more information or enter "next" and receive a list of the next 10 restaurants from the database: ')
#print another 10 restaurants
        if number_next_input=='next':
            statement='SELECT RestaurantName, rating '
            statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
            statement+='Order By rating Desc Limit 20'
            nextinfo=cur.execute(statement)
            countagain=11
            list1=[]
            for x in nextinfo:
                list1.append(x)
            updatedlist=list1[10:]
            for x in updatedlist:
                print(countagain, x[0], 'Rating:', x[1])
                countagain+=1
            finalinput=input('Enter a number that corresponds with a restaurant from the list for more information: ')
#print info based on selected restaurant
            if finalinput.isdigit() and int(finalinput)<= 20:
                statement='SELECT RestaurantName, rating, Address, City, State, zipcode '
                statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
                statement+='ORDER BY rating Desc Limit 20'
                nextinfo=cur.execute(statement)
                list1=[]
                for x in nextinfo:
                    list1.append(x)
                print(list1[int(finalinput)-1][0], '\n', 'Rating:', list1[int(finalinput)-1][1], '\n', list1[int(finalinput)-1][2], list1[int(finalinput)-1][3], list1[int(finalinput)-1][4])
                tweetinput=input('Enter "tweets" for a list of tweets about the selected restaurant: ')
#print tweets
                if tweetinput=='tweets':
                    get_tweets_for_restaurant_from_db(list1[int(finalinput)-1][0])
                else:
                    print('Invalid input')
                return(list1)
        elif number_next_input.isdigit() and int(number_next_input)<= 10:
            statement='SELECT RestaurantName, rating, Address, City, State, zipcode '
            statement+='FROM yelp WHERE term="{}" and location="{}" '.format(term, location)
            statement+='Order by rating DESC Limit 10'
            moreinfo=cur.execute(statement)
            listagain=[]
            for x in moreinfo:
                listagain.append(x)
            print(listagain[int(number_next_input)-1][0], '\n', 'Rating:', listagain[int(number_next_input)-1][1], '\n', listagain[int(number_next_input)-1][2], listagain[int(number_next_input)-1][3], listagain[int(number_next_input)-1][4], listagain[int(number_next_input)-1][5])
            tweetinput=input('Enter "tweets" for a list of tweets about the selected restaurant: ')
            if tweetinput=='tweets':
                get_tweets_for_restaurant_from_db(listagain[int(number_next_input)-1][0])
            else:
                print('Invalid input')
            return(listagain)

    elif newinput=='exit':
        response='exit'
        print(response)

    else:
        print('Invalid input')


def get_data_from_yelp(term, location):
    url='https://api.yelp.com/v3/businesses/search'
    params={'term': term, 'location': location, 'limit': 50}
    response=make_yelp_request_using_db(url, params=params, term=term, location=location, verify=False)
    conn=sqlite3.connect(DBNAME)
    cur=conn.cursor()
    conn.close()
    return(response)

def get_tweets_for_restaurant_from_db(restaurant):
    twitter_key=secrets.twitter_client_key
    twitter_secret=secrets.twitter_client_secret
    access_token=secrets.twitter_access_token
    access_secret=secrets.twitter_access_token_secret

    baseurl='https://api.twitter.com/1.1/search/tweets.json'
    params={'q': restaurant, 'count': 100}
    auth=OAuth1(twitter_key, twitter_secret, access_token, access_secret)
    response=make_twitter_request_using_cache(baseurl, params=params, auth=auth)
    tweetdict=json.loads(response)

    try:
        conn=sqlite3.connect(DBNAME)
        cur=conn.cursor()
    except Error in e:
        print(e)
    tweet_list=[]
    tweetinfo=tweetdict['statuses']
#keep track of how many times each restaurant has been searched
    insert=(None, restaurant)
    statement1='INSERT INTO "tweet_check" '
    statement1+='Values(?, ?)'
    cur.execute(statement1, insert)
    conn.commit()
    statement= 'SELECT * FROM tweet_check '
    statement+= 'WHERE RestaurantName="{}"'.format(restaurant)
    x=cur.execute(statement)
#only inputs data into the database if its not already in there
    if len(x.fetchall())==1:

        for x in tweetinfo:
            insert=(None, restaurant, x['text'], x['user']['screen_name'], int(x['retweet_count']), int(x['user']['favourites_count']), int(x['retweet_count']*2)+int(x['user']['favourites_count']*3))
            statement="INSERT INTO 'tweets' "
            statement+= 'Values (?, ?, ?, ?, ?, ?, ?)'

            cur.execute(statement, insert)
            conn.commit()
    statement='SELECT username, tweettext, retweets, favorites, popularity_score FROM tweets '
    statement+='WHERE RestaurantName="{}" '.format(restaurant)
    statement+='Order By popularity_score DESC LIMIT 10'
    cur.execute(statement)
#tweet formatting
    for x in cur:
        print('@{}: {}'.format(x[0], x[1]))
        print('[retweeted {} times]'.format(x[2]))
        print('[favorited {} times]'.format(x[3]))
        print('[popularity {}]'.format(x[4]))
        print('-'*20)





def interactive_prompt():
    response = ''
    help_text= 'Enter any term related to food. This can include a type of cuisine, a type of food, or a specific meal. \nExamples: \nTacos, Encino\nBreakfast, New York\nItalian, Ann Arbor'
    while response != 'exit':
        response = input('Enter a term and location separated by a comma, enter "help" for more information, or enter "exit" to leave: ')
        if response == 'help':
            print(help_text)
            continue
        elif "," in response:
            searchterm=response.split(', ')
            get_data_from_yelp(searchterm[0], searchterm[1])
        elif response=='exit':
            break
        else:
            print('Invalid input, try again.')
    print('Bye!')
if __name__=="__main__":
# init_db()

    interactive_prompt()
