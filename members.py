import pickle
import csv
import xml.etree.ElementTree as ET
import tweepy as tw

class BTMember(object):
    def __init__(self, name, display_name, bio, followers_count, following_count, creation_date, location):
        self.name = name
        self.display_name = display_name
        self.bio = bio
        self.followers_count = followers_count
        self.following_count = following_count
        self.creation_date = creation_date
        self.location = location
        self.tweets = []

class BTMember2(object):
    def __init__(self, name, display_name, bio, followers_count, following_count, creation_date, location, gender,
                 party, birthyear, academic_title, religion):
        self.name = name
        self.display_name = display_name
        self.bio = bio
        self.followers_count = followers_count
        self.following_count = following_count
        self.creation_date = creation_date
        self.location = location
        self.gender = gender
        self.party = party
        self.birthyear = birthyear
        self.academic_title = academic_title
        self.religion = religion


def load_member_list(filename):
    with open(filename, "rb") as f:
        memberlist = pickle.load(f)
    f.close()
    return memberlist


def extract_member_list(filename, api):
    # create list of all members of the Twitter list
    screennames = get_list_screen_names(api, 912241909002833921)
    # create userdata and store persistently
    create_data(filename, screennames, api)


# create new memberlist
def create_data(filename, usernames, api):
    memberlist = []
    # add each member to the memberlist
    for name in usernames:
        memberlist.append(get_userinfo(name, api))
    with open(filename, "wb") as f:
        pickle.dump(memberlist, f)


def init_member_assgn(memberlist):
    with open('sa.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        tree = ET.parse('MDB_STAMMDATEN.XML')
        root = tree.getroot()
        for m1 in memberlist:
            nachnamen = m1.display_name.split()
            found = 0
            id = []
            for mdb in root.findall("MDB"):
                name = mdb.find("NAMEN/NAME")
                if name.find("NACHNAME").text in nachnamen:
                    found += 1
                    id.append(mdb.find("ID").text)
            if found == 0:
                writer.writerow([m1.name, "Unknown"])
            elif found == 1:
                writer.writerow([m1.name, id[0]])
            else:
                writer.writerow([m1.name, "conflict"])


def get_userinfo(name, api):
    # get all user data via a Tweepy API call
    user = api.get_user(screen_name=name)
    # create row data as a list
    user_info = BTMember(user.screen_name,
                 user.name,
                 user.description,
                 user.followers_count,
                 user.friends_count,
                 user.created_at,
                 user.location)
    # send that one row back
    return user_info


def findID(asgns, name):
    for asgn in asgns:
        if asgn[0] == name:
            return asgn[1]
    return "Not found"


def load_member_asgn(filename):
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=';')
        asgns = []
        for row in reader:
            asgns.append(row)
    return asgns


def update_member_metadata(memberlist, filename):
    asgns = load_member_asgn("twitter_to_member_complete.csv")
    newlist = []
    tree = ET.parse('MDB_STAMMDATEN.XML')
    root = tree.getroot()
    for m1 in memberlist:
        id = findID(asgns, m1.name)
        if id == "0":
            continue
        for mdb in root.findall("MDB"):
            if mdb.find("ID").text == id:
                bio = mdb.find("BIOGRAFISCHE_ANGABEN")
                gender = bio.find("GESCHLECHT").text
                party = bio.find("PARTEI_KURZ").text
                birthyear = bio.find("GEBURTSDATUM").text.split('.')[2]
                acad_title = mdb.find("NAMEN/NAME/AKAD_TITEL").text
                religion = bio.find("RELIGION").text
                member = BTMember2(m1.name, m1.display_name, m1.bio, m1.followers_count, m1.following_count,
                                  m1.creation_date, m1.location, gender, party, birthyear, acad_title, religion)
                newlist.append(member)
    with open(filename, "wb") as f:
        pickle.dump(newlist, f)


def get_list_screen_names(api, id, limit=10):
    members = []
    i=0
    # without this you only get the first 20 list members
    for page in tw.Cursor(api.list_members, list_id=id).items():
        i += 1
        if i > limit:
            break
        members.append(page)
    # create a list containing all usernames
    return [m.screen_name for m in members]


#method to assign twitter names to ID of the stammdaten xml (manual correction partially required)
def init_member_assgn(memberlist, xml_file='MDB_STAMMDATEN.XML', asgnfile="asgn.csv"):
    with open(asgnfile, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for m1 in memberlist:
            nachnamen = m1.display_name.split()
            found = 0
            id = []
            for mdb in root.findall("MDB"):
                name = mdb.find("NAMEN/NAME")
                if name.find("NACHNAME").text in nachnamen:
                    found += 1
                    id.append(mdb.find("ID").text)
            if found == 0:
                writer.writerow([m1.name, "Unknown"])
            elif found == 1:
                writer.writerow([m1.name, id[0]])
            else:
                writer.writerow([m1.name, "conflict"])

