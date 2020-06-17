#ShradhaUttarwar

import scrapy 
from scrapy.http import Request 
from scrapy.selector import Selector 
import re 
import json 
import io 
import hashlib 
from nltk.stem import PorterStemmer 

N = int(input("Enter value of N=40. 40 document to be indexed :"))
class IRProject12(scrapy.Spider): 
    name = 'IRProject12' 
    start_urls = ['https://s2.smu.edu/~fmoore/', ]  
    dup_dic = {} 
    count = 0 
    
    
    def parse(self, response): #parse function is defined
        selector = Selector(response) 
        md = hashlib.md5() 
        md.update(response.body) 
        hashed_data = md.hexdigest() 
        outgoing_urls = [] 
        ingoing_urls = [] 
        full_url = [] 
        broken_urls = [] 
        nontxt_urls = [] 
        in_going_pdf_xlsx_urls = [] 
        duplicated_urls = [] 
        meta_noindex = [] 
        URL_Frontier = [] 
        graphic_urls = []
        
        if hashed_data in self.dup_dic: 
            duplicated_urls.append(response.url) 
        else: 
            self.dup_dic[hashed_data] = 1 
            
            if response.status == 404: 
                broken_urls.append(response.url)
                
            if response.status == 200: 
                if self.count < int(N): #Limiting the number of pages to N
                    self.count += 1 
                    word_dic = {} 
                    title = selector.xpath('//title') #extracting titles
                    title = ''.join(title.xpath('string(.)').extract()) 
                    title = title.replace('\n', '').replace('\r', '').strip()
                    title = re.sub(r"\s{2,}", " ", title) 
                    urls = selector.xpath('//a/@href | //img/@src').extract()
                    for url_part in urls: #filtering out URLs outside the domain of http and fmoore
                        if re.match(r'^http', url_part): 
                            url = url_part 
                        else: 
                            if not re.search(r'~fmoore/$', response.url): 
                                response_list = response.url.split('/') 
                                del response_list[-1] 
                                url = '/'.join(response_list) + '/' + url_part 
                            else: url = response.url + url_part 
                            
                        if re.match(r'^https://s2.smu.edu/~fmoore/', url) or re.match(r'^http://s2.smu.edu/~fmoore/', url): 
                            ingoing_urls.append(url) 
                            # appending non-text URLs
                            if not (re.search(r'txt$', url_part) or re.search(r'htm$', url_part) or re.search(r'html$', url_part) or re.search(r'php$', url_part)):
                                nontxt_urls.append(url) 
                            #filer out non-txt URLs (pdf, xlsx, jpg, jpeg, png, gif, pptx, dontgohere)
                            if re.search(r'gif$', url_part) or re.search(r'jpg$', url_part) or re.search(r'jpeg$', url_part) or re.search(r'png$', url_part) or re.search(r'pptx$',url_part): 
                                graphic_urls.append(url)
                            elif re.search(r'pdf$', url) or re.search(r'xlsx$', url): 
                                in_going_pdf_xlsx_urls.append(url) 
                            elif 'dontgohere/' in url: 
                                broken_urls.append(url) 
                            elif '@lyle' in url: 
                                broken_urls.append(url) 
                            else: URL_Frontier.append(url) 
                        else: 
                            outgoing_urls.append(url)
                            full_url.append(url) 
                             
                        
                    noindex = False 
                    meta_tag = selector.xpath('//head/meta/@content').extract()
                    if meta_tag: 
                        if re.match(r'^noindex', ''.join(meta_tag).lower()):
                            self.count -= 1
                            meta_noindex.append(response.url) 
                            noindex = True 
                            exit
                            
                    if not noindex: #further processing
                        with io.open('indexed_urls.txt', 'a', encoding='utf-8') as file: 
                            url_title = response.url + ' --- ' + title 
                            file.write(url_title) 
                            file.write('\n')
                        ps = PorterStemmer() 
                        texts = ' '.join(selector.xpath('//*/text()').extract()).replace('\n', ' ').replace('\r', ' ').strip() 
                        special_symbols = [',', '.', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', ':',"'", '=', 
                        '+', "\\", '/', '"', '-', '{', '}', '<', '>'] 
                        
                        for special_symbol in special_symbols: 
                            texts = texts.replace(special_symbol, ' ') 
                        new_text = re.sub(r"\s{2,}", " ", texts) 
                        new_text = new_text.lower() 
                        text_list = new_text.split(' ') 
                        for word in text_list: 
                            if word != '': 
                                word_porter = ps.stem(word) 
                                if word_porter not in word_dic: 
                                    word_dic[word_porter] = 1 
                                else: word_dic[word_porter] += 1 
                        word_dic['*DocID*'] = self.count
                        title = title.strip() 
                        title_list = title.split(' ') 
                        word_dic['*title*'] = [] 
                        for title_word in title_list: 
                            if title_word.strip() != '': 
                                word_title_porter = ps.stem(title_word.strip()) 
                                word_dic['*title*'].append(word_title_porter) 
                        
                        word_dic['*description*'] = ' '.join(text_list[len(title_list):len(title_list)+20]) 
                        word_dic['*url*'] = response.url 
                        
                        with io.open('words_porter.json', 'a', encoding='utf-8') as file: 
                            file.write(json.dumps(word_dic, ensure_ascii=False)) 
                            line = u"\r\n" 
                            file.write(line) 
                            
    
                else:
                  print("Too high value of N")
                  exit                
        if URL_Frontier: 
            for in_url in URL_Frontier: 
                yield Request(in_url, callback=self.parse, dont_filter=True)
                
        if outgoing_urls: 
            for outgoing_url in outgoing_urls: 
                with io.open('outgoing_urls.txt', 'a', encoding='utf-8') as file: 
                    file.write(outgoing_url) 
                    file.write('\n') 
                    
        if broken_urls: 
            for broken_url in broken_urls: 
                with io.open('broken_urls.txt', 'a', encoding='utf-8') as file1: 
                    file1.write(broken_url) 
                    file1.write('\n') 
                    
        if nontxt_urls: 
            for nontxt_url in nontxt_urls: 
                with io.open('nontext_urls.txt', 'a', encoding='utf-8') as file2: 
                    file2.write(nontxt_url) 
                    file2.write('\n') 
                    
        if graphic_urls: 
            for graphic_url in graphic_urls: 
                with io.open('graphic_urls.txt', 'a', encoding='utf-8') as file2: 
                    file2.write(graphic_url) 
                    file2.write('\n')
                    
        if in_going_pdf_xlsx_urls: 
            for in_going_pdf_xlsx_url in in_going_pdf_xlsx_urls: 
                with io.open('in_going_pdf_xlsx_urls.txt', 'a', encoding='utf-8') as file3: 
                    file3.write(in_going_pdf_xlsx_url) 
                    file3.write('\n') 
                  
        if duplicated_urls: 
            for duplicated_url in duplicated_urls: 
                with io.open('duplicated_urls.txt', 'a', encoding='utf-8') as file4: 
                    file4.write(duplicated_url) 
                    file4.write('\n') 
                    
        if meta_noindex: 
            for meta_noindex_url in meta_noindex:
                with io.open('meta_noindex.txt', 'a', encoding='utf-8') as file5: 
                    file5.write(meta_noindex_url) 
                    file5.write('\n')
                    


