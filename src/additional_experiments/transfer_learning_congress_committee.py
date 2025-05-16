import os
import sys
from time import time, sleep
import pandas as pd

from datasets import load_dataset

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig 


mapping_stance = {'neutral': 0, 'hawkish': 1, 'dovish': 2, 'irrelevant': 3} 
mapping_time = {'forward looking': 0, 'not forward looking': 1} 
mapping_certain = {'certain': 0, 'uncertain': 1} 

hf_token=os.getenv("HF_TOKEN")

tasks = ["time_label", "certain_label"] 


test_dataset = pd.read_excel("transfer_cocohd_env_data.xlsx")

for task in tasks: 

    if task == "stance_label": 
        mapping = mapping_stance
        number_labels = 4 
    elif task == "time_label": 
        mapping = mapping_time
        number_labels = 2
    elif task == "certain_label": 
        mapping = mapping_certain
        number_labels = 2

    sentence_list = list(test_dataset["sentences"])


    ## get general model results

    # Load the tokenizer, model, and configuration
    tokenizer = AutoTokenizer.from_pretrained(f"gtfintechlab/model_WCB_{task}", do_lower_case=True, do_basic_tokenize=True, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(f"gtfintechlab/model_WCB_{task}", num_labels=number_labels, token=hf_token)
    config = AutoConfig.from_pretrained(f"gtfintechlab/model_WCB_{task}", token=hf_token) 

    # Initialize the text classification pipeline
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

    results = classifier(sentence_list, batch_size=150, truncation="only_first") 

    result_df = pd.DataFrame.from_dict(results)

    test_dataset[f'label_{task}'] = result_df['label']
    test_dataset[f'score_{task}'] = result_df['score'] 

test_dataset.to_excel(f"./transfer_cocohd_env_results.xlsx", index=False)