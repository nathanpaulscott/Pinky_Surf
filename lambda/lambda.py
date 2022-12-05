import re
from datetime import datetime, timedelta, timezone
import os
import json
import sys
import time
import base64
import requests
from bs4 import BeautifulSoup
import html5lib

import globals





def ind2str(ind):
    '''
    converts an integer offset to the required string offset for the stormsurf url
    '''
    ind = str(int(float(ind)))
    if ind == '0': ind = '00'
    return ind


def get_image(url, b64, gp):
    '''
    downloads the image from the given url and returns b64 encoded or the file object depending on b64 being true/false
    '''
    r = requests.get(url)
    if b64:
        return base64.b64encode(r.content).decode("utf-8")
    return r.content


def get_images_sync_requests(urls, b64):
    """
    performs synchronous get requests
    """
    # use session to reduce network overhead
    session = requests.Session()
    output = [session.get(url).content for url in urls]
    if b64:
        output = [base64.b64encode(x).decode("utf-8") for x in output]
    return output



def get_full_set(gp):
    full_set = []
    for item in gp.data:
        for ind in range(gp.data[item]['min_offset'], gp.data[item]['max_offset'], 6):
            key = '{}{}{}'.format(gp.data[item]['filename']['prefix'], ind2str(ind), gp.data[item]['filename']['suffix'])
            full_set.append(key)
    return set(full_set)








def fetch(gp):
    '''
    the client requests a chunk of images
    1) if you use get, add them as get params and they will be added to the url
    params = {'offsets':'00,6,12,18,24', 'pw':'your password'}
    r = requests.get(url=url, params=params)
    or
    params = {'os1':'00,'os2':6,'os3':12,'os4':18,'os5':24', 'pw':'your password'}
    r = requests.get(url=url, params=params)
    
    2) if you use post, you can add the offsets as data as a real json object, they will not be added to the url, it will all be in the request body
    data = {'offsets':['00,6,12,18,24'], 'pw':'your password'}
    r = requests.post(url=url, data=data)

    if I send from client js as ajax post like this:
    fetch_data = {'offsets':['00','6','12','18'], 'pw':'your password'};
    $.ajax({
        type: "POST",
        url: "some url/fetch",
        data: JSON.stringify(fetch_data),
        success: function(response){ 
            do somehting wiht response;
        }
    });

    In lambda, I read the data with:
    data = json.loads(event['body'])
    offsets = data['offsets']
    pw = data['pw']

    '''
    try:
        #get this chunk of images, 4 urls/images per offset and send back as b64 encoded json string
        #can try to send back file objects, but if more than one, I think it will not work
        urls = []
        offset_key = []
        for offset in gp.offsets:
            offset_s = ind2str(offset)
            urls += ['{}{}{}'.format(x['url']['prefix'], offset_s, x['url']['suffix']) for x in gp.data]
            offset_key += [offset_s]*4
        #get the urls
        print(urls)
        images = get_images_sync_requests(urls, b64=True)
        #format for the client object whcih is {ind1:[img1, img2, img3, img4], ind2:[img1, img2...]}
        output = {}
        for i, offset in enumerate(offset_key):
            output[offset] = output.get(offset, []) + [images[i]]
        
        #send back to the client
        response = {
            'statusCode': 200,
            'headers': {"Content-Type": "application/json"},
            'body': json.dumps(output)
            #'headers': {"Content-Type": "image/png"},
            #'body': images[0]
        }
        return response

    except Exception as e:
        gp.error_exit(str(e))









def handler(event, context):
    '''
    testing this in the terminal
    -----------------------------------
    this is the simulated Get req for the intial page to run in terminal:
    curl -X GET https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/index?pw=DfThGfDjNv4D3F67YtgB98HGb
    
    this is the simulated post req from your terminal:
    curl -X POST https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/fetch -H "pw:DfThGfDjNv4D3F67YtgB98HGb" --data "{\"offsets\": [\"6\"]}"
    '''
    #make your globals object
    gp = globals.global_params()

    #process your incoming request params
    #http method is in event['requestContext']['http']['method']
    #route is in event['requestContext']['http']['path']
    #headers are in event['headers']
    
    if event['httpMethod'] == 'POST' and event['path'] == '/fetch':
        #post asking for some images from a list of offsets
        gp.offsets = json.loads(event['body'])['offsets']
        response = fetch(gp)
        return response
    
    else:
        raise Exception('Only supports GET and POST')


