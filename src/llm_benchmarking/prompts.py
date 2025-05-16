from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
GUIDES_DIR = ROOT_DIR / "llm_benchmarking" / "annotation_guides"
FEWSHOT_DIR = ROOT_DIR / "llm_benchmarking" / "few_shot_examples"



def stance_prompt(sentence, bank_name):
    if bank_name == "Central Bank of the Philippines":
        prompt = f"""You are given a sentence related to the {bank_name}' monetary policy meeting. Your task is to classify its monetary policy stance and briefly justify your choice.
 
        Input:
        - Sentence: {sentence}
        
        Instructions:
        1. Assign one of the following labels under the `label` key:
        "hawkish", "neutral", "dovish", or "irrelevant".
        
        2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
        
        3. Your output must follow this structure:
        {{
        "label": "hawkish | dovish | neutral | irrelevant",
        "justification": "One-sentence explanation for the assigned label"
        }}"""
        
    else:
        prompt = f"""You are given a sentence related to the {bank_name}'s monetary policy meeting. Your task is to classify its monetary policy stance and briefly justify your choice.
    
        Input:
        - Sentence: {sentence}
        
        Instructions:
        1. Assign one of the following labels under the `label` key:
        "hawkish", "neutral", "dovish", or "irrelevant".
        
        2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
        
        3. Your output must follow this structure:
        {{
        "label": "hawkish | dovish | neutral | irrelevant",
        "justification": "One-sentence explanation for the assigned label"
        }}"""
        
    return prompt
    
def time_prompt(sentence, bank_name):
    if bank_name == "Central Bank of the Philippines":
        prompt = f"""You are given a sentence related to the {bank_name}' monetary policy meeting. Your task is to classify whether it is forward looking or not forward looking and briefly justify your choice.
 
        Input:
        - Sentence: {sentence}
        
        Instructions:
        1. Assign one of the following labels under the `label` key:
        "forward looking", "not forward looking".
        
        2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
        
        3. Your output must follow this structure:
        {{
        "label": "forward looking | not forward looking",
        "justification": "One-sentence explanation for the assigned label"
        }}"""
        
    else:
        prompt = f"""You are given a sentence related to the {bank_name}'s monetary policy meeting. Your task is to classify whether it is forward looking or not forward looking and briefly justify your choice.
 
        Input:
        - Sentence: {sentence}
        
        Instructions:
        1. Assign one of the following labels under the `label` key:
        "forward looking", "not forward looking".
        
        2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
        
        3. Your output must follow this structure:
        {{
        "label": "forward looking | not forward looking",
        "justification": "One-sentence explanation for the assigned label"
        }}"""
    return prompt

def certain_prompt(sentence, bank_name):
    
    if bank_name == "Central Bank of the Philippines":
        prompt = f"""You are given a sentence related to the {bank_name}' monetary policy meeting. Your task is to classify whether it is certain or uncertain and briefly justify your choice.
 
        Input:
        - Sentence: {sentence}
        
        Instructions:
        1. Assign one of the following labels under the `label` key:
        "certain", "uncertain".
        
        2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
        
        3. Your output must follow this structure:
        {{
        "label": "certain | uncertain",
        "justification": "One-sentence explanation for the assigned label"
        }}"""
        
    else:
        prompt = f"""You are given a sentence related to the {bank_name}'s monetary policy meeting. Your task is to classify whether it is certain or uncertain and briefly justify your choice.
 
        Input:
        - Sentence: {sentence}
        
        Instructions:
        1. Assign one of the following labels under the `label` key:
        "certain", "uncertain".
        
        2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
        
        3. Your output must follow this structure:
        {{
        "label": "certain | uncertain",
        "justification": "One-sentence explanation for the assigned label"
        }}"""

    return prompt



######## With guide stuff #########

def load_guide(feature: str, bank_slug: str) -> str:
    """
    Read the .tex guide for the given bank/feature and return plain text.
    """
    guide_path = GUIDES_DIR / bank_slug / f"{feature}.tex"
    if not guide_path.exists():
        raise FileNotFoundError(f"Guide not found: {guide_path}")
    return guide_path.read_text(encoding="utf‑8")

def system_header(feature: str, bank_name: str) -> str:
    """
    Generic system prompt — keeps all rules in ONE place.
    """
    lbl_map = {
        "stance":   '"hawkish", "neutral", "dovish", or "irrelevant"',
        "time":     '"forward looking" or "not forward looking"',
        "certain":  '"certain" or "uncertain"',
    }
    instruct_map = {
        "stance":   "hawkish | dovish | neutral | irrelevant",
        "time":     "forward looking | not forward looking",
        "certain":  "certain | uncertain",
    }
    if bank_name == "Central Bank of the Philippines":
        return (
            f"""You are given one sentence related to the {bank_name}' monetary policy meeting. You are also given an annotation guide for the feature: {feature}.
            Strictly follow the guide; do not invent new criteria or labels.\n
            Your task is to classify whether it is {lbl_map[feature]} and briefly justify your choice.
            
            Instructions:
            1. Assign one of the following labels under the `label` key:
            {lbl_map[feature]}
            
            2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
            
            3. Your output must follow this structure:
            {{
            "label": "{instruct_map[feature]}",
            "justification": "One-sentence explanation for the assigned label"
            }}"""
            )
    else:
        return (
            f"""You are given one sentence related to the {bank_name}'s monetary policy meeting. You are also given an annotation guide for the feature: {feature}.
            Strictly follow the guide; do not invent new criteria or labels.\n
            Your task is to classify whether it is {lbl_map[feature]} and briefly justify your choice.
            
            Instructions:
            1. Assign one of the following labels under the `label` key:
            {lbl_map[feature]}
            
            2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
            
            3. Your output must follow this structure:
            {{
            "label": "{instruct_map[feature]}",
            "justification": "One-sentence explanation for the assigned label"
            }}"""
            )
    
def stance_prompt_with_guide(sentence: str, bank_slug: str, bank_official: str):
    guide_text = load_guide("stance", bank_slug)
    return [
        {"role": "system", "content": system_header("stance", bank_official)},
        {
            "role": "user",
            "content": (
                f"""Input:\n
                ### Annotation Guide: {guide_text}\n\n
                ### Sentence: {sentence}
                """
            ),
        },
    ]


def time_prompt_with_guide(sentence: str, bank_slug: str, bank_official: str):
    """
    Returns a prompt for time analysis with a guide.
    """
    guide_text = load_guide("time", bank_slug)
    return [
        {"role": "system", "content": system_header("time", bank_official)},
        {
            "role": "user",
            "content": (
                f"""Input:\n
                ### Annotation Guide: {guide_text}\n\n
                ### Sentence: {sentence}
                """
            ),
        },
    ]

def certain_prompt_with_guide(sentence: str, bank_slug: str, bank_official: str):
    """
    Returns a prompt for certain analysis with a guide.
    """
    guide_text = load_guide("certain", bank_slug)
    return [
        {"role": "system", "content": system_header("certain", bank_official)},
        {
            "role": "user",
            "content": (
                f"""Input:\n
                ### Annotation Guide: {guide_text}\n\n
                ### Sentence: {sentence}
                """
            ),
        },
    ]
    
    
    
############ Few-shot prompting ############

def load_examples(feature: str, bank_slug: str, seed: int) -> str:
    """
    Return the raw text of few‑shot examples for (bank, feature, seed).
    """
    ex_path = FEWSHOT_DIR / bank_slug / feature / f"examples_{seed}.txt"
    if not ex_path.exists():
        raise FileNotFoundError(f"Few‑shot file missing: {ex_path}")
    return ex_path.read_text(encoding="utf-8").strip()

def system_header_few_shot(feature: str, bank_name: str) -> str:
    lbl_map = {
        "stance":  '"hawkish", "neutral", "dovish", or "irrelevant"',
        "time":    '"forward looking" or "not forward looking"',
        "certain": '"certain" or "uncertain"',
    }
    instruct_map = {
        "stance":  "hawkish | dovish | neutral | irrelevant",
        "time":    "forward looking | not forward looking",
        "certain": "certain | uncertain",
    }

    bank_phrase = (
        f"the {bank_name}' monetary‑policy meeting"
        if bank_name == "Central Bank of the Philippines"
        else f"{bank_name}'s monetary‑policy meeting"
    )

    return (
        f"""You are given one sentence related to {bank_phrase}. You are also given a set of few-shot examples for the feature: {feature}.
            Follow these examples; do not invent new criteria or labels.\n
            Your task is to classify whether it is {lbl_map[feature]} and briefly justify your choice.
            
            Instructions:
            1. Assign one of the following labels under the `label` key:
            {lbl_map[feature]}
            
            2. Provide a concise explanation for your classification using the `justification` key. Limit the justification to one sentence.
            
            3. Your output must follow this structure:
            {{
            "label": "{instruct_map[feature]}",
            "justification": "One-sentence explanation for the assigned label"
            }}"""
    )

def prompt_with_examples(sentence: str, bank_slug: str,
                          bank_official: str, feature: str, seed: int):
    examples = load_examples(feature, bank_slug, seed)
    return [
        {"role": "system", "content": system_header_few_shot(feature, bank_official)},
        {
            "role": "user",
            "content": (
                f"""Input:\n"
                ### Few‑shot Examples\n{examples}\n\n"
                ### Sentence\n{sentence}"""
            ),
        },
    ]

def stance_prompt_fewshot(s, slug, off, seed):
    return prompt_with_examples(s, slug, off, "stance", seed)

def time_prompt_fewshot(s, slug, off, seed):
    return prompt_with_examples(s, slug, off, "time", seed)

def certain_prompt_fewshot(s, slug, off, seed):
    return prompt_with_examples(s, slug, off, "certain", seed)
