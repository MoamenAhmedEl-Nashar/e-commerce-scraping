from bs4 import BeautifulSoup
import requests
import pandas as pd


class Scraper:
    def __init__(self, keywords, maxNumPages=1):
        self.keywords = keywords
        self.maxNumPages = maxNumPages
        self.baseLink = "https://drive.carrefour.be/fr"

    def run(self):
        data = []
        for keyword in self.keywords:
            for page in range(self.maxNumPages):
                print(f"Scraping keyword {keyword} and page {page}")
                link = f"https://drive.carrefour.be/fr/search?q={keyword}%3Arelevance&page={page}"
                requestResult = requests.get(link)
                content = requestResult.content
                soup = BeautifulSoup(content, 'html.parser')

                for itemSoup in soup.findAll('div', attrs={'class': 'wrapper'}):
                    item = Item()
                    item = item.getItemDetails(self.baseLink, itemSoup)
                    if item is not None:
                        itemDetails = item.viewItemDetailsList()
                        # print(itemDetails)
                        data.append(itemDetails)

        df = pd.DataFrame(data=data, columns=['name', 'price'])
        df.to_csv('carrefour.csv')



class Item:
    def __init__(self):
        self.name = None
        self.price = None


    def getItemDetails(self, baseLink, itemSoup):

        itemName = itemSoup.find('a', attrs={'class': 'name select_item name-title select_promotion_item'})
        itemNameText = itemName.text.strip()
        self.name = itemNameText
        self.getPrice(itemSoup)
        if self.isItemInStock():
            return self
        else:
            print(f"{self.name}: out of stock")
            return None

    def getPrice(self, itemSoup):
        priceTag = itemSoup.find('div', attrs={'class': 'baseprice'})
        if priceTag:
            priceString = priceTag.text
            formattedPriceString = priceString.replace(',', '.').strip()
            price = float(formattedPriceString[:-1])
            self.price = price


    def isItemInStock(self):
        return self.price != None


    def viewItemDetailsDict(self):
        itemDetails = {}
        itemDetails['name'] = self.name
        itemDetails['price'] = self.price

        return itemDetails

    def viewItemDetailsList(self):
        itemDetails = [self.name, self.price]
        return itemDetails


scraper = Scraper(['cat'], 3)
scraper.run()


