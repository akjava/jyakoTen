MORAS = ["a","i","u","e","o",
               "ba","bi","bu","be","bo",
               "bya",   "byu","bye","byo",
               "cha","chi","chu","che","cho",
               "da","di","du","de","do",
               "dya",   "dyu",  "dyo",
               "fa","fi","fu","fe","fo",
               "ga","gi","gu","ge","go",
               "gya",   "gyu","gye","gyo",
               "ha","hi",   "he","ho",
               "hya",   "hyu","hye","hyo",
               "ja","ji","ju","je","jo",
               "ka","ki","ku","ke","ko",
               "kya",   "kyu","kye","kyo",
               "ma","mi","mu","me","mo",
               "mya",   "myu","mye","myo",
               "na","ni","nu","ne","no",
               "nya",   "nyu","nye","nyo",
               "pa","pi","pu","pe","po",
               "pya",   "pyu","pye","pyo",
               "ra","ri","ru","re","ro",
               "rya",   "ryu","rye","ryo",
               "sa","si","su","se","so",
               "sha","shi","shu","she","sho",
               "ta","ti","tu","te","to",
               "tsa","tsi","tsu","tse","tso",
               "tya",   "tyu",  "tyo",
               "va", "vi", "vu", "ve", "vo",
               "wa","wi",   "we","wo",
               "ya",    "yu","ye","yo",
               "za","zi","zu","ze","zo"]
MORA_N = "N"
MORA_CL = "cl"

def is_vowel(phonem):
    vowels = ["a","i","u","e","o"]
    for vowel in vowels:
        if vowel == phonem.lower():
            return True
    return False

def phonemes_to_mora(g2p_text,ignore_kanma = False,convert_mora=True):
    g2p_text = g2p_text.replace("pau",",")
    # TODO option
    g2p_text = g2p_text.replace("A","a")
    g2p_text = g2p_text.replace("I","i")
    g2p_text = g2p_text.replace("U","u")
    g2p_text = g2p_text.replace("E","e")
    g2p_text = g2p_text.replace("O","o")
    moras = []
    phonemes = g2p_text.split(" ")

    if not convert_mora: #just clean g2p
        for phoneme in phonemes:
            if phoneme == ",":
                if not ignore_kanma:
                    moras.append(",")
            elif phoneme == "":
                continue
            else:
                moras.append(phoneme)
        return moras

    is_last_vowel = False
    last = ""
    for phoneme in phonemes:
        #print(phoneme)
        if phoneme == "N":
            moras.append("N")
        elif phoneme == ",":
            if not ignore_kanma:
                moras.append(",")
        elif phoneme == "cl":
            moras.append("cl")
        else :
            
            if is_vowel(phoneme):
                if is_last_vowel:
                    moras.append(last)
                    is_last_vowel = True
                    last = phoneme
                else:
                    moras.append(last+phoneme)
                    is_last_vowel = False
                    last = ""
            else:
                if is_last_vowel:
                    moras.append(last)
                    is_last_vowel = False
                    last = phoneme
                else:
                    if last:
                        print(f"invalid convination {last} {phoneme}:{phonemes}")
                        break
                    else:
                        is_last_vowel = False
                        last = phoneme
    if last:
        if is_last_vowel:
            moras.append(last)
        else:
            print(f"invalid last mora {last} :{phonemes}")
    return moras

def get_all_moras(spacer = " "):
    output = []
    text = ""
    for mora in MORAS:
        if "a" in mora:
            output.append(text)
            text = ""
        text += mora if text == "" else spacer+mora
        #print(text)
    if text != "":
        output.append(text)
    return output