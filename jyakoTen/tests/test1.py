REPLACE_WORD = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z','0','1','2','3','4','5','6','7','8','9','0','#','$','%','&','(',')','=','~','|','<','>','*','+','-','_']
def convert_to_two_character(moras):
    replace_dic={}
    result = []
    word_index = 0
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

print(convert_to_two_character(['a','ka','kya']))
print(convert_to_two_character("na no ko ga ki cl ki cl u re shi so".split(" ")))