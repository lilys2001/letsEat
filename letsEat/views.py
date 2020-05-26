from django.shortcuts import render
import requests
import json
import random

def button(request):
    return output(request)
    # return render(request, 'home.html')

def output(request):
    api_key = "pdW_LVpLDwXRDHJKzUs2TO6pXNAcJpLGoxvGAAwGx170CaPuQhyOybkUfIPatnuoqt_PiZruq5P-MP9F-1l2PqWeoQo8qPAQ1_nUQgSlVVMF-b5fI5mCJqxY-Xl6XXYx"
    headers = {"Authorization": "Bearer %s" % api_key}

    send_url = 'http://api.ipstack.com/check?access_key=0060b34a33ed8e31edfc58a3966ae596'    # for regular deployment

    ip = request.META.get('HTTP_X_REAL_IP')    # for python anywhere
    send_url = 'http://api.ipstack.com/' + ip + '?access_key=0060b34a33ed8e31edfc58a3966ae596'

    r = requests.get(send_url)
    j = json.loads(r.text)

    lat = j['latitude']     # 37.871593
    long = j['longitude']   # -122.272743

    parameters = {
        "term": "restaurant",
        "latitude": str(lat),
        "longitude": str(long),
        "open_now": True
    }

    if request.POST.getlist('price'):
        parameters["price"] = ""
        for i in request.POST.getlist('price'):
            parameters["price"] += i + ", "
        parameters["price"] = parameters["price"][:len(parameters["price"]) - 2]

    r = requests.get("https://api.yelp.com/v3/businesses/search", params=parameters, headers=headers)

    restaurants = json.loads(r.text)
    filtered_restaurants = restaurants['businesses']

    # print(request.POST)
    #
    # print(request.POST.get('rating'))
    # print(request.POST.getlist('price'))
    # print(request.POST.get('distance'))

    if request.POST.get('rating'):
        filtered_restaurants = [r for r in filtered_restaurants if ('rating' in r and
                                r['rating'] >= int(request.POST.get('rating')))]

    if request.POST.get('distance'):
        filtered_restaurants = [r for r in filtered_restaurants if ('distance' in r and
                                r['distance'] <= int(request.POST.get('distance')))]

    if request.POST.get('transactions') and request.POST.get('transactions') != 'eatthere':
        filtered_restaurants = [r for r in filtered_restaurants if ('transactions' in r and
                                request.POST.get('transactions') in r['transactions'])]

    # print(filtered_restaurants)

    if filtered_restaurants:
        rand = random.choice(filtered_restaurants)
        rName = rand["name"]
        rLocation = rand["location"]["display_address"]
        rURL = rand['url']

        return render(request, 'home.html', {'rName': rName, 'rAddress': rLocation[0], 'rCityStateZIP': rLocation[1],
                                             'rURL': rURL, 'ip': ip})
    else:
        return render(request, 'home.html', {'rName': "Sorry, there are no open restaurants with the filters you chose. "
                                                      "Try pressing the 'Let's Eat' button without selecting filters!",
                                             'rAddress': '', 'rCityStateZIP': '', 'rURL': '', 'ip': ip})
