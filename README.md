# Pinky_Surf

This is a simple web app using aws api-gateway rest-api as an https proxy.  The backend is S3 for static and lambda for auth and dynamic content.

I basically scrape 4 images from other websites that show maps of ocean conditions going out 180hrs into the future in 6 hr intervals.  For one of the images (surface level pressure) it also goes back 216 hrs.  It shows these images side by side where you can swipe through them or use the left/right arrow keys.  You can click the down load icon to down load all images to the browser for faster movement through them.  This was the breif from the customer "Pinky" who paid me nothing.  I was unable to build this in a browser thanks to CORS, and "Pinky" can use Python or anything complex, so I had to wait until I could set up a serverless system in AWS to get it down.

you can see it in action a this url:

https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/index?pw=DfThGfDjNv4D3F67YtgB98HGb
