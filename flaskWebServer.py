import numpy
import json
import re
import os
from mongoengine import connect
from flask import Flask, Response, render_template, request, redirect
import pygal
from pygal.style import Style
from scipy import polyfit
from Car import Car

app = Flask(__name__)
if os.getenv('MONGOLAB_URI') is not None: # on Heroku
    mongolab_uri = os.getenv('MONGOLAB_URI')
    db = mongolab_uri[mongolab_uri.rfind('/')+1:] # get database name
    connect(db, host=mongolab_uri)
else:
    connect('usedCars')
    
class Data:
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.price_vs_mile=[]
        self.price_vs_year=[]
        self.price=[]
        self.miles=[]
        self.year=[]
        self.exterior=[]
        self.brand=""
        self.model=""
        self.zipcode=""

class Query:
    def __init__(self):
        self.brand='Subaru'
        self.model='Forester'
        self.zipcode='07302'
        self.display_zipcode='07302'
        
class BMZ: #brand, model, zipcode
    def __init__(self):
        self.bm_dict = {}
        self.zipcode_map = {}
        with open("json/brandModel.json") as data_file:
        	self.bm = json.load(data_file)
        with open("json/zipcodeNY.json") as data_file:
        	self.zipcodeNY = json.load(data_file)
        with open("json/zipcodeNJ.json") as data_file:
        	self.zipcodeNJ = json.load(data_file)
        with open("json/zipcodeCA.json") as data_file:
        	self.zipcodeCA = json.load(data_file)
        
        for key, val in self.zipcodeNY.items():
            self.zipcode_map[key] = val
        for key, val in self.zipcodeNJ.items():
            self.zipcode_map[key] = val
        for key, val in self.zipcodeCA.items():
            self.zipcode_map[key] = val
            
        for item in self.bm:
            models = item["model"]
            self.bm_dict[item["brand"].lower()] = []
            for m in models:
                self.bm_dict[item["brand"].lower()].append(m.lower())
    	
data = Data()
query = Query()
bmz = BMZ()

@app.route('/', methods=['GET', 'POST'])
def index():
    global query
    global bmz
    error = None
    if request.method == 'GET':
        error = calculate_stats(query)
    elif request.method == 'POST':
        input_brand = request.form['brand'].strip()
        input_model = request.form['model'].strip()
        input_zipcode = request.form['zipcode'].strip()
        new_brand = re.sub(' +', '-', input_brand).lower()
        new_model = re.sub(' +', '-', input_model).lower()
        new_zipcode = re.sub(' +', '', input_zipcode)

        if new_brand not in bmz.bm_dict:
            error = "Brand " + new_brand.title() + " is not supported. Previous results are still shown below."
            return render_template('index.html', error = error)
        elif new_model not in bmz.bm_dict[new_brand]:
            error = "Model " + new_model.title() + " is not supported in brand " + new_brand.title() + " Previous results are still shown below."
            return render_template('index.html', error = error)
        elif  new_zipcode not in bmz.zipcode_map:
            error = "zipcode " + new_zipcode + " is not supported. Previous results are still shown below."
            return render_template('index.html', error = error)
        else:
            query.brand = new_brand
            query.model = new_model
            query.zipcode = bmz.zipcode_map[new_zipcode]
            query.display_zipcode = new_zipcode
        
        error = calculate_stats(query)
        
    return render_template('index.html', error = error)

def calculate_stats(query):
    global data

    record = Car.objects(brand=query.brand.lower(), model=query.model.lower(), zipcode=query.zipcode)
    if len(record) <=3:
        return "Not enought data for " + query.brand.title() + " " + query.model.title() + " at " + query.display_zipcode + \
                ". Please query other combinations. Prevous results is still shown below."
  
    data.clear()
    data.brand=query.brand
    data.model=query.model
    data.zipcode=query.zipcode

    for x in record:
        data.price_vs_mile.append((x.miles, x.price))
        data.price_vs_year.append((x.year, x.price))
        data.price.append(x.price)
        data.miles.append(x.miles)
        data.year.append(x.year)
        data.exterior.append(x.exterior)
    
    return None

@app.route('/price_vs_miles_svg/')
def graph():
    global data
    (ar, br) = polyfit(data.miles, data.price, 1)
    xy_chart = pygal.XY(stroke=False, width=800, height=700, explicit_size=True, legend_at_bottom=True)
    xy_chart.title = "Price($USD) vs Miles. Price depreciation coefficent: " + str(round(ar, 3))
    xy_chart.add("Used " + data.model.title() + " price vs. miles", data.price_vs_mile)
    xy_chart.add("Linear regression with slope of " + str(round(ar, 3)), \
                [(min(data.miles), min(data.miles)*ar + br), (max(data.miles), max(data.miles)*ar + br)], \
                stroke=True, stroke_style={'width': 5, })
    xy_chart.render()
    return Response(response=xy_chart.render(), content_type='image/svg+xml')

@app.route('/price_vs_year_svg/')
def graph2():
    global data
    (ar, br) = polyfit(data.year, data.price, 1)
    xy_chart = pygal.XY(stroke=False, width=800, height=700, explicit_size=True, legend_at_bottom=True)
    xy_chart.title = "Price($USD) vs years. Price appreciaiton coefficent: " + str(round(ar, 3))
    xy_chart.add("Used " + data.model.title() + " price vs. years", data.price_vs_year)
    xy_chart.add("Linear regression with slope of " + str(round(ar, 3)), \
                 [(min(data.year), min(data.year)*ar + br), (max(data.year), max(data.year)*ar + br)], \
                 stroke=True, stroke_style={'width': 5, })
    xy_chart.render()
    return Response(response=xy_chart.render(), content_type='image/svg+xml')

@app.route('/year_histogram_svg/')
def graph3():
    global data
    hist, bins = numpy.histogram(data.year, bins=(max(data.year)-min(data.year)+1))
    bar_chart = pygal.Bar(width=800, height=700, explicit_size=True, legend_at_bottom=True)
    bar_chart.x_labels = map(str, range(min(data.year), max(data.year)+1))
    bar_chart.title = "Used " + data.model.title() + " release year popularity (in number of on market used cars)"
    bar_chart.add('Number of used cars on market for the made of year', hist)
    return Response(response=bar_chart.render(), content_type='image/svg+xml')

@app.route('/exterior_pie_svg/')
def graph4():
    global data
    colors = ['black','blue','brown','gold','gray','green','red','silver','#EFEDDA']
    color_percent=[0,0,0,0,0,0,0,0,0]
    for x in data.exterior:
        for idx, val in enumerate(colors):
            if val in x:
                color_percent[idx] += 1
            if idx == len(colors) - 1 and "white" in x:
                color_percent[idx] += 1

    total = sum(color_percent)
    for idx, val in enumerate(color_percent):
        color_percent[idx] = round(color_percent[idx]/total, 2)*100

    custom_style = Style(colors = colors)
    pie_chart = pygal.Pie(width=800, height=700, explicit_size=True, \
                          print_values=True, legend_at_bottom=False, \
                          style=custom_style)

    for idx, val in enumerate(colors):
        if idx == len(colors) -1:
            pie_chart.add("white", color_percent[idx])
        else:
            pie_chart.add(val, color_percent[idx])


    pie_chart.title = "Used " + data.model.title() + " exterior color popularity(in %)"
    pie_chart.render()
    return Response(response=pie_chart.render(), content_type='image/svg+xml')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('IP', '0.0.0.0')
    app.run(port=port, host=host)
