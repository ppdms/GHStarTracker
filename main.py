import re, json, requests
from turtle import update
from .secrets import *
from time import sleep
import tweepy

def getStars(account):
    stars = []
    pages = int(re.search("[0-9]+$", requests.get("https://api.github.com/users/{}/starred?per_page=1".format(account), headers={"Authorization":accessToken,"Accept":"application/vnd.github.v3+json"}).links["last"]["url"]).group(0))
    for page in range(1, (pages)//100 + 2):
        data_json = json.loads(requests.get("https://api.github.com/users/{}/starred?per_page=100&page={}".format(account, str(page)), headers={"Authorization":accessToken,"Accept":"application/vnd.github.v3+json"}).text)
        for object in data_json:
            stars.append(object["full_name"])
    return stars

def storeJSON(jsonStore):

    json_object = json.dumps(jsonStore, indent=4)

    with open("stars.json", "w") as outfile:
        outfile.write(json_object)

def dbGen():

    with open('accounts.json') as f:
        accounts = [account for account in json.load(f)]

    jsonStore = {}

    for account in accounts:
        stars = getStars(account)
        jsonStore[account]=stars

    json_object = json.dumps(jsonStore, indent=4)

    storeJSON(json_object)

def detectNameChange(repoName):
    if requests.get("https://github.com/{}".format(repoName)).status_code == 302:
        return requests.get("https://github.com/{}".format(repoName)).url[19:]
    else:
        return repoName

def notifyTwitter(account, repo):
    client.create_tweet(text="{} has just starred {}!".format(names[account], repo))


def main():
    client = tweepy.Client(
        consumer_key=twitterAPIKey,
        consumer_secret=twitterAPIKeySecret,
        access_token=twitterAccessToken,
        access_token_secret=twitterAccessTokenSecret
    )

    try:
        with open("stars.json", "r") as f:
            data_json = json.load(f)
    except FileNotFoundError:
        dbGen()

    with open('accounts.json') as f:
        names = json.load(f)
        accounts = list(names.keys())
    
    if accounts != list(data_json.keys()):
        newAccounts, deletedAccounts = [], []

        for account in accounts:
            if account not in list(data_json.keys()):
                newAccounts.append(account)
        for account in list(data_json.keys()):
            if account not in accounts:
                deletedAccounts.append(account)

    workingAccounts = accounts
    for account in (deletedAccounts + newAccounts):
        try:
            workingAccounts.remove(account)
        except ValueError:
            pass
    
    updatedStars = {}

    for account in workingAccounts:
        stars = getStars(account)
        updatedStars[account] = stars
        for star in stars:
            if star not in data_json[account]:
                Stars = stars
                Stars.remove(star)
                for Star in Stars:
                    if detectNameChange(Star) == star:
                        continue
                print(account,star)
                #notifyTwitter(account, star)
    
    storeJSON(updatedStars)

if __name__ == "__main__":
    while True:
        main()
        sleep(3600)