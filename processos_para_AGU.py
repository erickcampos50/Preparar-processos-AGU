#%%
import base64
import datetime
import time
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



# ESTA É UMA FUNÇÃO PROVISÓRIA, QUE IRÁ VARRER O DIRETÓRIO RAIZ PARA EXIBIR OS ARQUIVOS. A INTENÇÃO É ENTENDER COMO FUNCIONA A INSTÂNCIA DO STREAMLIT COM RELAÇÃO AOS ARQUIVOS CONVERTIDOS E ATUAR PARA EVITAR QUE O DISCO FIQUE SOBRECARREGADO
def list_files_from_root():
    """Lista todos os arquivos do diretório raiz com tamanho e data de criação."""
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório atual do script.
    files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]
    
    file_details = []
    for file in files:
        file_path = os.path.join(root_dir, file)
        
        # Tamanho do arquivo em bytes
        file_size = os.path.getsize(file_path)
        
        # Data de criação do arquivo
        creation_timestamp = os.path.getctime(file_path)
        creation_date = datetime.datetime.fromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        file_details.append((file, file_size, creation_date))
    
    return file_details




def delete_old_zip_files():
    """Exclui arquivos ZIP com mais de X horas."""
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório atual do script.
    current_time = time.time()  # Obtém o tempo atual em segundos.
    

    # Lista todos os arquivos ZIP do diretório.
    zip_files = [f for f in os.listdir(root_dir) if f.endswith('.zip') and os.path.isfile(os.path.join(root_dir, f))]

    deleted_files = []  # Lista de arquivos excluídos.

    # Verifica cada arquivo ZIP.
    for file in zip_files:
        file_path = os.path.join(root_dir, file)
        file_creation_time = os.path.getctime(file_path)  # Obtém o tempo de criação do arquivo em segundos.

        
        if current_time - file_creation_time > 43200:
            os.remove(file_path)  # Remove o arquivo.
            deleted_files.append(file)  # Adiciona o nome do arquivo à lista de arquivos excluídos.

    return deleted_files


#%% SEÇÃO MAIN

def main():
    # Inicializar o estado da sessão
    if 'already_processed' not in st.session_state:
        st.session_state.already_processed = False

    if 'output_filenames' not in st.session_state:
        st.session_state.output_filenames = []

    # Defina o título e as informações da página.
    st.title("Conversor de arquivos para envio ao comitê AGU")
    st.markdown("""
                Esta ferramenta visa facilitar o atendimento aos procedimentos determinados pela AGU para envio de documentação para análise, realizando o processamento, extração, conversão e ajuste de nomes de todos os arquivos de forma automatizada.

                Para utilizá-la é preciso gerar gerar uma versão ZIP do seu processo *SEI* a partir do excelente [**SEI PRO**](https://sei-pro.github.io/sei-pro/) e inseri-la aqui. Acesse o tutorial abaixo para mais instruções.
    """)

    with st.expander("Depuração (apenas para testes da ferramenta)"):
        # Defina o título e as informações da página.
        st.write("Clique no botão abaixo para listar todos os arquivos do diretório raiz:")
        # Botão para listar arquivos.
        if st.button("Listar Arquivos"):
            file_details = list_files_from_root()
            if file_details:
                st.write("Detalhes dos arquivos no diretório raiz:")
                for file_info in file_details:
                    st.write(f"Nome: {file_info[0]}, Tamanho: {file_info[1]} bytes, Data de criação: {file_info[2]}")
            else:
                st.write("Nenhum arquivo encontrado no diretório raiz.")
        if st.button("Excluir Arquivos ZIP Antigos"):
            deleted_files = delete_old_zip_files()
            if deleted_files:
                st.write("Arquivos ZIP excluídos:")
                for file in deleted_files:
                    st.write(file)
            else:
                st.write("Nenhum arquivo ZIP antigo encontrado para exclusão.")



    with st.expander("Ver tutorial completo"):
        st.markdown("""
            

        # Tutorial: Conversor de processos SEI->AGU

        Este tutorial guiará você através do processo de conversão de arquivos do SEI para o padrão AGU utilizando o Conversor de processos SEI->AGU.

        ## Requisitos iniciais
        1. **SEI PRO** - Antes de utilizar o Conversor de processos SEI->AGU, você deve ter instalado e ativo o [SEI PRO](https://sei-pro.github.io/sei-pro/). Este é uma extensão para navegadores que adiciona novas funcionalidades ao SEI convencional e está disponível para Chrome, Firefox, Edge, e outros navegadores baseados em Chromium.

        ## Passo a passo

        ### 1. Ativação e uso do SEI PRO

        1. **Instale** o SEI PRO conforme seu navegador.
        2. **Acesse** o processo SEI de seu interesse.
        3. **Clique** na opção `Gerar Arquivo ZIP`.
        ![Gerar ZIP no Menu](app/static/gerar_zip_menu.png)
            - Caso essa opção não esteja disponível, você pode se guiar pelas seguintes imagens:
                - Passe o mouse sobre o número do processo e clique em **Personalizar Menu**
                ![Personalizar Menu](app/static/personalizar_menu.png)
                - Dentro as opçoes que surgirem procure e ative aquela que diz **Gerar Arquivo ZIP do Processo**
                ![Ativar Menu](app/static/ativar_menu.png)

                - Pronto! Agora você pode gerar um arquivo ZIP contendo todos os arquivos do processo.Após clicar em **Gerar Arquivo ZIP** É possível selecionar quais arquivos irão compor o ZIP.
                

        4. **Selecione** os arquivos desejados na tela que surgirá.
        ![Selecionar Arquivos para ZIP](app/static/selecionar_arquivos_zip.png)
        5. **Clique** em `Gerar`.

        ### 2. Conhecendo o arquivo ZIP

        O arquivo ZIP gerado conterá:
        - Documentos nativos do SEI em formato HTML.
        - Outros arquivos em seus formatos nativos (normalmente PDF, XLS, ou ZIP).
        
        A partir deste ponto já seria possível criar um novo processo com caracteristicas identicas ao processo original (sem perder as assinaturas 
        como ocorre caso você duplique o processo utilizando o SEI PRO). 
                    
        No entanto o comitê da AGU, até a presente data, só permite que sejam incluidos arquivos nos foramtos PDF ou XLS no processo. O que demanda que todos os arquivos compactados estejam descompactados, que os arquivos HTML/JPG/PNG/DOC estejam convertidos em PDF e que todos sejam nomeados de forma legível.

        ### 3. Utilização do Conversor de processos SEI->AGU

        1. **Abra** o Conversor de processos SEI->AGU.
        2. **Faça o upload** do arquivo ZIP gerado anteriormente.
        3. **A ferramenta irá**:
        - Converter documentos nativos do SEI em formato HTML para PDF.
        - Extrair arquivos ZIP (incluindo ZIPs aninhados).
        - Converter todos os outros formatos de arquivo para PDF (exceto XLS e DOC)
        - Renomear todos os arquivos para fácil referência ao processo original.
        - Gerar um novo arquivo ZIP com o resultado final de todas as etapas
                            
        4. **Baixe** o novo arquivo ZIP gerado após a conversão.

        ### 4. Inserção dos novos arquivos no SEI

        1. **Descompacte** o novo arquivo ZIP em um diretório de sua escolha.
        2. **Use** a ferramenta SEI PRO para inserir os arquivos em lote no SEI.
        
        - Se você não sabe como fazer o upload em lote, siga este tutorial: [Inserir arquivos externos em lote usando SEI PRO](https://sei-pro.github.io/sei-pro/pages/UPLOADDOCS.html).
        - Com a funcionalidade de upload em lote, você pode inserir vários arquivos no SEI de uma vez, e até mesmo organizar a ordem dos arquivos na árvore de processos (lembre-se de ativar essa opção).

        ## Limitações

        - O Conversor de processos SEI->AGU **não consegue converter arquivos DOC/DOCX para PDF**. Essa conversão terá que ser feita manualmente.

        Esperamos que este tutorial tenha sido útil!
   
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



# %%
