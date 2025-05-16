from time import time
from datetime import date
import os
from time import sleep
import sys
LOG_DIR = "logs"
LOG_LEVEL = "INFO"
import logging 
from pathlib import Path
from datasets import load_dataset
from prompts import stance_prompt, time_prompt, certain_prompt, stance_prompt_with_guide, time_prompt_with_guide, certain_prompt_with_guide, stance_prompt_fewshot, time_prompt_fewshot, certain_prompt_fewshot
import pandas as pd
from litellm import batch_completion
import yaml
import argparse
from sklearn.metrics import classification_report
import json
from huggingface_hub import login
from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils.logging import setup_logger

ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT_DIR / "llm_benchmarking" / "logs"


sys.path.append(str(ROOT_DIR))

from utils.logging import setup_logger

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    
    config["temperature"] = 0.0
        
    return config

args = parse_args()
logger = setup_logger(
    name="together_inference",
    log_file=LOG_DIR / f"{args['bank']}_inference.log"
)

RESULTS_DIR = ROOT_DIR / "llm_inference_outputs" / f"llm_inference_{args['prompt_format']}"
CONFIG_DIR = ROOT_DIR / "configs" / f"configs_{args['prompt_format']}"


def chunk_list(lst, chunk_size):
    """Split a list into smaller chunks of specified size.
    
    Args:
        lst: The input list to be chunked
        chunk_size: The size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

def process_batch_with_retry(args, messages_batch, batch_idx, total_batches):
    logger.info(f"Processing batch {batch_idx + 1}/{total_batches}")
    if args["model"].startswith("gemini/"):
        gemini_model_name = args["model"].split("/", 1)[1]
        batch_responses = []
        for msg in messages_batch:
            if isinstance(msg, list):                   
                prompt = "\n".join(m["content"] for m in msg)
            else:                                    
                prompt = msg
            max_retries = 3
            for attempt in range(1, max_retries+1):
                try:
                    res = client.models.generate_content(model=gemini_model_name, contents=prompt)
                    batch_responses.append(res.text)
                    break
                except Exception as e:
                    err = str(e)
                    # detect rate‑limit by HTTP 429 or RESOURCE_EXHAUSTED
                    if "429" in err or "RESOURCE_EXHAUSTED" in err:
                        wait = 5 * attempt
                        logger.warning(f"Rate limit hit on attempt {attempt}/{max_retries}, sleeping {wait}s…")
                        sleep(wait)
                        continue
                    else:
                        logger.error(f"Gemini call failed ({e}), skipping.")
                        batch_responses.append(None)
                        break
            else:
                logger.error("Exceeded max Gemini retries, appending None")
                batch_responses.append(None)
           
        return batch_responses
    try:
        
        batch_responses = batch_completion(
            model=args["model"],
            messages=messages_batch,
            temperature=args["temperature"],
            max_tokens=args["max_tokens"],
            # top_k=args.top_k,
            # top_p=args.top_p,
            # repetition_penalty=args.repetition_penalty,
            num_retries=3,
            # stop=tokens(args.model),
        )
        logger.info(f"Completed batch {batch_idx + 1}/{total_batches}")
        print(batch_responses)
        return batch_responses
    except Exception as e:
        logger.error(f"Batch {batch_idx + 1} failed: {str(e)}")
        raise 
    

def get_prompt_function(feature: str, fmt: str, bank_slug: str, bank_official: str, seed: int):
    if fmt == "guide":
        if feature == "stance":
            return lambda sent: stance_prompt_with_guide(sent, bank_slug, bank_official)
        if feature == "time":
            return lambda sent: time_prompt_with_guide(sent, bank_slug, bank_official)
        if feature == "certain":
            return lambda sent: certain_prompt_with_guide(sent, bank_slug, bank_official)
    elif fmt == "few_shot":
        if feature == "stance":
            return lambda sent: stance_prompt_fewshot(sent, bank_slug, bank_official, seed)
        if feature == "time":
            return lambda sent: time_prompt_fewshot(sent, bank_slug, bank_official, seed)
        if feature == "certain":
            return lambda sent: certain_prompt_fewshot(sent, bank_slug, bank_official, seed)
    else:  # no‑guide
        if feature == "stance":
            return lambda sent: stance_prompt(sent, bank_official)
        if feature == "time":
            return lambda sent: time_prompt(sent, bank_official)
        if feature == "certain":
            return lambda sent: certain_prompt(sent, bank_official)
    raise ValueError(f"Unknown feature/format: {feature}/{fmt}")
    
    

def inference_function(args, bank_official_name):
    today = date.today()
    logger.info(f"Starting inference on {today}")
    logger.info("Loading dataset...")
    dataset = load_dataset(f"gtfintechlab/{args['bank']}", str(args['seed']), trust_remote_code=True)
    results_path = (
    RESULTS_DIR
    / args["bank"]
    / f"{args['model']}_{args['seed']}_{today}.csv"
)
    sentences = dataset['test']['sentences']
    llm_responses = []
    complete_responses = []
    logger.info(f"Loaded {len(sentences)} sentences from the dataset.")
    logger.info(f"Using model: {args['model']}")
    logger.info(f"Using seed: {args['seed']}")
    if args["feature"] == "stance":
        actual_labels = dataset['test']['stance_label']
    elif args["feature"] == "time":
        actual_labels = dataset['test']['time_label']
    elif args["feature"] == "certain":
        actual_labels = dataset['test']['certain_label']
    
    batch_size = args["batch"]
    total_batches = len(sentences) // batch_size + int(len(sentences) % batch_size > 0)

    logger.info(f"Processing {len(sentences)} documents in {total_batches} batches.")

    sentences_batches = chunk_list(sentences, batch_size)
    label_batches = chunk_list(actual_labels, batch_size)
    
    for batch_idx, sentence_batch in enumerate(sentences_batches):
        # batching
        prompt_fn = get_prompt_function(
                        args['feature'], args['prompt_format'], args['bank'], bank_official_name, args['seed']
                    )
        logger.info(f"Processing batch {batch_idx + 1}/{total_batches} with {len(sentence_batch)} sentences.")
        messages_batch = [prompt_fn(sentence) for sentence in sentence_batch]
        try:
            batch_responses = process_batch_with_retry(args, messages_batch, batch_idx, total_batches)

            for response in batch_responses:
                try:
                    if args["model"].startswith("gemini/"):
                        # response is already a plain string (or None)
                        response_text = (response or "").strip()
                    else:
                        # litellm object
                        response_text = response.choices[0].message.content.strip()
                    # print(response) if response else print("None")
                    # response_text = response.choices[0].message.content.strip()  # type: ignore
                    llm_responses.append(response_text)
                    complete_responses.append(response)
                    logger.info(prompt_fn(sentence_batch[0]))
                    logger.info(f"Response: {response_text}")
                except (KeyError, IndexError, AttributeError) as e:
                    logger.error(f"Error extracting response: {e}")
                    llm_responses.append("error")
                    complete_responses.append(None)
        except Exception as e:
            logger.error(f"Batch {batch_idx + 1} failed: {e}")
            llm_responses.extend(["error"] * len(sentence_batch))
            complete_responses.extend([None] * len(sentence_batch))
            continue
        
    df = pd.DataFrame(
        {
            "documents": sentences,
            "llm_responses": llm_responses,
            "actual_labels": actual_labels,
            "complete_responses": complete_responses,
        }
    )

    logger.info(f"Inference completed. Returning DataFrame with {len(df)} rows.")
    # results_path = RESULTS_DIR / args["bank"] / f"{args["task"]}_{args['model']}_{today}_{args["seed"]}.csv"
    # results_path.parent.mkdir(parents=True, exist_ok=True)
    # df.to_csv(results_path, index=False)
    return df


def evaluate_predictions(df: pd.DataFrame, feature: str, save_path: Path, seed: str):
    """Evaluates predictions and saves the classification report to a CSV."""
    logger.info("Starting evaluation of LLM predictions...")

    llm_labels = []
    for i in range(len(df)):
        try:
            pred = json.loads(df.iloc[i]["llm_responses"])
            label = pred.get("label", "").lower()
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            logger.warning(f"Failed to parse LLM response at row {i}: {e}")
            label = "error"
        llm_labels.append(label)

    actual_labels = df["actual_labels"]
    report_dict = classification_report(actual_labels, llm_labels, output_dict=True)

    # Convert to DataFrame for saving
    report_df = pd.DataFrame(report_dict).transpose()
    metrics_path = save_path.parent / f"{feature}_metrics_{seed}.csv"
    report_df.to_csv(metrics_path)

    logger.info(f"Evaluation metrics saved to {metrics_path}")
    print(report_df)
    return report_df

bank_map = {
    "bank_negara_malaysia": "Bank Negara Malaysia",
    "bank_of_canada": "Bank of Canada",
    "bank_of_the_republic_colombia": "Bank of the Republic (Colombia)",
    "bank_of_england": "Bank of England",
    "bank_of_israel": "Bank of Israel",
    "bank_of_japan": "Bank of Japan",
    "bank_of_korea": "Bank of Korea",
    "bank_of_mexico": "Bank of Mexico",
    "central_bank_of_the_philippines": "Central Bank of the Philippines",
    "bank_of_thailand": "Bank of Thailand",
    "central_bank_of_brazil": "Central Bank of Brazil",
    "central_bank_of_chile": "Central Bank of Chile",
    "central_bank_of_egypt": "Central Bank of Egypt",
    "central_bank_of_the_russian_federation": "Central Bank of the Russian Federation",
    "central_bank_republic_of_turkey": "Central Bank of Turkey",
    "central_bank_of_china_taiwan": "Central Bank of China (Taiwan)",
    "central_reserve_bank_of_peru": "Central Reserve Bank of Peru",
    "european_central_bank": "European Central Bank",
    "federal_reserve_system": "Federal Reserve System",
    "monetary_authority_of_singapore": "Monetary Authority of Singapore",
    "national_bank_of_poland": "National Bank of Poland",
    "peoples_bank_of_china": "People's Bank of China",
    "reserve_bank_of_india": "Reserve Bank of India",
    "reserve_bank_of_australia": "Reserve Bank of Australia",
    "swiss_national_bank": "Swiss National Bank"
}



def main():
    args = parse_args()
    today = date.today().strftime("%Y%m%d")
    bank = args["bank"]
    bank_official_name = bank_map.get(bank)
    print(f"Running inference for {bank_official_name}")
    if bank not in bank_map:
        raise ValueError(f"Bank '{bank}' not found in bank_map.")

    start_t = time()
    df = inference_function(args, bank_official_name)
    time_taken = time() - start_t
    logger.info(f"Time taken for inference: {time_taken}")

    task = args["feature"]
    results_path = RESULTS_DIR / bank / f"{task}_{args['model']}_{today}_{args['seed']}.csv"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(results_path, index=False)
    logger.info(f"Inference completed for {task}. Results saved to {results_path}")
    # evaluate_predictions(df, task, results_path, str(args["seed"]))

if __name__ == "__main__":
    main()