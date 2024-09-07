import pyopenjtalk
import difflib
import os
import argparse

from .utils import mora_utils,mecab_utils,alkana_utils

def replace_chars(line):
    line = line.replace("\n","")
    line = line.replace("、","")
    line = line.replace("?","")
    line = line.replace("!","")
    line = line.replace("。","")
    line = line.replace("？","")
    line = line.replace("！","")
    return line


def detect_success_fail_words(word1,word2):
    d = difflib.Differ()
    diff = d.compare(word1, word2)
    success = []
    faild = []
    for line in diff:
        split = line.split(" ")
        if  split[0] == "":
            success.append(split[2])
        else:
            if split[0] == "+":
                faild.append(split[1])
        #print(f"result = '{line}'")
    return " ".join(success)," ".join(faild)


# arg parser
def score_main():
     parser = argparse.ArgumentParser(description='Score result')
     parser.add_argument('--transcript_path',"-tp" ,
                         help='correct text path')
     parser.add_argument('--transcript_index', "-ti",
                         help='1 for kana',default=1,type=int)
     parser.add_argument('--transcript_splitter',"-ts" ,
                         help='split text',default=":")

     parser.add_argument('--min_score' ,
                         help='print minscore',type = float, default=0)

     parser.add_argument('--recognition_path', "-rp",
                         help='correct text path')
     parser.add_argument('--recognition_index', "-ri",
                         help='0 means flat',default=0,type=int)
     parser.add_argument('--recognition_splitter',"-rs" ,
                         help='split text',default="|")

     parser.add_argument('--key_dir', 
                         help='file exist dir')
     
     parser.add_argument('--key1', 
                         help='key1 cv01 or ita01..')
     parser.add_argument('--key2', 
                         help='key2 epoch number or voice changed  cv02',default='0000')

     parser.add_argument('--key3', 
                         help='key3 recitation or emotion or endsville400',default='recitation')
     parser.add_argument('--key4', 
                         help='optional int or float')
     parser.add_argument('--no_mecab', 
                         help='not use mecab',action='store_false')
     parser.add_argument('--use_mora', 
                         help='calcurate mora base',action='store_true')


     args = parser.parse_args()
     key1 = args.key1
     key2 = args.key2
     key3 = args.key3
     key4 = args.key4
     use_mecab = args.no_mecab

     transcript_path = args.transcript_path
     transcript_index = args.transcript_index
     transcript_splitter = args.transcript_splitter

     recognition_path = args.recognition_path
     recognition_index = args.recognition_index
     recognition_splitter = args.recognition_splitter

     min_score = args.min_score

     # use openjtalk dic and replace text
     use_user_dic = False

     # check args
     if args.recognition_path is None and args.key1 is None:
          print("Error: At least one of --recognition_path or --key1 must be specified.")
          parser.print_help() 
          exit(1) 




     current_dir=os.path.dirname(__file__)

     if use_user_dic:
          pyopenjtalk.mecab_dict_index(current_dir+"/"+"user.csv", "user.dic")
          pyopenjtalk.update_global_jtalk_with_user_dict("user.dic")


     emotion_path = "transcripts/emotion_transcript_utf8.txt"
     emotion_path = current_dir+"/transcripts/"+f"{key3}_transcript_utf8.txt"
    
     if transcript_path:
          print(f"use transcript:{transcript_path} index = {transcript_index}")
          emotion_path = transcript_path
     emotion_kanas = []
     with open(emotion_path) as f:
          lines = f.readlines()
          for line in lines:
               line = line.replace("\n","")
               if line == "":
                    continue
               id,kanji_kana = line.split(transcript_splitter)
               kanji_kana = kanji_kana.split(",")
               kana = kanji_kana[transcript_index]
               kana = replace_chars(kana)
               emotion_kanas.append(kana)


     option_key=""
     if key4!= None:
          option_key="_"+key4
     


     file_path = f"{key1}_{key2}_{key3}_result{option_key}.txt"
     if args.key_dir!= None:
          file_path = os.path.join(args.key_dir,file_path)
     else:
          file_path = os.path.join(os.getcwd(),file_path) 
          
     
     if recognition_path:
          print(f"file path({file_path}) replaced recognition_path({recognition_path})")
          file_path = recognition_path




     index = 0
     out = []
     lows = []
     total_score = 0
     low_text = ""
     low_score = 1
     case2 = 0
     case3 = 0


     with open(file_path) as f:
          lines = f.readlines()
          for line in lines:
               
               values = line.split(recognition_splitter)
               line = values[recognition_index]
               line = replace_chars(line)
               
               converted_dic=alkana_utils.convert_alphabet_to_kana(line)
               
               if line != converted_dic["text"]:
                    print(f"English-Converted {line} to {converted_dic['text']}")
                    line = converted_dic["text"]
               else:
                    if converted_dic["no_alakana_words"]:
                         print(f"Converting English to Kan faild(no in dictionary) or skipped(short words) {converted_dic['no_alakana_words']}.most of case pronounce english is too bad.should add dictionary the wordss")

               # TODO separate dic
               # recitation 324  
               if key3 == "recitation":
                    line = line.replace("1877","センハッピャクナナジュウナナ")

               line= line.replace("50-50","フィフティーフィフティー")
               if use_user_dic:
                    line= line.replace("50-50","フィフティーフィフティー")
                    line= line.replace("720","セブントゥウェンティ")
                    line= line.replace("7-20","セブントゥウェンティ")
                    line= line.replace("360","スリーシックスティ")
               
               

               kana = emotion_kanas[index]
               phones2 = pyopenjtalk.g2p(kana, kana=False)
               moras2 = mora_utils.phonemes_to_mora(phones2,True)
               
               
               high_score,high_score_text,high_moras = mecab_utils.get_best_group(line,kana,True,args.use_mora)
               high_score2,high_score_text2,high_moras2 = mecab_utils.get_best_group(line,kana,False,True,args.use_mora)
               if high_score2 > high_score:
                    high_score = high_score2
                    high_score_text = high_score_text2
                    high_moras = high_moras2
                    case2+=1
               high_score3,high_score_text3,high_moras3 = mecab_utils.get_best_group(line,kana,True,False,args.use_mora)
               if high_score3 > high_score:
                    is_case2 = high_score == high_score2
                    high_score = high_score3
                    high_score_text = high_score_text3
                    high_moras = high_moras3
                    case3+=1
                    if is_case2:
                         case3-=1
               

               score = high_score

               
               if score <low_score:
                    low_score = score
                    low_text = line+"/"+high_score_text
                    low_correct = kana
                    low_id = index

               sucdess, faild = detect_success_fail_words(high_moras, moras2)
               
               # convert readable text
               moras1 = " ".join(high_moras)
               moras2 = " ".join(moras2)

               result = f"{index+1:03d},{score},{faild},{sucdess},{line},{high_score_text},{kana},{moras1},{moras2}\n"
               out.append(result)
               if score < min_score:
                    lows.append(result)
               total_score += score
               
               index += 1
               
     max_score = index
     print(f"{key1} {key2} Total:{total_score}")
     print(f"Lowest:{low_id} {low_score}:{low_text} = {low_correct}")
     # TODO add verbose mode
     #print(f"no mecab:{case2},no group:{case3}")
     score = total_score
     for low in lows:
          print(low)

     if not use_mecab:
          option_key +="_no-mecab"

     if args.use_mora:
          option_key +="_use-mora"

     output_file_name = f"{key1}_{key2}_{key3}_score({score:.3f} of {max_score}){option_key}.txt"
     output_path = os.path.join(os.getcwd(),output_file_name) 

     with open(output_path, 'w') as f:
          f.writelines(out)