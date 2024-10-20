import re
import os
import pdfminer
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys

nltk.download('punkt')
nltk.download('stopwords')

###############################################################################################################
######################################## Funcoes utilizadas ###################################################
###############################################################################################################

def read_pdf(pdf_path):
    text = extract_text(pdf_path)
    text = text.lower()
    return text

def extract_section_from_string(text):
    section_text = ""
    # Search for the start of the first section
    start_match = re.search(r'i\.', text)
    if start_match:
        start_index = start_match.end()
        # Search for the start of the next section
        end_match = re.search(r'ii\.', text[start_index:])
        if end_match:
            end_index = start_index + end_match.start()
            # Extract the text between the start and end indices
            section_text = text[start_index:end_index]

    return section_text.strip()

def remove_first_introduction(text):
    # Replace the first occurrence of "introduction" with an empty string
    cleaned_text = text.replace("introduction", "", 1)
    return cleaned_text

def remove_non_words(text):
    # Regular expression pattern to match numbers between square brackets
    number_pattern = r'\[\d+\]'
    
    # Regular expression pattern to match punctuation and numbers
    punctuation_and_numbers_pattern = r'[^\w\s]|\d'

    # Use re.sub to replace numbers between square brackets with an empty string
    cleaned_text = re.sub(number_pattern, '', text)

    # Use re.sub to replace punctuation and numbers with an empty string
    cleaned_text = re.sub(punctuation_and_numbers_pattern, '', cleaned_text)

    return cleaned_text

def remove_stopwords(text):
    # Download the stopwords list from NLTK
    stopwords_list = set(stopwords.words('english'))

    # Remove numbers between square brackets
    text = re.sub(r'\[\d+\]', '', text)

    # Remove punctuation and split the text into words
    words = re.findall(r'\b\w+\b', text)

    # Filter out stop words
    filtered_words = [word for word in words if word.lower() not in stopwords_list]

    # Join the filtered words back into a single string
    cleaned_text = ' '.join(filtered_words)

    cleaned_text = cleaned_text.lower()
    
    return cleaned_text

def remove_first_introduction(text):
    # Replace the first occurrence of "introduction" with an empty string
    cleaned_text = text.replace("introduction", "", 1)
    return cleaned_text


def list_files(path):
    # List all files in the specified path
    files = os.listdir(path)
    return files

def save_string_to_file(string, file_path):
    file_path = file_path + 'software_testing_content.txt'
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(string)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '=', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def progres(count, total, status='', bar_len=60):
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    fmt = '[%s] %s%s ...%s' % (bar, percents, '%', status)
    print('\b' * len(fmt), end='')  # clears the line
    sys.stdout.write(fmt)
    sys.stdout.flush()

########################################################################################################################

def extrai_palavras_conteudo(directory_path, file_path):
    # directory_path: diretorio com os pdfs
    
    # Lista de pdfs
    pdfs_in_directory = list_files(directory_path)

    # Adicionando o caminho completo
    pdfs_in_directory = [directory_path + x for x in pdfs_in_directory]

    software_testing_words = ''

    # Barra de progresso
    l = len(pdfs_in_directory)
    # printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    progres(0, l, 'Processando...')
    i = 0
    for pdf_path in pdfs_in_directory:
        # Lendo o pdf
        text_1 = read_pdf(pdf_path)

        # Extraindo somente a introducao
        text_2 = extract_section_from_string(text_1)

        # Removendo o texto gerado no download dos pdfs
        licenca_usp = 'authorized licensed use limited to: universidade de sao paulo. downloaded on april 20,2024 at 17:19:03 utc from ieee xplore.  restrictions apply.'
        text_2 = text_2.replace(licenca_usp.lower(), '')

        # Removendo o nome da da secao "introduction"
        text_2 = remove_first_introduction(text_2)

        # Removendo pontuacao e numeros
        text_3 = remove_non_words(text_2)

        # Removendo stop words
        text_4 = remove_stopwords(text_3)

        # Adicionando as palavras do pdf ao conjunto de palavras de software testing
        software_testing_words = software_testing_words + text_4
        # printProgressBar(i+1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        progres(i+1, l, 'Processando')
        i += 1
    
    # Salvando as palavras em um txt
    save_string_to_file(software_testing_words, file_path)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python function.py directory_path output_file_path")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    extrai_palavras_conteudo(directory_path, output_file_path)
    print("/nConteudo processado e salvo com sucesso!")