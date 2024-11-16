from flask import Flask,render_template, request, session, redirect
import requests
import json
app = Flask(__name__)    #KR_7194336697
app.secret_key = 'chominhu'
API_KEY = "RGAPI-d99fdc77-13a4-4894-8381-fb51379ccf5d"
TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
CSECRET ="BGDkauFdjU9lEtb1n6G7tesgpoNNONwb"
CID = "57f9d0c11d0039471ba6a9d38162c466"
RURI= "https://minhu.site/callback"   #REDIRECT_URI  #https://127.0.0.1:5000/callback
KAKAO_LOGIN_URL = "https://kauth.kakao.com/oauth/authorize?client_id="+CID+"&redirect_uri="+RURI+"&scope=profile_nickname,profile_image,talk_message&response_type=code"

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

# zz game 접어라
"""
여기에 로그아웃 함수 작성 route 를 logout 으로 한다음에
AG.HTML 에서 로그아웃 버튼 만들고 클릭하면 
session.clear() 하고 다시 메인화면 리디렉트 할 수 있게
"""


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



def getMatchHistroy(gameName, tagLine):
    response = requests.get("https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+ gameName+"/"+tagLine+"?api_key="+API_KEY)
    #게임네임이랑 태그라인 넣어서 apikey 사용해서 puuid를받아오는 API호출해서 응답받은 결과를 response변수에 저장.
    puuid = response.json()['puuid']
    #응답받은 response에서, puuid를 추출

    #https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/쮸니1/KR1?api_key=RGAPI-2772a19c-520f-4571-af40-31a5dcb6f07f
    #puuid로 이제 최근 매치 리스트 볼 수 있는데 API호출
    matchListResponse = requests.get('https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?start=0&count=20&api_key='+API_KEY)
    matchListResponse = matchListResponse.json()
    #printMatchList(matchListResponse)
    #응답 받은거 json바꾸고 그중 첫번째 매치 번호를 matchNumber0 에 넣기.
    #print(matchNumber0)
    matchDetail = []
    for i in range(5):
        try:
            matchDetailResponse = requests.get("https://asia.api.riotgames.com/lol/match/v5/matches/"+ matchListResponse[i]+"?api_key="+API_KEY)
            matchDetailResponse = matchDetailResponse.json()
            matchDetail.append(matchDetailResponse)
        except:
            matchDetailResponse = "error"
    return matchDetail, puuid
    #여서 리턴 ㄱㄱ puuid 도 같이 리턴해주네..?

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
    #이게 제일 중요
    matchHistoryRetList, puuid = getMatchHistroy(name, tag)
    PersonalTier = ""
    PersonalRank = ""
    try:
        Personaltier = requests.get("https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/Wsbfae1squ2_zUNKfUQPKA-J5NzhAUd4mZGr8vBtzPQX49M?api_key="+API_KEY)
        print("내 티어 결과 수신: ",Personaltier)
        Personaltier = Personaltier.json()
        PersonalTier = (Personaltier[0]['tier'])
        PersonalRank = (Personaltier[0]['rank'])
    except:
        PersonalTier = "Undefined"
        PersonalRank = "Undefined"

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
        print("내 인덱스 번호: ", myIndexNum)
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
            print(profileicon)

            if items == 2021:
                items = "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/1da3c726b2c888fcadef76f75de1c24c1ed090cf-512x512.png"
            elif items == 6610:
                items = "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/1da3c726b2c888fcadef76f75de1c24c1ed090cf-512x512.png"
            #10명의 유저 tier뽑기
            
            # 티어 정보 가져오기
            Tier = ""
            Rank = ""
            try:
                tier_response = requests.get(f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={API_KEY}")
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
            lst = [gamename, teamId, championname, position, kdaa, kill, death, solokill, assists, winandworse, items, Tier, Rank, profileicon, level]  # Add level to the list
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


    return render_template('a.html', match_history_lst_10 = match_history_lst_10, summoner_name = summoner_name, PersonalTier = PersonalTier, PersonalRank = PersonalRank, level=level)


def printMatchList(matchListResponse):
    
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
        tier = requests.get("https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/"+summonerId+"?api_key="+apiKey)
        tier = tier.json()
        #이후print하기

        print(tier)
        Tier = (tier[0]['tier'])
        Rank = (tier[0]['rank'])
    #여기서 반복문사용해서 매치기록 10개를 콜하고 프린트하세요

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
    return render_template('riot_txt.html')

@app.route('/championanalyze')
def champion_analyze():
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

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port="5000")#, port="443", ssl_context='adhoc')