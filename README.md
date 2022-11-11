# We_ball
A simple modelling project using USports Mens volleyball stats


## Getting Data
Because teams are unlikely to be added frequently, we opted to use pythons
standard request library instead of a dedicated web scraper like Scrapy. Each
parameter would just be formatted into the URL before getting the request:

```python
requests.get("https://canadawest.org/stats.aspx?path=mvball&year={}&school={}", headers={'User-Agent': 'Custom'})
```

Without altering our custom header, we would get only 404s because most websites
blacklist Python as a user agent. Now that we have the html, we parse it using
BeautifulSoup, an elegant library to handle html in python. 





