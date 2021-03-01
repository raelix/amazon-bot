# Amazon bot 
Those simple python scripts allow users to buy from amazon when an item is available again. **This script is intented to be used just to understand how scraper works, please just study it but DO NOT use it to buy products, I do not take any responsibility for improper use**


## Requirements
- python3
- google-chrome
- pip3

## Testing
This project has been tested only with Amazon.it, so there could be strange behaviour for other countries

## Dependencies
Run this command to satisfy all dependencies
```
pip3 install -r requirements.txt
```

## Run it!
Create a file called ```secrets.py``` and add those lines:
```
limit_price = 1000 # Limit price to buy
email = 'youemail@gmail.com' # Your amazon email
password = 'MyImpossiblePassword' # Your amazon password
```
> By default the buy is disabled to avoid mistake. Please change the variable ```isTest=True``` in the  ```main.py``` to ```False``` otherwise the script will not buy anything.

Then run it:
```
python3 main.py
```

## TODO
- [] Generate a scraper to fetch dynamic URL based on keywords
- [] Create a Dockerfile to skip install dependencies
- [] Optimize for all Amazon countries