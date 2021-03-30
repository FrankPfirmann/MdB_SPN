import pickle
import tweepy as tw

class BTTweet(object):
    def __init__(self, text, id, retweets, favorites, created_at):
        self.text = text
        self.id = id
        self.retweets = retweets
        self.favorites = favorites
        self.created_at = created_at


def load_tweet_list(filename):
    with open(filename, "rb") as f:
        tweet_list = pickle.load(f)
    f.close()
    return tweet_list


def tweet_scraping(tweet_list, api, filename):
    for t in tweet_list:
        try:
            a = api.user_timeline(t[0], count=100, max_id=t[1], exclude_replies=True, include_rts=False)
            for tweet in a:
                t[2].append(BTTweet(tweet.text, tweet.id, tweet.retweet_count, tweet.favorite_count, tweet.created_at))
            if len(t[2]) != 0:
                t[1] = min(t[1], t[2][-1].id)
            for p in t[2]:
                print(p.text)
            with open(filename, "wb") as f:
                pickle.dump(tweet_list, f)
        except tw.error.TweepError:
            pass


def create_tweet_list(memberlist, filename="bttweets.dat"):
    tweet_list = []
    for member in memberlist:
        #store tweet_list as tuple of name, id of latest tweet and the tweets themselves
        tweet_list.append([member.name, 1373895723381587970, []])
    with open(filename, "wb") as f:
        pickle.dump(tweet_list, f)


