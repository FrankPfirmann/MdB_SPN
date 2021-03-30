
from features import get_features, get_features_single, get_labels
from members import extract_member_list, load_member_list, BTMember2, BTMember, update_member_metadata
from tweets import load_tweet_list, BTTweet
from spn.algorithms.MPE import mpe
from spn.structure.Base import Context
from spn.algorithms.Sampling import sample_instances
from numpy.random.mtrand import RandomState
from spn.structure.leaves.parametric.Parametric import Categorical, Gaussian
from spn.io.Graphics import plot_spn
import matplotlib.pyplot as plt
from spn.algorithms.Inference import log_likelihood
from spn.algorithms.Marginalization import marginalize

import os
import tweepy as tw
import numpy as np


#private api keys loaded from file in order (consumer_key, consumer_secret, access, acces_secret)
def load_api(filename):
    f = open(filename, "r")
    apikeys = f.read().split("\n")
    auth = tw.OAuthHandler(apikeys[0], apikeys[1])
    auth.set_access_token(apikeys[2], apikeys[3])
    api = tw.API(auth, wait_on_rate_limit=True)
    return api


def build_spn(features):
    spn_classification = learn_classifier(features,
                                          Context(parametric_types=[Gaussian, Categorical, Categorical, Gaussian]).add_domains(features),
                                          learn_parametric, 2)
    return spn_classification

def mask_data(data, mask):
    ca = data.copy()
    for c in ca:
        c[mask] = np.nan
    return ca

def accuracy(pred, test, label):
    i = 0
    acc = 0
    while i < len(pred):
        if pred[i][label] == test[i][label]:
            acc += 1
        i += 1
    return acc/len(pred)

def cross_validate(data, n_folds, label=2):
    splitind = int(np.floor(len(data)/n_folds))
    splits = []
    i = 0
    while i < n_folds - 1:
        splits.append(data[splitind*i:splitind*(i+1)])
        i += 1
    splits.append(data[splitind * (n_folds - 1):])
    i = 0
    acc = 0
    while i < n_folds:
        train = splits.copy()
        test_data = train.pop(i)
        train = np.concatenate(train)
        masked = mask_data(test_data, label)
        spn = build_spn(train)
        prediction = mpe(spn, masked)
        acc += accuracy(prediction, test_data, label)
        i+=1
    return acc/n_folds


if __name__ == '__main__':
    from spn.algorithms.LearningWrappers import learn_parametric, learn_classifier
    #os.environ["PATH"] += os.pathsep + 'C:/Programme/Graphviz/bin/'
    #api = load_api("apikeys.txt")
    #extract_member_list("userinfotest.dat", api)
    memberlist = load_member_list("userinfo_plus.dat")
    # create_tweet_list(memberlist)
    tweet_list = load_tweet_list("bttweets.dat")
    # print(get_tweets_for_member(tweet_list, memberlist[0].name))
    features = ["birthyear", "gender", "party"]
    co_keys = ["corona", "covid", "pandem", "vaccin", "Corona", "Covid", "Pandem", "Vaccin", "impf", "Impf", "Maske",
               "mask", "Lockdown", "infiz", "Infektio"]
    fl_keys = ["Migrat", "Asyl", "Flücht", "Schlepper", "Seenot", "Einwanderung"
            , "asyl", "flücht", "schlepp", "seenot", "einwander"]
    is_keys = ["Islamis", "islamis", "Terror", "terror"]
    keywords = [co_keys]
    train_data = get_features(memberlist, features, tweet_list, keywords)
    spn = build_spn(train_data)
    print(cross_validate(train_data, 5, label=2))
    #print(sample_instances(spn, np.array([0, np.nan] * 50).reshape(-1, 2), RandomState(123)))
    # tweet_scraping(tweet_list, api)
    ex = np.array([1976., 1., 4., 0.3]).reshape(-1, 4)
    ex2 = np.array([4., 0.2]).reshape(-1, 2)
    ds_context = Context(parametric_types=[Gaussian, Categorical, Categorical, Gaussian]).add_domains(train_data)
    spn2 = learn_parametric(train_data, ds_context, min_instances_slice=20)

    spn_marg = marginalize(spn, [2, 3])
    ll = log_likelihood(spn, ex)
    ll2 = log_likelihood(spn2, ex)
    llm = log_likelihood(spn_marg, ex)
    print(ll, np.exp(ll))
    print(ll2, np.exp(ll2))
    print(llm, np.exp(llm))