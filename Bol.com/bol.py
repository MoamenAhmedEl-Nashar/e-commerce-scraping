from bs4 import BeautifulSoup
import requests
import pandas as pd


class Scraper:
    def __init__(self, keywords, maxNumPages=1):
        self.keywords = keywords
        self.maxNumPages = maxNumPages
        self.baseLink = "https://www.bol.com"

    def run(self):
        data = []
        for keyword in self.keywords:
            for page in range(1, self.maxNumPages+1):
                print(f"Scraping keyword {keyword} and page {page}")
                link = f"https://www.bol.com/nl/s/?page={page}&searchtext={keyword}&view=list"
                requestResult = requests.get(link)
                content = requestResult.content
                soup = BeautifulSoup(content, 'html.parser')

                for itemSoup in soup.findAll('li', attrs={'class': 'product-item--row js_item_root'}):
                    item = Item()
                    item = item.getItemDetails(self.baseLink, itemSoup)
                    if item is not None:
                        itemDetails = item.viewItemDetailsList()
                        # print(itemDetails)
                        data.append(itemDetails)

        df = pd.DataFrame(data=data, columns=['name', 'ean', 'price', 'discount(%)', 'brand'])
        df.to_csv('bol.csv')



class Item:
    def __init__(self):
        self.name = None
        self.ean = None
        self.price = None
        self.discount = 0
        self.brand = None
        self.seller = None

    def getItemDetails(self, baseLink, itemSoup):

        itemName = itemSoup.find('a', attrs={'class': 'product-title px_list_page_product_click'})
        itemNameText = itemName.text
        self.name = itemNameText
        self.getPrice(itemSoup)
        self.getSeller(itemSoup)
        if self.isItemInStock() and self.supportedSeller():
            self.getDiscount(itemSoup)
            self.getBrand(itemSoup)
            itemNameLink = itemName['href']
            itemDetailsLink = baseLink + itemNameLink
            itemDetailsRequestResult = requests.get(itemDetailsLink)
            itemDetailsContent = itemDetailsRequestResult.content
            itemDetailsSoup = BeautifulSoup(itemDetailsContent, 'html.parser')
            self.getEan(itemDetailsSoup)
            return self
        else:
            print(f"{self.name}: out of stock or not supported seller")
            return None

    def getPrice(self, itemSoup):
        priceTag = itemSoup.find('span', attrs={'class': 'promo-price'})
        if priceTag:
            priceString = priceTag.text

            formattedPriceString = priceString.replace('\n  ', '.').strip()
            fraction = formattedPriceString.split('.')[1]
            if fraction != '-':
                price = float(formattedPriceString)
            else:
                price = float(formattedPriceString.split('.')[0])
            self.price = price

    def getEan(self, itemDetailsSoup):
        eanItem = itemDetailsSoup.find(lambda tag:tag.name=="dt" and "EAN" in tag.text)
        if eanItem:
            eanValue = eanItem.find_next('dd', attrs={'class': 'specs__value'}).text.strip()
            self.ean = eanValue

    def getDiscount(self, itemSoup):
        discountItem = itemSoup.find('p', attrs={'class': 'product-prices ab-discount small_details'})
        if discountItem:
            # print(f'{self.name}: has a discount')
            discountValue = discountItem.find('strong').text.strip().split('Je bespaart ')[1]
            self.discount = float(discountValue[:-1])

    def getBrand(self, itemSoup):
        brandItem = itemSoup.find('a', attrs={'data-test': 'party-link'})
        if brandItem:
            brand = brandItem.text
            self.brand = brand

    def getSeller(self, itemSoup):
        sellerItem = itemSoup.find('div', attrs={'class': 'product-delivery-highlight'})
        if sellerItem:
            seller = sellerItem.text.strip()
            self.seller = seller

    def isItemInStock(self):
        return self.price != None

    def supportedSeller(self):
        return self.seller == 'Op voorraad'

    def viewItemDetailsDict(self):
        itemDetails = {}
        itemDetails['name'] = self.name
        itemDetails['ean'] = self.ean
        itemDetails['price'] = self.price
        itemDetails['discount(%)'] = self.discount
        itemDetails['brand'] = self.brand
        return itemDetails

    def viewItemDetailsList(self):
        itemDetails = [self.name, self.ean, self.price, self.discount, self.brand]
        return itemDetails


scraper = Scraper(['cat'], 3)
scraper.run()


