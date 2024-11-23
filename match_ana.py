import requests, json
import time
API_KEY = "RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791"

challenger_user_response = requests.get("https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791")
entries = challenger_user_response.json()['entries']
print(entries)
for j in entries:
    summonerId = j['summonerId']
    #print(summonerId)
    try:
        puuid_response = requests.get("https://kr.api.riotgames.com/lol/summoner/v4/summoners/"+summonerId+"?api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791")
        puuid = puuid_response.json()['puuid']
        print(puuid)
        matchListResponse = requests.get('https://kr.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?start=0&count=20&api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791')
        matchListResponse = matchListResponse.json()
        for i in range(5):
            matchDetailResponse = requests.get("https://kr.api.riotgames.com/lol/match/v5/matches/"+ matchListResponse[i]+"?api_key=RGAPI-6fdc0d77-ae7a-466b-b001-41e653eff791")
            matchDetailResponse = matchDetailResponse.json()
            #쪼개기...
            #빨리해라...
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
                championname = (matchhistory['info']['participants'][a]['championName'])
                winordefault = (matchhistory['info']['participants'][a]['win'])
                #pritn(championname, winordefault)
            #chapionId = matchDetailResponse[~~~][~~~]
            #champion[chapionId] = champion[chapionId] + 1
            #champion = [200,190,길이 170개짜리 json만들어서.. count ++ 해줘야함 리스트에.. ok?]
            #wins = [1,4,5,7,2]
            #default = []
            
    except:
        print("summonerId 에서 puuid 를 받는데 실패했습니다.")

def getMatchHistroy(gameName, tagLine,region,country):
    
    matchListResponse = matchListResponse.json()
    #printMatchList(matchListResponse)
    #응답 받은거 json바꾸고 그중 첫번째 매치 번호를 matchNumber0 에 넣기.
    print(matchNumber0)
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