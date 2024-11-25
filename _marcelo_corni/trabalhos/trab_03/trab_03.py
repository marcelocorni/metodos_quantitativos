import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm  # Importa a biblioteca tqdm para a barra de progresso

def get_latest_downloaded_file(download_path):
    files = os.listdir(download_path)
    paths = [os.path.join(download_path, basename) for basename in files if basename.startswith("export-transaction-list")]
    return max(paths, key=os.path.getctime)

def download_csv(driver, block_number, page_number, download_path):
    url = f"https://etherscan.io/txs?block={block_number}&ps=100&p={page_number}"
    driver.get(url)
    
    try:
        # Localizar o botão de download pelo ID e clicar nele
        download_button = driver.find_element(By.ID, 'btnExportQuickTransactionListCSV')
        download_button.click()
        
        # Esperar um pouco para o download ser concluído
        time.sleep(2)
        
        # Encontrar o arquivo mais recente na pasta Downloads
        latest_file = get_latest_downloaded_file(download_path)
        
        # Renomear e mover o arquivo baixado
        new_filename = f"{block_number}_{page_number}.csv"
        new_filepath = os.path.join(os.getcwd(), new_filename)
        shutil.move(latest_file, new_filepath)
        print(f"Downloaded and moved {new_filename}")
        return True
    except Exception as e:
        # print(f"Failed to download for block {block_number}, page {page_number}: {str(e)}")
        return False

def get_last_downloaded_block(target_dir):
    files = os.listdir(target_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    
    if not csv_files:
        return None
    
    # Extrair números dos blocos dos nomes dos arquivos
    block_numbers = [int(f.split('_')[0]) for f in csv_files]
    return max(block_numbers)

def scrape_block_transactions(target_dir, start_block, end_block, num_blocks, download_path):
    if num_blocks != -1:
        # Caso num_blocks esteja definido, ignorar start_block e end_block
        last_downloaded_block = get_last_downloaded_block(target_dir)
        if last_downloaded_block is not None:
            start_block = last_downloaded_block + 1
        end_block = start_block + num_blocks - 1
    elif start_block != -1 and end_block != -1:
        # Se num_blocks for -1 e os blocos de início e término estiverem definidos, usar esses valores
        pass
    else:
        raise ValueError("Invalid arguments: You must provide either a valid num_blocks or both start_block and end_block.")

    total_blocks = end_block - start_block + 1

    # Configurar o WebDriver (assumindo que o ChromeDriver está no PATH)
    driver = webdriver.Chrome()
    
    try:
        # Usando tqdm para criar uma barra de progresso
        with tqdm(total=total_blocks, desc="Downloading blocks") as pbar:
            for block_number in range(start_block, end_block + 1):
                page_number = 1
                while True:
                    success = download_csv(driver, block_number, page_number, download_path)
                    if not success:
                        break
                    page_number += 1
                    time.sleep(1)  # Pausa para evitar sobrecarregar o servidor
                
                # Atualizar a barra de progresso
                pbar.update(1)
                
                # print(f"Completed block {block_number}")
    finally:
        driver.quit()

# Caminho da pasta de destino onde os arquivos CSV estão sendo salvos
target_dir = os.path.join(os.getcwd(), '')

# Caminho da pasta de downloads do usuário corrente
download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

# Defina os blocos de início e término ou o número de blocos a serem baixados
start_block = -1  # Defina um valor válido se necessário
end_block = -1    # Defina um valor válido se necessário
num_blocks = 1000  # Defina como -1 se quiser usar start_block e end_block

scrape_block_transactions(target_dir, start_block, end_block, num_blocks, download_path)