from __future__ import annotations
import argparse, yaml, logging, os, sys, json, time as t
from datetime import date
from pathlib import Path
from typing import List

import torch, pandas as pd
from datasets import load_dataset
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


RESULTS_DIR = Path("llm_inference_output_no_guide")
LOGS_DIR    = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logger(tag: str, file: Path) -> logging.Logger:
    fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt,
                        handlers=[logging.StreamHandler(),
                                  logging.FileHandler(file, encoding="utf-8")])
    return logging.getLogger(tag)

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
    "swiss_national_bank": "Swiss National Bank",
}

def _prompt(task: str, sent: str, bank: str, choices: str) -> str:
    apostrophe = "'" if bank == "Central Bank of the Philippines" else "'s"
    return f"""You are given a sentence related to the {bank}{apostrophe} monetary policy meeting. \
Your task is to classify its {task} and briefly justify your choice.

Input:
- Sentence: {sent}

Instructions:
1. Assign one of the following labels under the `label` key:
{choices}
2. Provide a concise explanation for your classification using the `justification` key. Limit it to one sentence.
3. Your output must follow **exactly** this JSON:
{{
"label": "...",
"justification": "..."
}}

### Response:
"""

def stance_prompt(s, b):   return _prompt("monetary policy stance",                    s, b, '"hawkish", "neutral", "dovish", or "irrelevant".')
def time_prompt(s, b):     return _prompt("time-orientation (forward looking or not)", s, b, '"forward looking", "not forward looking".')
def certain_prompt(s, b):  return _prompt("certainty (certain or uncertain)",          s, b, '"certain", "uncertain".')

PROMPT_FN = {"stance": stance_prompt,
             "time":   time_prompt,
             "certain": certain_prompt}


def parse_cfg() -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    cfg_path = Path(ap.parse_args().config)
    with cfg_path.open() as f:
        cfg = yaml.safe_load(f)

    cfg.setdefault("batch", 8)
    cfg.setdefault("temperature", 0.0)
    cfg.setdefault("max_tokens", 128)
    cfg.setdefault("prompt_format", "no_guide")
    cfg["seed"] = str(cfg.get("seed", 0))

    if cfg["bank"] not in bank_map:
        raise ValueError(f"Unknown bank key {cfg['bank']}")
    return cfg

def chunks(lst: List, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def run(cfg: dict, logger: logging.Logger):
    if os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        login(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"), add_to_git_credential=False)

    bank_long  = bank_map[cfg["bank"]]
    prompt_fn  = PROMPT_FN[cfg["feature"]]

    logger.info(f"Loading dataset gtfintechlab/{cfg['bank']} seed {cfg['seed']}")
    ds   = load_dataset(f"gtfintechlab/{cfg['bank']}", cfg["seed"], trust_remote_code=True)
    sents = ds["test"]["sentences"]
    gold  = ds["test"][f"{cfg['feature']}_label"]

    logger.info("Loading model %s", cfg["model"])
    tok = AutoTokenizer.from_pretrained(cfg["model"], trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        cfg["model"],
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    gen = pipeline(
        "text-generation",
        model=model,
        tokenizer=tok,
        device=0 if torch.cuda.is_available() else -1,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else None,
    )

    outputs: List[str] = []
    logger.info("%d sentences | batch=%d", len(sents), cfg["batch"])
    start = t.time()
    for bi, batch in enumerate(chunks(sents, cfg["batch"]), 1):
        prompts = [prompt_fn(s, bank_long) for s in batch]
        results = gen(
            prompts,
            max_new_tokens=cfg["max_tokens"],
            temperature=cfg["temperature"],
            do_sample=False,
            eos_token_id=tok.eos_token_id,
        )
        for p, r in zip(prompts, results):
            txt = r[0]["generated_text"][len(p):].strip()
            outputs.append(txt)
        logger.info("Batch %d complete", bi)
    logger.info("Finished in %.1fs", t.time() - start)

    df = pd.DataFrame(
        dict(documents=sents,
             llm_responses=outputs,
             actual_labels=gold)
    )

    outdir = RESULTS_DIR / cfg["bank"]
    outdir.mkdir(parents=True, exist_ok=True)
    fname  = f"{cfg['feature']}_{cfg['model'].split('/')[-1]}_{date.today():%Y%m%d}_{cfg['seed']}.csv"
    df.to_csv(outdir / fname, index=False)
    logger.info("Saved → %s", outdir / fname)

def main():
    cfg = parse_cfg()
    log_file = LOGS_DIR / cfg["bank"] / f"log_{cfg['feature']}_{cfg['model'].split('/')[-1]}.txt"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = setup_logger("inference", log_file)

    run(cfg, logger)

if __name__ == "__main__":
    main()
