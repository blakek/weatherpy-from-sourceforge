#! /usr/bin/env python

import sys, argparse, urllib2
from xml.etree.ElementTree import parse
from datetime import datetime, timedelta

# Grab our data and return XML with weather data
def get_data(zipCode, startTime, endTime):
	weatherURI = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?'
	
	weatherURI += 'zipCodeList=' + zipCode + "&begin=" + str(startTime).replace(" ", "T") + "&end=" + str(endTime).replace(" ", "T")
	
	try:
		response = urllib2.urlopen(weatherURI)
	except urllib2.URLError as e:
		print(e.reason)
		print("Make sure your internet connection is active.")
		sys.exit(1)
	
	if response == None:
		response = ''
	
	return response

def print_title(text):
	print("\n%s\n%s" % (text, '=' * len(text)))

# Make it easy to add needed variables to URL
def av(var):
	return "&{0}={0}".format(var, '&')

def Main(zipCode='38873', timeShift=0):
	precipitation = 0.0
	
	startTime = datetime.now() + timedelta(days=timeShift)	
	endTime = startTime + timedelta(days=1)

	# Grab an XML document from the National Weather Service
	weatherData = parse(get_data(zipCode, startTime, endTime))

	print("Weather forecast for %s:" % zipCode)
	print("\__ %s to %s" % (startTime.strftime('%b %d (%I:%M %P)'), endTime.strftime('%b %d (%I:%M %P)')))
	
	try:
		# Weather alerts (watches, warnings, & advisories)
		print_title("Watches, warnings, & advisories")
		for e in weatherData.findall('.//data/parameters/hazards/hazard-conditions/hazard'):
			print('| %s %s' % (e.attrib['phenomena'], e.attrib['significance']))
		else: print('| None')
	except:
		print('| Failed to find data')
	
	try:
		# Total forecasted precipitation
		print_title("Expected precipitation")
		for value in weatherData.findall(".//data/parameters/precipitation/value"):
			precipitation = precipitation + float(value.text)
		print("| %4.2f %s" % (precipitation, weatherData.find('.//data/parameters/precipitation').attrib['units']))
	except:
		print('| Failed to find data')
	try:
		# Severe weather forecast with detailed probabilities
		print_title("Severe forecast")
		print("| Overview:  " + weatherData.find('.//data/parameters/convective-hazard/outlook/value').text)
		for e in weatherData.findall('.//data/parameters/convective-hazard/severe-component'):
			print("|   " + e.find("name").text + ": " + e.find(".//value").text + "%")
	except:
		print('| Failed to find data')

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-z', '--zipcode',  help='Zip code to retrieve forcase for', type=str, default='38873')
	parser.add_argument('-t', '--timeshift', help='Shift the forecast forwards/backwards this many days', type=int, default=0)
	args = parser.parse_args()
	
	Main(args.zipcode, args.timeshift)
