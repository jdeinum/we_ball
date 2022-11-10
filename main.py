import sqlite3 as sq3
from bs4 import BeautifulSoup


def initDB(db_name):
    db = sq3.connect(db_name)
    curs = db.cursor()

    statements = [
        "PRAGMA foreign_keys = ON;",
        "CREATE TABLE team(name TEXT, year TEXT, stat TEXT, value REAL);",
        "CREATE TABLE individual(name TEXT, year TEXT, team TEXT, stat TEXT, value REAL, FOREIGN KEY(team) REFERENCES team(name));",
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
    pass


def craftUrl(team, year):
    """
    if team is None, we want overall team stats from a particular year
    otherwise we want individual stats from a particular team for a particular
    year
    """
    pass


def extractTeamStats(response):
    pass


def extractIndividualStats(response):
    pass


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

    # open up and initialize the DB
    conn = initDB("stats.db")


if __name__ == "__main__":
    main()
