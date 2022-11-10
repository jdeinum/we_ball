import sqlite3
import requests
import json


def getPage(url):
    r = requests.get(url, headers={'User-Agent': 'Custom'})
    
    if r.status_code != 200:
        # will deal with this better later
        raise Exception("Request unsuccessful.")
        return

    return r


# if team is None, we want overall team stats from a particular year
# otherwise we want individual stats from a particular team for a particular
# year
def craftUrl(team, year):
    if team:
        url = "https://canadawest.org/teamstats.aspx?path=mvball&year={}&school={}".format(year, team)
    else:
        url = "https://canadawest.org/stats.aspx?path=mvball&year={}".format(year)
    
    return url


def extractTeamStats(response):
    stats = json.loads(response.json())
    print(stats)


def extractIndividualStats(response):
    stats = response.json()
    print(stats)


def main():
    teams = [
        "alberta",
        "bc",
        "twu",
        "tru",
        "manitoba",
        "mountroyal",
        "winnipeg",
        "brandon",
        "fraservalley",
        "saskatchewan",
        "macewan",
        "calgary",
        "ubco",
    ]

    url = craftUrl(teams[0], 2022)
    page = getPage(url)
    extractIndividualStats(page)



if __name__ == "__main__":
    main()
