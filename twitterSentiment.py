#http://www.cbsnews.com/8301-505123_162-41142308/the--happiest-and-saddest-cities-in-the-us/
import httplib
import re
import time

# We run NUM_TESTS amount of trials to determine how accurate the Gallup survey predictions were.
# It utilizes Arup's list of English words and sentiments.
# We compute an average sentiment for each area, and rank them overall.


#to gather the tweets, we had to feed it a distance from the lattitude and longitude of the area we wanted
MILES_FROM_LOCATION = 10.0

#how many tweets per region to get
NUM_TWEETS = 100

#number of trials, to get a more accurate measure of the happiness in the region
NUM_TESTS = 20

#wait time between each trial
WAIT_TIME = 5

#holds the lattitude and longitude for each city
geoDict = {}

#10 happiest cities (from most happy to least happy)
geoDict['BoulderCO'] = (40.0150, -105.2700)
geoDict['LincolnNE'] = (40.8000, -96.6667)
geoDict['FortCollinsCO'] = (40.5853, -105.0839)
geoDict['ProvoOremUT'] = (40.2969, -111.6939)
geoDict['HonoluluHI'] = (21.3069, -157.8583)
geoDict['MadisonWI'] = (43.0731, -89.4011)
geoDict['CedarRapidsIA'] = (42.0083, -91.6439)
geoDict['GainesvilleFL'] = (29.6514, -82.3250)
geoDict['BridgeportCT'] = (41.1669, -73.2053)
geoDict['WashingtonDC'] = (38.8900, -77.0300)

#10 saddest cities (from least sad to most sad)
geoDict['UticaNY'] = (43.1008, -75.2331)
geoDict['PrescottAZ'] = (34.5400, -112.4678)
geoDict['LakeHavasuCityAZ'] = (34.4839, -114.3217)
geoDict['SpartanburgSC'] = (34.9494, -81.9322)
geoDict['HickoryNC'] = (35.7331, -81.3414)
geoDict['FortSmithAR'] = (35.3858, -94.3983)
geoDict['ReddingCA'] = (40.5867, -122.3906)
geoDict['BeaumontTX'] = (30.0858, -94.1017)
geoDict['YoungstownOH'] = (41.0997, -80.6497)
geoDict['HuntingtonWV'] = (38.4192, -82.4453)

#stores the sentiments of the 2000+ English words that Finn defined
sentimentDict = {}
f = open('AFINN/AFINN-111.txt', 'r')
for line in f:
    sline = line.split()
    if (len(sline)) == 2: 
        sentimentDict[sline[0]] = int(sline[1])

f.close()


# queries the twitter search api to get twwets from given geo locations
def getTweets(geo_location):
    conn = httplib.HTTPConnection("search.twitter.com")
    #the most recent 100 English tweets from within 2 miles of a given location
    full_request = "/search.json?rpp="+str(NUM_TWEETS) \
                                      +"&geocode=" + str(geo_location[0])+"%2C"+str(geo_location[1]) \
                                      +"%2C"+str(MILES_FROM_LOCATION)+"mi&result_type=recent" 

    conn.request("GET", full_request)
    r = conn.getresponse()
    data =  r.read()
    match = re.search(r'(\"text\"):(\"[^\"]*\")', data, re.M|re.I)
    p = re.compile('(\"text\"):(\"[^\"]*\")')
    tweet_list = map(lambda x: x[1], p.findall(data))
    tweet_list = map(lambda x: x[1:-2], tweet_list)
    conn.close
    return tweet_list
    

#calculates the average sentiment for a string of text.
#returns None if no calculation is possible (no valid words in the text)
def avg_sentiment(text):
    text = text.split()
    if len(text)==0:
        raise Exception("need at least one word to analyze sentiment")
    total_sentiment = 0
    has_sentiment = False
    for word in text:
        word = re.sub('[^A-Za-z]+', '', word) #removes everything but letters
        
        if word in sentimentDict:
            has_sentiment = True
            total_sentiment += sentimentDict[word]

    if not has_sentiment:
        return None
    else:
        return float(total_sentiment)/len(text)


def average(values):
    """Computes the arithmetic mean of a list of numbers.

    >>> print average([20, 30, 70])
    40.0
    """
    return sum(values, 0.0) / len(values)



# gathers NUM_TWEETS each WAIT_TIME for a total of NUM_TESTS trials (for each of the regions)
def test_predictions(num_test=10, wait_time = 2):
    ranks = {}
    for city in geoDict:
        ranks[city] = []

    for n in range(num_test):
        print "run "+str(n+1)+" out of "+str(num_test)+", waiting..."
        time.sleep(wait_time*60)
        
        sent_dict = {}
        for key in geoDict:
            content_in_region = " ".join( getTweets(geoDict[key]) )
            avg_sent = avg_sentiment(content_in_region)
            if avg_sent ==None:
                raise Exception("no valid words in this region => no sentiment")
            sent_dict[key] = avg_sent

        for i,city in enumerate(sorted(sent_dict, key = sent_dict.get, reverse =True)):
            ranks[city].append(i)

    for city in ranks:
        ranks[city] = average(ranks[city] )

    return ranks




#prints the results in sorted order    
result = test_predictions(NUM_TESTS, WAIT_TIME)
sresult = sorted(result, key=result.get)
for city in sresult:
    print city+ ", average happiness: "+str(1+result[city])
