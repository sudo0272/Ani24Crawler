from bs4 import BeautifulSoup
import urllib
import re
import time
import ssl
import os
import multiprocessing

ANI24_URL = 'https://ani24zo.com'

VIDEO_READ_SIZE = 2048

def isNumber(n):
    return bool(re.match(r'^\d+$', n))

def downloadVideo(animeDownloadItem):
    videoName = re.search(r'(?<=<div class="subject">).*(?=</div>)', animeDownloadItem).group()
        
    with urllib.request.urlopen(urllib.request.Request('%s' % (re.search(r'(?<=<a href=").*(?=">)', animeDownloadItem).group()), headers={'User-Agent': 'Mozilla/5.0'})) as videoSite:
        iframeLink = ''.join(re.findall(r'(?<=ifr_adr \+= ")[^"]*(?=")', videoSite.read().decode('utf-8')))

        with urllib.request.urlopen(urllib.request.Request('https://%s' % (iframeLink), headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'a'})) as iframeSite:
            iframeHtml = iframeSite.read().decode('utf-8')
            
            isVideoDownloaded = False

            # jwplayer
            if not isVideoDownloaded:
                try:
                    link = re.search(r'(?<=file":")[^"]*(?=")', iframeHtml).group()

                    with urllib.request.urlopen(urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'}), context=ssl.SSLContext()) as video:
                        with open('%s/%s.%s' % (downloadPath, videoName, link.split('.')[-1]), 'wb') as f:
                            print(' %s 다운로드 시작' % (videoName))
                            f.write(video.read())
                            print(' %s 다운로드 완료' % (videoName))

                    isVideoDownloaded = True

                except:
                    pass

            # video player
            if not isVideoDownloaded:
                try:
                    link = re.search(r'(?<=title="video 플레이어" data-link=")[^"]*(?=")', iframeHtml).group()

                    with urllib.request.urlopen(urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'}), context=ssl.SSLContext()) as video:
                        with open('%s/%s.%s' % (downloadPath, videoName, link.split('.')[-1]), 'wb') as f:
                            print(' %s 다운로드 시작' % (videoName))
                            f.write(video.read())
                            print(' %s 다운로드 완료' % (videoName))

                    isVideoDownloaded = True

                except:
                    pass

            # mp4upload
            if not isVideoDownloaded:
                try:
                    link = re.search(r'(?<=title="mp4upload 플레이어" data-link=")[^"]*(?=")', iframeHtml).group().replace('embed-', '')
                    with urllib.request.urlopen(urllib.request.Request(link, data=urllib.parse.urlencode({'op': 'download2', 'id': link.split('/')[-1].replace('.html', '')}).encode('utf-8'), method='POST'), context=ssl.SSLContext()) as video:
                        with open('%s/%s.mp4' % (downloadPath, videoName), 'wb') as f:
                            print(' %s 다운로드 시작' % (videoName))
                            f.write(video.read())
                            print(' %s 다운로드 완료' % (videoName))

                    isVideoDownloaded = True

                except:
                    pass


            #TODO openload
            #TODO dailymotion
            # stremango
            if not isVideoDownloaded:
                try:
                    link = re.search(r'(?<=title="streamango 플레이어" data-link=")[^"]*(?=")', iframeHtml).group()

                    with urllib.request.urlopen(urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'}), context=ssl.SSLContext()) as video:
                        with open('%s/%s.%s' % (downloadPath, videoName, link.split('.')[-1]), 'wb') as f:
                            print(' %s 다운로드 시작' % (videoName))
                            f.write(video.read())
                            print(' %s 다운로드 완료' % (videoName))

                    isVideoDownloaded = True

                except:
                    pass
                
            if not isVideoDownloaded:
                print(' %s 다운로드 실패' % videoName)

downloadPath = input('저장 위치: ')
if not os.path.exists(downloadPath):
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

    pool = multiprocessing.Pool(processes=len(animeDownloadList))
    pool.map(downloadVideo, animeDownloadList)
    pool.close()
    pool.join()
