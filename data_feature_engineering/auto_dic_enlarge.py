# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import word2vec
import logging

# 主程序
def word_2_vec_model(txt_file):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus(txt_file)  # 加载语料
    n_dim = 300
    # 训练skip-gram模型;
    model = word2vec.Word2Vec(sentences, size=n_dim, min_count=5, sg=1)
    # about the meaning of the model :
    # sg=0 C-BOW算法  sg=1 使用skip-gram算法
    # window 训练窗口，默认为为5 考虑前5个词与后5个词
    #min_count 少于5次次词频的单词会被丢掉
    #skip-gram对于小型语料库和一些罕见的词有更好的效果，CBOW在常用词有更高的识别效果
    return model

def likely_cacu(target_word,model,top_n):
    result= model.most_similar([target_word], topn=top_n)
    return result

def auto_enlarge_dic(model,likly_hood,top_n,loop_time,original_dic_path):
    file=open(original_dic_path,'r',encoding='UTF_8')
    file.readline()
    total_list=[]
    this_loop=[]
    for line in file:
        line=line.replace('\n','')
        total_list.append(str(line))
        this_loop.append(str(line))

    for i in range(loop_time):
        result_list = []
        for word in this_loop:
            result = likely_cacu(word, model, top_n)
            result_list.append(result)
        this_loop = []
        for results in result_list:
            for item in results:
                if item[1]>=likly_hood:
                    if item[0] not in total_list:
                         this_loop.append(str(item[0]))
                         total_list.append(str(item[0]))
                    else:
                        continue
                else:continue
    return total_list


def new_dic_generate(word_list,dic_path,loop_time):
    file=open(dic_path,'w',encoding='UTF-8')
    file.write(str("该词典为"+str(loop_time)+"自动扩增结果"))
    file.write("\n")
    for word in word_list:
        file.write(str(word))
        file.write('\n')
    file.close()


if __name__ == "__main__":
    model=word_2_vec_model('C:/Users/surface/Desktop/final project/codes/the whole process/data_using/full_text_segement.txt')
    final_list=auto_enlarge_dic(model,0.6,5,1,"C:/Users/surface/Desktop/final project/codes/the whole process/DICS/depressed_negative_autoenlarge.txt")
    new_dic_generate(final_list,'depressed_negative_autoenlarge_1.txt',4)
