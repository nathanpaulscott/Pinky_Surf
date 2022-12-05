This version is the best:
--------------------------------
1) uses api-gateway rest-api as a proxy offsering one https domain to the browser.
https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com

2) the initial url is a get request including a query string parameter pw='some random password'
https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/index?pw=DfThGfDjNv4D3F67YtgB98HGb
this routes the call to static pages on s3, do not need to enable web hosting on s3, it just reads the data from s3 and returns it via the proxy
the main complexity here is to make roles with policies for api gateway to interact with s3
test with:
curl -X GET https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/index?pw=DfThGfDjNv4D3F67YtgB98HGb

3) the js in the static pages sets up listeners in teh browser DOM to send POST requests with pw='some password' in the header and a stringified json object for the offsets list in the body
https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/fetch
you can simulate it in your terminal with:
curl -X POST https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/fetch -H "pw:DfThGfDjNv4D3F67YtgB98HGb" --data "{\"offsets\": [\"6\"]}"
NOTE: in api gateway, you need to setup lambda integration as proxy, meaning that api gateway will pass through the post req straight to the lambda instead of trying to map it, although you can map it if you want also


4) authosisation is half assed, just testing features really,
I have pw checking authorized by a separate lambda function and the authoriser lambda also returns the API key on successful pw check.
api gateway checks on the auth return if the api key is in it, what is the point of doing it this way?  not much, jsut testing features
you could set it up to require an api key instead of the pw and to read it from the request header (GET and POST), 

Flow is:
1) https Get req => api GW rest api (carry pw)
2) api GW to auth lambda (check pw)
3) if pw ok, return allow + API key to api GW
4) if positive response and API key is ok, API GW fetches static html from S3 html and passes it back to the client
5) the html in teh client has the relative paths of the css and js that are then requested (GET with pw) by the browser via the same process as above (auth, then fetched from s3 and passed back the client
5) js in client then sends POST req to api GW (with pw in header and req data in body) to the api GW /fetch route.
6) api GW authorizes the POST req similarly to the GET req except it gets the pw from the header as opposed to the qeury string, it sends back a sucess and the API key
7) on success the API GW invokes the given lambda which retrieves the desired data from some 3rd party url, repackages it and passes it back to api GW in a json response
8) API GW passes the response back to the client still in json

NOTE: for the option where the client asks to download ALL images (250+ images), it chunks them into ~10 POST requests, each one containing 20+ urls, previously, I sent 100s of concurrent lambda req for this...



to do:
1) just use the API key as opposed to the pw, it makes more sense, do not need the pw
I think you can pu thte api key in teh query string for get and header for post req
2) take a look at cloud front, apparently it does the same thing
3) look at cloud formation for ci/cd















