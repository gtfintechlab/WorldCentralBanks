import os
import sys
from time import time, sleep
import pandas as pd

from datasets import load_dataset

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig 

from sklearn.metrics import f1_score, accuracy_score

hf_token=os.getenv("HF_TOKEN")

tasks = ["stance_label", "time_label", "certain_label"] 

dataset = pd.read_excel("master_file_metadata.xlsx") 

dataset['sentence'] = dataset['sentence'].astype(str).fillna('').str.strip()

print(dataset.columns)

for task in tasks: 

    if task == "stance_label": 
        number_labels = 4 
    elif task == "time_label": 
        number_labels = 2
    elif task == "certain_label": 
        number_labels = 2

    sentence_list = list(dataset["sentence"])


    ## get general model results

    # Load the tokenizer, model, and configuration
    tokenizer = AutoTokenizer.from_pretrained(f"gtfintechlab/model_WCB_{task}", do_lower_case=True, do_basic_tokenize=True, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(f"gtfintechlab/model_WCB_{task}", num_labels=number_labels, token=hf_token)
    config = AutoConfig.from_pretrained(f"gtfintechlab/model_WCB_{task}", token=hf_token) 

    # Initialize the text classification pipeline
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

    results = classifier(sentence_list, batch_size=150, truncation="only_first") 

    result_df = pd.DataFrame.from_dict(results)

    dataset[f'label_{task}'] = result_df['label'] 
    dataset[f'score_{task}'] = result_df['score'] 

    
dataset.to_excel("labeled_master_file_metadata.xlsx", index=False) 
    