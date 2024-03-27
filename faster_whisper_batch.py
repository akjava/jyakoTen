from faster_whisper import WhisperModel
import argparse
import os
import time

import re
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

ver = 0.1

# arg parser
parser = argparse.ArgumentParser(description='Process language option.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--audio_dir', type=str, help='Path to the audio file.')
group.add_argument('--audio_file_list', type=str, help='Name list of the audio file.If audio_dir files not formated.like 1.wav 10.wav')

parser.add_argument('--audio_list_dir', type=str, help='If exist combine audio_list_dir/audio_file_list',default = "")

parser.add_argument('--out', 
                    help='outputpath')
parser.add_argument('--add_audio_path', 
                    help='output has audio path',action='store_true') #type bool is broken
parser.add_argument('--out_splitter', 
                    help='output text splitter', default =":")

parser.add_argument('--lang', choices=['en', 'ja'], default='ja',
                    help='Language option (en or ja)')
parser.add_argument('--compute_type', choices=['int8', 'float32'], default='float32',
                    help='float16 or int8_float16 ,only support some device')

parser.add_argument('--beam', 
                    help='faster whisper beam',type = int,default = 10)
parser.add_argument('--no_vad', 
                    help='not use vad',action='store_false')
parser.add_argument('--cpu', 
                    help='CPU Mode',action='store_true')

# TODO device
args = parser.parse_args()


audio_dir = args.audio_dir
add_audio_path = args.add_audio_path
out_splitter = args.out_splitter
use_vad = args.no_vad
cpu = args.cpu

lang = args.lang
out = args.out
beam = args.beam

print(args)

def safe_filename(filename):
    # replace invalid filename charas
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # take care max file name size
    return filename[:255-4]




base_path = os.path.dirname(os.path.abspath(__file__))
def full_path(*relative_paths):
    return os.path.join(base_path, *relative_paths)

# TODO add model_
model_name = "large-v3"


#model = WhisperModel(model_name, device="cuda", compute_type="int8_float16") #4 time faster 1sec
if cpu:
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    if args.compute_type!="int8":
        print("warrning device cpu only support int8") 
else:
    model = WhisperModel(model_name, device="cuda", compute_type=args.compute_type) 

def whisper_transcribe(audio_path):
    segments, info = model.transcribe(audio_path, language=lang,beam_size=beam,vad_filter=use_vad,without_timestamps=True,word_timestamps=False)
    #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    texts = []
    for segment in segments:
        texts.append(segment.text)

    return '\n'.join(texts)


def run_script(audio_path):
    """指定されたターゲットディレクトリでスクリプトを実行します。"""
    try:
        result = transcribe(audio_path)
    except RuntimeError as e:
        print(f"{audio_path} のスクリプト実行中にエラーが発生しました: {e}")
    return result


    
        
def transcribe(path):
    print(path)
    if path.lower().endswith(".wav") or path.lower().endswith(".mp3"):
        result = whisper_transcribe(path)
        
        if add_audio_path:
            output_line = f"{path}{out_splitter}{result}"
        else:
            output_line=result
            
    else:
        print(f"not support file {path}")
        return ""
    
    return output_line +"\n"


output_lines =[]
def thread_execute(run_script,arg1,max_workers=1):
    global out 
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_script, audio_path) for audio_path in arg1]

        for future in as_completed(futures):
            try:
                output_lines.append(future.result())
            except Exception as e:
                print(e)
    if not out:
        out = f"fw_batch_result_{args.compute_type}.txt"
    with open(out, 'w') as f:
        f.writelines(output_lines)



if __name__ == "__main__":
    print("faster-whisper-batch ver: %s model: %s audio_txt = %s,dir = %s"%(ver,model_name,args.audio_file_list,audio_dir))
    audios_paths = []
    if args.audio_file_list:
        with open(args.audio_file_list) as f:
            filenames = f.readlines()
            for filename in filenames:
                filename = filename.replace("\n","")
                if args.audio_file_dir:
                    filename = args.audio_file_dir+"/"+filename
                audios_paths.append(filename)
            thread_execute(run_script,audios_paths)
               
    else:
        filenames = os.listdir(audio_dir)
        filenames.sort()
        for filename in filenames:
            if filename.endswith(".wav") or filename.endswith(".mp3"):
                filename = audio_dir+"/"+filename
                audios_paths.append(filename)
        thread_execute(run_script,audios_paths)



