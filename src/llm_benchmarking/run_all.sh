#!/bin/bash

set -euo pipefail

PROMPT_FORMAT="${1:-guide}" 

BANKS=(
  "bank_negara_malaysia" "bank_of_canada" "bank_of_the_republic_colombia" "bank_of_england"
  "bank_of_israel" "bank_of_japan" "bank_of_korea" "bank_of_mexico"
  "central_bank_of_the_philippines" "bank_of_thailand" "central_bank_of_brazil"
  "central_bank_of_chile" "central_bank_of_egypt" "central_bank_of_the_russian_federation"
  "central_bank_republic_of_turkey" "central_bank_of_china_taiwan"
  "central_reserve_bank_of_peru" "european_central_bank" "federal_reserve_system"
  "monetary_authority_of_singapore" "national_bank_of_poland"
  "peoples_bank_of_china" "reserve_bank_of_india" "reserve_bank_of_australia"
  "swiss_national_bank"
)

SEEDS=(5768 78516 944601)

MODELS=(
  "together_ai/deepseek-ai/DeepSeek-r1"
)

FEATURES=("stance" "certain" "time")
CONFIG_DIR="../../configs/configs_${PROMPT_FORMAT}"
LOG_DIR="../../llm_inference_logs/logs_${PROMPT_FORMAT}"
mkdir -p "$CONFIG_DIR" "$LOG_DIR"

JOBS_FILE="jobs.txt"
> "$JOBS_FILE"  

for bank in "${BANKS[@]}"; do
  for seed in "${SEEDS[@]}"; do
    for model in "${MODELS[@]}"; do
      for feature in "${FEATURES[@]}"; do
        echo "$bank $seed $model $feature" >> "$JOBS_FILE"
      done
    done
  done
done

TOTAL_JOBS=$(wc -l < "$JOBS_FILE")
COUNTER=0

while IFS=' ' read -r BANK SEED MODEL FEATURE; do
  (( COUNTER++ ))
  MODEL_ID="${MODEL//\//_}"  # sanitize
  CONFIG_SUBDIR="$CONFIG_DIR/$BANK"
  LOG_SUBDIR="$LOG_DIR/$BANK"
  mkdir -p "$CONFIG_SUBDIR" "$LOG_SUBDIR"

  CONFIG_FILE="$CONFIG_SUBDIR/config_${BANK}_${SEED}_${MODEL_ID}_${FEATURE}.yaml"
  LOG_FILE="$LOG_SUBDIR/log_${BANK}_${SEED}_${MODEL_ID}_${FEATURE}.txt"

  if [ -f "$LOG_FILE" ]; then
    echo "[$COUNTER/$TOTAL_JOBS] [SKIP] Already have $LOG_FILE"
    continue
  fi

  sed -e "s|{{BANK}}|$BANK|g" \
      -e "s|{{SEED}}|$SEED|g" \
      -e "s|{{MODEL}}|$MODEL|g" \
      -e "s|{{FEATURE}}|$FEATURE|g" \
      -e "s|{{PROMPT_FORMAT}}|$PROMPT_FORMAT|g" \
      template.yaml > "$CONFIG_FILE"

  echo "[$COUNTER/$TOTAL_JOBS] Running inference for $BANK | seed=$SEED | model=$MODEL | feature=$FEATURE" | prompt_format="$PROMPT_FORMAT"
  python inference.py --config "$(realpath "$CONFIG_FILE")" > "$LOG_FILE" 2>&1

  PROGRESS=$(( 100*COUNTER/TOTAL_JOBS ))
  echo -ne "Progress: $PROGRESS%   \r"
done < "$JOBS_FILE"

echo
echo "All $TOTAL_JOBS jobs completed"