# Amazon bot 
This project allows to buy from amazon when an item becomes available. It works mainly when it is sells and shipped by Amazon. 
You need to define a list of URLs and a price limit. 

It relies on ToR exit-nodes to be anonymous. 

The scrape process is python based and uses Selenium to buy the items when the scrape returns a matching item. It uses multiprocesses to speed up the scraping and the data are shared using multiple queues. 
Main components are:
- Supervisor - Supervise processes and stop them once buy is done.
- Producer - Interact with ToR and produce URLs and proxies for the consumers.
- Consumers/Workers - Scrape endpoint and generate a result for the buyer.
- Buyer - Runs login at the beginning and after a specific amount of time to keep the session ope. It wait for an item to be available and then purchase it.
- Statistic module - Receives info about requests. It takes care of replacing ToR circuit when scraping is blocked.

***This script is intented to be used just to understand how scraper works, please just study the code but DO NOT use against real Amazon endpoints to buy products, this is not allowed! I do not have any responsibility for improper use!!!!***


## Environment variables

| Variable | Default| Description |
|----------|:----:|-------------|
|AMAZON_EMAIL   | "" | [Required] Amazon email|
|AMAZON_PASSWORD| ""| [Required] Amazon password |
|PORTAL | https://www.amazon.it| Amazon home page to execute the login|
|IS_CONTAINERIZED|False| True if running as container else False|
|IS_TEST| True | True if don't want buy the item else False|
|PROXY_TYPE|tor| Which proxy use (available "tor" or "empty")|
|STANDALONE_PROXY|True|If ```PROXY_TYPE``` is set to tor this flag  start and stop tor automatically. N.B.: stop the service on your host before running the script
|WAIT_BEFORE_LOGIN|1800|Seconds before running again the login with selenium to keep the session open|
|REQUEST_TIMEOUT|5|Request timeout in seconds|
|PERCENTAGE|60|Percentage of failure before skipping the current proxy|
|SAMPLES|10|Number of success+failure requests before checking failure percentage|
|WAIT_RANDOM|False|Wait random time before running a request|
|POOL_SIZE|URLs size|The size of the requests pool, by default it match the number of the items in the URLs list|


## Run using docker container
In order to run the tool as docker container you need to move to the ```run``` directory then:
```
docker-compose up
```
Remember to fill the required variables in the ```docker-compose.yml``` file. The csv file which contains the URLs and the limit price is under ```src``` folder.
## Run on the host
In this scenario you need to install all the requirements mentioned before.
### Python 3 Dependencies
Run this command to satisfy all dependencies
```
pip3 install -r requirements.txt
```

### Requirements
- python3*
- google-chrome*
- pip3*
- tor*

*Those requirements are already satisfied when running it as container and with ```IS_CONTAINERIZED``` variable set to False

Then run it:
```
./run_without_container.sh
```

## TODO
- [] Generate a scraper to fetch dynamic URL based on keywords
- [] Optimize for all Amazon countries
- [] Add one more middleware to interact using telegram
- [] Switch to logging instead of print
- [] Enable screenshot when running in container mode
