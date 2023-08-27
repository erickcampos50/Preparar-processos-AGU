#%%
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
def safe_filename(filename):
    valid_chars = set("-_.()[] %s%s" % (string.ascii_letters, string.digits))
    return ''.join(c for c in filename if c in valid_chars)

def convert_html_to_pdf(html_path, pdf_path):
    # st.write(f"Convertendo {os.path.basename(html_path)} para PDF...")
    try:
        pdfkit.from_file(html_path, pdf_path)
    except Exception as e:
        print(f"Erro ao converter {html_path} para PDF. Erro: {e}")

def extract_and_process_files(zip_path, output_folder):
    image_exts = {'.jpeg', '.jpg', '.png','.JPEG','.JPG','.PNG'}
    other_exts = {'.DOC', '.DOCX', '.doc', '.docx', '.xls', '.xlsx'}
    
    def process_directory(directory):
        items = os.listdir(directory)

        for item in items:
            current_path = os.path.join(directory, item)
            extension = os.path.splitext(item)[-1]

            if extension in image_exts:
                # st.write(f"Convertendo imagem {os.path.basename(current_path)} para PDF")
                with Image.open(current_path) as image:
                    img_rgb = image.convert('RGB')
                    target_name = safe_filename(item[:22] + "_" + os.path.basename(current_path))
                    target_path_pdf = os.path.join(directory, target_name+'.pdf')
                    img_rgb.save(target_path_pdf)
                os.remove(current_path)

            elif extension in other_exts:
                continue
            
            elif extension == '.zip':
                # st.write(f"Extraindo {os.path.basename(current_path)}...")
                with zipfile.ZipFile(current_path, 'r') as inner_zip:
                    for member in inner_zip.namelist():
                        target_name = safe_filename(item[:22] + "_" + os.path.basename(member))
                        target_path = os.path.join(directory, target_name)
                        with inner_zip.open(member) as source, open(target_path, "wb") as target:
                            target.write(source.read())
                os.remove(current_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    process_directory(output_folder)
    convert_all_html_to_pdf(output_folder)

    # Check for nested zips and process until no new zip files are found
    extensions_to_check = tuple(image_exts) + ('.zip',)
    while any(fname.endswith(extensions_to_check) for fname in os.listdir(output_folder)):
        process_directory(output_folder)
        convert_all_html_to_pdf(output_folder)




def convert_all_html_to_pdf(output_folder):
    for root, _, files in os.walk(output_folder):
        for file in files:
            if file.endswith(".html"):
                html_path = os.path.join(root, file)
                pdf_path = os.path.splitext(html_path)[0] + '.pdf'
                convert_html_to_pdf(html_path, pdf_path)
                os.remove(html_path)

def zip_dir(path, ziph):
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))


def remove_empty_files(output_folder):
    # Listar todos os arquivos no diretório
    items = os.listdir(output_folder)

    for item in items:
        current_path = os.path.join(output_folder, item)
        
        # Verificar se o item é um arquivo e tem tamanho zero
        if os.path.isfile(current_path) and os.path.getsize(current_path) == 0:
            os.remove(current_path)
            # st.write(f"Arquivo {item} removido por ter tamanho zero.")


#%% SEÇÃO MAIN

def main():
    # Inicializar o estado da sessão
    if 'already_processed' not in st.session_state:
        st.session_state.already_processed = False

    if 'output_filenames' not in st.session_state:
        st.session_state.output_filenames = []

    # Defina o título e as informações da página.
    st.title("Conversor de arquivos para envio ao comitê AGU")
    st.write("""
    Esta ferramenta processa arquivos de um ZIP gerado pelo SEI PRO, converte documentos nativos do SEI em PDF e, em seguida, cria um novo ZIP com os arquivos processados.
    """)

    # Permita o upload do arquivo ZIP.
    uploaded_file = st.file_uploader("Escolha um arquivo ZIP", type="zip")

    if uploaded_file is None:
        uploaded_filename = ''
    else:
        uploaded_filename = uploaded_file.name.rsplit('.', 1)[0]  # Extrai o nome sem a extensão

        if uploaded_file.size / (1024 * 1024) > 50 and not st.checkbox("Clique aqui se tiver certeza que o processo deve continuar"):
            st.warning("O arquivo é maior que 50MB. Arquivos muito grandes podem gerar instabilidades no processamento. Deseja continuar?")
            return
        
        # Verifique se o nome do arquivo mudou para redefinir o indicador de processamento.
        if uploaded_filename != st.session_state.get('last_uploaded_filename', ''):
            st.session_state.already_processed = False

        # Salve o nome do arquivo atual no session_state para comparações futuras.
        st.session_state.last_uploaded_filename = uploaded_filename

    # Se um arquivo foi carregado e ainda não foi processado:
    if uploaded_file is not None and not st.session_state.already_processed:
        
 
        
        # Iniciar barra de progresso
        progress_bar = st.progress(0)
        progress_text = st.empty()

        # ...[Todo o processamento que estava anteriormente aqui]

        # Para referência, isso inclui:
        # - Ler e salvar o arquivo temporariamente
        # - Processar o arquivo (extração, conversão, etc.)
        # - Criar o novo arquivo ZIP

        # Criar nome de diretório de saída com o nome do arquivo e a data-hora atual.




        

        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        uploaded_filename = uploaded_file.name.rsplit('.', 1)[0]  # Extrai o nome sem a extensão
        output_folder = f"{uploaded_filename}_{current_datetime}"
        temp_filename = f"temp_{current_datetime}.zip"
        output_filename = f"{output_folder}_processado.zip"
        
        # Crie um diretório temporário para salvar o ZIP carregado.
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Atualize a barra de progresso
        progress_bar.progress(25)
        progress_text.text("25% completo: Arquivo salvo temporariamente.")

        # Extrai e processa o arquivo ZIP.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        extract_and_process_files(temp_filename, output_folder)

        # Atualize a barra de progresso
        progress_bar.progress(75)   
        progress_text.text("75% completo: Arquivos extraídos e processados.")


        remove_empty_files(output_folder)

        # Crie um novo arquivo ZIP.
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zip_dir(output_folder, zipf)

        # Atualize a barra de progresso para 100% e mostre a mensagem de conclusão
        progress_bar.progress(100)
        progress_text.text("100% completo: Tudo concluído!")
        st.markdown("✅ Processamento concluído!")

        # Adicione o arquivo de saída à lista no session_state
        st.session_state.output_filenames.append(output_filename)

        # Limpe os arquivos e diretórios temporários.
        shutil.rmtree(output_folder)
        os.remove(temp_filename)

        # Marque que o processamento foi concluído
        st.session_state.already_processed = True


    # Mostre os botões de download para todos os arquivos processados
    for output_filename in st.session_state.output_filenames:
        with open(output_filename, "rb") as f:
            btn = st.download_button(
                label=f"Baixar {output_filename}",
                data=f.read(),
                file_name=output_filename,
                mime="application/zip"
            )

if __name__ == "__main__":
    main()

# #%%
# #SEÇÃO PARA TESTES SIMPLES
# current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# uploaded_file = "SEI_23071.934529_2023_95.zip"
# output_folder = f"{uploaded_file}_{current_datetime}"
# output_filename = f"{output_folder}_processado.zip"


# # Extrai e processa o arquivo ZIP.
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# extract_and_process_files(uploaded_file, output_folder)

# remove_empty_files(output_folder)

# # Crie um novo arquivo ZIP.
# with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
#     zip_dir(output_folder, zipf)


# # Limpe os arquivos e diretórios temporários.
# shutil.rmtree(output_folder)
# # %%
