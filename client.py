import json, requests
from pprint import pprint
from operator import itemgetter

API_BASE="http://data.coding.kitchen/api/"


def get_url(url):
    
    resp = requests.get(url)
    if resp.status_code!=200:
        return None

    return json.loads(resp.text)

def get_json(group, id):
    url=API_BASE+group+'/'+str(id)
    return get_url(url)

def get_state(stateAbbr):
    return get_json("state", stateAbbr)


def get_state_city(stateAbbr):
    state=get_state(stateAbbr)
    statename=state["name"]
    cities=state['cities']
    cityList=[]

    for url in cities:
        city=get_url(str(url))
        cityList.append((statename, city['name']))

    return cityList

def get_state_capital(stateAbbr):
    state=get_state(stateAbbr)
    cities=state['cities']
    for url in cities:
        city=get_url(str(url))
        if city['is_capital']:
             return (state['name'], city['name'])

    return (state['name'], "None")
            
def print_all_state_capital():
    url=API_BASE+"states/"
    states=get_url(url)
    for state in states:
        print_state_capital(state["abbreviation"])

def print_state_capital(stateAbbr):
    state, capital=get_state_capital(stateAbbr)
    print("State: {} > Capital: {}".format(state, capital))

#get all unemployed people

def get_current_job(id):
    person=get_json("person", id)
    jobUrl=person["current_job"]
    if jobUrl:
        department=get_url(jobUrl)
        return (person["first"]+" "+person["last"], department["name"])
    else:
        return (person["first"]+" "+person["last"], "None")


def print_all_jobs(unemployed=0):
    id=1
    people=get_json("people", id)
    while people!=None:
        print(id)
        for p in people:
            name, job=get_current_job(p["id"])

            if unemployed:
                if job=="None":
                    print("Name: {} > Current Employment: {}".format(name, job))
            else:
                print("Name: {} > Current Employment: {}".format(name, job))
        
        id=id+1
        people=get_json("people", id)


#get club membership

def get_current_club(id):
    person=get_json("person", id)
    memberUrl=person["current_membership"]
    if memberUrl:
        club=get_url(memberUrl)
        return (person["first"]+" "+person["last"], club["name"])
    else:
        return (person["first"]+" "+person["last"], "None")

def print_all_clubs(noClub=0):
    id=1
    people=get_json("people", id)
    while people!=None:
        print(id)
        for p in people:
            name, club=get_current_club(p["id"])

            if noClub:
                if club=="None":
                    print("Name: {} > Curent Club: {}".format(name, club))
            else:
                print("Name: {} > Current Club: {}".format(name, club))
        
        id=id+1
        people=get_json("people", id)


#get all league in the city

def get_club_by_league(leagueid):
    league=get_json("league", leagueid)
    clubList=[]
    for clubUrl in league["clubs"]:
        club=get_url(clubUrl)
        cityUrl=club["city"]

        stateUrl=get_url(cityUrl)["state"]

        clubList.append((club["name"], cityUrl, stateUrl))

    return clubList

def get_club_by_sports(sportsName):
    leagues=get_url(API_BASE+"leagues/")
    leaguesList=[l["id"] for l in leagues if l["sport"]==sportsName]
    
    clubList=[]
    for lid in leaguesList:
        print(lid)
        clubList=clubList+get_club_by_league(lid)

    return clubList

def print_state_city_club(sportsName):

    clubList=get_club_by_sports(sportsName)

    clubDict={}

    for club in clubList:
        name, cityUrl, stateUrl=club

        if clubDict.get(stateUrl):
            if clubDict.get(stateUrl).get(cityUrl):
                clubDict[stateUrl][cityUrl].append(name)
            else:
                clubDict[stateUrl][cityUrl]=[name]
                
        else:
            clubDict[stateUrl]={}
            clubDict[stateUrl][cityUrl]=[name]
    

    for key, value in clubDict.items():
        state=get_url(key)["name"]
        print("State: {}".format(state))
        print("---------")

        for k, v in value.items():
            city=get_url(k)["name"]
            print("City: {}".format(city))
            
            for team in v:
                print("\t {}".format(team))

    print("======\n")

#find all state with exchange
def state_exchange():

    url=API_BASE+"exchanges/"

    exchanges=get_url(url)
    stateList=[]

    for ex in exchanges:
        city=get_json("city", ex["city"])

        stateURL=get_url(city["state"])

        stateList.append(stateURL["name"])

    print(stateList)

#all company with finance department
def department_in_company(departmentName):
    dsid=1

    dList=get_json("departments", dsid)

    while dList!=None:
        for department in dList:
            if department["name"]==departmentName:
                company=get_json("company", department["company"])
                print(company["name"])

        dsid=dsid+1
        dList=get_json("departments", dsid)


#find top 5 companies in the industry with revenue

def find_top_companies(industryName, nrank):


    cid=1
    companyList=get_json("companies", cid)
    rankList=[]

    while companyList!=None:
        for c in companyList:
            company=get_url(c["api"])
            iName=""
            if company.get("industry"):
                iName=company["industry"]
            else:
                iName="None"

            if iName==industryName:
                # print((company["name"], company["revenue"]))
                rankList.append((company["name"], company["revenue"]))
        
        cid=cid+1
        companyList=get_json("companies", cid)

    rankList.sort(key=itemgetter(1), reverse=True)

    if len(rankList) < nrank:
        nrank=len(rankList)

    for i in range(nrank):
        print(rankList[i])

find_top_companies("Petroleum", 5)
