import requests
API_KEY = "RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791"
TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
CSECRET ="BGDkauFdjU9lEtb1n6G7tesgpoNNONwb"
CID = "57f9d0c11d0039471ba6a9d38162c466"
RURI= "http://127.0.0.1:5000/callback"   #REDIRECT_URI  #https://127.0.0.1:5000/callback
KAKAO_LOGIN_URL = "https://kauth.kakao.com/oauth/authorize?client_id="+CID+"&redirect_uri="+RURI+"&scope=profile_nickname,profile_image,talk_message&response_type=code"

def getMatchHistroy(gameName, tagLine,region,country):
    response = requests.get("https://"+country+".api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+ gameName+"/"+tagLine+"?api_key="+API_KEY)
    #게임네임이랑 태그라인 넣어서 apikey 사용해서 puuid를받아오는 API호출해서 응답받은 결과를 response변수에 저장.
    print(response)
    puuid = response.json()['puuid']
    #응답받은 response에서, puuid를 추출

    #https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/쮸니1/KR1?api_key=RGAPI-2772a19c-520f-4571-af40-31a5dcb6f07f
    #puuid로 이제 최근 매치 리스트 볼 수 있는데 API호출
    matchListResponse = requests.get('https://'+country+'.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?start=0&count=20&api_key='+API_KEY)
    matchListResponse = matchListResponse.json()
    #printMatchList(matchListResponse)
    #응답 받은거 json바꾸고 그중 첫번째 매치 번호를 matchNumber0 에 넣기.
    #print(matchNumber0)
    matchDetail = []
    for i in range(5):
        try:
            matchDetailResponse = requests.get("https://"+country+".api.riotgames.com/lol/match/v5/matches/"+ matchListResponse[i]+"?api_key="+API_KEY)
            matchDetailResponse = matchDetailResponse.json()
            matchDetail.append(matchDetailResponse)
        except:
            matchDetailResponse = "error"
    return matchDetail, puuid
    #여서 리턴 ㄱㄱ puuid 도 같이 리턴해주네..?