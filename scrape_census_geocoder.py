from bs4 import BeautifulSoup as soup
import requests
import csv
import time


def main():
    print('Started...')
    startTime = time.time()
    # open source file to generate urls
    input_file = 'shootings data test copy.csv'
    # write headers to result file outside of loop
    with open('results.csv', mode='w') as results:
                fieldnames = ['id','longitude_wp', 'latitude_wp','cousubgeoid_wp', 'cousubname_wp', 'tractgeoid_wp', 'tractcode_wp','tractname_wp']
                writer = csv.DictWriter(results, fieldnames)
                writer.writeheader()

    with open(input_file) as csvfile:
        file = csv.DictReader(csvfile)
        for row in file:
            long = row['longitude_wp']
            lat = row['latitude_wp']
            row_id = row['id']
            if lat and long:
                url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={long}&y={lat}&benchmark=4&vintage=418"
       
                # within the loop, get the soup and return the values from the webpage needed
                x = get_soup(url)
                y = get_data(x, row_id, long, lat)
                print(y)
                #write the new values to a csv file
                with open('results.csv', mode='a') as results:
                    fieldnames = ['id','longitude_wp', 'latitude_wp','cousubgeoid_wp', 'cousubname_wp', 'tractgeoid_wp', 'tractcode_wp','tractname_wp']
                    writer = csv.DictWriter(results, fieldnames)
                    writer.writerow(y)
            else:
                pass
    
    endTime = time.time()
    print(f'The program took {(endTime-startTime)/60} minutes to complete')

def get_soup(url):
    headers = {
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
    ret = requests.get(url, headers=headers)
    page_soup = soup(ret.content, 'html.parser')
    good_soup = page_soup.select('fieldset div')  
    good_soup = good_soup.pop() # the div we want is the last one
    good_soup = list(good_soup.strings) #change to strings so I can work with the output

    return good_soup


def get_data(soup, id, long, lat):
    result_list = []
    #adding these to dict here, but could do it in main
    result_dict = {'id': id, 'longitude_wp': long, 'latitude_wp': lat}
    # create list from soup
    for i, x in enumerate(soup):
        if 'Census Tracts' in x or 'County Subdivision' in x:
            result_list.append(x)
        if 'GEOID' in x:
            result_list.append(soup[i + 1])
        if 'NAME' in x:
            result_list.append(soup[i + 1])
        if 'TRACT CODE' in x:
            result_list.append(soup[i + 1])
    print(result_list)
    # narrow list down to those we need
    for ind, item in enumerate(result_list):
        if 'County Subd' in item:
            result_dict.update({'cousubgeoid_wp' : result_list[ind+1]})
            result_dict.update({'cousubname_wp' : result_list[ind+2]})
        if 'Census Tracts' in item:
            result_dict.update({'tractgeoid_wp' : result_list[ind+1]})
            result_dict.update({'tractcode_wp' : result_list[ind+2]})
            result_dict.update({'tractname_wp' : result_list[ind+3]})
    return result_dict


if __name__ == "__main__":
    main()

