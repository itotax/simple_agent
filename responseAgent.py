# simple agent for discourse

import requests, pprint,json,os,argparse,time
import simpledcapi
import openai, tiktoken

user_name = "xxx"
simpledcapi.discourse_url = "https://hyper-democracy.com/"
simpledcapi.Api_Key = "yyy" # hyper-democracy
simpledcapi.Api_Username = user_name

openai.api_key = os.getenv('OPENAI_API_KEY')
model="xxx"

parser = argparse.ArgumentParser(description="A program for a very simple Response agent")
parser.add_argument('-t')  # -t はトピック
parser.add_argument('-c')  # -c はカテゴリ
parser.add_argument('-phase')
args = parser.parse_args()
#print(args.t) # -t => t とparseしてくれる
if args.t != None:
    topic_id = int(args.t)
else:
    topic_id = xx

# 110 president election
# 111 global warming
    
if args.c != None:    
    category_id = int(args.c)
else:
    category_id =xx

if args.phase != None:
    phase = str(args.phase)
else:
    phase = "introduction"

##

aTopic = simpledcapi.get_topic(topic_id) # topic
print("A Topic--->")
pprint.pprint(aTopic)
print("topic title---->"+aTopic['title'])

print("len(post):")
pprint.pprint(len(aTopic['post_stream']['posts']))
 
##   
instruct =f"""
You will role-play as a gentle man who can discuss with people very positively and in a gentle manner. 
"""
responded_post_ids = []
while True:

    aRecentPost = simpledcapi.get_recent_post_in_topic(topic_id)

    if user_name != aRecentPost['username'] and aRecentPost['id'] not in responded_post_ids: # 最新ポストが自分のポストでないなら返信をする   
        pprint.pprint(simpledcapi.get_recent_post_in_topic(topic_id))
        aRecentPost = simpledcapi.get_recent_post_in_topic(topic_id)
        aRecentMessage = aRecentPost['cooked'] # 最新のpostのメッセージ部分cooked

        res = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": instruct},
                {"role": "user", "content": f"Reply to the message {aRecentMessage}  in less than 200 words"}              
            ],
            temperature=1  # 温度（0-2, デフォルト1）
        )
        gptMessage1 = res["choices"][0]["message"]["content"]
        post_number = aRecentPost['post_number']
        simpledcapi.create_reply(gptMessage1, topic_id, post_number)
        responded_post_ids.append(aRecentPost['id']) # responsしたpostのidを保管しておく

    time.sleep(180)
