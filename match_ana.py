import requests, json
import time
API_KEY = "RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791"

challenger_user_response = requests.get("https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791")
entries = challenger_user_response.json()['entries']
print(entries)
for j in entries:
    summonerId = j['summonerId']
    print("요청을 시도하는 SummonerId:", summonerId)
    time.sleep(1)
    try:
        puuid_response = requests.get("https://kr.api.riotgames.com/lol/summoner/v4/summoners/"+summonerId+"?api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791")
        time.sleep(1)
        puuid = puuid_response.json()['puuid']
        print("받아온 PUUID: ", puuid)
        matchListResponse = requests.get('https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?start=0&count=20&api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791')
        time.sleep(1)
        matchList = matchListResponse.json()
        print(matchList)
        print(matchList[0])
        for i in range(5):
            time.sleep(1)
            print("matchDetailResponse 받기 시도...")
            matchDetailResponse = requests.get(f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchList[i]}?api_key={API_KEY}")
            print(matchDetailResponse)
            matchDetailResponse.json()
            print("matchDetail 받기 성공")
    except:
        print("summonerId 에서 puuid 를 받는데 실패했습니다.")

