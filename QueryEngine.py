# -*- coding: utf-8 -*-
"""
Created on Sat May  2 16:49:18 2020

@author: Shradha
"""
import json 
import io 
import math 
import numpy as np 
from nltk.stem import PorterStemmer 

number_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', ': ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] 

words_documents = {} 
document_number = 0 

for line in io.open("words_porter.json", 'r', encoding='utf-8'): 
    new_line = line.replace('\n', '').replace('\r', '').strip() 
    if new_line != '': 
        document_number += 1 
        word_dic = json.loads(new_line) 
        words_documents[document_number] = word_dic 
        
words_matrix = {} 
for line in io.open("Words_Frequency_Matrix_porter_query.json", 'r', encoding='utf-8'): 
    new_line = line.replace('\n', '').replace('\r', '').strip() 
    if new_line != '': 
        word_dic_temp = json.loads(new_line) 
        for key in word_dic_temp: 
            words_matrix[key] = word_dic_temp[key] 
            
documents_list = {} 
for word in words_matrix.keys(): 
    for idx, frequency in enumerate(words_matrix[word]): 
        if idx+1 not in documents_list: 
            documents_list[idx+1] = [] 
        documents_list[idx+1].append(frequency) 
        
idf_dict = {} 
word_number = 0
for word in words_matrix.keys(): 
    word_number += 1 
    idf_dict[word_number] = document_number - words_matrix[word].count(0) + 1
    
words_expansion = {'beautiful': ['nice', 'fancy'], 'chapter': ['chpt'], 
'chpt': ['chapter'], 'responsible': ['owner', 'accountable'], 'freemanmoore': 
['freeman', 'moore'], 'dept': ['department'], 'photo': ['photograph', 'image', 
'picture'], 'brown': ['beige', 'tan', 'auburn'], 'tues': ['Tuesday'], 'sole': 
['owner', 'single', 'shoe', 'boot'], 'homework': ['hmwk', 'home', 'work'], 
'novel': ['book', 'unique'], 'computer': ['cse'], 'story': ['novel', 'book'], 
'hocuspocus': ['magic', 'abracadabra'], 'thisworks': ['this', 'work'], } 
is_expanded = False 
last_query_list = [] 
while True: 
    if not is_expanded: 
        query = input('\nInput query you wish: ') 
       
        if query == 'stop': 
            print('\nClosing the query engine...')
            break
        query_list = query.split(' ') 
    else: 
        query_list = [query_word for query_word in last_query_list] 
        for query_word in last_query_list: 
            if words_expansion.get(query_word): 
                for expanded_word in words_expansion[query_word]: 
                    query_list.append(expanded_word) 
                    
    ps = PorterStemmer() 
    query_list_porter = [] 
    for original_word in query_list: 
        word_porter = ps.stem(original_word) 
        query_list_porter.append(word_porter) 
        
    for matrix_word in words_matrix.keys(): 
        words_matrix[matrix_word].append(0) 
    
        
    word_flag = False 
    for porter_word in query_list_porter: 
        for matrix_word in words_matrix.keys(): 
            if matrix_word == porter_word: 
                word_flag = True 
                words_matrix[matrix_word][-1] += 1 
                
    if word_flag: 
        documents_list[0] = [] 
        for matrix_word in words_matrix.keys(): 
            documents_list[0].append(words_matrix[matrix_word][-1]) 

        similarity_scores_dict = {} 
        for i in range(1, document_number+1): 
            query_score = [] 
            query_sum = 0 
            for idx, tf in enumerate(documents_list[0]): 
                if tf > 0: 
                    tf_temp = (1 + math.log(tf)) * math.log(document_number/(idf_dict[idx+1]+1)) 
                else: 
                    tf_temp = 0 
                query_sum += tf_temp * tf_temp 
                query_score += [tf_temp] 
            query_normalized = math.sqrt(query_sum) 
            query_score_processed = np.array([score/(query_normalized+1) for score in query_score]) 
            
            document_score = [] 
            document_sum = 0 
            for tf in documents_list[i]: 
                if tf > 0: 
                    tf_temp = (1 + math.log(tf)) 
                else: 
                    tf_temp = 0 
                document_sum += tf_temp * tf_temp 
                document_score += [tf_temp] 
            document_normalized = (math.sqrt(document_sum) )
            document_score_processed = np.array([score/(document_normalized+1) for score in document_score]) 

            similarity_score = np.dot(query_score_processed, document_score_processed) 

            query_in_title = False
            for porter_word in query_list_porter: 
                if porter_word in words_documents[i]['*title*']: 
                    query_in_title = True 
            if query_in_title: 
                similarity_score += 0.1 
            similarity_scores_dict[i] = similarity_score 
        similarity_scores_dict_new = sorted(similarity_scores_dict.items(), key=lambda d: d[1], reverse=True) 
        result_count = 0 
        for number, score in similarity_scores_dict_new[:5]: 
            if score > 0: 
                result_count += 1 
                print('---------------------') 
                print('Score: ', score) 
                print('URL: ', words_documents[number]['*url*']) 
                if not words_documents[number]['*title*']: 
                    title = 'No title for this article.' 
                else: 
                    title = ' '.join(words_documents[number]['*title*']) 
                print('Title: ', title) 
                print('Description: ', words_documents[number]['*description*']) 
        if not is_expanded: 
                print('---------------------------') 
                print('No article related this query. Now you can reenter Query:') 
                is_expanded = True 
                last_query_list = [query_word for query_word in query_list] 
        else: 
           if is_expanded:
            is_expanded = False 
            last_query = [] 
                    
    else:
        if is_expanded: 
            is_expanded = False 
            print('Sorry, we cannot find any result about this query.') 
        else: 
            print('---------------------------') 
            print('No article related this query. Now let us try query expansion:') 
            is_expanded = True 
            last_query_list = [query_word for query_word in query_list]
        
                