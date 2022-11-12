import json
import os
import sqlite3
import sqlite3 as sq3

from bs4 import BeautifulSoup, Doctype
import numpy as np
import requests
from selenium import webdriver


def initDB(db_name):
    db = sq3.connect(db_name)
    curs = db.cursor()

    statements = [
        "PRAGMA foreign_keys = ON;",
        "CREATE TABLE IF NOT EXISTS team_season(name TEXT, year TEXT, stat TEXT, units TEXT, value REAL);",
        "CREATE TABLE IF NOT EXISTS team(name TEXT, date TEXT, stat TEXT, units TEXT, value REAL);",
        "CREATE TABLE IF NOT EXISTS individual_season(name TEXT, year TEXT, team TEXT, stat TEXT, units TEXT, value REAL, FOREIGN KEY(team) REFERENCES team_season(name));",
        "CREATE TABLE IF NOT EXISTS individual(name TEXT, date TEXT, team TEXT, stat TEXT, units TEXT, value REAL, FOREIGN KEY(team) REFERENCES team_season(name));",
    ]

    for x in statements:
        curs.execute(x)

    curs.close()
    return db


def insertTeamSeasonStats(db, stats):
    """
    stats is a list of data tuples, i.e:
    [
    ("ab", 2000, "points", 100),
    ...
    ]

    It's expected that all strings are lowercase and underscores replace any spaces
    """

    curs = db.cursor()
    curs.executemany("INSERT INTO team_season VALUES (?, ?, ?, ?, ?)", stats)
    curs.close()


def insertIndividualStats(db, stats):
    """
    stats is a list of data tuples, i.e:
    [
        ("jacob_deinum", "team", 2022, "blocks", 100),
    ...
    ]
    It's expected that all strings are lowercase and underscores replace any spaces
    """
    curs = db.cursor()
    curs.execute("INSERT INTO team VALUES (?, ?, ?, ?)", stats)
    curs.close()


def getPageSource(url):
    os.environ["MOZ_HEADLESS"] = "1"
    driver = webdriver.Firefox()
    driver.get(url)
    return driver.page_source


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


def extractTeamSeasonStats(response):
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
    tables = bs.find_all("table")[0:13]  # only interested in the team stats, not
    # game to game etc

    result_set = []

    school_labels = [
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
            if x[i] in school_labels:
                index = i
                break

        headers = x[2:index]
        teams = x[index:]

        # now we split values in the array
        split = using_clump(values)

        for i in range(len(teams)):
            for j in range(len(headers)):
                try:
                    team_name = teams[i].lower().replace(" ", "_")
                    stat_name = labels[i].lower().replace(" ", "_")
                    stat_header = headers[j].lower().replace(" ", "_")
                    value = float(split[i][j])
                    result_set.append((team_name, stat_name, stat_header, value))

                except:
                    print("Error getting stat")

    return np.array(result_set)


def extractIndividualStats(response, team):
    """
    Given the response (html source page), extracts and converts all individual
    stats to their respective forms. It returns a list of data tuples for all
    players in the current response page (to be inserted into db).
    """
    stats = []

    page = BeautifulSoup(response, "html.parser")
    year = int((page.find("article").find("h2").string)[0:4])
    # Need all tables: offence/defence
    tables = page.find_all("table")

    for table in tables:
        rows = table.find_all("tr")

        stat_strings = [x.string for x in rows[0].find_all(["th", "td"])]
        # Get rid of player name statistic since this is accounted
        # for in its row representation in db
        stat_strings.pop(0)

        for i in range(1, len(rows)):
            cells = rows[i].find_all(["th", "td"])
            # Format and get player name
            name = cells[0].string
            name = name.lower().replace(" ", "_")
            # Get vals for stats
            vals = [float(x.string) for x in cells[1::]]

            for j in range(len(stat_strings)):
                stats.append((name, year, stat_strings[j], vals[j]))

    return stats


def req_test(team, year):
    if team:
        url = craftUrl(team, year)
        page = getPageSource(url)
        extractIndividualStats(page)
    else:
        url = craftUrl(None, year)
        response = getPage(url)


def doTeamStats(years, db):

    for year in years:
        url = craftUrl(None, year)

        response = getPage(url)
        if not response:
            print("Invalid Response!")
            continue

        stats = extractTeamSeasonStats(response)
        if len(stats) == 0:
            print("No stats for year ", year)
            continue

        # insert the year into the stats
        # year is the second arg
        stats = [np.insert(x, 1, year) for x in stats]

        insertTeamSeasonStats(db, stats)


def doIndividualStats(years, teams, db):

    for year in years:
        for team in teams:
            url = craftUrl(team, year)
            response = getPageSource(url)
            if not response:
                print("Invalid Response!")
                continue

            stats = extractIndividualStats(response)
            if len(stats) == 0:
                print("No stats for {} {}".format(team, year))
                continue

            insertIndividualStats(db, stats)


def doSeasonStats(db):
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

    doTeamStats(range(2018, 2022, 1), db)
    # doIndividualStats(range(2018, 2022, 1), teams, conn)


def main():
    conn = initDB("stats.db")
    doSeasonStats(conn)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
