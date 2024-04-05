import re

# ひらがなの範囲
hiragana_range = '[\u3041-\u309F]+'
# カタカナの範囲
katakana_range = '[\u30A1-\u30FF]+'

# 正規表現パターンを作成
pattern = re.compile(f'{hiragana_range}|{katakana_range}')



def split_kanji_dic(text):
    text_groups = []
    text_groups_dic ={}
    is_kana = True
    group_text = ""
    for char in text:
        if is_kana:
            if pattern.match(char):
                group_text += char
            else:
                if group_text!="":# at first
                    text_groups.append(group_text)
                    text_groups_dic[group_text] = is_kana
                group_text = ""+char
                is_kana = False
        else:
            if pattern.match(char):
                if group_text!="":
                    text_groups.append(group_text)
                text_groups_dic[group_text] = is_kana
                group_text = ""+char
                is_kana = True
            else:
                group_text += char
    if group_text != "":
        text_groups.append(group_text)
        text_groups_dic[group_text] = is_kana

    return text_groups_dic
#print(text_groups)
    
def split_kanji_group(text):
    text_groups_dic = split_kanji_dic(text)
    has_kanji=False
    text_groups = []
    text =""
    for item in text_groups_dic:
        if has_kanji:
            if text_groups_dic[item]:
                text += item
            else:
                if text!="":
                    text_groups.append(text)
                text = item
                has_kanji = True
        else:
            if text_groups_dic[item]:
                text += item
            else:
                text += item
                has_kanji = True

    if text!="":
        text_groups.append(text)

    return text_groups

#print(split_kanji_group(text))
    





