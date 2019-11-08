from bs4 import BeautifulSoup
import urllib
import re
import time
import ssl

ANI24_URL = 'https://ani24zo.com'

VIDEO_READ_SIZE = 2048

searchKeyword = input('검색어: ')

print('%s/ani/search.php?%s' % (ANI24_URL, urllib.parse.urlencode({'query': searchKeyword})))
with urllib.request.urlopen(urllib.request.Request('%s/ani/search.php?%s' % (ANI24_URL, urllib.parse.urlencode({'query': searchKeyword})), headers={'User-Agent': 'Mozilla/5.0'})) as response:
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    animeList = []

    for i in map(str, soup.find_all('a', {'class': 'subject'})):
        animeList.append((re.search(r'(?<=\">).*(?=<\/a>)', i).group(),
                          re.search(r'(?<=href=")[^"]*(?=")', i).group()))
    
    for i in range(len(animeList)):
        print(' %d. %s' % (i + 1, animeList[i][0]))
    
    animeTargetIndex = None
    while True:
        try:
            animeTargetIndex = int(input(' > ')) - 1
            
            break
        except:
            pass

with urllib.request.urlopen(urllib.request.Request('%s%s' % (ANI24_URL, animeList[animeTargetIndex][1]), headers={'User-Agent': 'Mozilla/5.0'})) as response:
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    animeVideoListDivSoup = BeautifulSoup(str(soup.find('div', {'class': 'ani_video_list'})), 'html.parser')

    for i in map(str, sorted(animeVideoListDivSoup.find_all('a'))):
        videoName = re.search(r'(?<=<div class="subject">).*(?=</div>)', i).group()
        
        with urllib.request.urlopen(urllib.request.Request('%s' % (re.search(r'(?<=<a href=").*(?=">)', i).group()), headers={'User-Agent': 'Mozilla/5.0'})) as videoSite:
            iframeLink = ''.join(re.findall(r'(?<=ifr_adr \+= ")[^"]*(?=")', videoSite.read().decode('utf-8')))

            with urllib.request.urlopen(urllib.request.Request('https://%s' % (iframeLink), headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'a'})) as iframeSite:
                videoLink = re.search(r'(?<=file":")[^"]*(?=")', iframeSite.read().decode('utf-8')).group()

                f = open('%s.%s' % (videoName, videoLink.split('.')[-1]), 'wb')

                with urllib.request.urlopen(urllib.request.Request(videoLink, headers={'User-Agent': 'Mozilla/5.0'}), context=ssl.SSLContext()) as video:
                    videoSize = int(video.getheader('content-length'))
                    videoDownloadedSize = 0

                    while videoDownloadedSize < videoSize:
                        f.write(video.read(VIDEO_READ_SIZE))

                        videoDownloadedSize += VIDEO_READ_SIZE

                        if videoDownloadedSize > videoSize:
                            videoDownloadedSize = videoSize

                        print('%s 다운로드중... %2d%% [%d/%d bytes]' % (videoName, videoDownloadedSize * 100 // videoSize, videoDownloadedSize, videoSize), end='\r')
                
                f.close()
                print('')
