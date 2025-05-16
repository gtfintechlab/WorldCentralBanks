import os,sys
import pandas as pd
from time import sleep, time
from datetime import date, datetime
import re

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")
)

df = pd.read_excel("../bench-exp/labeled_master_file_metadata.xlsx") 

# ['bank', 'year', 'doc_id', 'release_date', 'start_date', 'end_date',
#        'minutes_link', 'cleaned_name', 'original_name', 'sentence',
#        'label_stance_label', 'score_stance_label', 'label_time_label',
#        'score_time_label', 'label_certain_label', 'score_certain_label']

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

banks = ["european_central_bank", "reserve_bank_of_india", "central_bank_of_the_russian_federation", "bank_of_korea", "central_bank_of_egypt",
        "central_bank_of_the_philippines", "bank_of_the_republic_colombia", "federal_reserve_system", "bank_of_japan", "bank_of_england", 
        "reserve_bank_of_australia", "bank_of_canada", "bank_of_israel", "bank_of_mexico", "bank_negara_malaysia",
        "swiss_national_bank", "central_bank_of_china_taiwan", "national_bank_of_poland", "central_bank_of_brazil", "central_bank_republic_of_turkey",
        "peoples_bank_of_china", "bank_of_thailand", "monetary_authority_of_singapore", "central_bank_of_chile", "central_reserve_bank_of_peru"]

banks_to_analyse = ["european_central_bank", "reserve_bank_of_india", "central_bank_of_the_russian_federation", "bank_of_korea", "central_bank_of_egypt",
        "central_bank_of_the_philippines", "bank_of_the_republic_colombia", "federal_reserve_system", "bank_of_japan", "bank_of_england", 
        "reserve_bank_of_australia", "bank_of_canada", "bank_of_israel", "bank_of_mexico", "bank_negara_malaysia",
        "swiss_national_bank", "central_bank_of_china_taiwan", "national_bank_of_poland", "central_bank_of_brazil", "central_bank_republic_of_turkey",
        "peoples_bank_of_china", "bank_of_thailand", "monetary_authority_of_singapore", "central_bank_of_chile", "central_reserve_bank_of_peru"]

df = df[df["year"] > 2023]



df = df[["bank", "release_date", "sentence"]] 

df["release_date"] = pd.to_datetime(df["release_date"], format="%d-%m-%Y")

grouped_df = df.groupby(["bank", "release_date"])["sentence"].apply(list).reset_index()

for target_bank in banks_to_analyse: 
    target_bank_nice_name = bank_map[target_bank]

    # Filter all release dates of the target bank after May 31, 2024
    target_dates = grouped_df[
        (grouped_df["bank"] == target_bank) & (grouped_df["release_date"] > "31-05-2024")
    ]

    for _, target_row in target_dates.iterrows():
        target_date = target_row["release_date"] 
        
        if os.path.exists(f"./generated_mm/{target_bank}_{str(target_date.date())}.txt"): 
            continue

        print(f"Processing: {target_bank} {target_date}")
    
        # Get example output for the target bank (its most recent MM before target_date)
        target_prior_mms = grouped_df[
            (grouped_df["bank"] == target_bank) & (grouped_df["release_date"] < target_date)
        ]
        if target_prior_mms.empty:
            continue  # no valid example output
        target_example_output = target_prior_mms.sort_values("release_date").iloc[-1]["sentence"]
        example_output_str = "\\n ".join(target_example_output)



        prior_target_date = target_prior_mms.sort_values("release_date").iloc[-1]["release_date"]
        # print(prior_target_date, "\n") 

        # Get example input: latest MM before target_date for each of 24 other banks
        other_banks = [b for b in banks if b != target_bank]
        example_inputs = []

        for bank in other_banks:
            prior_mms = grouped_df[
                (grouped_df["bank"] == bank) & (grouped_df["release_date"] < prior_target_date)
            ]
            if not prior_mms.empty:
                latest_mm = prior_mms.sort_values("release_date").iloc[-1]
                example_inputs.append((latest_mm["bank"], latest_mm["sentence"]))
                # print(latest_mm["bank"], latest_mm["release_date"])

        example_input_str = ""
        for bank, sentences in example_inputs:
            example_input_str += f"{bank_map[bank]}: " + "\\n ".join(sentences) + "\n\n"


        
        # print(prior_target_date, "\n")
        # New input for this target_date: latest MMs from other banks
        current_inputs = []

        for bank in other_banks:
            prior_mms = grouped_df[
                (grouped_df["bank"] == bank) & (grouped_df["release_date"] < target_date)
            ]
            if not prior_mms.empty:
                latest_mm = prior_mms.sort_values("release_date").iloc[-1]
                current_inputs.append((latest_mm["bank"], latest_mm["sentence"]))
                # print(latest_mm["bank"], latest_mm["release_date"])

        current_input_str = ""
        for bank, sentences in current_inputs:
            current_input_str += f"{bank_map[bank]}: " + "\\n ".join(sentences) + "\n\n"



        system_prompt = f"""
You are a precise and formal meeting minutes generator for the central bank called {target_bank_nice_name}.
Your job is to read meeting minutes (MM) from 24 other central banks and, based on those, 
produce meeting minutes that reflect what {target_bank_nice_name}'s stance would be, in line with the example provided.
You should write clearly and professionally, mimicking the tone of central bank communication. 
Each MM is a list of sentences, separated by a newline (\\n). 
""".strip() 


        user_prompt = f"""
Below is one example of an input-output pair, where the input consists of MM from 24 banks, each taken from their most recent meeting 
prior to the current target date, and the output is the MM generated for {target_bank_nice_name} from its own most recent meeting.

Example:
[Input from 24 banks]
{example_input_str}

[Output for {target_bank_nice_name}]
{example_output_str}

Now, here is a new input from 24 banks for {target_date.date()}. Based on the previous example, generate the MM for {target_bank_nice_name}.

[Input from 24 banks]
{current_input_str}

[Your Output for {target_bank_nice_name}]
""".strip()


        prompt_json = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4.1-2025-04-14",
                messages=prompt_json,
                temperature=0.0,
                max_tokens=20000
            )
            answer = chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error processing {target_bank} on {target_date.date()}: {e}")
            sleep(10.0)
            answer = "ERROR"

        with open(f"./generated_mm/{target_bank}_{str(target_date.date())}.txt", "w") as file:
            file.write(answer)



        # output[str(target_date.date())] = {
        #     "system_prompt": system_prompt,
        #     "user_prompt": user_prompt
        # }