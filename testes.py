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