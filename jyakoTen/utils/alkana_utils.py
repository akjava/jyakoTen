import alkana
import re
import os

def split_camel_case(input_string):
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', input_string).split()

def convert_alphabet_to_kana(text):
    converted_text = ''
    start = 0
    cached_words = {}  # キーワードのキャッシュ用
    no_alakana_words = []
    for match in re.finditer(r'[a-zA-Z]+', text):
    #for match in re.finditer(r'[a-zA-Z]+(?:-[0-9]+)*', text):
        converted_text += text[start:match.start()]
        word = match.group()

        if word not in cached_words:  # キャッシュされていないものだけ調べる
            kana = alkana.get_kana(word)
            if kana:
                converted_text += kana
                cached_words[word] = kana  # 結果をキャッシュ
            else:
                camels = split_camel_case(word)
                camel_kana_result = []
                solve_all = True
                for camel in camels:
                    c_kana = alkana.get_kana(camel)
                    if c_kana:
                        camel_kana_result.append(c_kana)
                    else:
                        solve_all = False
                        camel_kana_result.append(camel)
                camel_kana = ''.join(camel_kana_result)  

                converted_text += camel_kana
                cached_words[word] = camel_kana
                if solve_all == False: 
                    no_alakana_words.append(camel_kana)
        else:
            converted_text += cached_words[word]  # キャッシュされた結果を使用

        start = match.end()

    converted_text += text[start:]
    
    return {"text": converted_text, "no_alakana_words": no_alakana_words}