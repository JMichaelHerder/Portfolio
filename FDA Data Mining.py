import requests
import urllib
import json
import math
from tkinter import *
import csv
import datetime
from openpyxl import Workbook

count = []
class1 = []
class2 = []
class3 = []
classU = []
countList = []
classCount = [0,0,0,0,0]

master = Tk()
master.title("FDA Datamining")
Label(master, text="Firm Name").grid(row=0)

e1 = Entry(master)
master.geometry("275x75")


sites = []

registration_nums_to_indeces = {
}

def site_lookup(reg_num):
    """
    Checks registration_nums_to_indeces for index of site.

    Parameters:
    reg_num (String): The registration number associated with a given site.

    Returns:
    (int): Integer corresponding to location of site information in sites array; -1 if not present.
    """
    return registration_nums_to_indeces.get(reg_num, -1)

def change_site_index(reg_num, new_index):
    """
    Changes index of site in registration_nums_to_indeces based on registration number.

    Parameters:
    reg_num (String): The registration number associated with a given site.
    new_index (int): New index of site in site array.
    """
    registration_nums_to_indeces[reg_num] = new_index

def format_address(result, country_code):
    """
    Formats address based on whether site is located in United States.

    Parameters:
    result (String): single result entry containing site and product information

    Returns:
    address (String): String comprised of all relevant information for a site address
    """
    address = ""
    if country_code == 'US':
        address = (str(result['registration']['address_line_1']) + "\n"
        + str(result['registration']['address_line_2'])
        + str(result['registration']['city']) + ", "
        + str(result['registration']['state_code']) + " " 
        + str(result['registration']['zip_code']))
    else:
        address = (str(result['registration']['address_line_1']) + "\n"
        + str(result['registration']['address_line_2'])
        + str(result['registration']['city']) + ", "
        + str(result['registration']['postal_code']) + " " 
        + str(result['registration']['zip_code']))
    return address

def retrieve_product_activities(result):
    """
    Gets establishment_type entries in each result and properly reformats them to desired activity types

    Parameters:
    result (String): single result entry containing site and product information

    Returns:
    activities [String]: array of string containing activity types of products in result entry
    """
    establishment_type_to_activity = {
        "Complaint File Establishment per 21 CFR 820.198": "Complaint File Establishment",
        "Manufacture Medical Device for Another Party (Contract Manufacturer)": "Contract Manufacturer",
        "Sterilize Medical Device for Another Party (Contract Sterilizer)": "Contract Sterilizer",
        "Export Device to the United States But Perform No Other Operation on Device": "Foreign Exporter",
        "Manufacture Medical Device": "Manufacturer",
        "Remanufacture Medical Device": "Remanufacturer",
        "Repack or Relabel Medical Device Manufacture Device in the United States for Export Only": "Repackager/Relabeler",
        "Reprocess Single-Use Device": "Reprocessor of Single Use Devices",
        "Develop Specifications But Do Not Manufacture At This Facility": "Specification Developer",
        "Manufacture Device in the United States for Export Only": "U.S. Manufacturer of Export Only Devices"
    }
    activities = []
    for i in result['establishment_type']:
        activities.append(establishment_type_to_activity.get(i))

    return activities
   

class Product:
    def __init__(self, device_name, activities, product_code, device_class, regulation_num):
        self.device_name = device_name
        self.activities = activities
        self.product_code = product_code
        self.device_class = device_class
        self.regulation_num = regulation_num
        

class Site:
    def __init__(self, name, address, registration_num, fei_num,  us_agent, official_correspondent):
        self.name = name
        self.address = address
        self.registration_num = registration_num
        self.fei_num = fei_num
        self.us_agent = us_agent
        self.official_correspondent = official_correspondent
        self.product_list = []
        self.class1_count = 0
        self.class2_count = 0
        self.class3_count = 0
        self.classU_count = 0

    def add_product(self, product):
        self.product_list.append(product)
        if product.device_class == '1':
            self.class1_count += 1
        elif product.device_class == '2':
            self.class2_count += 1
        elif product.device_class == '3':
            self.class3_count += 1
        else:
            self.classU_count += 1

def doQuery(search_term, skip):
    """
    Performs search with given term, starting at position _skip_

    Parameters:
    searchTerm (String): The user's search query.
    skip (int): The position to begin the search.

    Returns:
    json (string): A string in JSON format - not a JSON object.
    """ 
    
    limit = 100
    api_key = 'mCdiZYCGPCQVwOZfV03bR6roCGAcr8BGPceHWlca'

    params = ''

    if '&' in search_term:
        # Accounts for names including an ampersand (ex: Smith & Nephew)
        terms = search_term.split('&', 1)
        params = 'api_key=' + api_key + '&search=registration.owner_operator.firm_name:"' + terms[0] + '"+AND+registration.owner_operator.firm_name:"' + terms[1] + '"&skip=' + str(skip) + '&limit=' + str(limit)
    else:
        # Default behavior
        params = 'api_key=' + api_key + '&search=registration.owner_operator.firm_name:"' + search_term + '"&skip=' + str(skip) + '&limit=' + str(limit)

    query = f'https://api.fda.gov/device/registrationlisting.json?' + params
    
    response = requests.get(query)

    payload = json.loads(response.text)

    return payload
    

# Function get_data ets data from fda once input is received.
def get_data():
    if e1.get() is not '':
        company_name = e1.get()
        payload = doQuery(company_name, 0)
    else:
        print('Didn\'t compute input')

    wb = Workbook()
    ws = wb.active

    if len(payload.keys()) > 1:
        total = payload['meta']['results']['total'] # Gets total number of results
        print(total)   
        
        num_skips = math.ceil(total / 100) # Always rounds up to match number of skip needed
        
        for i in range(num_skips):
            for j in range (0, len(payload['results'])):
                result = payload['results'][j] # Represents single result from search

                registration_num = result['registration']['registration_number']

                # Checks if site informatino has already been recorded (-1 returned if new site)
                if site_lookup(registration_num) == -1:
                    name = result['registration']['name']

                    '''
                    Checks if site is in United States - those outside the U.S. will use postal_code
                    field rather than zip_code and will have us_agent
                    '''
                    country_code = result['registration']['iso_country_code'] #use this to check if us_agent is needed
                    address = format_address(result, country_code)

                    fei_num = result['registration']['fei_number']
                    us_agent = result['registration']['us_agent'].get('name', '') + "\015" + result['registration']['us_agent'].get('bus_phone_area_code', '') + "-" + result['registration']['us_agent'].get('bus_phone_num', '')[:3] + "-" + result['registration']['us_agent'].get('bus_phone_num', '')[3:]+ "\015" + result['registration']['us_agent'].get('email_address', '') + "\015" + result['registration']['us_agent'].get('address_line_1', '') + "\015" + result['registration']['us_agent'].get('city', '') + " " + result['registration']['us_agent'].get('zip_code', '') + " " + result['registration']['us_agent'].get('state_code', '')
                    official_correspondent = result['registration']['owner_operator']['official_correspondent'].get('first_name', '') + " " + result['registration']['owner_operator']['official_correspondent'].get('middle_initial', '') + " " + result['registration']['owner_operator']['official_correspondent'].get('last_name', '') + "\015" + result['registration']['owner_operator']['official_correspondent'].get('phone_number', '')
                    
                    site = Site(name, address, registration_num, fei_num, us_agent, official_correspondent) # Creates new site object
                    sites.append(site) # Adds new site object to list 
                    registration_nums_to_indeces[registration_num] = len(sites) - 1

                # Retrieves relevant product activity types and stores them in array
                product_activities = retrieve_product_activities(result)

                # Retrieves product information in each database entry
                for k in range (0, len(result['products'])):
                    device_name = result['products'][k]['openfda'].get('device_name', " MISSING DEVICE NAME")
                    product_code = result['products'][k].get('product_code', " MISSING PRODUCT CODE")
                    device_class = result['products'][k]['openfda'].get('device_class', " MISSING DEVICE CLASS")
                    regulation_num = result['products'][k]['openfda'].get('regulation_number', " MISSING REGISTRATION NUMBER")

                    product = Product(device_name, product_activities, product_code, device_class, regulation_num)

                    sites[registration_nums_to_indeces.get(registration_num)].add_product(product)
                    
            # Only executes another query if not in last run of the loop
            if i != num_skips - 1:
                payload = doQuery(company_name, (i * 100))
                countDeviceClass(payload)

        countTotal()
        date = datetime.datetime.now()
        date1 = str(date).replace(':','-')
        row = ["Owner Operator Name: " + company_name + "\r\nTotal Number of Sites: " + str(len(sites)) + "\r\nTotal number of products across all sites: "
                            + str(classCount[0]) +"\r\n\nTotal Number of:\r\n\tClass 1 products: " + str(classCount[1]) + "\r\n\tClass 2 products: " + str(classCount[2]) +
                            "\r\n\tClass 3 products: " + str(classCount[3]) + "\r\n\tOther: " + str(classCount[4]),]
        ws.append(row)
        num = 1
        for i in sites:
            row = [str("Site " + str(num) + ": " + str(i.name) + "\015Address: " + i.address + "\015Registration Number: "
                             + i.registration_num + "\015FEI Number: " + i.fei_num + "\015US Agent: " + i.us_agent + "\015\015Official Correspondent: " + i.official_correspondent
                             + "\015\015Total Number of Products: " + str(count[countList.index(i.fei_num)]) + "\015\015Total Number of: \015Class 1 products: " + str(i.class1_count)
                             + "\015Class 2 products: " + str(i.class2_count) + "\015Class 3 products: " + str(i.class3_count) + "\015Other: " + str(i.classU_count))]
            ws.append(row)
            headers = ["Listing", "Description", "Activity", "Product Code", "Class", "Reg. Number"]
            ws.append(headers)
            prodNum = 1
            for j in i.product_list:
                activities = ""
                listNum = str(num) + "-" + str(prodNum)
                activity_index = 0
                for k in j.activities:
                    if activity_index != len(j.activities) - 1:
                        activities += str(k) + "\015"
                    else:
                        activities += str(k)
                    activity_index += 1
                des = "\"" + j.device_name + "\""
                row = [listNum, j.device_name, activities, j.product_code, j.device_class, j.regulation_num]
                ws.append(row)
                prodNum += 1
            num += 1

        wbName = str(company_name) + "_" + date1 + '.xlsx'
        wb.save(wbName)
                
        print('Done')

        count.clear()
        class1.clear()
        class2.clear()
        class3.clear()
        classU.clear()
        countList.clear()

        for i in range(0, len(classCount)):
            classCount[i] = 0

        sites.clear()

        registration_nums_to_indeces.clear()

    else:
        print("Invalid firm name.")
        


def countDeviceClass(payload):
    for i in range(0, len(payload['results'])):
        for j in range(0, len(payload['results'][i]['products'])):
            classCount[0] += 1
            if(countList.count(payload['results'][i]['registration']['fei_number']) == 0):
                countList.append(payload['results'][i]['registration']['fei_number'])
                if(payload['results'][i]['products'][j]['openfda'].get('device_class') == '1'):
                    classCount[1] += 1
                    class1.insert(countList.index(payload['results'][i]['registration']['fei_number']), 1)
                    class2.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    class3.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    classU.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                elif(payload['results'][i]['products'][j]['openfda'].get('device_class') == '2'):
                    classCount[2] += 1
                    class1.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    class2.insert(countList.index(payload['results'][i]['registration']['fei_number']), 1)
                    class3.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    classU.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                elif(payload['results'][i]['products'][j]['openfda'].get('device_class') == '3'):
                    classCount[3] += 1
                    class1.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    class2.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    class3.insert(countList.index(payload['results'][i]['registration']['fei_number']), 1)
                    classU.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                else:
                    classCount[4] += 1
                    class1.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    class2.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    class3.insert(countList.index(payload['results'][i]['registration']['fei_number']), 0)
                    classU.insert(countList.index(payload['results'][i]['registration']['fei_number']), 1)
            else:
                if(payload['results'][i]['products'][j]['openfda'].get('device_class') == '1'):
                    classCount[1] += 1
                    class1[countList.index(payload['results'][i]['registration']['fei_number'])] += 1
                elif(payload['results'][i]['products'][j]['openfda'].get('device_class') == '2'):
                    classCount[2] += 1
                    class2[countList.index(payload['results'][i]['registration']['fei_number'])] += 1
                elif(payload['results'][i]['products'][j]['openfda'].get('device_class') == '3'):
                    classCount[3] += 1
                    class3[countList.index(payload['results'][i]['registration']['fei_number'])] += 1
                else:
                    classCount[4] += 1
                    classU[countList.index(payload['results'][i]['registration']['fei_number'])] += 1

def countTotal():
    for i in range(0, len(countList)):
        count.insert(countList.index(countList[i]), class1[countList.index(countList[i])] + class2[countList.index(countList[i])] + class3[countList.index(countList[i])] + classU[countList.index(countList[i])])

#Enables enter key to be used to run program from input 
def on_return_keypress(event):
    get_data()

#Entry point for the exe to run
def main():
    # Main code that runs first we should wrap this into a function then run the function, but for time being this works.
    e1.grid(row=0, column=1, pady=8)
    e1.bind("<Return>", on_return_keypress)

    Button(master, text='Run', command=get_data).grid(row=3, column=0, sticky=W, pady=4)

    mainloop( )


if __name__ == '__main__':
    main()

