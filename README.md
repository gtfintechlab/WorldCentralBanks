# Words That Unite The World: A Unified Framework for Deciphering Central‑Bank Communications Globally

## Authors
| Role                     | Contributors                                                                                                   |
|--------------------------|---------------------------------------------------------------------------------------------------------------|
| **Equal‑first (\*)**     | Agam Shah\*, Siddhant Sukhani\*, Huzaifa Pardawala\*                                                          |
| **Core contributors (†)**| Saketh Budideti†, Riya Bhadani†, Rudra Gopal†, Siddhartha Somani†, Michael Galarnyk†, Rutwik Routu†, Soungmin Lee† |
| **Additional contributors** | Akshar Ravichandran, Eric Kim, Pranav Aluru, Joshua Zhang, Sebastian Jaskowski, Veer Guda, Meghaj Tarte, Liqin Ye, Spencer Gosden, Rachel Yuh, Arnav Hiray, Sloka Chava, Sahasra Chava, Dylan Kelly, Aiden Chiang, Harsit Mittal, Sudheer Chava | 


- **🐝 Georgia Institute of Technology**  
  Contact: `{ashah482, ssukhani3, hpardawala3}@gatech.edu`  
  Links:  
  - 🌐 [WCB Website](https://gcb-web-bb21b.web.app/)  
  - 🤗 [Data & Models](https://huggingface.co/gtfintechlab)  
  - 💻 [Code](https://github.com/gtfintechlab/WorldCentralBanks)

> **Note** – \* denotes equal first authors, † denotes core contributors.

---

### Paper & Website

* 🌐 Explore interactive visualisations on the [WCB website](https://gcb-web-bb21b.web.app/)

![World map of participating central banks](resources/figure_1.png)

### Dataset Overview
| **Dataset**           | Value       |
|-----------------------|-------------|
| Central Banks         | 25          |
| Years                 | 1996 – 2024 |
| Scraped Sentences     | 380,200     |
| Annotated Sentences   | 25,000      |
| Total Words           | 10,289,163  |
| Corpus Size (tokens)  | 2,661,400   |
| Sentences / Year\*    | 13,110.34   |
| Words / Sentence\*    | 27.06       |

### Model Information
| **Models**                   | Value                               |
|------------------------------|-------------------------------------|
| Pre‑trained Language Models  | 7                                   |
| Large Language Models        | 9                                   |
| **Best Stance Model\***      | `RoBERTa‑Large` (0.740)             |
| **Best Temporal Model\***    | `RoBERTa‑Base` (0.868)              |
| **Best Uncertainty Model\*** | `RoBERTa‑Large` (0.846)             |
| Benchmarking Experiments     | 15,075                              |
| Few‑shot                     | ✅                                   |
| Few‑shot + Ann. Guide        | ✅                                   |

### Annotation Details
| **Annotations**      | Value                                                                |
|-----------------------|----------------------------------------------------------------------|
| Annotators            | 104                                                                  |
| Annotation Guides     | 26                                                                   |
| Annotation Steps      | 6                                                                    |
| **Tasks**             |                                                                      |
| Stance Detection      | Hawkish, Dovish, Neutral, Irrelevant                                 |
| Temporal Classification | (Not) Forward‑looking                                                |
| Uncertainty Estimation | (Un)certain                                                          |

Figure 1. **A summary of the World Central Bank (WCB) dataset and experiments.**  
We systematically scrape, clean, and analyze 1996 – 2024 communications from 25 central banks at the sentence level, yielding 380,200 sentences (avg. 27.06 words/sentence). An annotated subset of 25,000 sentences spans three tasks (Stance Detection, Temporal Classification, and uncertainty Estimation) using comprehensive individual annotation guides and detailed instructions for annotation. We benchmark seven PLMs and eight LLMs on these tasks, under a bank-specific (1,000 bank-specific annotated sentences) and global setup (25,000 annotated sentences). The performance of the General (All-Banks) Setup model for each task is showcased in the figure.

In these tables, \* represents that it is an average.


---

## Abstract

Central banks around the world play a crucial role in maintaining economic stability. Deciphering policy implications in their communications is essential, especially as misinterpretations can disproportionately impact vulnerable populations. To address this, we introduce the World Central Banks (WCB) dataset, the most comprehensive monetary policy corpus to date, comprising over 380k sentences from 25 central banks across diverse geographic regions, spanning 28 years of historical data. After uniformly sampling 1k sentences per bank (25k total) across all available years, we annotate and review each sentence using dual annotators, disagreement resolutions, and secondary expert reviews. We define three tasks: Stance Detection, Temporal Classification, and Uncertainty Estimation, with each sentence annotated for all three. We benchmark seven Pretrained Language Models (PLMs) and nine Large Language Models (LLMs) (Zero-Shot, Few-Shot, and with annotation guide) over 15,075 experiments. We find that a model trained on aggregated data across banks significantly surpasses a model trained on an individual bank's data, confirming the principle *"the whole is greater than the sum of its parts"*. Additionally, rigorous human evaluations, error analyses, and predictive tasks validate our framework's economic utility. Our artifacts are accessible through the WCB Homepage, HuggingFace, and GitHub under the CC-BY-NC-SA 4.0 license.

---

## Repository Layout

| Path | Description |
| :--- | :--- |
| `cleaned_data/` | Markdown and txt files with cleaned data |
| `configs/` | configs for the LLM experiments |
| `croissant_files/` | croissant files for the 25k annotated sentences and the full corpus (380k sentences) |
| `final_data/` | csv files with annotated sentences |
| `llm_inference_outputs/` | files containing outputs of the LLMs for different experiments |
| `llm_inference_logs/` | logs for the LLM experiments |
| `raw_data/` | Raw documents (PDF, txt, docx) |
| `resources/` | Figures & logos for the paper/README |
| `sanitized_data/` | txt files with only sentences |
| `src/llm_benchmarking/` | LLM experimentation pipeline |
| `src/plm_benchmarking/` | Pre‑trained encoder benchmarks |
| `src/additional_experiments/` | Scripts for generating synthetic meeting minutes, performing ablation studies, etc. |
| `utils/` | Utility scripts for logging and other helper functions. |
| `master_file_metadata.json` | Metadata file containing detailed information about the dataset (JSON). |
| `master_file_metadata.xlsx` | Metadata file containing detailed information about the dataset (Excel). |

---

## Format of Released Data

### Released Splits

* **Per‑bank** datasets: `gtfintechlab/<bank_slug>`, 3 seeds each.  
* **Aggregated** dataset: `gtfintechlab/all_annotated_sentences_25000`.

### Metadata
The master_file_metadata.json in the root directory contains the metadata for the entire dataset. The entries are formatted as follows:

```json
    { 
      "central_bank_name": { 
        "year": { 
          "document_key": {
            "release_date": "DD-MM-YYYY",
            "start_date": "DD-MM-YYYY",
            "end_date": "DD-MM-YYYY",
            "minutes_link": "URL to the source document",
            "cleaned_document_name": "Filename of cleaned document",
            "original_document_name": "Filename of original document",
            "sentences": [
              "First sentence from the document.",
              "Second sentence from the document.",
              "..."
            ]
          }
        }
      }
    }
```


<br>

---

## Environment Setup
> Tested on **Python 3.9 – 3.11**.  
> GPU support: CUDA 11.8 (optional).

1. **Clone and create a virtual environment**

```bash
git clone https://github.com/gtfintechlab/WorldCentralBanks.git
cd WorldCentralBanks
python -m venv .venv              # or: conda create -n wcb python=3.10
source .venv/bin/activate         # # conda activate wcb
```         

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Keys**

Copy the sample file:
```bash
cp .env.example .env
```

Open .env and paste your credentials

HF_TOKEN=           # read or read‑write scope

TOGETHERAI_API_KEY=

OPENAI_API_KEY=

GEMINI_API_KEY=


---

## Code - getting started

**Note**: Ensure your environment is correctly set up before running the scripts.

### Bank Dictionary: Mapping Dataset Keys to Official Central Bank Names
```json
  {
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
```

## Dataset Availability

### Access the Dataset on Hugging Face

Access the **25k annotated sentences dataset** on [Hugging Face](https://huggingface.co/datasets/gtfintechlab/all_annotated_sentences_25000)  
<img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face Logo" width="25"/>

The **World Central Bank (WCB)** dataset is available on Hugging Face. It includes:

- **Individual central banks' datasets**
- **Aggregated dataset** (25k annotated sentences, 1k per bank)
- **Full corpus** (380,200 sentences without splits)

#### Loading the Full Corpus (380k Sentences)
```python
from datasets import load_dataset

dataset = load_dataset("gtfintechlab/WCB_380k_sentences")
```

#### Loading the Aggregated Dataset (25k Annotated Sentences)
```python
from datasets import load_dataset

dataset = load_dataset("gtfintechlab/all_annotated_sentences_25000", '{SEED}')
```

#### Loading a Specific Central Bank's Dataset
```python
from datasets import load_dataset

dataset = load_dataset("gtfintechlab/{bank_name}", '{SEED}')
```

### Available Seeds
- 5768
- 78516
- 944601

### Croissant Files
- **Full corpus (380k sentences)**: `root/croissant_files/croissant_WCB_380k_sentences.json`
- **Annotated dataset (25k sentences)**: `root/croissant_files/croissant_all_annotated_sentences_25000.json`
---

## Loading Models from Hugging Face

### Using Pre-Trained Models for WCB Tasks

Use `bank="WCB"` for the best-performing general model, or any key from `bank_map` for a bank‑specific model.

Below are examples for all three tasks:

---

#### 1. Stance Detection  
**Model Name Pattern**: `model_<bank>_stance_label`  
**Labels**: Hawkish, Dovish, Neutral, Irrelevant  

**Intended Use**  
This model is designed for researchers and practitioners working on subjective text classification, particularly within financial contexts. It assesses the **Stance** attribute, aiding in the analysis of subjective content in financial communications.

**How to Use**  
```python
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

# Load tokenizer, model, and configuration
tokenizer = AutoTokenizer.from_pretrained("gtfintechlab/model_{bank}_stance_label", do_lower_case=True, do_basic_tokenize=True)
model = AutoModelForSequenceClassification.from_pretrained("gtfintechlab/model_{bank}_stance_label", num_labels=4)
config = AutoConfig.from_pretrained("gtfintechlab/model_{bank}_stance_label")

# Initialize text classification pipeline
classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

# Classify Stance
sentences = [
  "[Sentence 1]",
  "[Sentence 2]"
]
results = classifier(sentences, batch_size=128, truncation="only_first")
print(results)
```

**Label Interpretation**  
- `LABEL_0`: Hawkish; supports contractionary monetary policy.  
- `LABEL_1`: Dovish; supports expansionary monetary policy.  
- `LABEL_2`: Neutral; neither hawkish nor dovish, or both sentiments present.  
- `LABEL_3`: Irrelevant; unrelated to monetary policy.  

---

#### 2. Temporal Classification  
**Model Name Pattern**: `model_<bank>_time_label`  
**Labels**: Forward-looking, Not Forward-looking  

**Intended Use**  
This model is designed for researchers and practitioners working on subjective text classification, particularly within financial contexts. It assesses the **Temporal Classification** attribute, aiding in the analysis of subjective content in financial communications.

**How to Use**  
```python
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

# Load tokenizer, model, and configuration
tokenizer = AutoTokenizer.from_pretrained("gtfintechlab/model_{bank}_time_label", do_lower_case=True, do_basic_tokenize=True)
model = AutoModelForSequenceClassification.from_pretrained("gtfintechlab/model_{bank}_time_label", num_labels=2)
config = AutoConfig.from_pretrained("gtfintechlab/model_{bank}_time_label")

# Initialize text classification pipeline
classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

# Classify Temporal Classification
sentences = [
  "[Sentence 1]",
  "[Sentence 2]"
]
results = classifier(sentences, batch_size=128, truncation="only_first")
print(results)
```

**Label Interpretation**  
- `LABEL_0`: Forward-looking; discusses future economic events or decisions.  
- `LABEL_1`: Not Forward-looking; discusses past or current economic events or decisions.  

---

#### 3. Uncertainty Estimation  
**Model Name Pattern**: `model_<bank>_certainty_label`  
**Labels**: Certain, Uncertain  

**How to Use**  
```python
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

# Load tokenizer, model, and configuration
tokenizer = AutoTokenizer.from_pretrained("gtfintechlab/model_{bank}_certainty_label", do_lower_case=True, do_basic_tokenize=True)
model = AutoModelForSequenceClassification.from_pretrained("gtfintechlab/model_{bank}_certainty_label", num_labels=2)
config = AutoConfig.from_pretrained("gtfintechlab/model_{bank}_certainty_label")

# Initialize text classification pipeline
classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, framework="pt")

# Classify Uncertainty Estimation
sentences = [
  "[Sentence 1]",
  "[Sentence 2]"
]
results = classifier(sentences, batch_size=128, truncation="only_first")
print(results)
```

**Label Interpretation**  
- `LABEL_0`: Certain; presents information definitively.  
- `LABEL_1`: Uncertain; presents information with speculation, possibility, or doubt.  

---


### Running the Benchmarking Scripts

### LLM Benchmarking

<p align="center">
  <img src="resources/anthropic.png" alt="Anthropic Logo" width="50"/> &nbsp;
  <img src="resources/deepseek.png" alt="DeepSeek Logo"   width="70"/> &nbsp;
  <img src="resources/FinMA.png"    alt="FinMA Logo"      width="50"/> &nbsp;
  <img src="resources/openai.png"   alt="OpenAI Logo"     width="50"/> &nbsp;
  <img src="resources/HKUST.png"    alt="Gemini Logo"     width="50"/> &nbsp;
  <img src="resources/llama.png"    alt="Llama Logo"      width="50"/> &nbsp;
  <img src="resources/modernbert.png" alt="BERT Logo"     width="50"/> &nbsp;
  <img src="resources/qwen.png"     alt="Qwen Logo"       width="50"/>
</p>


All commands are executed from src/llm_benchmarking:

#### Run every bank × 3 seeds for a given prompt format:

```bash
./run_all.sh <prompt_format>
```
prompt_format ∈ [guide (with annotation guides),
few_shot (few‑shot examples), no_guide (zero‑shot)]

#### Custom experiment

Edit root/src/llm_benchmarking/template.yaml (temperature, max_tokens, feature, etc.), then:

```bash
python inference.py --config template.yaml
```


#### FinMA inference

```bash
python finma_inference.py --config template.yaml
```

---

### Pre-Trained Language Models Benchmarking

#### Aggregated‑dataset run
Run this from the root/src/plm_benchmarking;

```bash
python general_setup_run.py
```

#### Bank‑specific setup 
Run this from the root/src/plm_benchmarking;

```bash
python bank_specific_setup_run.py
```
---


## Results

### Table 1.  F1 scores for Stance Detection in the General Setup (Hawkish / Dovish / Neutral / Irrelevant)

*Standard deviations in parentheses.  
Best‑performing **PLM** cells are in **bold**; best‑performing *LLM* cells are in *italics*.*

<details>
<summary><strong>Model abbreviation key</strong> – click to expand</summary>

| Abbrev | Model (checkpoint) | Category | Params |
|--------|-------------------|----------|--------|
| **MBB** | `ModernBERT‑base` | PLM – Base | 150 M |
| **BB**  | `bert‑base‑uncased` | PLM – Base | 110 M |
| **FB**  | `finbert‑pretrain` | PLM – Base | 110 M |
| **RBB** | `roberta‑base` | PLM – Base | 125 M |
| **MBL** | `ModernBERT‑large` | PLM – Large | 396 M |
| **BL**  | `bert‑large` | PLM – Large | 340 M |
| **RBL** | `roberta‑large` | PLM – Large | 355 M |
| **FM**  | `finma‑7b‑full` | LLM (Closed) | 7 B |
| **Gem** | `gemini‑2.0‑flash` | LLM (Closed) | — |
| **4o**  | `gpt‑4o‑2024‑08‑06` | LLM (Closed) | — |
| **4.1** | `gpt‑4.1‑2025‑04‑14` | LLM (Closed) | — |
| **4.1M**| `gpt‑4.1‑mini‑2025‑04‑14` | LLM (Closed) | — |
| **DS**  | `DeepSeek‑V3‑0324` | LLM (Open) | 671 B |
| **Qwen**| `Qwen2.5‑72B‑Instruct‑Turbo` | LLM (Open) | 72.7 B |
| **L3**  | `Llama‑3‑70b‑chat‑hf` | LLM (Open) | 70 B |
| **L4S** | `Llama‑4‑Scout‑17B‑16E‑Instruct` | LLM (Open) | 405 B |

</details>

<details>
<summary><strong>Central Banks' abbreviation key</strong> – click to expand</summary>

| Abbrev | Full Name |
|--------|-----------|
| **FOMC**  | Federal Open Market Committee (USA) |
| **PBoC**  | People's Bank of China |
| **BoJ**   | Bank of Japan |
| **BoE**   | Bank of England |
| **SNB**   | Swiss National Bank |
| **BCB**   | Central Bank of Brazil |
| **RBI**   | Reserve Bank of India |
| **ECB**   | European Central Bank |
| **CBR**   | Central Bank of the Russian Federation |
| **CBCT**  | Central Bank of China (Taiwan) |
| **MAS**   | Monetary Authority of Singapore |
| **BoK**   | Bank of Korea (South Korea) |
| **RBA**   | Reserve Bank of Australia |
| **BoI**   | Bank of Israel |
| **BoC**   | Bank of Canada |
| **BdeM**  | Bank of Mexico |
| **NBP**   | Narodowy Bank Polski (Poland) |
| **CBRT**  | Central Bank of Turkey |
| **BoT**   | Bank of Thailand |
| **CBE**   | Central Bank of Egypt |
| **BNM**   | Bank Negara Malaysia |
| **BSP**   | Central Bank of the Philippines |
| **CBoC**  | Central Bank of Chile |
| **BCRP**  | Central Reserve Bank of Peru |
| **BanRep**| Bank of the Republic (Colombia) |

</details>


| Bank | MBB | BB | FB | RBB | MBL | BL | RBL | Gem | 4o | 4.1m | 4.1 | DS | Qwen | FM | L3 | L4S |
|------|--------|-----------|------------|----------|--------|-----------|----------|------------|-----------|-------------|------------|-------------|------|----------|---------|----------|
| BCB | <ins>**.678 (.039)**</ins> | .635 (.057) | .609 (.008) | .655 (.018) | .673 (.016) | .636 (.014) | .634 (.050) | .528 (.027) | .498 (.017) | .462 (.020) | .504 (.017) | <ins>*.613 (.021)*</ins> | .525 (.028) | .350 (.034) | .503 (.021) | .589 (.049) |
| BCRP | .788 (.021) | .781 (.008) | .764 (.009) | .779 (.028) | .798 (.013) | .801 (.024) | <ins>**.821 (.015)**</ins> | <ins>*.675 (.004)*</ins> | .628 (.008) | .634 (.035) | .665 (.004) | .666 (.010) | .503 (.062) | .301 (.031) | .641 (.014) | .620 (.043) |
| BNM | .626 (.029) | .629 (.017) | <ins>**.653 (.023)**</ins> | .601 (.012) | .630 (.041) | .644 (.013) | .640 (.009) | .409 (.006) | .443 (.027) | .430 (.007) | .409 (.025) | .475 (.013) | .333 (.026) | .160 (.033) | <ins>*.567 (.025)*</ins> | .435 (.005) |
| BSP | .741 (.015) | .697 (.020) | .707 (.028) | .749 (.010) | .724 (.049) | .698 (.025) | <ins>**.784 (.017)**</ins> | .424 (.042) | .420 (.069) | .451 (.039) | .514 (.076) | .534 (.029) | .380 (.015) | .245 (.027) | <ins>*.584 (.042)*</ins> | .500 (.035) |
| BanRep | .685 (.031) | .638 (.022) | .679 (.017) | .673 (.013) | <ins>**.702 (.001)**</ins> | .650 (.017) | .701 (.013) | .515 (.021) | .455 (.031) | .520 (.036) | .553 (.015) | .570 (.037) | .450 (.023) | .230 (.033) | <ins>*.573 (.038)*</ins> | .423 (.033) |
| BoC | .722 (.033) | .740 (.006) | .750 (.010) | .745 (.032) | .721 (.004) | .755 (.005) | <ins>**.785 (.010)**</ins> | .629 (.069) | .647 (.052) | .641 (.052) | .657 (.028) | .657 (.026) | .524 (.038) | .264 (.029) | <ins>*.669 (.043)*</ins> | .644 (.024) |
| BoE | .686 (.031) | .706 (.056) | .734 (.052) | .769 (.019) | .735 (.039) | .755 (.009) | <ins>**.785 (.034)**</ins> | .543 (.026) | .524 (.031) | .537 (.048) | .602 (.031) | .543 (.070) | .396 (.021) | .129 (.026) | <ins>*.661 (.044)*</ins> | .518 (.045) |
| BoI | .652 (.003) | .642 (.023) | .616 (.019) | .614 (.008) | .658 (.023) | .628 (.033) | <ins>**.689 (.017)**</ins> | .474 (.011) | .460 (.005) | .433 (.032) | .526 (.013) | .482 (.001) | .329 (.025) | .085 (.011) | <ins>*.594 (.023)*</ins> | .430 (.008) |
| BoJ | .691 (.020) | .662 (.044) | .629 (.047) | .660 (.020) | <ins>**.708 (.042)**</ins> | .683 (.033) | .702 (.025) | .524 (.010) | .545 (.021) | .465 (.028) | .565 (.008) | .498 (.009) | .406 (.040) | .157 (.033) | <ins>*.574 (.027)*</ins> | .507 (.026) |
| BoK | .723 (.056) | .664 (.009) | .679 (.011) | .706 (.018) | .740 (.009) | .700 (.028) | <ins>**.755 (.019)**</ins> | .646 (.040) | .648 (.030) | .594 (.066) | <ins>*.678 (.016)*</ins> | .629 (.016) | .466 (.076) | .181 (.031) | .632 (.032) | .592 (.047) |
| BdeM | .696 (.020) | .694 (.048) | .642 (.032) | .724 (.023) | .716 (.008) | .684 (.026) | <ins>**.735 (.030)**</ins> | .596 (.009) | .602 (.024) | .509 (.023) | .626 (.016) | <ins>*.669 (.034)*</ins> | .447 (.047) | .118 (.018) | .642 (.012) | .552 (.013) |
| BoT | .717 (.046) | .696 (.064) | .723 (.021) | .735 (.057) | .733 (.071) | .728 (.006) | <ins>**.741 (.017)**</ins> | .547 (.004) | .549 (.032) | .551 (.039) | .573 (.012) | .581 (.029) | .484 (.038) | .258 (.026) | <ins>*.596 (.009)*</ins> | .577 (.030) |
| CBCT | .641 (.049) | .637 (.031) | .635 (.029) | .667 (.015) | .616 (.035) | .678 (.032) | <ins>**.688 (.024)**</ins> | .451 (.044) | .474 (.044) | .474 (.031) | .485 (.026) | .522 (.022) | .388 (.049) | .180 (.037) | <ins>*.556 (.015)*</ins> | .475 (.051) |
| CBE | .773 (.027) | .783 (.026) | .790 (.004) | .810 (.016) | .822 (.015) | .788 (.029) | <ins>**.836 (.014)**</ins> | .629 (.037) | .672 (.036) | .581 (.045) | .648 (.036) | .636 (.007) | .352 (.056) | .142 (.014) | <ins>*.702 (.021)*</ins> | .594 (.024) |
| CBR | .763 (.031) | .754 (.017) | .750 (.020) | .798 (.032) | .811 (.023) | .779 (.022) | <ins>**.835 (.011)**</ins> | .759 (.015) | .749 (.027) | .693 (.026) | .701 (.049) | <ins>*.794 (.028)*</ins> | .573 (.035) | .146 (.022) | .772 (.029) | .665 (.013) |
| CBRT | .717 (.015) | .743 (.016) | .724 (.012) | .746 (.011) | .746 (.014) | .724 (.032) | <ins>**.762 (.027)**</ins> | .495 (.006) | .421 (.014) | .424 (.018) | .475 (.015) | .539 (.030) | .277 (.006) | .133 (.020) | <ins>*.653 (.036)*</ins> | .416 (.032) |
| CBoC | .760 (.048) | .747 (.006) | .743 (.054) | .779 (.049) | .792 (.043) | .793 (.058) | <ins>**.799 (.037)**</ins> | .668 (.032) | .604 (.027) | .605 (.033) | .678 (.057) | .676 (.038) | .559 (.072) | .223 (.040) | <ins>*.685 (.019)*</ins> | .539 (.071) |
| ECB | .707 (.040) | .699 (.048) | .668 (.030) | .724 (.050) | .724 (.014) | .713 (.022) | <ins>**.755 (.024)**</ins> | .638 (.023) | .599 (.019) | .610 (.038) | <ins>*.660 (.021)*</ins> | .637 (.005) | .548 (.017) | .206 (.052) | .613 (.020) | .595 (.016) |
| FOMC | .671 (.029) | .674 (.035) | .675 (.046) | .747 (.020) | .732 (.037) | .685 (.044) | <ins>**.749 (.047)**</ins> | .572 (.021) | .584 (.025) | .564 (.018) | <ins>*.649 (.023)*</ins> | .653 (.023) | .512 (.023) | .170 (.025) | .599 (.012) | .498 (.015) |
| MAS | .656 (.049) | .681 (.043) | .666 (.005) | .666 (.066) | .698 (.042) | .680 (.049) | <ins>**.703 (.033)**</ins> | .553 (.046) | .581 (.026) | .588 (.034) | .569 (.015) | <ins>*.689 (.041)*</ins> | .540 (.026) | .347 (.024) | .638 (.035) | .646 (.023) |
| NBP | .685 (.016) | .690 (.013) | .705 (.026) | <ins>**.731 (.013)**</ins> | .725 (.009) | .697 (.010) | .695 (.020) | .637 (.015) | .631 (.043) | .614 (.063) | <ins>*.665 (.031)*</ins> | .660 (.002) | .508 (.028) | .118 (.017) | .618 (.035) | .597 (.015) |
| PBoC | .791 (.033) | .763 (.008) | .742 (.046) | .787 (.026) | <ins>**.813 (.014)**</ins> | .793 (.007) | .786 (.017) | .492 (.046) | .559 (.037) | .531 (.026) | .535 (.033) | <ins>*.592 (.037)*</ins> | .379 (.017) | .128 (.018) | .613 (.033) | .446 (.024) |
| RBA | .685 (.023) | .681 (.019) | .682 (.027) | .672 (.015) | .707 (.029) | .695 (.024) | <ins>**.741 (.028)**</ins> | .531 (.049) | .478 (.079) | .483 (.058) | .553 (.074) | .537 (.055) | .358 (.049) | .133 (.020) | <ins>*.614 (.034)*</ins> | .495 (.057) |
| RBI | .604 (.037) | .649 (.035) | .653 (.041) | .628 (.034) | .633 (.032) | .655 (.039) | <ins>**.668 (.044)**</ins> | .489 (.025) | .519 (.041) | .509 (.026) | .495 (.027) | <ins>*.542 (.016)*</ins> | .431 (.008) | .231 (.058) | .581 (.030) | .557 (.032) |
| SNB | .692 (.017) | .685 (.028) | .653 (.016) | .685 (.009) | <ins>**.725 (.018)**</ins> | .698 (.030) | .713 (.020) | .635 (.003) | .601 (.015) | .640 (.037) | <ins>*.652 (.016)*</ins> | .643 (.024) | .554 (.029) | .252 (.008) | .612 (.014) | .607 (.051) |
| **Average** | .702 (.030) | .695 (.028) | .691 (.025) | .714 (.025) | .723 (.026) | .710 (.025) | <ins>**.740 (.024)**</ins> | .562 (.085) | .556 (.084) | .542 (.075) | .586 (.078) | <ins>*.601 (.075)*</ins> | .449 (.083) | .196 (.071) | .620 (.053) | .541 (.074) |



For more results and a comprehensive leaderboard, visit the [WCB website](https://gcb-web-bb21b.web.app/).

---

## License

The WCB dataset is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC-BY-NC-SA 4.0) license, which allows others to share, copy, distribute, and transmit the work, as well as to adapt the work, provided that appropriate credit is given, a link to the license is provided, and any changes made are indicated.

 
## Citation: If you use our open-source dataset or refer to our results, please cite our paper:


```bash
@article{WCBShahSukhaniPardawala,
  title={Words That Unite The World: A Unified Framework for Deciphering Global Central Bank Communications},
  author={Agam Shah, Siddhant Sukhani, Huzaifa Pardawala et. al},
  year={2025}
}
```


## Issue Reporting

For any questions or concerns, please open a GitHub issue or email: huzaifahp7@gmail.com, ashah482@gatech.edu, siddhantsukhani5@gmail.com

