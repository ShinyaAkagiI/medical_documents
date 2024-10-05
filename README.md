# 概要

Answers Newsに掲載された2018年度国内医薬品売上高ランキングのランキング上位50件の医薬品名(https://answers.ten-navi.com/pharmanews/16487/) について, 医薬品添付文書とくすりのしおり®︎の文章を抽出したデータセットを作成および公開している.  
  
医薬品添付文書からは『警告』, 『禁忌』, 『効能・効果』, 『用法・用量』, 『使用上の注意』『副作用』の文章を抽出し, くすりのしおり®︎からは『この薬の作用と効果について』, 『次のような方は使う前に必ず担当の医師と薬剤師に伝えてください』, 『生活上の注意』, 『この薬を使ったあと気をつけていただくこと（副作用）』の文章を抽出している.組成・性状, 相互作用など, 文章として抽出が難しかったり, 比較分析に使用しづらかったりした項目は一部抽出していない.また, 医薬品添付文書の表に記載されていた文章を抽出した際, 改行や「, 」で区切って体裁を整えており, 元の記載内容と構成が少し変わっている.  
  
グラクティブの説明文が医薬品添付文書に存在しなかったり, サイラムザ, リュープリン, アリムタ, アイリーアの説明文がくすりのしおり®︎に存在しなかったり, ランキング上で重複していた医薬品名を１つにまとめたりしたため, 医薬品添付文書の文書数は48件, くすりのしおり®︎の文書数は計45件, 両方に文章が存在するのは44件となっている.  
  
また, 複合名詞に対して助詞「の」を補完するプログラム（complete.py）も公開している.  
  
  
# データセットの使い方

```
from calculate_readability import calculate_readability

# attachment: 医薬品添付文書
# kusurinoshiori: くすりのしおり®︎
with open("attachment", "r") as f:
    # parse the dataset
    dataset = f.read()
    dataset = dataset.split(",\n")
    dataset = [ data.split(",",3) for data in dataset ]

    count = 0

    # data[0]: medicine name
    # data[1]: disease name
    # data[2]: company name
    # data[3]: document
    for data in dataset:
        try:
            result = calculate_readability(data[3])
            print(data[0], result["jfre"])
            count += 1
        except:
            print("")

    print("データ数：{}".format(count))
```
  
# 関連論文
- 変数置き換えモデルを用いた医薬品情報の可読性分析と検索件数を用いた複合名詞の文章平易化の検討
  - Shinya Akagi, 2022-09
  - https://jglobal.jst.go.jp/detail?JGLOBAL_ID=202202255387090014

