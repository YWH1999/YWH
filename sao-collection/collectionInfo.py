import requests
import time
import pymongo
import cloudscraper
import config

# This will create a new Scraper instance that can be protected by OpenSea Cloudflare
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)
headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

#Get the address from mongodb and the collection name from the contract address
client = pymongo.MongoClient(config.mangodb)
db = client[config.database]
dc = db.collections
c = dc.find({"abi": 6,"collectionImage_url":{"$exists":False}})
c = dc.find({"abi": 6})
contract_base_url = config.contract_base_url
collection_base_url = config.collection_base_url

address = []
count = 0
for i in c:
    count = count + 1
    address.append(i["contract"])
    contract = i["contract"]
    contract_url = contract_base_url + contract
    responseS = scraper.get(contract_url,headers=headers).json()
    time.sleep(1)
    collect = responseS["collection"]
    slug = collect["slug"]

    collection_url = collection_base_url + slug
    response = requests.get(collection_url).json()
    time.sleep(1)

    #if no collectionInfo
    try:
        collection = response["collection"]
    except KeyError:
        print(count, ">The collection does not exist")
        pass
        continue

    medium_username = collection["medium_username"]
    twitter_username = collection["twitter_username"]
    instagram_username = collection["instagram_username"]
    discord_url = collection["discord_url"]
    telegram_url = collection["telegram_url"]
    website_url = collection["external_url"]
    wiki_url = collection["wiki_url"]

    name = collection["name"]
    collection_image = collection["image_url"]
    background_image = collection["featured_image_url"]
    description = collection["description"]

    db.collections.update_one({"contract": contract}, {"$set": {"name": name,"collectionImage_url": collection_image,
                                                                "background_url": background_image,"description": description,
                                                                "twitter_username": twitter_username,"instagram_username": instagram_username,
                                                                "discord_url": discord_url,"telegram_url": telegram_url,
                                                                "medium_username": medium_username,"website_url": website_url,
                                                                "wiki_url": wiki_url}})
    print(count,">success")

