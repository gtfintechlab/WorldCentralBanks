import os
import sys
from time import time, sleep
import pandas as pd

from datasets import load_dataset

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig 

mapping_stance = {'neutral': 0, 'hawkish': 1, 'dovish': 2, 'irrelevant': 3} 

hf_token=os.getenv("HF_TOKEN")

task = "stance_label" 

seed = 5768

def get_gain_samples(bank: str): 

    dataset_HF = load_dataset(f"gtfintechlab/{bank}", data_dir=str(seed), token=hf_token) 
    test_dataset = dataset_HF['test'].to_pandas() 
    test_dataset[task] = test_dataset[task].map(mapping_stance) 

    sentence_list = list(test_dataset["sentences"])

    

    ## get specialized model results

    # Load the tokenizer, model, and configuration
    tokenizer = AutoTokenizer.from_pretrained(f"gtfintechlab/model_{bank}_{task}", do_lower_case=True, do_basic_tokenize=True, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(f"gtfintechlab/model_{bank}_{task}", num_labels=4, token=hf_token)
    config = AutoConfig.from_pretrained(f"gtfintechlab/model_{bank}_{task}", token=hf_token) 

    # Initialize the text classification pipeline
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

    results = classifier(sentence_list, batch_size=150, truncation="only_first") 

    result_df = pd.DataFrame.from_dict(results)

    test_dataset['label_special'] = result_df['label'] 
    test_dataset['score_special'] = result_df['score'] 

    ## get general model results

    # Load the tokenizer, model, and configuration
    tokenizer = AutoTokenizer.from_pretrained(f"gtfintechlab/model_WCB_{task}", do_lower_case=True, do_basic_tokenize=True, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(f"gtfintechlab/model_WCB_{task}", num_labels=4, token=hf_token)
    config = AutoConfig.from_pretrained(f"gtfintechlab/model_WCB_{task}", token=hf_token) 

    # Initialize the text classification pipeline
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

    results = classifier(sentence_list, batch_size=150, truncation="only_first") 

    result_df = pd.DataFrame.from_dict(results)

    test_dataset['label_general'] = result_df['label']
    test_dataset['score_general'] = result_df['score'] 

    test_dataset.to_csv(f"./gain_analysis/test_5768_{bank}_{task}.csv", index=False)


    return 0







banks = ["european_central_bank", "reserve_bank_of_india", "central_bank_of_the_russian_federation", "bank_of_korea", "central_bank_of_egypt",
        "central_bank_of_the_philippines", "bank_of_the_republic_colombia", "federal_reserve_system", "bank_of_japan", "bank_of_england", 
        "reserve_bank_of_australia", "bank_of_canada", "bank_of_israel", "bank_of_mexico", "bank_negara_malaysia",
        "swiss_national_bank", "central_bank_of_china_taiwan", "national_bank_of_poland", "central_bank_of_brazil", "central_bank_republic_of_turkey",
        "peoples_bank_of_china", "bank_of_thailand", "monetary_authority_of_singapore", "central_bank_of_chile", "central_reserve_bank_of_peru"] 

for bank in banks:
    get_gain_samples(bank=bank)