# simple agent for discourse

import requests,pprint,json,datetime,time,tiktoken,os

def create_post(title, body, category_id):
    api_url = discourse_url + "posts.json/" 
    theData = {
        'title': title,
        'raw' :body,
        'category': category_id,
    }
    theHeaders = {
        'Api-Key': Api_Key,
        'Api-Username': Api_Username
    }
    res = requests.post(api_url, theData, headers=theHeaders)
    res = res.json()
    return res

def create_post_in_topic(body, topic_id):#postする　category_idやtitleは必要ない どのtopicの何番の返信かをbodyと一緒に渡すのみ
    api_url = discourse_url + "posts.json/"
    theData = {
        'raw' :body,
        'topic_id' : topic_id
    }
    theHeaders = {
        'Api-Key': Api_Key,
        'Api-Username': Api_Username
    }
    res = requests.post(api_url, theData, headers=theHeaders)
    res = res.json()
    while "error" in res.keys():
        if res['error_type'] == 'rate_limit':
            print("rate_limit, wait 180 sec")
            time.sleep(120)
            res = requests.post(api_url, theData, headers=theHeaders)
            res = res.json()
            print("create_post: ", res) 
    return res

def create_reply(body, topic_id, reply_to_post_number):#replyする　category_idやtitleは必要ない どのtopicの何番の返信かをbodyと一緒に渡すのみ
    api_url = discourse_url + "posts.json/"
    print('create_post:'+'body='+body)
    theData = {
        'raw' :body,
        'topic_id' : topic_id,
        'reply_to_post_number' : reply_to_post_number
    }
    theHeaders = {
        'Api-Key': Api_Key,
        'Api-Username': Api_Username
    }
    res = requests.post(api_url, theData, headers=theHeaders)
    res = res.json()
    print("create_post: ", res)#レスポンスコードを表示する.
    while "error" in res.keys():
        if res['error_type'] == 'rate_limit':
            print("rate_limit, wait 180 sec")
            time.sleep(120)
            res = requests.post(api_url, theData, headers=theHeaders)
            res = res.json()
    return res

def get_posts():
    api_url = discourse_url + "posts.json/"
    res = requests.get(api_url)
    #print(res)
    res = res.json()
    #print(res)
    return res

def get_posts_in_topic(topic_id):
    api_url = discourse_url + f"/t/-/{topic_id}.json"
    #print(api_url)
    res = requests.get(api_url)
    res = res.json()
    initial_20_posts_in_a_topic  = res['post_stream']['posts'] #最初の20ポストの中身のみ
    post_ids_list_in_a_topic = res['post_stream']['stream']
    posts_in_a_topic = initial_20_posts_in_a_topic # []でもいい？
    # get a post
    i = 0
    for a_post_id in post_ids_list_in_a_topic:
        i = i + 1
        if i > 20:
            time.sleep(3) # 待たないとレートリミットになる
            api_url = discourse_url + f"posts/{a_post_id}.json"
            #print(api_url)
            res = requests.get(api_url)
            #print('*************************')
            #pprint.pprint(res)
            res = res.json()
            posts_in_a_topic.append(res)
    #posts_in_a_topic = list(filter(lambda a_post: a_post['topic_id'] == topic_id,posts))
    return posts_in_a_topic 

def get_post_ids_in_a_topic(topic_id):
    api_url = discourse_url + f"/t/-/{topic_id}.json"
    #print(api_url)
    res = requests.get(api_url)
    res = res.json()
    post_ids_in_a_topic = res['post_stream']['stream']
    return post_ids_in_a_topic

def get_all_messages(posts_dict):
    all_messages = []
    for a_post_id in posts_dict.keys():
        a_post = posts_dict[a_post_id]
        a_message = a_post['cooked']
        all_messages.append(a_message)
    return all_messages

def get_all_messages_without_the_user(posts_dict,the_user):
    all_messages = []
    for a_post_id in posts_dict.keys():
        a_post = posts_dict[a_post_id]
        a_message = a_post['cooked']
        if a_post['username'] != the_user:
            all_messages.append(a_message)
    return all_messages        

def get_recent_post_in_topic(topic_id): 
    api_url = discourse_url + f"/t/-/{topic_id}.json"
    res = requests.get(api_url)
    res = res.json()
    post_ids_list_in_a_topic = list(res['post_stream']['stream'])
    recent_post_id = post_ids_list_in_a_topic[-1]
    return get_a_post(recent_post_id)

def dateKey(aPost):
    dateStr = aPost['created_at']
    return datetime.datetime.strptime(dateStr,'%Y-%m-%dT%H:%M:%S.%fZ')

def get_a_post(post_id):
    api_url = discourse_url + f"posts/{post_id}.json"
    res = requests.get(api_url)
    res = res.json()
    return res

def get_topic(topic_id):
    api_url = discourse_url + f"t/{topic_id}.json/"
    res = requests.get(api_url)
    res = res.json()
    return res

def get_all_categories():
    api_url = discourse_url + "categories.json/"
    res = requests.get(api_url)
    res = res.json()
    return res

def show_category(id):
    api_url = discourse_url + f"c/{id}/show.json"
    res = requests.get(api_url)
    res = res.json()
    return res

def split_by_token(text,block_size,sep):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    if type(text) is not list:
        lines = text.split(sep)
    else:
        lines = text
    blocks = []
    token = 0
    block = ''
    for line in lines:
        t = len(encoding.encode(line))
        if token > 0 and block_size < (token + t):
            blocks.append(block)
        token = 0
        block = '' 
        token += t
        block += line
        blocks.append(block)
    return blocks

