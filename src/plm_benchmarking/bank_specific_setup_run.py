import os
import sys
from time import time, sleep
import pandas as pd
from transformers import BertForSequenceClassification, BertTokenizer, RobertaTokenizerFast, RobertaForSequenceClassification, AutoTokenizer, ModernBertForSequenceClassification, BertTokenizerFast
import torch
from torch.utils.data import TensorDataset, DataLoader
import torch.optim as optim
from sklearn.metrics import f1_score, accuracy_score
import numpy as np
from datasets import load_dataset

import threading

def fine_tune_plm(gpu_numbers: str, seed: int, language_model_to_use: str, batch_size: int, learning_rate: float, bank: str, task: str, save_model_path: str):
    """
    Fine-tunes a pre-trained language model (PLM) for sequence classification.
    Args:
        gpu_numbers (str): Comma-separated string of GPU numbers to use.
        seed (int): Random seed for reproducibility.
        language_model_to_use (str): The pre-trained language model to use. Options include 'bert-base-uncased', 'yiyanghkust/finbert-pretrain', 'roberta', and 'roberta-large'.
        batch_size (int): Batch size for training and evaluation.
        learning_rate (float): Learning rate for the optimizer.
        task (str): The target task/label column in the dataset.
        save_model_path (str): Path to save the fine-tuned model and tokenizer.
    Returns:
        list: A list containing experiment results including seed, learning rate, batch size, best cross-entropy loss, best accuracy, best F1 score, test cross-entropy loss, test accuracy, test F1 score, training time taken, and testing time taken.
    Raises:
        ValueError: If an unsupported language model is specified.
    """
    # GPU setup
    os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"# gpu_numbers
    device = torch.device("cuda:"+gpu_numbers) if torch.cuda.is_available() else torch.device('cpu')

    print("GPU and Device", gpu_numbers, device)


    # Tokenizer
    try:
        if language_model_to_use == 'ModernBERT-large':
            tokenizer = AutoTokenizer.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/ModernBERT-large', do_lower_case=True)
        elif language_model_to_use == 'ModernBERT-base':
            tokenizer = AutoTokenizer.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/ModernBERT-base', do_lower_case=True)
        elif language_model_to_use == 'finbert-pretrain':
            tokenizer = BertTokenizer.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/finbert-pretrain', do_lower_case=True)
        elif language_model_to_use == 'roberta-large':
            tokenizer = RobertaTokenizerFast.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/roberta-large', do_lower_case=True)
        elif language_model_to_use == 'roberta-base':
            tokenizer = RobertaTokenizerFast.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/roberta-base', do_lower_case=True)
        elif language_model_to_use == 'bert-base':
            tokenizer = BertTokenizerFast.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/bert-base-uncased', do_lower_case=True)
        elif language_model_to_use == 'bert-large':
            tokenizer = BertTokenizerFast.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/bert-large-uncased', do_lower_case=True)
        else:
            raise ValueError("Unsupported language model.")
    except Exception as e:
        print(e)
    
    # Load from Hugging Face
    dataset_HF = load_dataset(f"gtfintechlab/{bank}", data_dir=str(seed), token=os.getenv("HF_TOKEN"))


    # Access train, validation, and test splits
    train_dataset = dataset_HF['train'].to_pandas()
    val_dataset = dataset_HF['validation'].to_pandas()
    test_dataset = dataset_HF['test'].to_pandas()

    mapping_stance = {'neutral': 0, 'hawkish': 1, 'dovish': 2, 'irrelevant': 3} 
    mapping_time = {'forward looking': 0, 'not forward looking': 1} 
    mapping_certain = {'certain': 0, 'uncertain': 1} 

    if task == "stance_label": 
        mapping = mapping_stance
        number_labels = 4 
    elif task == "time_label": 
        mapping = mapping_time
        number_labels = 2
    elif task == "certain_label": 
        mapping = mapping_certain
        number_labels = 2



    train_dataset[task] = train_dataset[task].map(mapping)
    val_dataset[task] = val_dataset[task].map(mapping)
    test_dataset[task] = test_dataset[task].map(mapping)


    # Preprocess HF data
    def preprocess_data(dataset):
        concatenated_texts = list(dataset['sentences'])
        labels = list(dataset[task])
        tokens = tokenizer(concatenated_texts, return_tensors='pt', padding=True, truncation=True, max_length=256)
        return TensorDataset(tokens['input_ids'], tokens['attention_mask'], torch.LongTensor(labels))

    train_data = preprocess_data(train_dataset)
    val_data = preprocess_data(val_dataset)
    test_data = preprocess_data(test_dataset)

    # Dataloaders
    train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_dataloader = DataLoader(val_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

    # Seed setup
    torch.manual_seed(seed)

    # Model setup
    try:
        if language_model_to_use == 'ModernBERT-large':
            model = ModernBertForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/ModernBERT-large', num_labels=number_labels).to(device)
        elif language_model_to_use == 'ModernBERT-base':
            model = ModernBertForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/ModernBERT-base', num_labels=number_labels).to(device)
        elif language_model_to_use == 'finbert-pretrain':
            model = BertForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/finbert-pretrain', num_labels=number_labels).to(device)
        elif language_model_to_use == 'roberta-large':
            model = RobertaForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/roberta-large', num_labels=number_labels).to(device)
        elif language_model_to_use == 'roberta-base':
            model = RobertaForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/roberta-base', num_labels=number_labels).to(device)
        elif language_model_to_use == 'bert-base':
            model = BertForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/bert-base-uncased', num_labels=number_labels).to(device)
        elif language_model_to_use == 'bert-large':
            model = BertForSequenceClassification.from_pretrained('/storage/home/hcoda1/9/ashah482/p-schava6-0/global-central-banks/bert-large-uncased', num_labels=number_labels).to(device)
        else:
            raise ValueError("Unsupported language model.")
    except Exception as e:
        print(e)


    # Optimizer
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)

    # Early stopping parameters
    max_num_epochs = 50 
    max_early_stopping = 7
    early_stopping_count = 0
    best_ce = float('inf')
    best_accuracy = float('-inf')
    best_f1 = float('-inf')

    # Training and validation loop
    start_fine_tuning = time()
    for epoch in range(max_num_epochs):
        if early_stopping_count >= max_early_stopping:
            break

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            total_loss, total_accuracy, total_f1 = 0, 0, 0
            for batch in (train_dataloader if phase == 'train' else val_dataloader):
                batch = [b.to(device) for b in batch]
                inputs, masks, labels = batch
                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs, attention_mask=masks, labels=labels)
                    loss = outputs.loss
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                logits = outputs.logits
                preds = torch.argmax(logits, dim=1).flatten()
                total_loss += loss.item()
                batch_accuracy = accuracy_score(labels.cpu(), preds.cpu())
                total_accuracy += batch_accuracy
                total_f1 += f1_score(labels.cpu(), preds.cpu(), average='weighted')

            # Calculate average metrics
            avg_loss = total_loss / len(train_dataloader if phase == 'train' else val_dataloader)
            avg_accuracy = total_accuracy / len(train_dataloader if phase == 'train' else val_dataloader)
            avg_f1 = total_f1 / len(train_dataloader if phase == 'train' else val_dataloader)

            # Early stopping and best model logic
            if phase == 'val':
                if avg_loss < best_ce:
                    best_ce = avg_loss
                    best_accuracy = avg_accuracy
                    best_f1 = avg_f1
                    early_stopping_count = 0
                    torch.save({'model_state_dict': model.state_dict()}, f'best_model_{gpu_numbers}.pt')
                else:
                    early_stopping_count += 1

            # Print metrics
            print(f"Epoch {epoch + 1} / {max_num_epochs} - Phase: {phase}")
            print(f"Loss: {avg_loss}, Accuracy: {avg_accuracy}, F1 Score: {avg_f1}")
            print(f"Best CE: {best_ce}, Best Accuracy: {best_accuracy}, Best F1 Score: {best_f1}")
            print(f"Early Stopping Counter: {early_stopping_count}")

    training_time_taken = (time() - start_fine_tuning) / 60.0
    print(f"Training time taken: {training_time_taken} minutes")

    # Load best model
    checkpoint = torch.load(f'best_model_{gpu_numbers}.pt')
    model.load_state_dict(checkpoint['model_state_dict'])

    # Test phase
    start_test_labeling = time()
    model.eval()
    test_ce, test_accuracy, test_f1 = 0, 0, 0
    with torch.no_grad():
        for batch in test_dataloader:
            batch = [b.to(device) for b in batch]
            inputs, masks, labels = batch
            outputs = model(inputs, attention_mask=masks, labels=labels)
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1).flatten()
            test_ce += outputs.loss.item()
            test_accuracy += accuracy_score(labels.cpu(), preds.cpu())
            test_f1 += f1_score(labels.cpu(), preds.cpu(), average='weighted')

    # Print test metrics
    test_ce /= len(test_dataloader)
    test_accuracy /= len(test_dataloader)
    test_f1 /= len(test_dataloader)
    test_time_taken = (time() - start_test_labeling) / 60.0
    print("Test Metrics:")
    print(f"Test CE: {test_ce}, Test Accuracy: {test_accuracy}, Test F1 Score: {test_f1}")
    print(f"Testing time taken: {test_time_taken} minutes")

    experiment_results = [seed, learning_rate, batch_size, best_ce, best_accuracy, best_f1, test_ce, test_accuracy, test_f1, training_time_taken, test_time_taken]

    if save_model_path:
        model.save_pretrained(save_model_path)
        tokenizer.save_pretrained(save_model_path)

    return experiment_results


def train_lm_experiments(gpu_numbers: str, language_model_to_use: str, bank: str, task: str):
    """
    Conducts a series of experiments to fine-tune a pre-trained language model (PLM) using different seeds, batch sizes, and learning rates.
    Args:
        gpu_numbers (str): Comma-separated string of GPU numbers to use for training.
        language_model_to_use (str): The name of the pre-trained language model to fine-tune.
        task (str): The specific task or task for which the model is being fine-tuned.
    Returns:
        None: The function saves the results of the experiments to an Excel file.
    """
    results = []
    seeds = [5768, 78516, 944601]
    batch_sizes = [32, 16]
    learning_rates = [1e-5, 1e-6] 
    count = 0
    

    for seed in seeds:
        for batch_size in batch_sizes:
            for learning_rate in learning_rates:
                count += 1
                print(f'Experiment {count} of {len(seeds) * len(batch_sizes) * len(learning_rates)}:')
                results.append(fine_tune_plm(gpu_numbers, str(seed), language_model_to_use, batch_size, learning_rate, bank, task, None))
                df = pd.DataFrame(results, columns=["Seed", "Learning Rate", "Batch Size", "Val Cross Entropy", "Val Accuracy", "Val F1 Score", "Test Cross Entropy", "Test Accuracy", "Test F1 Score", "Fine Tuning Time(m)", "Test Labeling Time(m)"])
                df.to_excel(f'./plm_grid_search/{bank}_{task}_{language_model_to_use}.xlsx', index=False)

def run_experiment(gpu_numbers, language_model_to_use):

    banks = ["european_central_bank", "reserve_bank_of_india", "central_bank_of_the_russian_federation", "bank_of_korea", "central_bank_of_egypt",
             "central_bank_of_the_philippines", "bank_of_the_republic_colombia", "federal_reserve_system", "bank_of_japan", "bank_of_england", 
             "reserve_bank_of_australia", "bank_of_canada", "bank_of_israel", "bank_of_mexico", "bank_negara_malaysia",
             "swiss_national_bank", "central_bank_of_china_taiwan", "national_bank_of_poland", "central_bank_of_brazil", "central_bank_republic_of_turkey",
             "peoples_bank_of_china", "bank_of_thailand", "monetary_authority_of_singapore", "central_bank_of_chile", "central_reserve_bank_of_peru"]

    tasks = ["stance_label", "time_label", "certain_label"] 

    # run experiments
    for bank in banks: 
        for task in tasks: 
            train_lm_experiments(gpu_numbers=gpu_numbers, language_model_to_use=language_model_to_use, bank=bank, task=task)

if __name__ == '__main__':

    list_models = ["bert-large", "roberta-large", "roberta-base", "ModernBERT-base", "ModernBERT-large", "bert-base", "finbert-pretrain"] 


    threads = []

    # Create and start a thread for each year
    for gpu in range(7):
        t = threading.Thread(target=run_experiment, args=(str(gpu), list_models[gpu]))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()
    