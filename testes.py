#%%
import processos_para_AGU as agu

import base64
import datetime
import os
import shutil
import string
import zipfile
from PIL import Image
import pdfkit
import streamlit as st



#%%
#SEÇÃO PARA TESTES SIMPLES
current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
uploaded_file = "SEI_23071.934529_2023_95.zip"
output_folder = f"{uploaded_file}_{current_datetime}"
output_filename = f"{output_folder}_processado.zip"


# Extrai e processa o arquivo ZIP.
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

agu.extract_and_process_files(uploaded_file, output_folder)

agu.remove_empty_files(output_folder)

# Crie um novo arquivo ZIP.
with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    agu.zip_dir(output_folder, zipf)


# Limpe os arquivos e diretórios temporários.
shutil.rmtree(output_folder)
# %%

# ESTA É UMA FUNÇÃO PROVISÓRIA, QUE IRÁ VARRER O DIRETÓRIO RAIZ PARA EXIBIR OS ARQUIVOS. A INTENÇÃO É ENTENDER COMO FUNCIONA A INSTÂNCIA DO STREAMLIT COM RELAÇÃO AOS ARQUIVOS CONVERTIDOS E ATUAR PARA EVITAR QUE O DISCO FIQUE SOBRECARREGADO
# def list_files_from_root():
#     """Lista todos os arquivos do diretório raiz com tamanho e data de criação."""
#     root_dir = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório atual do script.
#     files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]
    
#     file_details = []
#     for file in files:
#         file_path = os.path.join(root_dir, file)
        
#         # Tamanho do arquivo em bytes
#         file_size = os.path.getsize(file_path)
        
#         # Data de criação do arquivo
#         creation_timestamp = os.path.getctime(file_path)
#         creation_date = datetime.datetime.fromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
#         file_details.append((file, file_size, creation_date))
    
#     return file_details



    # with st.expander("Depuração (apenas para testes da ferramenta)"):
    #     # Defina o título e as informações da página.
    #     st.write("Clique no botão abaixo para listar todos os arquivos do diretório raiz:")
    #     # Botão para listar arquivos.
    #     if st.button("Listar Arquivos"):
    #         file_details = list_files_from_root()
    #         if file_details:
    #             st.write("Detalhes dos arquivos no diretório raiz:")
    #             for file_info in file_details:
    #                 st.write(f"Nome: {file_info[0]}, Tamanho: {file_info[1]} bytes, Data de criação: {file_info[2]}")
    #         else:
    #             st.write("Nenhum arquivo encontrado no diretório raiz.")
    #     if st.button("Excluir Arquivos ZIP Antigos"):
    #         deleted_files = delete_old_zip_files()
    #         if deleted_files:
    #             st.write("Arquivos ZIP excluídos:")
    #             for file in deleted_files:
    #                 st.write(file)
    #         else:
    #             st.write("Nenhum arquivo ZIP antigo encontrado para exclusão.")

