# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 16:29:41 2018

@author: lenovo
"""

import json
import warnings
warnings.filterwarnings("ignore")
print ("Content-type: text/html\n\n")

import requests
from requests.auth import HTTPBasicAuth

#-----------------Get WebId Part-----------------------
def getdata(url):
    """ Reads the url data, enters the username and password, ignore the ssl certificate and return the response as json string
    
    Arguments:
        url {[string]} -- [api url link]
    
    Returns:
        [string] -- [json response]
    """
    r = requests.get(url, auth=HTTPBasicAuth('bdgczma','*S8541196i88'), verify=False)
    if (r.status_code == 200):
        
        return r.json()
    else:
        print ("No data to access")
        return None

addr = "https://172.18.53.165/piwebapi/assetservers/S0PuLYsdTuuUqI0OYHjD6iEwV0lOLURWSExVS09UTVJW/assetdatabases"

allTheData =[]

def recData(url, n, itt, sub_node):
    """Recursive function to return only children objects that have data related to them.
    
    Arguments:
        url {string} -- url to the piwebapi 
        n {int} -- number of iterations before stop the recursion
        itt {int} -- The current iterations - just for counting the heirarchy (default: {0})
        sub_node {dictionary} -- the dictionary that contains different levels of nodes
    """
    hch = False
    if n >0:
        a = getdata(url)
        for i in a["Items"]:          
            key =  str(itt) + " - " + i["Name"]
            sub_node.update({key:i["WebId"]})
            for k, v in i.items():
                if k == "HasChildren":
                    if v == True:
                        hch = True
                elif k == "Path":
                    path = v
                elif k == "WebId":
                    webid = v
                elif k == "Links":
                    if hch:
                        recData(v["Elements"], n-1, itt+1, sub_node)
                    else :
                        sub_node.update({path:webid})
                                                       
def save_model_to_json(data, file_name):
    """Store the dictionary result into a json file.
    
    Arguments:
        data {dictionary} -- dictionary that includes different levels of elements 
        file_name {string} -- the filename of output file
    
    Keyword Arguments:
        itt {int} -- The current iterations - just for counting the heirarchy (default: {0})
    """
    with open(file_name, 'w') as fp:
        json.dump(data, fp)
        
def getlist(addr):
    """Main function to get the list of nodes of different levels.
    
    Arguments:
        addr {string} -- url to the piwebapi asset server
    
    Keyword Arguments:
        node {dictionary} -- the dictionary that contains all nodes
    """
    node = {}
    a = getdata(addr)
    count = 0
    for i in a["Items"]:
        sub_node = {}
        sub_node[0] = i["Name"]
        b = i["Links"]["Elements"]
        c = getdata(b)
        for j in c["Items"]:
            sub_node[1] = j["Name"]
            d = j["Links"]["Elements"]
            recData(d,8,2,sub_node)
        node[count] = sub_node
        count += 1
    #print (node)
    save_model_to_json(node, "result.json")
    return node

#---------------Search Function Part---------------------
leaf = "\\" #the path of the leaf
def getall(word, data):
    """Main function to get the leaves which contain the search word.
    
    Arguments:
        word {string} -- the search word
        data {dictionary} -- the dictionary of all the nodes
    
    Returns:
        alllis {list} -- list that include all the leaves that contain the search word
    """
    alllis = []
    for keys in data:
        value = data[keys]
        for sub_keys in value:
            if (word in sub_keys):
                if (" - " in sub_keys):
                    pass
                else:
                    alllis.append(sub_keys)     
    return alllis
              
def getwebid(subset, word):
    """After getting the final leaf path, go through the original dictionary to get the webid.
    
    Arguments:
        subset {dictionary} -- the dictionary of all the nodes that contain the word
        word {string} -- the search word
    
    Returns:
        value[item] -- the webid of the search word
    """
    for keys in subset:
        value = subset[keys]
        for item in value:
            if word in item:
                return value[item]
            
def getlist2(subset):
    """For all the leaves that contain the word, split the string before them.
    
    Arguments:
        subset {dictionary} -- the dictionary of all the nodes that contain the search word
    
    Returns:
        lis {list} -- the list that contain the information of different levels before the search word
    """
    lis = []
    for sub_keys in subset:
        point = sub_keys.find(word)
        bf = sub_keys[:point]
        ls = bf.split("\\")
        for item in range(2,len(ls)):
            if len(ls[item]) < 1:
                continue
            key = str(item) + ' - ' + ls[item]
            if key in lis:
                pass
            else:
                lis.append(key)
    return lis

def getaflist(word,subset):
    """For all the leaves that contain the word, split the string after them to get next step selection.
    
    Arguments:
        subset {dictionary} -- the dictionary of all the nodes that contain the search word
        word {string} -- the search word
    
    Returns:
        lis2 {list} -- the list that contain the information of different levels after the search word
    """
    lis2 = []
    for sub_keys in subset:
        if word in sub_keys:
            point = sub_keys.find(word)
            af = sub_keys[point + len(word):]
            ls2 = af.split("\\")
            for item2 in range(0,len(ls2)):
                if len(ls2[item2]) < 1:
                    continue
                key = str(item2) + ' - ' + ls2[item2]
                if key in lis2:
                    pass
                else:
                    lis2.append(key)
    return lis2

def transform(lis):
    """For better selection, transform the list into dictionary
    
    Arguments:
        lis {list} -- The list that contain all the levels key nodes which to be selected
    
    Returns:
        dic1 {dictionary} -- the key nodes of different levels
    """
    dic1 = {}
    for item in lis:
        key = item[:1]
        if key in dic1:
            dic1[key].append(item[4:])
        else:
            value = [item[4:]]
            dic1[key] = value
    return dic1
  
a = []
def select(dic1, subset, leaf):
    """Recursive function to return only leaf that fits all the selections on different levels.
    
    Arguments:
        dic1 {dictionary} -- the key nodes of different levels
        subset {dictionary} -- the dictionary of all the nodes that contain the search word
        leaf {string} --  the full string of search
    
    Key Argument：
        a {list} -- since string will not be stored, the final leaf string will be stored as a[0]
    """
    if bool(dic1):
        for item in dic1:
            if len(dic1[item]) == 1:
                leaf = leaf + dic1[item][0] + '\\'
            else:
                subleaf = leaf.split('\\')
                for i in subleaf:
                    if len(i) < 1:
                        subleaf.remove(i)
                print ("\nFor level " + str(len(subleaf)+int(item)) + ", your selection is:")
                print (dic1[item])
                level = input()
                leaf = leaf + level + '\\'
                
            lis2 = getaflist(leaf, subset)
            if len(lis2) == 0:
                a.append(leaf)
                break
            dic2 = transform(lis2)
            select(dic2, subset, leaf)
            break

#---------------Time Select Function Part---------------------
def getattributes(webid):
    """This function is used to use the webid got before to get all attributes and their addresses.
    
    Arguments:
        webid {string} --  the webid of search
    
    Return：
        attr {dictionary} -- the keys are the attributes and the values are corresponding web address
    """
    url = "https://172.18.53.165/piwebapi/streamsets/" + webid + "/value"
    a = getdata(url)
    attr = {}
    for i in a["Items"]:
        attr[i["Name"]] = i["Links"]["Source"]
    return attr

def gettime():
    """This function is used to let user select the time period of values.
    
    Return：
        stamp {string} -- the correct parameter of time string
    """
    print ("""Select start time:
        1 - Last 1 hours, 2 - Last 6 hours, 3 - Last 12 hours, 4 - Last 24 hours,
        5 - Last 7 days, 6 - Last 15 days, 7 - Last 30 days, 8 - This Year
        """)
    time =  input()
    stamp = "?startTime="
    if time == '1':
        stamp += "*-1h"
    elif time == '2':
        stamp += "*-6h"
    elif time == '3':
        stamp += "*-12h"
    elif time == '4':
        stamp += "*-24h"
    elif time == '5':
        stamp += "*-7d"
    elif time == '6':
        stamp += "*-15d"
    elif time == '7':
        stamp += "*-30d"
    elif time == '8':
        stamp += "*01/01"
    else:
        print ("Invalid input")
        stamp = gettime()
    return stamp

#first, get the node of different levels
data = getlist(addr)

#store the result as json file
with open('result.json') as f:
    data = json.load(f)

#Get the search word
print ("Please enter the word you want:")
word = input()
word = '\\' + word + '\\'

#find all the leaves that contain the search word
subset = getall(word,data)

#Get the candidate list of different levels
lis = getlist2(subset)
print (lis)

dic1 = transform(lis)
print (dic1)

#According to user's requirement, find the final target leaf
select(dic1, subset, leaf)
print (a[0])

#Back to search the original dictionary to get the webid
webid = getwebid(data, a[0][:-1])
print (webid)

#Get the attributes of leaf points
attr = getattributes(webid)
print ("\nPlease enter the attribute you want:")
for key in attr:
    print (key, end=', ')
word = input()

#After the user selection, get the correct web address of recorded data
data = getdata(attr[word])
record = data["Links"]["RecordedData"]
print (record)

#Call get time function to get the correct time parameter
timestamp = gettime()
record = record + timestamp

#Get data points
data = getdata(record)
for i in data["Items"]:
    timestamp = i["Timestamp"]
    value = i['Value']['Value']
    print ("Timestamp: ", timestamp, " Value: ", value)