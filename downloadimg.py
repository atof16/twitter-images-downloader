import os
import csv
import tweepy
import urllib.request
import urllib.error
import pandas as pd
import config

# 画像保存先ディレクトリ 無ければ作成
IMAGES_DIR = './images/'
if not os.path.exists(IMAGES_DIR):
    os.mkdir(IMAGES_DIR)

# Twitter API keys
CK = config.consumer_key
CS = config.consumer_secret
AT = config.access_token
AS = config.access_token_secret


def get_oauth():
    """
    API認証
    """
    auth = auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth, wait_on_rate_limit = True)
    return api


def search(api, term, count, fpath):
    """
    ツイートの検索 termで検索ワード、countで検索数指定
    """
    cpath = os.path.join(fpath, 'info.csv')
    download_url_list = []
    tw_info = []
    search_tweets = api.search(q=term, count=count)
    for tweet in search_tweets:
        if 'media' in tweet.entities:
            for media in tweet.entities['media']:
                url = media['media_url_https']
                if os.path.exists(cpath):
                    if check_url(cpath, url.split('/')[-1]):
                        continue
                download_url_list.append(url)
                # ツイート情報を保存
                tw_info.append([tweet.user.screen_name, url.split('/')[-1], 
                                tweet.created_at, tweet.text.replace('\n', ''), 
                                tweet.favorite_count, tweet.retweet_count])
    # ツイート情報をcsvとして出力
    # 検索ワードのディレクトリごとに作成
    output_csv(cpath, tw_info)
    return download_url_list


def output_csv(cpath, tw_info):
    """
    画像ファイルとツイート情報を紐づけ
    """
    if not os.path.exists(cpath):
        with open(cpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(['user', 'imgpath', 'created_at', 'description', 'fav', 'RT'])
            writer.writerows(tw_info)
    else:
        check_url(cpath, tw_info)
        with open(cpath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(tw_info)


def check_url(cpath, url):
    """
    過去にダウンロードした画像は保存しない
    """
    urllist = pd.read_csv(cpath).values.tolist()
    for temp in urllist:
        if temp[1] == url:
            return True
    return False


def download(fpath, url):
    """
    検索で得られたツイートの画像をダウンロード
    """
    url_orig = '{}:orig'.format(url)
    imgpath = os.path.join(fpath, url.split('/')[-1])
    response = urllib.request.urlopen(url=url_orig)
    with open(imgpath, "wb") as f:
        f.write(response.read())


def main():
    api = get_oauth()
    # 検索ワード
    terms = ['']
    # 検索条件
    query = ''
    # 検索数
    count = 40
    for tmp in terms:
        # 検索語句ごとにフォルダ作成
        # 検索ワードとのパスを結合
        fpath = os.path.join(IMAGES_DIR, tmp)
        if not os.path.exists(fpath):
            os.mkdir(fpath)

        term = '{} {}'.format(tmp, query)
        urls = search(api, term, count, fpath)
        dwcount = 0
        for url in urls:
            print('downloading... {}'.format(url))
            download(fpath, url)
            dwcount += 1
        print('downloaded {} images'.format(dwcount))

if __name__ == '__main__':
    main()