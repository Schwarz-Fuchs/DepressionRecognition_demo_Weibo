# coding: utf-8
import os
import paddle
import paddlehub as hub
from tqdm import tqdm
import pandas as pd

def autolable(df):
    for i in tqdm(range(len(df)-1)):
        origin_text = df.loc[i, "text"]
        text = [str(origin_text)]
        input_dict = {"text": text}
        results = senta.sentiment_classify(data=input_dict)
        if str(origin_text) != "nan" or "" or None:
            df.loc[i, "negative_probs"] = str(results[0]['negative_probs'])
            if results[0]['negative_probs']>=0.9:
                df.loc[i, "depressed_emo"] = "1"
            elif results[0]['negative_probs']<=0.1:
                df.loc[i, "depressed_emo"] = "-1"
            else:
                df.loc[i, "depressed_emo"] = "0"
        else:
            continue
    return df


if __name__ == "__main__":
    # Load Senta-BiLSTM module
    paddle.enable_static()
    senta = hub.Module(name="senta_cnn")
    df=pd.read_csv("C:/Users/surface/Desktop/final project/codes/the whole process/depressed_manuel_1.csv")
    # 对于每条文本的自动标注器
    df = df.dropna(subset=["id"])
    print(len(df))
    new_df=autolable(df)
    new_df.to_csv("depressed_manuel_labeled.csv")
