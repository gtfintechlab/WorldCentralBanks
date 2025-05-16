import os,sys
import pandas as pd
from time import sleep, time
from datetime import date, datetime
import re

import nltk
nltk.download('punkt')  

from nltk.tokenize import sent_tokenize

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig 

hf_token=os.getenv("HF_TOKEN")

banks = ["european_central_bank", "reserve_bank_of_india", "central_bank_of_the_russian_federation", "bank_of_korea", "central_bank_of_egypt",
        "central_bank_of_the_philippines", "bank_of_the_republic_colombia", "federal_reserve_system", "bank_of_japan", "bank_of_england", 
        "reserve_bank_of_australia", "bank_of_canada", "bank_of_israel", "bank_of_mexico", "bank_negara_malaysia",
        "swiss_national_bank", "central_bank_of_china_taiwan", "national_bank_of_poland", "central_bank_of_brazil", "central_bank_republic_of_turkey",
        "peoples_bank_of_china", "bank_of_thailand", "monetary_authority_of_singapore", "central_bank_of_chile", "central_reserve_bank_of_peru"]

tasks = ["stance_label", "time_label", "certain_label"] 

df = pd.read_excel("../bench-exp/labeled_master_file_metadata.xlsx") 

df = df[df["year"] > 2023]

df = df[["bank", "release_date"]] 

df = df.drop_duplicates(subset=["bank", "release_date"])

df["release_date"] = pd.to_datetime(df["release_date"], format="%d-%m-%Y")

all_dfs = []

for target_bank in banks: 

    # Filter all release dates of the target bank after May 31, 2024
    target_dates = df[
        (df["bank"] == target_bank) & (df["release_date"] > "31-05-2024")
    ]

    

    for _, target_row in target_dates.iterrows():
        target_date = target_row["release_date"] 

        with open(f"./generated_mm/{target_bank}_{str(target_date.date())}.txt", 'r', encoding='utf-8') as file:
            text = file.read()

        sentences = sent_tokenize(text)

        sentences = [sent.lower().strip() for sent in sentences] 

        temp_df = pd.DataFrame({
            'target_bank': [target_bank] * len(sentences),
            'target_date': [target_date] * len(sentences),
            'sentence': sentences
        })
        print(target_bank, target_date, temp_df.shape, len(sentences))
        all_dfs.append(temp_df)


combined_df = pd.concat(all_dfs, ignore_index=True)

print(combined_df.shape)

for task in tasks: 

    if task == "stance_label": 
        number_labels = 4 
    elif task == "time_label": 
        number_labels = 2
    elif task == "certain_label": 
        number_labels = 2

    sentence_list = list(combined_df["sentence"])


    ## get general model results

    # Load the tokenizer, model, and configuration
    tokenizer = AutoTokenizer.from_pretrained(f"gtfintechlab/model_WCB_{task}", do_lower_case=True, do_basic_tokenize=True, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(f"gtfintechlab/model_WCB_{task}", num_labels=number_labels, token=hf_token)
    config = AutoConfig.from_pretrained(f"gtfintechlab/model_WCB_{task}", token=hf_token) 

    # Initialize the text classification pipeline
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

    results = classifier(sentence_list, batch_size=150, truncation="only_first") 

    result_df = pd.DataFrame.from_dict(results)

    combined_df[f'label_{task}'] = result_df['label'] 
    combined_df[f'score_{task}'] = result_df['score'] 

print(combined_df.shape)
    
combined_df.to_excel("labeled_generated_mm.xlsx", index=False) 