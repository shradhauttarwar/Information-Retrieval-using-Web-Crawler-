#ShradhaUttarwar

import io 
import json
word_dic_full = {}
for line in io.open("words_porter.json", 'r', encoding='utf-8'):
    new_line = line.replace('\n', '').replace('\r', '').strip() 
    if new_line != '':
        word_dic = json.loads(new_line) 
        for key in word_dic.keys():
            if key != '*DocID*' and key != '*description*' and key != '*url*' and key != '*title*': 
                if key not in word_dic_full:
                    word_dic_full[key] = [0 for _ in range(40)]
                    word_dic_full[key][word_dic['*DocID*']-1] += word_dic[key] 
                else:
                    word_dic_full[key][word_dic['*DocID*']-1] += word_dic[key]
with io.open('Words_Frequency_Matrix_porter_query.json', 'a', encoding='utf-8') as file: 
    for item in word_dic_full.keys():
        word_dic_temp = {}
        word_dic_temp[item] = word_dic_full[item] 
        file.write(json.dumps(word_dic_temp, ensure_ascii=False)) 
        line = u"\r\n"
        file.write(line)