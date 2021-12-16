from bs4 import BeautifulSoup  # Navigating on the website
from requests import get       # Entering the website
import sqlite3
from sys import argv           # Getting arguments from the console
import re
import time

def main(province):
  # ///////////////////////////////////////////
  def clear_price(price):
    ''''''
    return float(price.replace(' ', '').replace('zł','').replace(',','.'))


  def num_of_pages():
    '''Calculate the number of pages to view.'''
    page = get(URL)
    bs = BeautifulSoup(page.content, 'html.parser')  
    numbs = []
    
    for num in bs.find_all('span', class_='item fleft'):
      numbs.append(int(num.find('span').get_text().strip()))
      
    return max(numbs)


  def olx_detail(link):
    '''Read the flat area from the "olx.pl" page.'''
    page = get(link)
    bs = BeautifulSoup(page.content, 'html.parser')
    detail = bs.find('li', class_='css-ox1ptj', text=re.compile('ierzchn')).get_text()
    return float(detail.split(' ')[1].replace(',', '.'))


  def otodom_detail(link):                                        
    '''Read the flat area from the "otodom.pl" page.'''
    page = get(link)
    bs = BeautifulSoup(page.content, 'html.parser')
    
    detail = bs.find(title=re.compile('wierzchnia')).next_sibling.next_sibling.get_text()
    return float(detail.split(' ')[0].replace(',', '.'))


  def parse_page(number):                                       
    '''Searching for the necessary information on the website.'''
    print(f"I'm working on page {number}.")
    page = get(f'{URL}?page={number}')
    bs = BeautifulSoup(page.content, 'html.parser')
    
    for offer in bs.find_all('div', class_='offer-wrapper'):
      try:
        footer = offer.find('td', class_='bottom-cell')                                         # Offer footer
        location = footer.find('small', class_='breadcrumb').get_text().strip().split(',')[0]   # Location
        title = offer.find('strong').get_text().strip()                                         # Offer title
        price = clear_price(offer.find('p', class_='price').get_text().strip())                 # Price
        link = offer.find('a')['href']                                                          # Link of the offer
        
        if 'olx' in link:                                                                       # Area of the apartment
          area = olx_detail(link)
        elif 'otodom' in link:
          area = otodom_detail(link)
        else:
          area = None
          
        per_sqr_meter = round(price/area, 2)                                                    # Price for one meter squared
        
      except:
        print(f"Something went wrong while reading: {link}")
      
      print(title, price, location, area, per_sqr_meter, link)
      cursor.execute(f'INSERT INTO offers_{province} VALUES (?, ?, ?, ?, ?, ?)', (title, price, location, area, per_sqr_meter, link))
    
    db.commit()                                                 

  # ///////////////////////////////////////////

  URL = f'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/{province}/'
  db = sqlite3.connect('dane.db')
  cursor = db.cursor()  # Operations on sqlite3


  if len(argv) > 1 and argv[1] == 'setup':
    cursor.execute(f'''CREATE TABLE offers_{province}(
                          name TEXT,
                          price REAL,
                          city TEXT,
                          area REAL,
                          "PLN / m2" REAL,
                          link TEXT)''')
    quit()

  pages = num_of_pages()
  print(f'The number of pages to be searched is {pages}.')
  
  
  '''Checking the correctness of the entered page range.'''
  start_page = (input('Start from page: '))
  while not(start_page.isnumeric() and int(start_page) > 0 and int(start_page) <= pages):
    start_page = input(f'Start from page (please enter a number in the range 1-{pages}): ')
  
  end_page = input('End on page: ')
  while not(end_page.isnumeric() and int(end_page) >= int(start_page) and int(end_page) <= pages):
    end_page = input(f'End on page (please enter a number in the range {start_page}-{pages}): ')
  
  
  '''Main calculations'''
  start = time.time()
  
  for page in range(int(start_page), int(end_page) + 1):   
    parse_page(page)
    
  end = time.time()  
  print(f'Search time: {time.strftime("%H:%M:%S",(time.gmtime(end-start)))}')

  print("Work completed successfully.")
  db.close()
  
provinces = ['dolnoslaskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 'lodzkie', 'malopolskie', 'mazowieckie', 'opolskie', 'podkarpackie', 'podlaskie', 'pomorskie', 'slaskie', 'swietokrzyskie', 'warminsko-mazurskie', 'wielkopolskie', 'zachodniopomorskie']

print('List of provinces')
n = 0
for i in provinces:
  n += 1
  print(f'{n}. {i}')
  
choice = input('Select the province from the list by entering its number:  ')

'''Checking the correctness of the entered province.'''     
while not (choice.isnumeric() and int(choice) > 0 and int(choice) < (len(provinces) + 1)):
  print(f'Invalid selection. Available numbers: 1 - {len(provinces)}')
  choice = input('Select the province from the list by entering its number: ')
  continue

main(provinces[int(choice) - 1])
