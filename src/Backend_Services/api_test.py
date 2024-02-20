import requests
import json
import re

def pull_json():
    # Omeka Collection Details
    url = 'http://georgeeliotarchive.org/api'
    collection_id = '66'

    # Construct Request URL
    url = f'{url}/items?collection={collection_id}'

    # Make request
    response = requests.get(url)


    if response.status_code == 200:
        items = response.json() #collection items
        
        #Create new dictionary with desired format and items
        data = []
        for item in items:
            json_item = {}
            for element in item['element_texts']:
                json_item[element['element']['name']] = element['text'] 
            data.append(json_item)

            
        # Save the data to a JSON file
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
            
        print("Succeeded")
    else:
        print(f'Failed. Status code: {response.status_code}')
        
def test_relation():
    file = open('data.json')
    data = json.load(file)
    for i in data:
        if 'Relation' in i:
            if i['Title'] != i['Relation']:
                print(i['Relation'] + "\n" + i['Title'])

def test_subject():
    file = open('data.json')
    data = json.load(file)
    subjects = []
    for i in data:
        if 'Subject' in i and i['Subject'] not in subjects:
            subjects.append(i['Subject'])
    print(subjects)

def test_all(): #need to not include description
    file = open('data.json')
    data = json.load(file)
    dump = []
    for i in data:
        if 'Title' not in i or 'Subject' not in i or 'Description' not in i or 'Source' not in i:
            dump.append(i)
    print(dump)
    
#we want an array of work items that contain two arrays of place items or character items that are a name and a description each
def organize_by_work():
    file = open('data.json')
    data = json.load(file)
    #compile list of works
    works = []
    dump = []
    final = {}
    for i in data:
        if 'Source' in i:
            source = i['Source']
            source = re.sub('<[^<]+?>', '', source) #test this out and make sure it's gonna work every time
            source = source.strip()
            if source.startswith("Multiple"):
                source = re.search('\(([^)]+)', source).group(1) #test to make sure it's grabbing correctly
                if "Felix Holt, the Radical" in source: #special case for titles that have a comma in them, need to update list or think of algorithm to do this automatically
                    source = source.replace("Felix Holt, the Radical","FHTR")
                sources = source.split(",")
                for s in sources:
                    s = s.strip()
                    if s == "FHTR":
                        s = "Felix Holt, the Radical"
                    if s not in works:
                        works.append(s)
            else:
                if  source not in works:
                    works.append(source)
    #iterate again through each item, for each of its works, add it to the master json under it's correct place
    #organize by work, and then by either place or character or item
    for w in works:
        work = {
            "characters": [],
            "places": [],
            "misc": []
        }
        final[w] = work
    for i in data:
        if 'Source' in i and 'Subject' in i and 'Title' in i:
            if 'Description' not in i:
                i['Description'] = "Description not found"
            for w in works:# I think we could change this to not make it iterate over all the works if it's causing performance issues by simply adding it to each work array that its Source contains
                if w in i['Source']:
                    if i['Subject'] in ['Character Name','Pet Name','Real Name','Historical Name']:
                        item = {
                            'name': i['Title'],
                            'desc': i['Description']
                        }
                        final[w]['characters'].append(item)
                    elif i['Subject'] in ['Place','Fictional Place','Real Place']:
                        item = {
                            'name': i['Title'],
                            'desc': i['Description']
                        } 
                        final[w]['places'].append(item)
                    else:
                        item = {
                            'name': i['Title'],
                            'desc': i['Description']
                        }
                        final[w]['misc'].append(item)
        else:
            dump.append(i)
    with open('final.json', 'w') as file:
        json.dump(final, file, indent=4)    
            
   
pull_json() 
#test_relation()
#test_subject()
#test_all()
organize_by_work()
