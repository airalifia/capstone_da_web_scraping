from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
table_exc_rates = table.find_all('a', attrs= {'class':'w'} )

row_length = len(table_exc_rates)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    
   #get tanggal 
   tanggal = table.find_all('a', attrs={'class':'n'})[i].text
   
   #get kurs
   kurs = table.find_all('span', attrs={'class':'w'})[i].text
       
   temp.append((tanggal, kurs))

temp = temp[::-1]

#change into dataframe
kurs_rate = pd.DataFrame(temp, columns=('date','kurs'))

#insert data wrangling here

# Ensure 'kurs' column is of type string before cleaning
kurs_rate['kurs'] = kurs_rate['kurs'].astype(str)

# Clean 'kurs' column by removing 'USD', 'IDR', and commas
kurs_rate['kurs'] = kurs_rate['kurs'].str.replace('1 USD = ', '', regex=False)
kurs_rate['kurs'] = kurs_rate['kurs'].str.replace(' IDR', '', regex=False)
kurs_rate['kurs'] = kurs_rate['kurs'].str.replace(',', '', regex=False)

# Convert 'kurs' column to float type
kurs_rate['kurs'] = kurs_rate['kurs'].astype('float64')

# Convert 'date' column to datetime type
kurs_rate['date'] = pd.to_datetime(kurs_rate['date'])

# Set 'date' as index
kurs_rate = kurs_rate.set_index('date')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{kurs_rate["kurs"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = kurs_rate.plot(figsize = (12,5)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
    