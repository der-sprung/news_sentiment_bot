#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json


# In[2]:


# Twitter Timeline requests, from https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/master/User-Tweet-Timeline/user_tweets.py

def create_url(user_id):
    # Replace with user ID below
    # user_id = 51241574
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)


def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": ["entities,public_metrics"]}


def create_headers(bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main(user_id):
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAADhpQAEAAAAAI4xQiiDWIPCkx%2BF4uBRR9mBqhME%3DRATRNDcvyTxs0Up7LEOd21cD3ywrq39UnzZgWOS08Rc9L9PxGo'
    url = create_url(user_id)
    headers = create_headers(bearer_token)
    params = get_params()
    json_response = connect_to_endpoint(url, headers, params)
    # print(json.dumps(json_response, indent=1, sort_keys=True))
    product = json.dumps(json_response, indent=1, sort_keys=True)
    data = json.loads(product)
    # return data
    
    # create a new dictionary to store all extracted data
    primary_dict = dict()

    # create a for loop to extract important data from JSON dict
    for a in data['data']:
        if a['entities'].get('urls', 0) == 0:
            continue
        elif 'twitter.com' in a['entities'].get('urls')[0]['expanded_url']:
            continue
        else:
            twitter_id = a['id']
            primary_dict[twitter_id] = {
                'user_id' : user_id,
                'tweet_text' : a['text'],
                'likes' : a['public_metrics']['like_count'],
                'quotes' : a['public_metrics']['quote_count'],
                'replies' : a['public_metrics']['reply_count'],
                'retweets' : a['public_metrics']['retweet_count'],
                'url' : a['entities']['urls'][0]['expanded_url']
            }
    return primary_dict


if __name__ == "__main__":
    main(51241574)


# In[ ]:




