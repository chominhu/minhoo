from flask import Flask,render_template, request, session, redirect
import requests
import json
from typing import List, Dict
from dataclasses import dataclass
import traceback
import os

@dataclass
class ChampionStats:
    name: str
    tier: int
    role: str
    win_rate: float
    pick_rate: float
    ban_rate: float
    counters: List[str]

app = Flask(__name__)    #KR_7194336697
app.secret_key = 'chominhu'
API_KEY = "RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791"
TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
CSECRET ="BGDkauFdjU9lEtb1n6G7tesgpoNNONwb"
CID = "57f9d0c11d0039471ba6a9d38162c466"
RURI= "http://127.0.0.1:5000/callback"   #REDIRECT_URI  #https://127.0.0.1:5000/callback
KAKAO_LOGIN_URL = "https://kauth.kakao.com/oauth/authorize?client_id="+CID+"&redirect_uri="+RURI+"&scope=profile_nickname,profile_image,talk_message&response_type=code"


def getMatchHistroy(gameName, tagLine, region, country):
    try:
        response = requests.get(f"https://{country}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={API_KEY}")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        puuid = data['puuid']

        matchListResponse = requests.get(f'https://{country}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={API_KEY}')
        matchListResponse.raise_for_status()
        matchList = matchListResponse.json()

        matchDetail = []
        for i in range(5):
            try:
                matchDetailResponse = requests.get(f"https://{country}.api.riotgames.com/lol/match/v5/matches/{matchList[i]}?api_key={API_KEY}")
                matchDetailResponse.raise_for_status()
                matchDetail.append(matchDetailResponse.json())
            except (requests.RequestException, IndexError) as e:
                print(f"Error fetching match detail {i}: {str(e)}")
                matchDetail.append(None)

        return matchDetail, puuid

    except requests.RequestException as e:
        print(f"Error in getMatchHistroy: {str(e)}")
        return [], None
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error processing data: {str(e)}")
        return [], None



@app.route('/')
def gg():
    if session.get('access_token') is not None:
        return render_template ('AG.html', isLogin = True)
    return render_template('AG.html', url = KAKAO_LOGIN_URL, isLogin=False)

@app.route('/logout')
def logout():
    if session.get('access_token') is not None:
        session.clear()
        print('session clear')
        return redirect("/")
    else:
        return redirect("/")

@app.route("/kakaomessage")
def kakaomessage():
    #라인전 넣기 line = request.args.get('line')
    championname = request.args.get('championname')
    name = request.args.get('name')
    print(name)
    access_token = session['access_token']  
    headerstr = "Bearer "+access_token
    template_object = {
        "object_type": "feed", #https://developers.kakao.com/docs/latest/ko/message/message-template#feed (피드관련정보 참고)
        "content": {
            "title": "https://5647-221-149-135-135.ngrok-free.app/search?name=erel&tag=irel",
            #"description": "2024년 10월 5일의 게임",
            "image_url": "https://ddragon-webp.lolmath.net/latest/img/profileicon/5.webp",
            "image_width": 640,
            "image_height": 640,
            "link": {
                "web_url": "https://5647-221-149-135-135.ngrok-free.app/search?name=erel&tag=irel",
                "mobile_web_url": "https://5647-221-149-135-135.ngrok-free.app/search?name=erel&tag=irel",
                "android_execution_params": "contentId=100",
                "ios_execution_params": "contentId=100"
            }
        },
        "item_content" : { #https://brand.riotgames.com/static/a91000434ed683358004b85c95d43ce0/8a20a/lol-logo.png
            "profile_text" :name, #유저 이름
            "profile_image_url" :"https://ddragon-webp.lolmath.net/latest/img/profileicon/5.webp", #인게임 프로필 아이콘/5가 아닌 유저에 따른 아이콘으로 변경//https://lolmath.net/articles/summoner-icons/ (참고)
            #"title_image_url" : "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news/9eb028de391e65072d06e77f06d0955f66b9fa2c-736x316.png?auto=format&fit=fill&q=80&w=300",
            "title_image_text" :"빠른대전", #격전종류
            "title_image_category" : "승리",
            "items" : [
                {
                    "item" :"챔피언",
                    "item_op" : "이렐리아" #챔피언이름
                },
                {
                    "item" :"라인전", #ex)53:47
                    "item_op" : "53:47"
                }
            ],
            "sum" :"승/패",
            "sum_op" : "승리" #승리/패배
        },
        "buttons": [
            {
                "title": "자세히 보기2",
                "link": {
                    "web_url": "https://5647-221-149-135-135.ngrok-free.app/search?name=erel&tag=irel",
                    "mobile_web_url": "https://5647-221-149-135-135.ngrok-free.app/search?name=erel&tag=irel"
                }
            }
        ]
    }
    data = {
        'template_object':  json.dumps(template_object)
    }   
    a = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send",
                   headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": headerstr,
                   },
                   data=data
                   )
    print(a)
    #메시지 보내버리기..ok?
    return "메시지 전송 성공"

@app.route("/callback")
def getAuthCode():
    authcode = request.args.get('code')
    token_response = requests.post(TOKEN_URL, data={
        'client_id' : CID,
        'client_secret' : CSECRET,
        'grant_type' : 'authorization_code',
        'redirect_uri' : RURI,
        'code' : authcode
    })
    token_response = token_response.json()
    access_token = token_response['access_token']
    print(access_token)
    session['access_token'] = access_token
    headerstr = "Bearer "+access_token
    user_response = requests.get("https://kapi.kakao.com/v2/user/me",
                        headers={
                            "Authorization": headerstr
                        })
    print(user_response.text)
    #여기서 너 이름이랑 카카오 프로필 아이콘 정도?
    #프린트 해두셈

    return redirect('/')


@app.route('/login', methods=['GET'])
def kakaotalkLogin():
    url = "http://127.0.0.1:5000"
    return render_template('katalk.html', url = url)


@app.route('/search', methods=['GET','POST'])
def search():
    summoner_name = ""
    if request.method == 'GET':
        name = request.args.get('name')
        tag = request.args.get('tag')
       
    else:
        summoner_name = request.form['summoner_name']
        print(summoner_name)
        nickname = summoner_name.split('#')
        name = nickname[0]
        tag = nickname[1]
        region = request.form['region']
        country = 'asia'
        if region in ['kr', 'jp', 'sg', 'ph', 'tw', 'vn', 'th']:  # Asia
            country = 'asia'
        elif region in ['na', 'br', 'las', 'lan']: 
            country = 'americas'
        elif region in ['eu_w', 'eu_ne', 'ru', 'tr']:  
            country = 'europe'
        else:
            country = 'asia'

    #이게 제일 중요 
    matchHistoryRetList, puuid = getMatchHistroy(name, tag, region, country)

    #매치결과 10개뽑기
    match_history_lst_10 = []
    for j in range(5):
        matchhistory = matchHistoryRetList[j]
        participantsNumbers = (matchhistory['metadata']['participants'])
        myIndexNum = 0
        for i in range(10):  # 10으로 수정 (0-9 인덱스)
            if participantsNumbers[i] == puuid:
                myIndexNum = i
                break
        #print("내 인덱스 번호: ", myIndexNum)
        match_history_lst = []
        for a in range(10):
            #10명의 유저 게임 기록 뽑기.
            gamename = (matchhistory['info']['participants'][a]['riotIdGameName'])
            teamId = (matchhistory['info']['participants'][a]['teamId'])
            championname = (matchhistory['info']['participants'][a]['championName'])
            position = (matchhistory['info']['participants'][a]['individualPosition'])
            kda = ((matchhistory['info']['participants'][a]['challenges']['kda']))
            # 예시: 3.141592를 소수 둘째 자리에서 반올림
            kda = round(float(kda), 2)
            kda = str(kda)
            kdaa = (str(kda))
            kill = (str(matchhistory['info']['participants'][a]['kills']))
            death = (str(matchhistory['info']['participants'][a]['deaths']))
            solokill = (str(matchhistory['info']['participants'][a]['challenges']['soloKills']))
            assists = (str(matchhistory['info']['participants'][a]['assists']))
            winandworse = (matchhistory['info']['participants'][a]['win'])
            # 아이템 ID 리스트 가져오기
            items = [
                matchhistory['info']['participants'][a]['item0'],
                matchhistory['info']['participants'][a]['item1'],
                matchhistory['info']['participants'][a]['item2'],
                matchhistory['info']['participants'][a]['item3'],
                matchhistory['info']['participants'][a]['item4'],
                matchhistory['info']['participants'][a]['item5'],
                matchhistory['info']['participants'][a]['item6']
            ]
            # 0이 아닌 아이템 ID만 필터링
            items = [item for item in items if item != 0]
            summonerId = (matchhistory['info']['participants'][a]['summonerId'])
            profileicon = (matchhistory['info']['participants'][a]['profileIcon'])
            #print(profileicon)

            if items == 2021:
                items = "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/1da3c726b2c888fcadef76f75de1c24c1ed090cf-512x512.png"
            elif items == 6610:
                items = "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/1da3c726b2c888fcadef76f75de1c24c1ed090cf-512x512.png"
            #10명의 유저 tier뽑기
            
            # 티어 정보 가져오기
            Tier = ""
            Rank = ""
            try:
                tier_response = requests.get(f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={API_KEY}")
                if tier_response.status_code == 200:
                    tier_data = tier_response.json()
                    if tier_data:
                        Tier = tier_data[0]['tier']
                        Rank = tier_data[0]['rank']
                    else:
                        Tier = "UNRANKED"
                        Rank = ""
                else:
                    Tier = "API_ERROR"
                    Rank = ""
            except Exception as e:
                print(f"Error fetching tier for summonerId {summonerId}: {str(e)}")
                Tier = "ERROR"
                Rank = ""

            if teamId == 100:
                teamId = "블루"
            else :
                teamId = "레드"
            level = (matchhistory['info']['participants'][a]['champLevel'])  # Get the championlevel
            lst = [gamename, teamId, championname, position, kdaa, kill, death, solokill, assists, winandworse, items, Tier, Rank]  # Add level to the list
            match_history_lst.append(lst)
            

        redbans = (matchhistory['info']['teams'][0]['bans']) # 레드팀 밴 목록
        bans_lst = []
        for ban in redbans:
            if ban['championId'] != -1:
                bans_lst.append(ban['championId'])
        print(bans_lst)

        bluebans = (matchhistory['info']['teams'][1]['bans']) # 블루팀 밴 목록
        bans_lst = []
        for ban in bluebans:
            if ban['championId'] != -1:
                bans_lst.append(ban['championId'])
        print(bans_lst)
        match_history_lst_10.append(match_history_lst)
        gamemode = (matchhistory['info']['gameMode'])
    
    my_summoner_id = (matchhistory['info']['participants'][myIndexNum]['summonerId'])
    PersonalTier = ""
    PersonalRank = ""
    try:
        Personaltier = requests.get("https://"+region+".api.riotgames.com/lol/league/v4/entries/by-summoner/"+my_summoner_id+"?api_key="+API_KEY)
        print("내 티어 결과 수신: ",Personaltier)
        Personaltier = Personaltier.json()
        PersonalTier = (Personaltier[0]['tier'])
        PersonalRank = (Personaltier[0]['rank'])
    except:
        PersonalTier = "Undefined"
        PersonalRank = "Undefined"



    return render_template('a.html', match_history_lst_10 = match_history_lst_10, summoner_name = summoner_name, PersonalTier = PersonalTier, PersonalRank = PersonalRank, level=level)


def printMatchList(matchListResponse):
    region = request.form['region']
    country = 'asia'
    for i in range(10):
        matchDetailResponse = requests.get("https://asia.api.riotgames.com/lol/match/v5/matches/"+matchListResponse[i]+"?api_key="+API_KEY)
        print(matchDetailResponse.text)
        matchhistory = matchDetailResponse.text
        apiKey = "RGAPI-503d7f15-4e2f-4646-9c10-99214e11ae90"
        gamename = (matchhistory['info']['participants'][i]['riotIdGameName'])
        teamId = (matchhistory['info']['participants'][i]['teamId'])
        championname = ('챔피언 : ' + matchhistory['info']['participants'][i]['championName'])
        position = ('라인 : ' + matchhistory['info']['participants'][i]['individualPosition'])
        kda = ('kda : ' + str(matchhistory['info']['participants'][i]['challenges']['kda']))
        # KDA값 반올림
        kda = round(float(kda), 2)
        kda = str(kda)
        kdaa = ('kda : ' + str(kda))
        print(kdaa)
        kill = ('총 킬 : ' + str(matchhistory['info']['participants'][i]['kills']))
        death = ('죽음 : ' + str(matchhistory['info']['participants'][i]['deaths']))
        solokill = ('솔킬 : ' + str(matchhistory['info']['participants'][i]['challenges']['soloKills']))
        assists = ('어시스트 : ' + str(matchhistory['info']['participants'][i]['assists']))
        winandworse = (matchhistory['info']['participants'][i]['win'])
        items = (matchhistory['info']['participants'][i]['items'])
        #여기서 summonerId뽑기
        summonerId = (matchhistory['info']['participants'][i]['summonerId'])
        profileicon = (matchhistory['info']['participants'][i]['profileIcon'])
        #여기서 추가 request날리기
        #tier = requests.get('https://asia.api.riotgames.com/lol/league/v4/entries/by-summoner/'+summonerId+"?api_key="+apiKey)
        tier = requests.get("https://"+region+".api.riotgames.com/lol/league/v4/entries/by-summoner/"+summonerId+"?api_key="+apiKey)
        tier = tier.json()
        #이후print하기

        print(tier)
        Tier = (tier[0]['tier'])
        Rank = (tier[0]['rank'])
    #여기서 반복문사용해서 매치기록 10개��� 콜하고 프린트하세요

    lst = [gamename, teamId, championname, position, kdaa, kill, death, solokill, assists, winandworse, items,Tier, Rank]
    #print("===============================================================================")
    #print(gamename)
    #print(teamId)
    #print(championname)
    #print(position)
    #print(kda)
    #print(kill)
    #print(death)
    #print(solokill)
    #print(assists)
    #print(winandworse)
    #print(Tier)
    #print(Rank)
    #print(kdaa)

@app.route('/riot.txt')
def riot_txt():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # riot.txt의 전체 경로
        file_path = os.path.join(current_dir, 'riot.txt')
        
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"File not found at: {file_path}")  # 디버깅을 위한 경로 출력
        return "riot.txt file not found", 404
    except Exception as e:
        print(f"Error reading riot.txt: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        # 개발 환경에서는 상세한 에러 메시지 반환
        if app.debug:
            return f"Error reading riot.txt: {str(e)}", 500
        # 프로덕션 환경에서는 일반적인 에러 메시지 반환
        return "Internal server error", 500
    
@app.route('/total')
def total():
    # Fetch all champions from the Riot Games API
    response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/14.22.1/data/en_US/champion.json")
    champions_data = response.json()
    champions = []

    # Extract champion details
    for champion_key, champion_info in champions_data['data'].items():
        champions.append({
            "name": champion_info['name'],
            "role": champion_info['tags'][0] if champion_info['tags'] else "Unknown",  # Get the first role
            "win_rate": "N/A"  # Placeholder for win rate
        })

    return render_template('total.html', champions=champions)

@app.route('/championanalyze')
def champion_analyze():
    champions = [
        {
            "name": "Nilah",
            "korean_name": "닐라",
            "position": "ADC",
            "win_rate": 53.38,
            "pick_rate": 1.56,
            "ban_rate": 2.73
        },
        {
            "name": "KaiSa",
            "korean_name": "카이사",
            "position": "ADC", 
            "win_rate": 53.21,
            "pick_rate": 1.87,
            "ban_rate": 1.52
        },
        {
            "name": "Vex",
            "korean_name": "벡스",
            "position": "MID",
            "win_rate": 52.84,
            "pick_rate": 2.76,
            "ban_rate": 7.03
        },
        {
            "name": "Ahri",
            "korean_name": "아리",
            "position": "MID",
            "win_rate": 51.92,
            "pick_rate": 8.45,
            "ban_rate": 4.21
        },
        {
            "name": "Jinx",
            "korean_name": "징크스",
            "position": "ADC",
            "win_rate": 51.76,
            "pick_rate": 12.34,
            "ban_rate": 2.15
        },
        {
            "name": "Leona",
            "korean_name": "레오나",
            "position": "SUP",
            "win_rate": 51.54,
            "pick_rate": 6.78,
            "ban_rate": 3.42
        },
        {
            "name": "Darius",
            "korean_name": "다리우",
            "position": "TOP",
            "win_rate": 51.23,
            "pick_rate": 9.87,
            "ban_rate": 15.63
        },
        {
            "name": "LeeSin",
            "korean_name": "리 신",
            "position": "JGL",
            "win_rate": 50.98,
            "pick_rate": 15.42,
            "ban_rate": 8.91
        },
        {
            "name": "Yasuo",
            "korean_name": "야스오",
            "position": "MID",
            "win_rate": 50.45,
            "pick_rate": 18.76,
            "ban_rate": 22.34
        },
        {
            "name": "Thresh",
            "korean_name": "쓰레쉬",
            "position": "SUP",
            "win_rate": 50.32,
            "pick_rate": 14.23,
            "ban_rate": 5.67
        },
        {
            "name": "Aatrox",
            "korean_name": "아트록스",
            "position": "TOP",
            "win_rate": 49.85,
            "pick_rate": 7.23,
            "ban_rate": 4.56
        },
        {
            "name": "Ahri",
            "korean_name": "아리",
            "position": "MID",
            "win_rate": 51.92,
            "pick_rate": 8.45,
            "ban_rate": 4.21
        },
        {
            "name": "Akali",
            "korean_name": "아칼리",
            "position": "MID",
            "win_rate": 48.76,
            "pick_rate": 9.12,
            "ban_rate": 12.34
        },
        {
            "name": "Alistar",
            "korean_name": "알리스타",
            "position": "SUP",
            "win_rate": 50.23,
            "pick_rate": 4.56,
            "ban_rate": 1.23
        },
        {
            "name": "Amumu",
            "korean_name": "아무무",
            "position": "JGL",
            "win_rate": 51.34,
            "pick_rate": 3.45,
            "ban_rate": 2.11
        },
        {
            "name": "Zyra",
            "korean_name": "자이라",
            "position": "SUP",
            "win_rate": 50.87,
            "pick_rate": 3.21,
            "ban_rate": 1.45
        },
        {
            "name": "Annie",
            "korean_name": "애니",
            "position": "MID",
            "win_rate": 51.23,
            "pick_rate": 2.45,
            "ban_rate": 0.89
        },
        {
            "name": "Ashe",
            "korean_name": "애쉬",
            "position": "ADC",
            "win_rate": 50.76,
            "pick_rate": 8.91,
            "ban_rate": 2.34
        },
        {
            "name": "AurelionSol",
            "korean_name": "아우렐리온 솔",
            "position": "MID",
            "win_rate": 52.12,
            "pick_rate": 1.23,
            "ban_rate": 0.67
        },
        {
            "name": "Azir",
            "korean_name": "아지르",
            "position": "MID",
            "win_rate": 48.89,
            "pick_rate": 3.45,
            "ban_rate": 1.23
        },
        {
            "name": "Bard",
            "korean_name": "바드",
            "position": "SUP",
            "win_rate": 50.34,
            "pick_rate": 2.78,
            "ban_rate": 0.45
        },
        {
            "name": "Blitzcrank",
            "korean_name": "블리츠크랭크",
            "position": "SUP",
            "win_rate": 51.23,
            "pick_rate": 7.89,
            "ban_rate": 15.67
        },
        {
            "name": "Brand",
            "korean_name": "브랜드",
            "position": "SUP",
            "win_rate": 50.87,
            "pick_rate": 4.56,
            "ban_rate": 2.34
        },
        {
            "name": "Braum",
            "korean_name": "브라움",
            "position": "SUP",
            "win_rate": 49.98,
            "pick_rate": 3.21,
            "ban_rate": 0.87
        },
        {
            "name": "Caitlyn",
            "korean_name": "케이틀린",
            "position": "ADC",
            "win_rate": 50.45,
            "pick_rate": 12.34,
            "ban_rate": 4.56
        },
        {
            "name": "Camille",
            "korean_name": "카밀",
            "position": "TOP",
            "win_rate": 51.23,
            "pick_rate": 5.67,
            "ban_rate": 3.45
        },
        {
            "name": "Zed",
            "korean_name": "제드",
            "position": "MID",
            "win_rate": 49.87,
            "pick_rate": 15.67,
            "ban_rate": 25.43
        },
        {
            "name": "Ziggs",
            "korean_name": "직스",
            "position": "MID",
            "win_rate": 50.12,
            "pick_rate": 2.34,
            "ban_rate": 0.78
        },
        {
            "name": "Zilean",
            "korean_name": "질리언",
            "position": "SUP",
            "win_rate": 51.34,
            "pick_rate": 2.12,
            "ban_rate": 0.56
        },
        {
            "name": "Cassiopeia",
            "korean_name": "카시오페아",
            "position": "MID",
            "win_rate": 51.23,
            "pick_rate": 3.45,
            "ban_rate": 2.11
        },
        {
            "name": "Chogath",
            "korean_name": "초가스",
            "position": "TOP",
            "win_rate": 50.87,
            "pick_rate": 2.34,
            "ban_rate": 0.89
        },
        {
            "name": "Corki",
            "korean_name": "코르키",
            "position": "MID",
            "win_rate": 49.76,
            "pick_rate": 1.23,
            "ban_rate": 0.45
        },
        {
            "name": "Darius",
            "korean_name": "다리우스",
            "position": "TOP",
            "win_rate": 51.34,
            "pick_rate": 8.90,
            "ban_rate": 12.34
        },
        {
            "name": "Diana",
            "korean_name": "다이애나",
            "position": "JGL",
            "win_rate": 50.98,
            "pick_rate": 6.78,
            "ban_rate": 4.56
        },
        {
            "name": "DrMundo",
            "korean_name": "문도 박사",
            "position": "TOP",
            "win_rate": 50.45,
            "pick_rate": 3.21,
            "ban_rate": 1.23
        },
        {
            "name": "Draven",
            "korean_name": "드레이븐",
            "position": "ADC",
            "win_rate": 51.87,
            "pick_rate": 4.56,
            "ban_rate": 3.45
        },
        {
            "name": "Ekko",
            "korean_name": "에코",
            "position": "JGL",
            "win_rate": 50.34,
            "pick_rate": 5.67,
            "ban_rate": 2.34
        },
        {
            "name": "Elise",
            "korean_name": "엘리스",
            "position": "JGL",
            "win_rate": 51.23,
            "pick_rate": 3.45,
            "ban_rate": 1.23
        },
        {
            "name": "Evelynn",
            "korean_name": "이블린",
            "position": "JGL",
            "win_rate": 50.87,
            "pick_rate": 4.56,
            "ban_rate": 3.21
        },
        {
            "name": "Ezreal",
            "korean_name": "이즈리얼",
            "position": "ADC",
            "win_rate": 49.98,
            "pick_rate": 15.67,
            "ban_rate": 5.43
        },
        {
            "name": "Fiddlesticks",
            "korean_name": "피들스틱",
            "position": "JGL",
            "win_rate": 51.34,
            "pick_rate": 2.34,
            "ban_rate": 1.23
        },
        {
            "name": "Fiora",
            "korean_name": "피오라",
            "position": "TOP",
            "win_rate": 50.76,
            "pick_rate": 7.89,
            "ban_rate": 8.90
        },
        {
            "name": "Fizz",
            "korean_name": "피즈",
            "position": "MID",
            "win_rate": 50.23,
            "pick_rate": 4.56,
            "ban_rate": 3.21
        },
        {
            "name": "Galio",
            "korean_name": "갈리오",
            "position": "MID",
            "win_rate": 49.87,
            "pick_rate": 2.34,
            "ban_rate": 0.89
        },
        {
            "name": "Gangplank",
            "korean_name": "갱플랭크",
            "position": "TOP",
            "win_rate": 50.45,
            "pick_rate": 5.67,
            "ban_rate": 3.45
        }
    ]

    return render_template('champion_analyze.html', champions=champions)

@app.route('/rangking')
def rangking():
    # Fetch all champions from the Riot Games API
    response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/14.22.1/data/en_US/champion.json")
    champions_data = response.json()
    champions = []

    # Extract champion details
    for champion_key, champion_info in champions_data['data'].items():
        champions.append({
            "name": champion_info['name'],
            "role": champion_info['tags'][0] if champion_info['tags'] else "Unknown",  # Get the first role
            "win_rate": "N/A"  # Placeholder for win rate
        })

    return render_template('rangking.html', champions=champions)

@app.route('/champions')
def champions():
    # Get query parameters for filtering
    patch = request.args.get('patch', '14.23')
    tier = request.args.get('tier', 'emerald_plus') 
    role = request.args.get('role', 'all')

    # Fetch champion data from Riot API
    champions_response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json")
    champions_data = champions_response.json()['data']

    # Create champion stats list (this would normally come from a database)
    champion_stats: List[ChampionStats] = [
        ChampionStats(
            name="Nilah",
            tier=1,
            role="Bottom",
            win_rate=53.36,
            pick_rate=1.56,
            ban_rate=2.73,
            counters=["Xayah", "Sivir", "Ziggs"]
        ),
        ChampionStats(
            name="Cassiopeia", 
            tier=1,
            role="Middle",
            win_rate=53.22,
            pick_rate=1.87,
            ban_rate=1.22,
            counters=["Zoe", "Anivia", "Lissandra"]
        ),
        # ... add more champions ...
    ]

    # Filter by role if specified
    if role != 'all':
        champion_stats = [c for c in champion_stats if c.role.lower() == role.lower()]

    # Sort by win rate descending
    champion_stats.sort(key=lambda x: x.win_rate, reverse=True)

    return render_template(
        'champions.html',
        champions=champion_stats,
        current_patch=patch,
        current_tier=tier,
        current_role=role
    )

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port="5000")#, port="443", ssl_context='adhoc')