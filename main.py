import sqlite3 as sq3


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





'''
stats is a list of data tuples, i.e:
[
("ab", 2000, "points", 100),
...
]

It's expected that all strings are lowercase and underscores replace any spaces
'''
def insertTeamStats(db, stats):
    curs = db.curs()
    curs.execute("INSERT INTO team VALUES (?, ?, ?, ?)", stats)
    curs.close()


'''
stats is a list of data tuples, i.e:
[
("jacob_deinum", 2022, "blocks", 100),
...
]
It's expected that all strings are lowercase and underscores replace any spaces
'''
def insertIndividualStats(db, stats):
    curs = db.cursor()
    curs.execute("INSERT INTO team VALUES (?, ?, ?, ?)", stats)
    curs.close()


def getPage(url):
    pass


# if team is None, we want overall team stats from a particular year
# otherwise we want individual stats from a particular team for a particular
# year
def craftUrl(team, year):
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
