#-*- coding: utf-8 -*-

import MeCab
import requests
import time

# mecab-ipadic-neologdを使用
#tagger = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
tagger = MeCab.Tagger()

# 検索件数取得用のAPIキー、カスタム検索エンジンID
GOOGLE_API_KEY = "please_input_your_api_key"
GOOGLE_SEARCH_ENGINE_ID = "please_input_your_search_engine_id"
BING_API_KEY = "please_input_your_api_key"

# 分析ファイル
dname = "kusurinoshiori_texts"
fname= "オプジーボ"
#fname= "イーケプラ"
#fname = "シムビコート"
#fname = "キイトルーダ"
#fname = "アバスチン"
#fname = "グラクティブ"
#fname = "セレコックス"
#fname = "プログラフ"

# 複合名詞リストの取得
def get_compound_nouns(text):
	#text = text.replace(" ", "　")
	text = text.replace("(", "（")
	text = text.replace("[", "［")
	text = text.replace(")", "）")
	text = text.replace("]", "］")
	#print(text)
	node = tagger.parseToNode(text)
	terms = []

	# 複合名詞の接続箇所の取得
	conj = []
	count = 0
	node = node.next
	while node:
		# 単語
		term = node.surface
		terms.append(term)

		# 品詞
		pos1 = node.feature.split(",")[0]
		pos2 = node.feature.split(",")[1]
		prev_pos1 = node.prev.feature.split(",")[0]
		prev_pos2 = node.prev.feature.split(",")[1]

		#print(term, pos1, pos2)
	
		if pos1 in ["名詞"] and prev_pos1 in ["名詞"]:
			if pos2 in ["一般", "固有名詞", "サ変接続"] and prev_pos2 in ["一般", "固有名詞", "サ変接続"]:
			#if pos2 in ["一般", "固有名詞", "サ変接続", "数"] and prev_pos2 in ["一般", "固有名詞", "サ変接続", "数"]:
			#if pos2 in ["一般", "固有名詞", "サ変接続", "接尾"] and prev_pos2 in ["一般", "固有名詞", "サ変接続", "接尾"]:
			#if pos2 in ["一般", "固有名詞", "サ変接続", "形容動詞語幹"] and prev_pos2 in ["一般", "固有名詞", "サ変接続", "形容動詞語幹"]:
				conj.append(count)
		count += 1
		node = node.next

	#print(conj)

	# 接続開始点と接続終了点を求める
	conj2 = [c-1 for c in conj]
	i_terms = sorted(list(set(conj) ^ set(conj2)))

	#print(i_terms)

	# 複合名詞リストの作成
	compound_nouns_list = []
	for i in range(0, len(i_terms), 2):
		compound_nouns_list.append({"text":"".join(terms[i_terms[i]:i_terms[i+1]+1]),
					    "morph":terms[i_terms[i]:i_terms[i+1]+1]})

	compound_nouns_list2 = []
	for c in compound_nouns_list:
		#文頭または文末の形態素が１の複合名詞を除外
		if len(c["morph"][0]) > 1 and len(c["morph"][-1]) > 1:
		#文頭または文末の形態素が１、または、2つの形態素からなる複合名詞を除外
		#if (len(c["morph"][0]) > 1 and len(c["morph"][-1]) > 1) or len(c["morph"]) > 2:
			compound_nouns_list2.append(c)

	return compound_nouns_list


#助詞を補完した検索クエリリストを作成
def create_complete_search_query(compound_nouns):
	# 用語リスト
	words = []

	# 複合名詞を用語リストに追加
	words.append(compound_nouns["text"])

	# 助詞を補完した検索クエリを作成
	for i in range(len(compound_nouns["morph"])-1):
		word = "".join(compound_nouns["morph"][:i+1]) + "の" + "".join(compound_nouns["morph"][i+1:])
		words.append(word)

	return words


# 検索件数の取得
def search_wikipedia_number(word):
	search_url = "https://ja.wikipedia.org/w/api.php"
	params = {
		"format": "json",
		"action": "query",
		"list": "search",
		"srsearch": word
	}
	response = requests.get(search_url, params=params)
	response.raise_for_status()
	try:
		search_number = response.json()["query"]["searchinfo"]["totalhits"]
	except:
		search_number = 0
	#接続負荷を軽減するため待機
	time.sleep(3)	
	return search_number


def search_google_number(word):
	search_url = "https://www.googleapis.com/customsearch/v1"
	params = {
		"key": GOOGLE_API_KEY,
		"cx": GOOGLE_SEARCH_ENGINE_ID,
		"q": word
	}
	response = requests.get(search_url, params=params)
	response.raise_for_status()
	try:
		search_number = response.json()["searchInformation"]["totalResults"]
	except:
		search_number = 0
	#接続制限を回避するため待機
	time.sleep(3)	
	return search_number


def search_bing_number(word):
	search_url = "https://api.bing.microsoft.com/v7.0/search"
	headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
	params = {
		"q": word,
		"textFormat": "HTML"
	}
	response = requests.get(search_url, headers=headers, params=params)
	response.raise_for_status()
	try:
		search_number = response.json()["webPages"]["totalEstimatedMatches"]
	except:
		search_number = 0
	#接続制限を回避するため待機
	time.sleep(3)
	return search_number


# 複合名詞の検索件数リストを取得
def get_search_numbers_list_wikipedia(fname, cn_query):
	# 複合名詞の検索件数リスト
	cn_search_numbers_list = []
	for cn in cn_query:
		# 元となる複合名詞のデータ構造
		cn_search_numbers = {"text": cn[0], "search_number":"", "complete_search":[]}
		# 検索件数の取得
		cn_search_numbers["search_number"] = search_wikipedia_number("\"" + cn[0] + "\"")
	
		# 助詞補完した検索クエリの検索件数の取得
		for word in cn[1:]:
			# 助詞補完した検索クエリのデータ構造
			cs = {"text": word, "search_number": ""}
			# 検索件数の取得
			cs["search_number"] = search_wikipedia_number("\"" + word + "\"")
			cn_search_numbers["complete_search"].append(cs)

		cn_search_numbers_list.append(cn_search_numbers)
	
	with open("kaiseki_wikipedia_"+fname, "w") as f:
		f.write(str(cn_search_numbers_list))

	return cn_search_numbers_list


def get_search_numbers_list_google(fname, cn_query):
	# 複合名詞の検索件数リスト
	cn_search_numbers_list = []
	for cn in cn_query:
		# 元となる複合名詞のデータ構造
		cn_search_numbers = {"text": cn[0], "search_number":"", "complete_search":[]}
		# 検索件数の取得
		cn_search_numbers["search_number"] = search_google_number("\"" + cn[0] + "\"")
	
		# 助詞補完した検索クエリの検索件数の取得
		for word in cn[1:]:
			# 助詞補完した検索クエリのデータ構造
			cs = {"text": word, "search_number": ""}
			# 検索件数の取得
			cs["search_number"] = search_google_number("\"" + word + "\"")
			cn_search_numbers["complete_search"].append(cs)

		cn_search_numbers_list.append(cn_search_numbers)
	
	# 検索APIには無料枠のアクセス上限が設定されているため、結果はファイルに保存しておく
	with open("kaiseki_google_"+fname, "w") as f:
		f.write(str(cn_search_numbers_list))

	return cn_search_numbers_list


def get_search_numbers_list_bing(fname, cn_query):
	# 複合名詞の検索件数リスト
	cn_search_numbers_list = []
	for cn in cn_query:
		# 元となる複合名詞のデータ構造
		cn_search_numbers = {"text": cn[0], "search_number":"", "complete_search":[]}
		# 検索件数の取得
		cn_search_numbers["search_number"] = search_bing_number("\"" + cn[0] + "\"")
	
		# 助詞補完した検索クエリの検索件数の取得
		for word in cn[1:]:
			# 助詞補完した検索クエリのデータ構造
			cs = {"text": word, "search_number": ""}
			# 検索件数の取得
			cs["search_number"] = search_bing_number("\"" + word + "\"")
			cn_search_numbers["complete_search"].append(cs)

		cn_search_numbers_list.append(cn_search_numbers)
	
	# 検索APIには無料枠のアクセス上限が設定されているため、結果はファイルに保存しておく
	with open("kaiseki_bing_"+fname, "w") as f:
		f.write(str(cn_search_numbers_list))

	return cn_search_numbers_list


# 複合名詞の置換
def replace_compound_nouns(fname, cn_serach_numbers_list):
	# 置換件数
	replace_count = 0

	# 元となる文章
	with open(fname, "r") as f:
		data = f.read()

	# 置換用語の辞書
	replace_dict = {}

	# 非置換用語の辞書
	not_replace_dict = {}

	# 複合名詞一覧をループ
	for cn_search_numbers in cn_search_numbers_list:
		#print(cn_search_numbers)
		origin_cn = cn_search_numbers["text"]
		origin_sn = cn_search_numbers["search_number"]
		
		if int(origin_sn) > 0:
			#補完用語のうち検索件数が最大のものを取得
			max_cn_search = max(cn_search_numbers["complete_search"], key=lambda x:x["search_number"])
			#検索件数が最大の補完用語で置換
			if int(max_cn_search["search_number"]) > 0:
				replace_count += 1
				replace_dict[origin_cn] = max_cn_search["text"]
			else:
				not_replace_dict[origin_cn] = cn_search_numbers["complete_search"][0:]
		else:
			not_replace_dict[origin_cn] = origin_sn

	# 置換用語に部分一致が存在するかチェック
	#for w1 in replace_dict.keys():
	#	for w2 in replace_dict.keys():
	#		if w1 != w2 and w1 in w2:
	#			print("error:{} is included {} in replace_dict".format(w1, w2))

	# 置換
	# 文字列長が長いものから置換することで、置換用語に部分一致があっても問題なく置換できるようにする
	sorted_replace_items = sorted(replace_dict.items(), key=lambda x:len(x[0]), reverse=True)
	for replace_word in sorted_replace_items:
		data = data.replace(replace_word[0], replace_word[1])

	# 出力する文章
	with open(fname+"_replaced", "w") as f:
		f.write(data)

	return replace_count, replace_dict, not_replace_dict


### main ###
if __name__=="__main__":
	with open(dname+"/"+fname, "r") as f:
		data = f.read()
	cn_list = get_compound_nouns(data)

	# 複合名詞の一覧、数を表示
	#print(cn_list)
	print("複合名詞の数：{}".format(len(cn_list)))

	# 助詞を補完した検索クエリのリストを作成
	cn_query = []
	for noun in cn_list:
		words = create_complete_search_query(noun)
		cn_query.append(words)

	# 複合名詞の検索件数リストの作成、kaiseki_[wikipedia|google|bing]_fnameファイルに結果を格納
	cn_search_numbers_list = get_search_numbers_list_wikipedia(fname, cn_query)
	#cn_search_numbers_list = get_search_numbers_list_google(fname, cn_query)
	#cn_search_numbers_list = get_search_numbers_list_bing(fname, cn_query)

	# kaiseki_[wikipedia|google|bing]_fnameファイルから複合名詞の検索件数リストの読み込み
	#with open("kaiseki_wikipedia_"+fname, "r") as f:
	#with open("kaiseki_google_"+fname, "r") as f:
	#with open("kaiseki_bing_"+fname, "r") as f:
	#	cn_search_numbers_list = f.read()
	#	cn_search_numbers_list = eval(cn_search_numbers_list)
	#print(cn_search_numbers_list)

	# 複合名詞の置換、fname_replacedファイルに置換後の結果が出力される
	with open(fname, "w") as f:
		f.write(data)
	replace_data = replace_compound_nouns(fname, cn_search_numbers_list)
	print("複合名詞の置換回数：{}".format(replace_data[0]))
	print("置換用語一覧：{}".format(replace_data[1]))
	print("非置換用語一覧：{}".format(replace_data[2]))
