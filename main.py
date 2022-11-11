import sqlite3
import requests
import json
import sqlite3 as sq3
from bs4 import BeautifulSoup, Doctype
import numpy as np


def initDB(db_name):
    db = sq3.connect(db_name)
    curs = db.cursor()

    statements = [
        "PRAGMA foreign_keys = ON;",
        "CREATE TABLE IF NOT EXISTS team(name TEXT, year TEXT, stat TEXT, value REAL);",
        "CREATE TABLE IF NOT EXISTS individual(name TEXT, year TEXT, team TEXT, stat TEXT, value REAL, FOREIGN KEY(team) REFERENCES team(name));",
    ]

    for x in statements:
        curs.execute(x)

    curs.close()
    return db


def insertTeamStats(db, stats):
    """
    stats is a list of data tuples, i.e:
    [
    ("ab", 2000, "points", 100),
    ...
    ]

    It's expected that all strings are lowercase and underscores replace any spaces
    """

    curs = db.curs()
    curs.execute("INSERT INTO team VALUES (?, ?, ?, ?)", stats)
    curs.close()


def insertIndividualStats(db, stats):
    """
    stats is a list of data tuples, i.e:
    [
    ("jacob_deinum", 2022, "blocks", 100),
    ...
    ]
    It's expected that all strings are lowercase and underscores replace any spaces
    """
    curs = db.cursor()
    curs.execute("INSERT INTO team VALUES (?, ?, ?, ?)", stats)
    curs.close()


def getPage(url):
    r = requests.get(url, headers={"User-Agent": "Custom"})

    if r.status_code != 200:
        # will deal with this better later
        raise Exception("Request unsuccessful.")

    return r


def craftUrl(team, year):
    """
    if team is None, we want overall team stats from a particular year
    otherwise we want individual stats from a particular team for a particular
    year
    """
    if team:
        url = "https://canadawest.org/teamstats.aspx?path=mvball&year={}&school={}".format(
            year, team
        )
    else:
        url = "https://canadawest.org/stats.aspx?path=mvball&year={}".format(year)

    return url


def using_clump(a):
    return [a[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(a))]


def extractTeamStats(response):
    """
    Given an http response, returns a list of data tuples following the team
    database format, i.e:
    [
        ("ab", "blocks", 100),
        ...
    ]
    """
    bs = BeautifulSoup(response.text, "html.parser")
    labels = bs.find_all("caption")
    labels = [x.string for x in labels][0:13]
    tables = bs.find_all("table")[0:13]

    result_set = []

    school_lables = [
        "Alberta",
        "Trinity Western",
        "UBC",
        "Thompson Rivers",
        "Manitoba",
        "Mount Royal",
        "Winnipeg",
        "Brandon",
        "UFV",
        "Saskatchewan",
        "MacEwan",
        "Calgary",
        "UBC Okanagan",
    ]

    for table in tables:

        # get the values
        values = table.find_all("td")
        values = [x.string for x in values]
        values = np.array(values, dtype=np.float64)

        # get the first row
        x = table.findAll("th")
        x = np.array([a.string for a in x])

        # seperate the first row into headers and teams
        index = None
        for i in range(len(x)):
            if x[i] in school_lables:
                index = i
                break

        headers = x[2:index]
        teams = x[index:]

        # now we split values in the array
        split = using_clump(values)

        for i in range(len(teams)):
            for j in range(len(headers)):
                team_name = teams[i].lower().replace(" ", "_")
                stat_name = labels[i].lower().replace(" ", "_")
                stat_header = headers[j].lower().replace(" ", "_")
                value = float(split[i][j])

                result_set.append([team_name, stat_name, stat_header, value])




def extractIndividualStats(response):
    """
    Given an http response, returns a list of data tuples following the individual
    database format, i.e:
    [
        ("ab", "blocks", 100),
        ...
    ]
    """
    stats = response.json()
    print(stats)


def req_test(team, year):
    url = craftUrl(team, year)
    response = getPage(url)
    extractTeamStats(response)


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

    req_test(None, 2022)

    # open up and initialize the DB
    conn = initDB("stats.db")


if __name__ == "__main__":
    main()
