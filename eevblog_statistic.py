from bs4 import BeautifulSoup
import urllib2
import urlparse
from os import path
from wordcloud import WordCloud
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import sys

import json
import urllib

#user input
api_key=open('api-key', 'r').read() #copy your api key into api-key file
replace={ "Today at": "July 16, 2017,", "Yesterday at": "July 15, 2017,"}
url="http://www.eevblog.com/forum/contests/giveaway-rohde-schwarz-rtb2004-oscilloscope/?all"


#Load page
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
response = opener.open(url)
page = response.read()

#pares page
soup = BeautifulSoup(page, 'html.parser')
data=[]
cvimo=0;
for post in soup.find('div', id="forumposts").form.find_all('div', recursive=False):
    aktentry={}
    post=post.find('div', class_="post_wrapper")
    poster=post.find('div', class_="poster")
    aktentry['user_name']=poster.h4.a.text
    aktentry['user_id']=urlparse.parse_qs(urlparse.urlparse(poster.h4.a['href']).query)['u']
    if poster.find('li', class_="postgroup")!=None:   
        aktentry['user_postgroup']=poster.find('li', class_="postgroup").text
    else:
        aktentry['user_postgroup']=""
    aktentry['user_postcount']=poster.find('li', class_="postcount").text.split(" ")[1]
    aktentry['text']=post.find('div', class_="postarea").find('div', class_="post").text
    if post.find('div', class_="moderatorbar").find("em")!=None:
        aktentry['edit']=post.find('div', class_="moderatorbar").find("em").text.split("Edit:")[1].split(" by")[0].strip()
    else:
        aktentry['edit']=None
    aktentry['date']=post.find('div', class_="keyinfo").find("div",class_="smalltext").text.split("on:")[1][:-2].strip()

    videos=[]
    for iframe in post.find('div', class_="postarea").find('div', class_="post").find_all("iframe"):
        videos.append(iframe["src"])
    for a in post.find('div', class_="postarea").find('div', class_="post").find_all("a"):
        videos.append(a["href"])
        
    aktentry['video']=[]
    for v in videos:    
        if len(v.split("youtu.be/"))==2:
            aktentry['video'].append(v.split("youtu.be/")[1].split("?")[0])
        elif len(v.split("www.youtube.com/embed/"))==2:
            aktentry['video'].append(v.split("www.youtube.com/embed/")[1].split("?")[0])
        elif len(v.split("www.youtube.com/watch?v="))==2:
            aktentry['video'].append(v.split("www.youtube.com/watch?v=")[1].split("&")[0])
        elif len(v.split("player.vimeo.com/video/"))==2:
            cvimo=cvimo+1;
    
    if poster.find('li', class_="gender")!=None:   
        aktentry['user_country']=poster.find('li', class_="gender").img["alt"]
    else:
        aktentry['user_country']=""
    
    data.append(aktentry)

data.remove(data[0]) #ignore post creator
print "#"+str(len(data))

# Generate a word cloud image
text=""
for t in data:
    text=text+t["text"];

d = path.dirname(__file__)
wordcloud = WordCloud(width=600,height=600).generate(text)
image = wordcloud.to_image()
image.save("cloud.png")

#Generate post date graph
dates=[]
dmin=datetime.now()+timedelta(days=100000)
dmax=datetime.now()-timedelta(days=100000)
for t in data:
    date=t["date"]
    for n,r in replace.iteritems():
        date=date.replace(n,r)
    date = datetime.strptime(date, '%B %d, %Y, %I:%M:%S %p')
    if date >dmax:
        dmax=date
    if date <dmin:
        dmin=date
        
    dates.append(date)
dmin= dmin.replace(hour=0, minute=0, second=0)
dmax= dmax.replace(hour=0, minute=0, second=0)+timedelta(days=1)
name=[]
count=[]
date=dmin
while date < dmax:
    c=0;
    for d in dates:
        if d>date and d<=date+timedelta(days=1):
            c=c+1;
    name.append(date.strftime("%B %d"))
    count.append(c)
    date=date+timedelta(days=1);
    
y_pos = np.arange(len(name))
plt.clf()
plt.bar(y_pos, count, align='center', alpha=0.5)
mean=reduce(lambda x, y: x + y, count) / len(count)
plt.plot([0, len(count)-1], [mean, mean], "k--")
plt.xticks(y_pos, name, rotation=30)
plt.ylabel('Posts')
plt.title('Posts per day:')
image = plt.savefig("post_per_day.png")

#Post per hour
name=[]
count=[]
for h in range(0,24):
    c=0;
    for d in dates:
        if h==d.hour:
            c=c+1;
    name.append(str(h)+"h")
    count.append(c)
    
y_pos = np.arange(len(name))
plt.clf()
plt.bar(y_pos, count, align='center', alpha=0.5)
plt.xticks(y_pos, name, rotation=30)
plt.ylabel('Posts')
plt.title('Post per hour:')
image = plt.savefig("posts_per_time.png")



#Postes per User
posts=[]
for t in data:
    posts.append(int(t["user_postcount"]))

y_pos = np.arange(len(posts))
plt.clf()
plt.bar(y_pos, posts, align='center', alpha=0.5)
mean=reduce(lambda x, y: x + y, posts) / len(posts)
plt.plot([0, len(posts)], [mean, mean], "k--")
plt.ylabel('Posts')
plt.title('Posts per User:')
image = plt.savefig("posts_per_user.png")

name=[]
count=[]
lv=0
for v in [3,6,8,10,30,80,100,300,800,sys.maxint]:
    c=0;
    for t in posts:
        if lv<=t and v>=t:
            c=c+1;
    if v==sys.maxint:
        name.append(str(lv)+"-MAX")
    else:
        name.append(str(lv)+"-"+str(v))
    count.append(c)
    lv=v+1;
    
y_pos = np.arange(len(name))
plt.clf()
plt.bar(y_pos, count, align='center', alpha=0.5)
plt.xticks(y_pos, name, rotation=30)
plt.ylabel('Users')
plt.title('Users per Post count:')
image = plt.savefig("users_per_portcount.png")

#videos durations
ids=[]
for t in data:
    if len(t["video"])>0:
        ids.append(t["video"][0])

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ] 

idss= split_list(ids, wanted_parts=len(ids)/40+1)

durs=[]
for ids in idss:
    sids=""
    for id in ids:
      sids=sids+id+","
    searchUrl="https://www.googleapis.com/youtube/v3/videos?id="+sids+"&key="+api_key+"&part=contentDetails"
    response = urllib.urlopen(searchUrl).read()
    for dur in json.loads(response)['items']:
        dur=dur['contentDetails']['duration']
        if "M" in dur and "S" in dur:
            m=dur.split("PT")[1].split("M")[0]
            s=dur.split("M")[1].split("S")[0]
        elif "M" not in dur and "S" in dur:
            m=0
            s=dur.split("PT")[1].split("S")[0]
        elif "M" in dur and "S" not in dur:
            m=dur.split("PT")[1].split("M")[0]
            s=0
        else:
            m=0
            s=0
        dur=int(m)*60+int(s)
        durs.append(dur)

def dur_to_string(dur):
    return str(dur/60).zfill(1)+":"+str(dur%60).zfill(2)
      
name=[]
count=[]
lv=0
for v in [30,45,60,75,90,105,110,115,120,125,130,135,150,sys.maxint]:
    c=0;
    for t in durs:
        if lv<=t and v>=t:
            c=c+1;
    if v==sys.maxint:
        name.append(dur_to_string(lv)+"-MAX")
    else:
        name.append(dur_to_string(lv)+"-"+dur_to_string(v))
    count.append(c)
    lv=v+1;
    
y_pos = np.arange(len(name))
plt.clf()
plt.bar(y_pos, count, align='center', alpha=0.5)
plt.xticks(y_pos, name, rotation=30)
plt.ylabel('Videos')
plt.title('Videos per length:')
image = plt.savefig("videos_per_length.png")             

#Posts per country
countries={}
for t in data:
    if t['user_country'] not in countries:
        countries[t['user_country']]=0;
    countries[t['user_country']]=countries[t['user_country']]+1;

name=[]
count=[]
for country in sorted(countries.iterkeys()):
    if country=="":
        name.append("None")
    else:
        name.append(country)
    count.append(countries[country])
    
y_pos = np.arange(len(name))
plt.clf()
plt.bar(y_pos, count, align='center', alpha=0.5)
plt.xticks(y_pos, name, rotation=90,size=8)
plt.ylabel('Posts')
plt.title('Posts per country:')
image = plt.savefig("posts_per_country.png")             





print "done"

