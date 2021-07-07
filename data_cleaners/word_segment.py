from pyhanlp import *
import jieba
import pandas as pd
from tqdm import tqdm
import re

def word_segment_han(df):
   for i in tqdm(range(len(df))):
      origin_text = df.loc[i, "chinese_only_text"]
      if str(origin_text) != "nan" or "" or None:
         origin_text = re.sub(r"\s+", " ", origin_text)
         segement = HanLP.segment(origin_text)
         word_list=[]
         for item in segement:
            if item.word!=' ':
                word_list.append(item.word)
         df.loc[i, "word_segment"]= str(word_list)
      else:
         continue
   return df

def word_segment_jieba(df):
   jieba.load_userdict("C:/Users/surface/Desktop/final project/codes/the whole process/DICS/LIWC2015_main.txt")
   for i in tqdm(range(len(df))):
      origin_text = df.loc[i, "chinese_only_text"]
      if str(origin_text) != "nan" or "" or None:
         origin_text = re.sub(r"\s+", " ", origin_text)
         segement = jieba.cut(origin_text)
         df.loc[i, "word_segment"]= str(','.join(segement))
      else:
         continue
   return df

def word_segment_jieba_txt(txtfile,target_file):
   jieba.load_userdict("C:/Users/surface/Desktop/final project/codes/the whole process/DICS/LIWC2015_main.txt")
   file=open(txtfile,'r',encoding="UTF-8")
   write_file=open(target_file,'w',encoding="UTF-8")
   file.readline()
   for line in file:
      if str(line)!='' or ' ' or '   ':
         segement = jieba.cut(line)
         textline=str(' '.join(segement))
         textline=re.sub(r"\s+", " ", textline)
         if  textline!=' ':
           write_file.write(str(textline))
           write_file.write('\n')
   write_file.close()
   file.close()




if __name__ == '__main__':
   csvfile="C:/Users/surface/Desktop/final project/codes/the whole process/depressed_used.csv"
   df=pd.read_csv(csvfile)
   #df_1=word_segment_han(df)
   df_1=word_segment_jieba(df)
   df_1.to_csv('test.csv')
   csvfile = "C:/Users/surface/Desktop/final project/codes/the whole process/test.csv"
   df_1 = pd.read_csv(csvfile)
   print(df_1['word_segment'])
   word_segment_jieba_txt("depressed_text.txt",'depressed_text_segement.txt')
   word_segment_jieba_txt('normal_text.txt','normal_text_segement.txt' )






