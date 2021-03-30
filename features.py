import sys

import numpy as np
import matplotlib.pyplot as plt
gender_dict = {"männlich": 0, "weiblich": 1}
inv_gender = {v: k for k, v in gender_dict.items()}
party_dict = { "CDU": 0, "CSU": 1,"SPD": 2, "FDP": 3, "AfD": 4, "BÜNDNIS 90/DIE GRÜNEN": 5,
                  "DIE GRÜNEN/BÜNDNIS 90": 5, "DIE LINKE.": 6, "Plos": 4}
inv_party = {v: k for k, v in party_dict.items()}
inv_party[4] = "AfD"
acad_dict = {None: 0, "Dr": 1, "Pr": 2}
inv_acad= {v: k for k, v in acad_dict.items()}

def get_tweets_for_member(tweet_list, name):
    for te in tweet_list:
        if te[0] == name:
            return te[2]


def get_features(memberlist, req_features, tweet_list, keywords):
    features = np.zeros((len(memberlist), len(req_features) + len(keywords)))
    i = 0
    while i < len(memberlist):
        j = 0
        tweets = get_tweets_for_member(tweet_list, memberlist[i].name)
        for req_f in req_features:
            if "gender" == req_f:
                features[i][j] = gender_dict[memberlist[i].gender]
            elif "party" == req_f:
                features[i][j] = party_dict[memberlist[i].party]
            elif "academic_title" == req_f:
                if memberlist[i].academic_title is None:
                    features[i][j] = 0
                else:
                    features[i][j] = acad_dict[memberlist[i].academic_title[0:2]]
            elif "birthyear" == req_f:
                features[i][j] = float(memberlist[i].birthyear)
            else:
                sys.exit("Requested feature " + req_f + " not supported!")
            j += 1
        for key_list in keywords:
            count = 0
            for t in tweets:
                check = any(item in t.text for item in key_list)
                if check:
                    count +=1
            features[i][j] = count/(len(tweets)+1)
            j += 1
        i += 1
    return features


def get_features_single(x, req_features):
    features = np.ones(len(req_features))
    j = 0
    for req_f in req_features:
        if "gender" == req_f:
            features[j] = gender_dict[x[j]]
        elif "party" == req_f:
            features[j] = party_dict[x[j]]
        elif "academic_title" == req_f:
            if x[j] is None:
                features[j] = 0
            else:
                features[j] = acad_dict[x[j][0:2]]
        elif "birthyear" == req_f:
            features[j] = float(x[j])
        else:
            sys.exit("Requested feature " + req_f + " not supported!")
        j += 1
    return features


def get_labels(features, req_features):
    labels = []
    i = 0
    while i < len(features):
        j = 0
        y = []
        for req_f in req_features:
            if "gender" == req_f:
                y.append(inv_gender[features[i][j]])
            elif "party" == req_f:
                y.append(inv_party[features[i][j]])
            elif "academic_title" == req_f:
                y.append(inv_acad[features[i][j]])
            elif "birthyear" == req_f:
                y.append(str(features[i][j]))
            else:
                sys.exit("Requested feature " + req_f + " not supported!")
            j += 1
        labels.append(y)
        i += 1
    return labels