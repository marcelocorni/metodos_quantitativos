# 1) Abrir o arquivo em anexo
# 2) Ler as colunas do scholar e do scopus
# 3) Para cada professor, pegar o número total de citações e o h-index
# 4) Gerar uma saida com "Nome - total scholar - hindex scholar - total scopus - hindex scopus
# ps: o arquivo de saída pode ser separado por vírgula


import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import pandas as pd

# Caminho para a pasta de downloads (exemplo: pasta Downloads do usuário)
download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

# Função para configurar o driver do Selenium
def setup_driver():    
    # Configurações para maximizar a janela
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Função para extrair total de citações e h-index no Google Scholar
def get_scholar_data(driver, scholar_url):
    driver.get(scholar_url)
    time.sleep(2)
    
    try:        
        total_citations = driver.find_element(By.XPATH, '/html/body/div/div[12]/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[2]').text
        h_index = driver.find_element(By.XPATH, '/html/body/div/div[12]/div[2]/div/div[1]/div[1]/table/tbody/tr[2]/td[2]').text
        return total_citations, h_index
    except Exception as e:
        print(f"Erro ao recuperar dados do Google Scholar: {str(e)}")
        return None, None

# Função para extrair total de citações e h-index no Scopus
def get_scopus_data(driver, scopus_url):
    driver.get(scopus_url)
    time.sleep(3)
    
    try:        
        total_citations = driver.find_element(By.XPATH, '//*[@id="scopus-author-profile-page-control-microui__general-information-content"]/div[3]/section/div/div[1]/div/div/div/div[1]/span').text
        h_index = driver.find_element(By.XPATH, '//*[@id="scopus-author-profile-page-control-microui__general-information-content"]/div[3]/section/div/div[3]/div/div/div/div[1]/span').text
        return total_citations, h_index
    except Exception as e:
        print(f"Erro ao recuperar dados do Scopus: {str(e)}")
        return None, None

# Função principal para processar cada professor e extrair os dados de Scholar e Scopus
def process_professor_data(driver, row):
    scholar_url = row['SCHOLAR']
    scopus_url = row['SCOPUS']
    name = row['NOME']
    
    # Extraindo dados do Google Scholar
    scholar_citations, scholar_h_index = get_scholar_data(driver, scholar_url)
    
    # Extraindo dados do Scopus
    scopus_citations, scopus_h_index = get_scopus_data(driver, scopus_url)
    
    return {
        'name': name,
        'scholar_citations': scholar_citations,
        'scholar_h_index': scholar_h_index,
        'scopus_citations': scopus_citations,
        'scopus_h_index': scopus_h_index
    }

# Função principal para ler o arquivo Excel, iterar sobre os dados e salvar em CSV
def scrape_professors_data(excel_path, output_csv):
    driver = setup_driver()
    data = pd.read_excel(excel_path)
    
    results = []
    
    try:
        # Usando tqdm para exibir a barra de progresso
        for _, row in tqdm(data.iterrows(), total=data.shape[0], desc="Processando professores"):
            result = process_professor_data(driver, row)
            results.append(result)
    finally:
        driver.quit()
    
    # Escrevendo os resultados em um arquivo CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nome', 'Total Scholar', 'H-Index Scholar', 'Total Scopus', 'H-Index Scopus'])
        
        for result in results:
            writer.writerow([
                result['name'],
                result['scholar_citations'],
                result['scholar_h_index'],
                result['scopus_citations'],
                result['scopus_h_index']
            ])

# Caminho para o arquivo Excel de entrada e o CSV de saída
excel_path = 'corpo_docente.xlsx'
output_csv = 'resultados_professores.csv'

# Executando a função principal
scrape_professors_data(excel_path, output_csv)
