import re, json, requests
from secrets import accessToken
import tweepy

def getStars(account):
    stars = []
    pages = int(re.search("[0-9]+$", requests.get("https://api.github.com/users/{}/starred?per_page=1".format(account), headers={"Authorization":accessToken,"Accept":"application/vnd.github.v3+json"}).links["last"]["url"]).group(0))
    for page in range(1, (pages)//100 + 2):
        data_json = json.loads(requests.get("https://api.github.com/users/{}/starred?per_page=100&page={}".format(account, str(page)), headers={"Authorization":accessToken,"Accept":"application/vnd.github.v3+json"}).text)
        for object in data_json:
            stars.append(object["full_name"])
    return stars

def getRepoNameByID(id):
    return 

def storeJSON(jsonStore):

    json_object = json.dumps(jsonStore, indent=4)

    with open("accounts.json", "w") as outfile:
        outfile.write(json_object)

def dbGen():

    with open('accounts.txt') as f:
        accounts = f.read().splitlines()

    jsonStore = {}

    for account in accounts:
        stars = getStars(account)
        jsonStore[account]=stars

    json_object = json.dumps(jsonStore, indent=4)

    with open("accounts.json", "w") as outfile:
        outfile.write(json_object)

def notifyTwitter(account, repo):
    pass

if __name__ == "__main__":
    try:
        with open("accounts.json", "r") as f:
            data_json = json.load(f)
    except FileNotFoundError:
        dbGen()

    with open('accounts.txt') as f:
        accounts = f.read().splitlines()
    
    if accounts != data_json.keys():
        newAccounts, deletedAccounts = [], []

        for account in accounts:
            if account not in data_json.keys():
                newAccounts.append(account)
        for account in data_json.keys():
            if account not in accounts:
                deletedAccounts.append(account)

    workingAccounts = accounts
    for account in (deletedAccounts + newAccounts):
        try:
            workingAccounts.remove(account)
        except ValueError:
            pass

    for account in workingAccounts:
        stars = getStars(account)
        for star in stars:
            print(account, data_json[account])
            if star not in data_json[account]:
                    notifyTwitter(account, star)
