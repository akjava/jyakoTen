import MeCab
import pyopenjtalk
import difflib
from nltk.metrics.distance import edit_distance

from . import mora_utils,kanji_split
# Create Mecab instance

# default design for unidic_lite
mecab = MeCab.Tagger()
dic_split ="\t" #, if unidic
dic_index = 1 # 9 unidic



def is_unidic_lite():
    path = MeCab.try_import_unidic()
    return path.find("unidic_lite")!=-1

if not is_unidic_lite():
    print("be caraful seems not unidic_lite is primary(maybe unidic installed)")

def get_unidic_lite_arg():
    import unidic_lite
    path = unidic_lite.__path__[0]
    path = path.replace("\\","/")
    return f"-r {path}/dicdir/mecabrc -d {path}/dicdir"

def set_up_mecab(args,split=",",index=9):
    print(f"mecab utils set mecab dic(unidic) to {args} split='{split}' index={index}")
    global mecab
    mecab = MeCab.Tagger(args)
    global dic_split
    global dic_index 
    dic_split = split #, if unidic
    dic_index = index # 9 unidic



def extract_unique_kanas(kanji,nbest_size=512):
    uniq_kanas = set()
    # parse and split wordss
    words = mecab.parseNBest(nbest_size,kanji)
    #print(words)
    kana = ""
    lines = words.split('\n')
    for line in lines:
        if line == "EOS":
            #print("End of Line")
            if not kana in uniq_kanas:
                uniq_kanas.add(kana)
            kana = ""
            continue

        
        
        data = line.split(dic_split)
       
        if len(data)>dic_index:
            #print(data[9])
            kana+=data[dic_index]
        else:
            kana+=data[0].split("\t")[0] #unidic index 0 has tab-separated 
            
            #print(data[9])
    return list(uniq_kanas)

    
def get_best_text(header,text,correct,use_mecab=True,convert_mora=True):
    phones2 = pyopenjtalk.g2p(correct, kana=False)
    moras2 = mora_utils.phonemes_to_mora(phones2,True,convert_mora)
    #moras2 = phones2.split(" ")

    #print(kanas)
    high_score = 0
    high_text = ""
    high_moras = []
    if use_mecab:
        kanas = extract_unique_kanas(text,512)
    else:
        kanas = [text]

    for kana in kanas:
        phones1 = pyopenjtalk.g2p(header+kana, kana=False)
        moras1 = mora_utils.phonemes_to_mora(phones1,True,convert_mora)
       
        mora2_joined = " ".join(moras2)
        d = edit_distance(" ".join(moras1),mora2_joined )
        current_score = 1.0 - max(1.0, d / len(mora2_joined))
       
        if current_score >high_score:
            high_score = current_score
            high_text = kana
            high_moras = moras1
        #print(f"{current_score} {kana} {moras1},{moras2}")
        #print(f"{current_score} {kana}")
    return [high_score,high_text,high_moras]



def get_best_group(result,correct,use_mecab=True,split_group=True,convert_mora=False):
    score = 0
    moras1 =[]
    if split_group:
        groups = kanji_split.split_kanji_group(result)
    else:
        groups = [result]
    #print(groups)
    

    result = ""
    for group in groups:
        #print(result+group)
        score,text,moras1 = get_best_text(result,group,correct,use_mecab,convert_mora)
        #print(f"{score} = {text}")
        result += text
    return [score,result,moras1]