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
            yomi = data[dic_index].strip()
            raw = data[0].strip()
           
            if yomi == "" and (raw=="っ" or raw=="ッ"):
                kana+="ッ"
            else:
                kana+=yomi
        else:
            kana+=data[0].split("\t")[0] #unidic index 0 has tab-separated 
            
            #print(data[9])
    return list(uniq_kanas)

    
# possible voewl AIUEO & N skipped.
REPLACE_WORD = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z','0','1','2','3','4','5','6','7','8','9','0','#','$','%','&','(',')','=','~','|','<','>','*','+','-','_']
replace_dic={}
word_index = 0

SINGLE_WORDS =['a','b', 'c', 'd', 'e','f', 'g', 'h', 'i','j', 'k', 'l', 'm','n','o', 'p', 'q', 'r', 's', 't', 'u','v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','0','1','2','3','4','5','6','7','8','9','0','#','$','%','&','(',')','=','~','|','<','>','*','+','-','_']
def convert_to_two_character(moras):
    global word_index
    global replace_dic
    result = []
    for mora in moras:
        mora_length = len(mora)
        if mora_length == 1:
            result.append(mora*2)
        elif mora_length == 2:
            result.append(mora)
        elif mora_length > 2:
            last_char = mora[-1]
            const = mora[0:-1]
            one_char = None
            if const in replace_dic:
                one_char = replace_dic[const]
            else:
                one_char = REPLACE_WORD[word_index]
                replace_dic[const] = one_char
                word_index+=1
                if word_index >= len(REPLACE_WORD):
                    print("maybe never happen")
                    word_index = 0
                
            result.append(one_char+last_char)
    return result

def convert_to_single_character(word1,word2):
    s_index = 0
    s_dic ={}
    one_word1s=[]
    one_word2s=[]
    for w in word1:
        if w in s_dic:
            one_word1s.append(s_dic[w])
        else:
            if s_index<len(SINGLE_WORDS):
                new_key = SINGLE_WORDS[s_index]
                s_index+=1
                s_dic[w]=new_key
                one_word1s.append(s_dic[w])
            else:#out out key
                one_word1s.append(w)
    for w in word2:
        if w in s_dic:
            one_word2s.append(s_dic[w])
        else:
            if s_index<len(SINGLE_WORDS):
                new_key = SINGLE_WORDS[s_index]
                s_index+=1
                s_dic[w]=new_key
                one_word2s.append(s_dic[w])
            else:#out out key
                one_word2s.append(w)
    return one_word1s,one_word2s             
       

def get_mora_phonome_error_rate(phonome1, phonome2,joiner=" "):
    text1=convert_to_two_character(phonome1)
    text2=convert_to_two_character(phonome2)

    words1,words2 = convert_to_single_character(text1,text2)
    #print(words1)
    #print(words2)
    mora_error_rate= get_cer(joiner.join(words1),joiner.join(words2))
    phonome_error_rate= get_cer(joiner.join(text1),joiner.join(text2))
    return mora_error_rate,phonome_error_rate

def get_cer(transcript, detect):
    if detect == "":
        return 1.0
    d = edit_distance(transcript, detect)
    cer = float(d) / max(len(transcript), len(detect))  
    return cer



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
        
        #print(header+kana,phones1)
       
        #oh my slow
        #mora2_joined = " ".join(moras2)
        #d = edit_distance(" ".join(moras1),mora2_joined )
        #current_score = 1.0 - max(0, d / len(mora2_joined))
        
        matcher = difflib.SequenceMatcher(None, moras1, moras2)
        current_score = matcher.ratio()

       
        if current_score >high_score:
            high_score = current_score
            high_text = kana
            high_moras = moras1
        #print(f"{current_score} {kana} {moras1},{moras2}")
        #print(f"{current_score} {kana}")

    if not convert_mora:
        re_text = " ".join(high_moras)
        high_moras = mora_utils.phonemes_to_mora(re_text,False,True)
    
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
    for group in groups:#
        #print(result+group)
        score,text,moras1 = get_best_text(result,group,correct,use_mecab,convert_mora)
        #print(f"{score} = {text}")
        result += text
    return [score,result,moras1]