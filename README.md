# Twitterbot
## Introduction
When I use Twitter, I often wish it was a just a little easier to see things that are of interest to me. Don't get me wrong, Twitter does a pretty good job of surfacing relevant and interesting things in my feed, but I wanted a little more control. Enter `twitterbot` (which is a lame name). Given a list of keywords (terms, phrases, or hashtags) and a list of user handles, it can find tweets from those users that contains the keywords one is interested in. It then favorites those tweets for one to look at on their Twitter homepage at a later time. It will also start following users that get enough mentions in relevant tweets.

## Background Information
There are a number of `.example` files in the directory here. Modify these as needed and remove the `.example` from the name before running the program.

You will also need a Twitter application with API keys and access tokens. Visit the [Twitter development page](http://dev.twitter.com) to get signed up and create an application. Once you have those keys, you will want to add those to your `.profile`, `.bashrc`, or whatever other file you use for your environmental variables. The name you give them will be used when you run the program.

The `.json` files in the directory (`mentions.json`, `hashtags.json`, and `users_activity.json`) are all important; do not delete these. They will be called (and written to) while using the program.

## Usage
To run the program, the following will suffice:
```
$ python bot.py -k TWITTER_KEY TWITTER_SECRET TWITTER_ACCESS TWITTER_ACCESS_SECRET
```

where the `TWITTER_KEY`, `TWITTER_SECRET`, `TWITTER_ACCESS`, and `TWITTER_ACCESS_SECRET` are all defined as environmental variables.

Using some of the optional goodies:
```
$ python bot.py -k TWITTER_KEY TWITTER_SECRET TWITTER_ACCESS TWITTER_ACCESS_SECRET -p 10 -o
```

This will set the threshold needed to start following someone at 10 mentions (default is 30) and the `-o` flag will request the program write out summary statistics (relevant tweets, mention counts, and hashtag counts) to an Excel workbook.

Regardless of the `-o` flag, each run will write a JSON file of relevant tweets to the working directory with a timestamp, called `tweets_YYYY-MM-DD.json`.

## Conclusion
If there are questions, contact me at matthew.a.hoover at gmail.com or open an issue on the repo.
