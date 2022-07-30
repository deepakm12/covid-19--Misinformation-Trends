import tweepy
import json
import math
import glob
import csv
import zipfile
import zlib
import argparse
import os
import os.path as osp
import pandas as pd
from tweepy import TweepError
from time import sleep


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputfile", help="Output file name with extension")
    parser.add_argument("-i", "--inputfile", help="Input file name with extension")
    parser.add_argument("-k", "--keyfile", help="Json api key file name")
    parser.add_argument("-c", "--idcolumn", help="tweet id column in the input file, string name")
    parser.add_argument("-m", "--mode", help="Enter e for extended mode ; else the program would consider default compatible mode")


    args = parser.parse_args()
    if args.inputfile is None or args.outputfile is None:
        parser.error("please add necessary arguments")
        
    if args.keyfile is None:
        parser.error("please add a keyfile argument")

    with open(args.keyfile) as f:
        keys = json.load(f)

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True, retry_delay=60*3, retry_count=5,retry_errors=set([401, 404, 500, 503]), wait_on_rate_limit_notify=True)
    
    if api.verify_credentials() == False: 
        print("Your twitter api credentials are invalid") 
        sys.exit()
    else: 
        print("Your twitter api credentials are valid.") 
    
    
    output_file = args.outputfile
    hydration_mode = args.mode

    output_file_noformat = output_file.split(".",maxsplit=1)[0]
    print(output_file)
    output_file = '{}'.format(output_file)
    output_file_short = '{}_short.json'.format(output_file_noformat)
    compression = zipfile.ZIP_DEFLATED    
    ids = []
    print(args.inputfile)
    if '.tsv' in args.inputfile:
        inputfile_data = pd.read_csv(args.inputfile, sep='\t')
        print('tab seperated file, using \\t delimiter')
    elif '.csv' in args.inputfile:
        inputfile_data = pd.read_csv(args.inputfile)
    elif '.txt' in args.inputfile:
        inputfile_data = pd.read_csv(args.inputfile, sep='\n', header=None, names= ['tweet_id'] )
        print(inputfile_data)
    
    if not isinstance(args.idcolumn, type(None)):
        inputfile_data = inputfile_data.set_index(args.idcolumn)
    else:
        inputfile_data = inputfile_data.set_index('tweet_id')
    
    ids = list(inputfile_data.index)
    print('total ids: {}'.format(len(ids)))

    start = 0
    end = 100
    limit = len(ids)
    i = int(math.ceil(float(limit) / 100))

    last_tweet = None
    if osp.isfile(args.outputfile) and osp.getsize(args.outputfile) > 0:
        with open(output_file, 'rb') as f:
            #may be a large file, seeking without iterating
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()
        last_tweet = json.loads(last_line)
        start = ids.index(last_tweet['id'])
        end = start+100
        i = int(math.ceil(float(limit-start) / 100))

    print('metadata collection complete')
    print('creating master json file')
    try:
        with open(output_file, 'a') as outfile:
            for go in range(i):
                print('currently getting {} - {}'.format(start, end))
                sleep(6)  # needed to prevent hitting API rate limit
                id_batch = ids[start:end]
                start += 100
                end += 100       
                backOffCounter = 1
                while True:
                    try:
                        if hydration_mode == "e":
                            tweets = api.statuses_lookup(id_batch,tweet_mode = "extended")
                        else:
                            tweets = api.statuses_lookup(id_batch)
                        break
                    except tweepy.TweepError as ex:
                        print('Caught the TweepError exception:\n %s' % ex)
                        sleep(30*backOffCounter)  # sleep a bit to see if connection Error is resolved before retrying
                        backOffCounter += 1  # increase backoff
                        continue
                for tweet in tweets:
                    json.dump(tweet._json, outfile)
                    outfile.write('\n')
    except:
        print('exception: continuing to zip the file')

    print('creating ziped master json file')
    zf = zipfile.ZipFile('{}.zip'.format(output_file_noformat), mode='w')
    zf.write(output_file, compress_type=compression)
    zf.close()


    def is_retweet(entry):
        return 'retweeted_status' in entry.keys()

    def get_source(entry):
        if '<' in entry["source"]:
            return entry["source"].split('>')[1].split('<')[0]
        else:
            return entry["source"]
    
    
    # print('creating minimized json master file')
    # with open(output_file_short, 'w') as outfile:
    #     with open(output_file) as json_data:
    #         for tweet in json_data:
    #             data = json.loads(tweet) 
    #             if hydration_mode == "e":
    #                 text = data["full_text"]
    #             else:
    #                 text = data["text"]
    #             country = "";
    #             country_code ="";
    #             lattitude = "";
    #             longitude = "";
    #             media_url = "";
    #             if data['place']:
    #               country = data['place']['country']
    #               # print(country)
    #               country_code = data['place']['country_code']
    #               # print(country_code)
    #             if data['coordinates']:
    #               lattitude = data['coordinates']['coordinates'][0]
    #               longitude = data['coordinates']['coordinates'][1]
    #             if data["entities"]:
    #               try:
    #                 data["entities"]["media"][0]["media_url"]
    #               except:
    #                 pass
    #               else:
    #                 media_url = data["entities"]["media"][0]["media_url"]
                
    #             t = {
    #                 "id_str": data["id_str"],
    #                 "created_at": data["created_at"],
    #                 "text": text,
    #                 "retweet_count": data["retweet_count"],
    #                 "favorite_count": data["favorite_count"],
    #                 "is_retweet": is_retweet(data),
    #                 "media": media_url,
    #                 "country_code": country_code,
    #                 "country": country,
    #                 "lattitude" : lattitude,
    #                 "longitude" : longitude,
    #                 "user_id" : data["user"]["id_str"],
    #                 "user_name" : data["user"]["name"],
    #                 "user_description" : data["user"]["description"],
    #                 "user_verification" : data["user"]["verified"],
    #                 "user_followers" : data["user"]["followers_count"],
    #               }

    #             json.dump(t, outfile)
    #             outfile.write('\n')
        
    f = csv.writer(open('/content/drive/MyDrive/Covid19/sep2021.csv'.format(output_file_noformat), 'a'))
    print('creating CSV version of minimized json master file') 
    fields = ["id_str", "text", "is_retweet", "created_at", "retweet_count","is_quote_status", "quoted_status_id_str","quoted_status","favorite_count", "media", "tweet_hashtag", "tweet_url","possibly_sensitive", "favorited", "retweeted", "language", "country_code", "country","place_url",
            "place_type",
            "place_name",
            "place_full_name",
            "polygon_longitude_1",
            "polygon_lattitude_1",
            "polygon_longitude_2",
            "polygon_lattitude_2",
            "polygon_longitude_3",
            "polygon_lattitude_3",
            "polygon_longitude_4",
            "polygon_lattitude_4","lattitude", "longitude", "user_id", "user_name", "screen_name", "user_location", "user_url", "user_description", "user_verification", "user_followers", "user_favorite_count(no. of tweets user liked)", "user_friend_count","user_list_count","user_statuses_count","user_created_at", "source", "truncated", "in_reply_to_status_id_str", "in_reply_to_user_id_str", "in_reply_to_screen_name"]                
    if os.path.getsize('/content/drive/MyDrive/Covid19/sep2021.csv') == 0:
      f.writerow(fields)       
    with open(output_file) as master_file:
        for tweet in master_file:
            data = json.loads(tweet)
            # print(data)
            country = "";
            country_code ="";
            place_url ="";
            place_type="";
            place_name="";
            place_full_name="";
            polygon_longitude_1="";
            polygon_lattitude_1="";
            polygon_longitude_2="";
            polygon_lattitude_2="";
            polygon_longitude_3="";
            polygon_lattitude_3="";
            polygon_longitude_4="";
            polygon_lattitude_4="";
            lattitude = "";
            longitude = "";
            media_url = [];
            tweet_hashtags=[]
            tweet_urls=""
            if data['place']:
              country = data['place']['country']
              # print(country)
              country_code = data['place']['country_code']
              # print(country_code)
              place_url = data['place']['url']
              place_type = data['place']['place_type']
              place_name = data['place']['name']
              place_full_name = data['place']['full_name']
              try:
                data['place']['bounding_box']['coordinates'][0][0][0];
                data['place']['bounding_box']['coordinates'][0][0][1];
                data['place']['bounding_box']['coordinates'][0][1][0];
                data['place']['bounding_box']['coordinates'][0][1][1];
                data['place']['bounding_box']['coordinates'][0][2][0];
                data['place']['bounding_box']['coordinates'][0][2][1];
                data['place']['bounding_box']['coordinates'][0][3][0];
                data['place']['bounding_box']['coordinates'][0][3][1];
              except:
                pass
              else:
                polygon_longitude_1=data['place']['bounding_box']['coordinates'][0][0][0];
                polygon_lattitude_1=data['place']['bounding_box']['coordinates'][0][0][1];
                polygon_longitude_2=data['place']['bounding_box']['coordinates'][0][1][0];
                polygon_lattitude_2=data['place']['bounding_box']['coordinates'][0][1][1];
                polygon_longitude_3=data['place']['bounding_box']['coordinates'][0][2][0];
                polygon_lattitude_3=data['place']['bounding_box']['coordinates'][0][2][1];
                polygon_longitude_4=data['place']['bounding_box']['coordinates'][0][3][0];
                polygon_lattitude_4=data['place']['bounding_box']['coordinates'][0][3][1];
            if data['coordinates']:
              lattitude = data['coordinates']['coordinates'][1]
              longitude = data['coordinates']['coordinates'][0]
            if data["entities"]:
              try:
                data["entities"]["media"][0]["media_url"]
              except:
                pass
              else:
                for i in data["entities"]["media"]:
                  media_url.append(i['media_url'])
            
            if data["entities"]:
              try:
                data["entities"]["hashtags"][0]["text"]
              except:
                pass
              else:
                for i in data["entities"]["hashtags"]:
                  tweet_hashtags.append(i["text"])

            if data["entities"]:
              try:
                data['entities']['urls'][0]['url'];
              except:
                pass
              else:
                tweet_urls = data['entities']['urls'][0]['url'];
            
            user_id = data["user"]["id_str"],
            user_name = data["user"]["name"],
            user_description = data["user"]["description"],
            user_verification = data["user"]["verified"],
            user_followers = data["user"]["followers_count"],
            quoted_status_id_str = "";
            quoted_status=""
            try:
              data['quoted_status_id_str']
            except:
              pass
            else:
              quoted_status_id_str=data['quoted_status_id_str'];
              
            try:
              data['quoted_status']
            except:
              pass
            else:
              quoted_status = data['quoted_status']
            possibly_sensitive = ""
            try:
              data['possibly_sensitive']
            except:
              pass
            else:
              possibly_sensitive = data['possibly_sensitive']
            f.writerow([data["id_str"], data["full_text"], is_retweet(data), data["created_at"], data["retweet_count"],data['is_quote_status'],quoted_status_id_str,quoted_status,  data['favorite_count'],media_url,tweet_hashtags,tweet_urls,possibly_sensitive,data['favorited'],data['retweeted'],data['lang'], country_code, country,place_url,place_type,
            place_name,
            place_full_name,
            polygon_longitude_1,
            polygon_lattitude_1,
            polygon_longitude_2,
            polygon_lattitude_2,
            polygon_longitude_3,
            polygon_lattitude_3,
            polygon_longitude_4,
            polygon_lattitude_4, lattitude, longitude, user_id, user_name, data["user"]["screen_name"],data["user"]["location"],data["user"]["url"], user_description, user_verification,user_followers,data["user"]["favourites_count"],data["user"]["friends_count"],data["user"]["listed_count"],data["user"]["statuses_count"],data["user"]["created_at"], data["source"], data["truncated"], data["in_reply_to_status_id_str"], data["in_reply_to_user_id_str"],data["in_reply_to_screen_name"], ])
    

# main invoked here    
main()
