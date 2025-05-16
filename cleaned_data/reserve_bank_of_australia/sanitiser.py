import os
import re
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory where the script and the year directories are located
root_dir = '/Users/hp/Desktop/global-central-banks/data/reserve_bank_australia_minutes'
output_data_dir = os.path.join(root_dir, 'sanitized_data')

# Create the sanitized_data directory if it doesn't exist
if not os.path.exists(output_data_dir):
    os.makedirs(output_data_dir)
    logging.info(f'Created sanitized data directory: {output_data_dir}')

def clean_rba_file(content):
    logging.info('Starting file content cleaning...')
    
    # 1. Remove browser settings message
    content = re.sub(r'Check your browser settings and network.*', '', content)
    logging.info('Browser settings message removed.')
    
    # 2. Remove Foundation for Children message
    content = re.sub(r'The Reserve Bank of Australia supports the\s+Foundation for Children\.', '', content)
    logging.info('Foundation for Children message removed.')

    # 3. Remove paragraphs containing mostly names separated by commas or conjunctions
    # content = re.sub(r'([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]*)*(?:\s\([A-Za-z\s,]+\))?,?(\s?and\s?)?)+', '', content)
    # logging.info('Paragraphs with names removed.')

    # 4. Improved regex to remove "location - date" patterns, including "and" ranges like "5 and 6 February"
    # Handles patterns like "Sydney – 5 and 6 February 2024" or "– 5 and 6 2024"
    content = re.sub(r'[A-Za-z]+\s+–\s+\d{1,2}(?:\s*and\s*\d{1,2})?\s*(?:[A-Za-z]+)?\s+\d{4}', '', content)
    logging.info('Location and date patterns removed.')

    logging.info('Location-date patterns removed.')

    # 5. Ensure the content starts from relevant text, e.g., "Members commenced" or similar
    # Match and start from "Members commenced" or phrases starting with "Members"
    content = re.sub(r'^(.*?)(\bMembers\b.*)', r'\2', content, flags=re.DOTALL)

    # 6. Remove excess blank lines
    content = re.sub(r'\n\s*\n', '\n', content)
    
    logging.info('Finished cleaning content.')
    return content.strip()

def process_rba_files():
    # Traverse the root_dir and process each file in the year subdirectories
    for subdir, _, files in os.walk(root_dir):
        logging.info(f'Processing directory: {subdir}')
        if 'sanitized_data' not in subdir:  # Skip the sanitized data directory to avoid reprocessing
            for file in files:
                if file.endswith('.txt'):  # Process only text files
                    file_path = os.path.join(subdir, file)
                    logging.info(f'Reading file: {file_path}')
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        logging.info(f'File content read: {file_path}')

                        # Clean the file content
                        cleaned_content = clean_rba_file(content)

                        # Create a corresponding file in the sanitized_data directory
                        relative_path = os.path.relpath(subdir, root_dir)
                        sanitized_subdir = os.path.join(output_data_dir, relative_path)
                        
                        if not os.path.exists(sanitized_subdir):
                            os.makedirs(sanitized_subdir)
                            logging.info(f'Created sanitized subdirectory: {sanitized_subdir}')

                        sanitized_file_path = os.path.join(sanitized_subdir, file)

                        with open(sanitized_file_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)

                        logging.info(f'Cleaned file saved at: {sanitized_file_path}')
                    except Exception as e:
                        logging.error(f'Error processing file {file_path}: {e}')

if __name__ == "__main__":
    logging.info('Starting file processing...')
    process_rba_files()
    logging.info('File processing completed.')
