# !/usr/bin/python
# -*- encoding: utf-8 -*-
import argparse
import codecs
import json
import os
import tweepy
import re

import numpy as np
import pandas as pd

from twitterbot import *


def open_flat(args_dict, file):
    try:
        with codecs.open('{}/{}'.format(args_dict['directory'], file), 'r', 'utf-8') as f:
            if os.path.splitext(file)[-1] == '.txt':
                tmp = [user.strip() for user in f]
            elif os.path.splitext(file)[-1] == '.json':
                tmp = json.load(f)
            else:
                raise TypeError('Invalid extension; try again.')
            return tmp
    except IOError:
        raise IOError('Bad file name; try again.')


def pull_callouts(user, tweets, outdict, ttype=['mention', 'hashtag']):
    if ttype == 'mention':
        tmps = [x for subl in [re.findall(r'@(\w+)', tweet.text, re.UNICODE) for tweet in tweets] for
               x in subl]
        try:
            tmps.remove(user)
        except ValueError:
            pass
    else:
        tmps = [x for subl in [re.findall(r'#(\w+)', tweet.text, re.UNICODE) for tweet in tweets] for
               x in subl]

    if '{}_count'.format(ttype) not in locals().keys():
        counter = {}
    for tmp in tmps:
        counter[tmp] = counter.get(tmp, 0) + 1

    for k, v in counter.items():
        try:
            outdict[k] += v
        except KeyError:
            outdict[k] = v

    return outdict


def dump_json(args_dict, file, data):
    with open('{}/{}'.format(args_dict['directory'], file), 'w') as f:
        json.dump(data, f)


def run(args_dict):
    args_dict = update_args(args_dict)

    # set up authorization
    auth = tweepy.OAuthHandler(args_dict['keys'][0], args_dict['keys'][1])
    auth.set_access_token(args_dict['keys'][2], args_dict['keys'][3])
    api = tweepy.API(auth)

    # get users, phrases, mentions, and hashtags
    users = open_flat(args_dict, 'users.txt')
    users_activity = open_flat(args_dict, 'users_activity.json')
    terms = open_flat(args_dict, 'terms.txt')
    mention_tally = open_flat(args_dict, 'mentions.json')
    hashtag_tally = open_flat(args_dict, 'hashtags.json')

    # get tweet dataframe, if available
    try:
        tweets_df = pd.read_json('{}/tweets_{}.json'.format(args_dict['directory'],
                                                            args_dict['date']))
    except ValueError:
        tweets_df = pd.DataFrame({'user': None, 'retweeted': None, 'text': None},
                                 index=np.arange(1))

    # ensure all users have a `last tweet` starting value
    for user in users:
        if user not in users_activity.keys():
            users_activity[user] = 1

    # iterate over users and terms, liking various tweets for later review
    for user in users:
        # gather tweets
        tweets = api.user_timeline(user, since_id=users_activity[user])

        # favorite tweets with relevant keywords
        rel_tweets = []
        for tweet in tweets:
            for term in terms:
                try:
                    if term.lower() in tweet.text.lower():
                        rel_tweets.append(api.create_favorite(tweet.id))
                except tweepy.TweepError:
                    pass

        # collect users/hashtags mentioned
        mention_tally = pull_callouts(user, rel_tweets, mention_tally, ttype='mention')
        hashtag_tally = pull_callouts(user, rel_tweets, hashtag_tally, ttype='hashtag')

        # follow highly-relevant people
        for k, v in mention_tally.items():
            if v >= args_dict['popularity']:
                try:
                    api.create_friendship(id=k)
                except tweepy.TweepError:
                    pass

        # update latest tweet id value
        try:
            users_activity[user] = max([tweet.id for tweet in tweets])
        except ValueError:
            pass

        # write data frames
        tweets_df = pd.concat([
            tweets_df,
            pd.DataFrame({
                'user': [tweet.user.name for tweet in rel_tweets],
                'retweeted': [tweet.retweeted for tweet in rel_tweets],
                'text': [tweet.text for tweet in rel_tweets],
            })
        ]).reset_index(drop=True)

    # write updated dictionaries to file
    dump_json(args_dict, 'users_activity.json', users_activity)
    dump_json(args_dict, 'mentions.json', mention_tally)
    dump_json(args_dict, 'hashtags.json', hashtag_tally)

    tweets_df.dropna(axis=0, how='all', inplace=True)
    tweets_df.to_json('{}/tweets_{}.json'.format(args_dict['directory'], args_dict['date']))

    # write data frame to disk
    if args_dict['output']:
        mentions_df = pd.DataFrame.from_dict(mention_tally, orient='index').reset_index()
        mentions_df.rename(columns={'index': 'mention', 0: 'count'}, inplace=True)

        hashtags_df = pd.DataFrame.from_dict(hashtag_tally, orient='index').reset_index()
        hashtags_df.rename(columns={'index': 'hashtag', 0: 'count'}, inplace=True)

        writer = pd.ExcelWriter('{}/tweets_{}.xlsx'
                                .format(args_dict['directory'], args_dict['date']),
                                engine='xlsxwriter')
        tweets_df.to_excel(writer, index=False, encoding='utf-8',
                           sheet_name='tweets_{}'.format(args_dict['date']))
        mentions_df.to_excel(writer, index=False, encoding='utf-8',
                             sheet_name='mentions_{}'.format(args_dict['date']))
        hashtags_df.to_excel(writer, index=False, encoding='utf-8',
                             sheet_name='hashtags_{}'.format(args_dict['date']))
        writer.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Twitter bot to favorite, follow, '
                                     'and collect interesting tweets.')
    parser.add_argument('-k', '--keys', required=True, nargs=4, help='Names of '
                        'environmental variables to pull for Twitter OAuth')
    parser.add_argument('-p', '--popularity', type=int, default=30, help='The '
                        'number of mentions needed before following a handle.')
    parser.add_argument('-o', '--output', action='store_true', help='Indicates whether '
                        'results should be written to disk.')
    parser.add_argument('-d', '--directory', required=False, help='Working directory; '
                        'can be specified, otherwise defaults to config.')

    args_dict = vars(parser.parse_args())

    run(args_dict)
