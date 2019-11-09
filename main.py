from bs4 import BeautifulSoup
import urllib
import re
import time
import ssl
import os

ANI24_URL = 'https://ani24zo.com'

VIDEO_READ_SIZE = 2048

def isNumber(n):
    return bool(re.match(r'^\d+$', n))

def downloadVideo(name, path, link):
    try:

        with urllib.request.urlopen(urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'}), context=ssl.SSLContext()) as video:
            with open('%s/%s.%s' % (path, name, link.split('.')[-1]), 'wb') as f:
                videoSize = int(video.getheader('content-length'))
                videoDownloadedSize = 0

                while videoDownloadedSize < videoSize:
                    f.write(video.read(VIDEO_READ_SIZE))

                    videoDownloadedSize += VIDEO_READ_SIZE

                    if videoDownloadedSize > videoSize:
                        videoDownloadedSize = videoSize

                    print(' %s 다운로드중... %2d%% [%d/%d bytes]' % (name, videoDownloadedSize * 100 // videoSize, videoDownloadedSize, videoSize), end='\r')
            
        print('')

        return True

    except:
        return False

downloadPath = input('저장 위치: ')
os.makedirs(downloadPath)

searchKeyword = input('검색어: ')

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
        animeTargetIndex = input(' > ')

        if isNumber(animeTargetIndex) and 1 <= int(animeTargetIndex) <= len(animeList):
            animeTargetIndex = int(animeTargetIndex) - 1

            break

with urllib.request.urlopen(urllib.request.Request('%s%s' % (ANI24_URL, animeList[animeTargetIndex][1]), headers={'User-Agent': 'Mozilla/5.0'})) as response:
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    animeVideoListDivSoup = BeautifulSoup(str(soup.find('div', {'class': 'ani_video_list'})), 'html.parser')

    animeDownloadParticipants = list(map(str, animeVideoListDivSoup.find_all('a')))
    animeDownloadParticipants.reverse()

    for i in range(len(animeDownloadParticipants)):
        print(' %d. %s' % (i + 1, re.search(r'(?<=<div class="subject">).*(?=</div>)', animeDownloadParticipants[i]).group()))
    
    print('')
    print(' ※ 다운로드할 목록을 공백으로 구분해 입력해주세요')
    print(' ※ 아무것도 입력되지 않으면 모두 다운로드합니다')
    print('')

    animeDownloadList = []
    while True:
        animeDownloadInput = input(' > ')
        
        if animeDownloadInput == '':
            animeDownloadList = animeDownloadParticipants

            break

        for i in animeDownloadInput.split():
            if isNumber(i) and 1 <= int(i) <= len(animeDownloadParticipants):
                animeDownloadList.append(animeDownloadParticipants[int(i) - 1])
        
        animeDownloadList.sort()

        break

    for i in animeDownloadList:
        videoName = re.search(r'(?<=<div class="subject">).*(?=</div>)', i).group()
        
        with urllib.request.urlopen(urllib.request.Request('%s' % (re.search(r'(?<=<a href=").*(?=">)', i).group()), headers={'User-Agent': 'Mozilla/5.0'})) as videoSite:
            iframeLink = ''.join(re.findall(r'(?<=ifr_adr \+= ")[^"]*(?=")', videoSite.read().decode('utf-8')))

            with urllib.request.urlopen(urllib.request.Request('https://%s' % (iframeLink), headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'a'})) as iframeSite:
                iframeHtml = iframeSite.read().decode('utf-8')
                
                isVideoDownloaded = False

                # jwplayer
                if not isVideoDownloaded:
                    isVideoDownloaded = downloadVideo(videoName, re.search(r'(?<=file":")[^"]*(?=")', iframeHtml).group(), downloadPath)
                
                #TODO video player
                if not isVideoDownloaded:
                    isVideoDownloaded = downloadVideo(videoName, re.search(r'(?<=title="video 플레이어" data-link=")[^"]*(?=")', iframeHtml).group(), downloadPath)

                #TODO openload
                #TODO dailymotion
                #TODO stremango
                if not isVideoDownloaded:
                    isVideoDownloaded = downloadVideo(videoName, re.search(r'(?<=title="streamango 플레이어" data-link=")[^"]*(?=")', iframeHtml).group(), downloadPath)

                #TODO mp4upload

                if not isVideoDownloaded:
                    print('%s가 다운로드되지 못했습니다' % videoName)
