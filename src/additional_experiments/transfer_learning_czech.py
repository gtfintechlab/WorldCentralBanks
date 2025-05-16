import os
import sys
from time import time, sleep
import pandas as pd

from datasets import load_dataset

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig 

from sklearn.metrics import f1_score, accuracy_score

mapping_stance = {'neutral': 'LABEL_0', 'hawkish': 'LABEL_1', 'dovish': 'LABEL_2', 'irrelevant': 'LABEL_3'} 
mapping_time = {'forward looking': 'LABEL_0', 'not forward looking': 'LABEL_1'} 
mapping_certain = {'certain': 'LABEL_0', 'uncertain': 'LABEL_1'} 

hf_token=os.getenv("HF_TOKEN")

seeds = [5768, 78516, 944601]

tasks = ["stance_label", "time_label", "certain_label"] 

dataset = pd.read_excel("transfer_czech.xlsx") 

outputs = []

for seed in seeds: 

    test_dataset = dataset.sample(n=150, random_state=int(seed))
    test_dataset = test_dataset.reset_index()

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


        test_dataset[task] = test_dataset[task].map(mapping) 
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

        
        temp_f1_score = f1_score(test_dataset[task], test_dataset[f'label_{task}'], average='weighted')

        outputs.append([seed, task, temp_f1_score])


df_results = pd.DataFrame(outputs, columns=["seed", "task", "Test F1 Score"])
df_results.to_excel(f"./transfer_czech_results.xlsx", index=False)