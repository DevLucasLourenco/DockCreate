from tkinter import filedialog
import pandas as pd
import os
import subprocess
from PIL import Image, ImageTk
from win10toast_click import ToastNotifier 
import docx
import tkinter as tk
import logging
import locale
from pathlib import Path
from tkinter import messagebox

#criando pasta para o armazenamento de events, os documentos que serão gerados área de backup e basciconfig do logging
logging.basicConfig(level=logging.INFO, filename=Path('EventFolder/event.log') , format='%(asctime)s - %(levelname)s - %(message)s')



class DockCreate():
    """
    As seguintes EXPRESSÕES devem compor o documento original, o qual será trabalhado 
    para alterar os dados por seus respectivos dados designados na interface gráfica
    
    [NOME]\n
    [RG]\n
    [CPF]\n
    [CTPS_NUMERO]\n
    [CTPS_SERIE]\n
    [ENDEREÇO]\n
    [CEP]\n
    [DATA_ADMISSIONAL]\n
    [FUNCAO]\n
    [SALARIO]\n
    """
    
    def __init__(self):
        self.dados_funcionarios = None
        self.nome = None
        self.cpf = None
        self.rg = None
        self.ctps_numero = None
        self.ctps_serie = None
        self.endereco = None
        self.cep = None
        self.salario = None
        self.funcao = None
        self.data_admissional = None
        self.data_admissional_por_extenso = None
        
        self.root = None
        
        self.contador = 1
        
        self.listagem_arquivos = []
        self._nomes_documentos_utilizados = []
        self.dados_validacao = {'Termo de Conhecimento': False, 'Política de Privacidade': False, 
                                'Contrato Indeterminado':False, 'Selecionar Arquivo': False}
        
        logging.info("{:=^50}".format("Software Inicializado"))
        
        
        try:
            self.planilha_df = pd.read_excel(Path('BackupFolder\BD.xlsx'))
            
        except:
            self.planilha_df = pd.DataFrame(columns=['Nome', 'CPF', 'RG','CTPS-Número','CTPS-Série','Endereço','CEP','Salário','Função','Data Admissional','Data Admissional por Extenso'])
            self.planilha_df.to_excel(Path('BackupFolder\BD.xlsx'), index=False)
        
            
        Path('EventFolder').mkdir(exist_ok=True)
        Path('DocumentosCriados').mkdir(exist_ok=True)
        Path('BackupFolder').mkdir(exist_ok=True)
        
        
        self.interface_grafica()


            
    @staticmethod
    def _formatar_rg(item):

        if len(item) == 9:
            item = '{}{}.{}{}{}.{}{}{}-{}'.format(*item)
            
        elif len(item) == 12:
            pass
        
        return item
    

    @staticmethod
    def _formatar_cpf(item):
        if len(item) == 11:
            item = '{}{}{}.{}{}{}.{}{}{}-{}{}'.format(*item)
        
        elif len(item) == 14:
            pass
        
        return item
    
    
    @staticmethod
    def _formatar_funcao(item:str):
        valores_tratados = []
        word_list = item.title().split(' ')
        
        for each in word_list:    
            if len(each) <= 3:
                if each == 'De' or each == 'de':
                    each = each.lower()
                each.upper()
                valores_tratados.append(each)
            else:
                valores_tratados.append(each)
                
        item = ' '.join(valores_tratados)
        
        return item
    
    
    @staticmethod
    def _formatar_cep(item:str):
        if len(item) == 8: 
            item = '{}{}.{}{}{}-{}{}{}'.format(*item)
        else:
            pass
        
        return item    
    
        
    @staticmethod
    def _campo_delete_insert(var, dado):
        var.delete(0, tk.END)
        var.insert(0, dado)
        
        
    
    def _guardar_backup(self, dados):
    
        self.planilha_df = self.planilha_df[['Nome','CPF','RG','CTPS-Número','CTPS-Série', 'Endereço', 'CEP', 'Salário', 'Função', 'Data Admissional', 'Data Admissional por Extenso']]
        self.planilha_df.loc[len(self.planilha_df) + 1] = dados
        self.planilha_df.to_excel(Path('BackupFolder\BD.xlsx'), index=False)
        
    
    
    @staticmethod
    def converter_por_extenso(item:str):
        tratamento = {
            1:'Janeiro',
            2:'Fevereiro',
            3:'Março',
            4:'Abril',
            5:'Maio',
            6:'Junho',
            7:'Julho',
            8:'Agosto',
            9:'Setembro',
            10:'Outubro',
            11:'Novembro',
            12:'Dezembro',
            }
        
        try:
            item_tratado = item.split('/')       
            item_tratado[1] = tratamento[int(item_tratado[1])]
            item_tratado = ' de '.join(item_tratado)
            
            return item_tratado
        
        except Exception:
            pass    
        
    
    # abrir uma janela de menu. Outra classe.
    def abrir_menu(self):     
        
        JanelaMenu(self)


    # Usado para notiicar quando os documentos forem gerados
    def notificacao(self):
        
        def abrir_pasta():
            pasta_especifica = Path('DocumentosCriados')
            subprocess.Popen(f'explorer "{pasta_especifica}"')


        texto = ', '.join(self._nomes_documentos_utilizados)
        
        toaster = ToastNotifier()
        
        toaster.show_toast(
                'Conclusão de Documentos',
                f'Documento(s) {texto} do {self.campo_nome.get()} criado(s)',
                icon_path = None, 
                duration = 5, 
                threaded = True, 
                callback_on_click = abrir_pasta
                )

       
    # Usado para formatar a entrada do valor no campo Salário
    def _formatar_moeda(self, valor:str):
        
        def adaptar_caso_monetario_reverso(valor_str):
            valor_str = valor_str.replace(".", "").replace(",", ".")
            valor_float = float(valor_str[2:])
            return valor_float

        try:
            if 'R$' in valor:
                valor = adaptar_caso_monetario_reverso(valor)
                
            elif valor == '':
                if self.campo_nome == '':
                    messagebox.showinfo('Atenção','Preencha o campo NOME')
                    pass
                return '0'

            elif ',' in valor:
                valor = valor.replace(',','.')
                
            elif '.' in valor:
                pass
            
            else:
                pass
            valor = float(valor)
            
            
            locale.setlocale(locale.LC_MONETARY, '')
            return locale.currency(valor, grouping=True)
        
        except:
            messagebox.showinfo('Atenção','Na guia SALÁRIO, insira somente os valores com números.')
    
    
    
    def salvar_info(self):
        self.nome = self.campo_nome.get().title().strip()
        self.cpf = DockCreate._formatar_cpf(self.campo_cpf.get()).strip()
        self.rg = DockCreate._formatar_rg(self.campo_rg.get()).strip()
        self.ctps_numero = self.campo_ctps_numero.get().strip()
        self.ctps_serie = self.campo_ctps_serie.get().strip()
        self.endereco = self.campo_endereco.get().strip()
        self.cep = DockCreate._formatar_cep(self.campo_cep.get()).strip()
        self.salario = self._formatar_moeda(self.campo_salario.get()).strip()
        self.funcao = DockCreate._formatar_funcao(self.campo_funcao.get()).strip()
        self.data_admissional = self.campo_data_admissional.get().strip()
        
        
        # Inserindo à variável de armazenamento
        self.dados_funcionarios = ';'.join((self.nome, self.cpf, self.rg, self.ctps_numero,self.ctps_serie, 
                                            self.endereco, self.cep, self.salario, self.funcao, self.data_admissional))
        
        
        
        if self.campo_nome.get() == '':
            messagebox.showinfo('Atenção','Preencha os dados corretamente')
            
        else:
            self.campo_nome.delete(0, tk.END)
            self.campo_cpf.delete(0, tk.END)
            self.campo_rg.delete(0, tk.END)
            self.campo_ctps_numero.delete(0, tk.END)
            self.campo_ctps_serie.delete(0, tk.END)
            self.campo_endereco.delete(0, tk.END)
            self.campo_cep.delete(0, tk.END)
            self.campo_salario.delete(0, tk.END)
            self.campo_funcao.delete(0, tk.END)
            self.campo_data_admissional.delete(0, tk.END)
            
            self.dados_funcionarios = {
                                       'Nome':self.nome, 
                                       'CPF':self.cpf, 
                                       'RG':self.rg, 
                                       'CTPS-Número':self.ctps_numero,
                                       'CTPS-Série':self.ctps_serie, 
                                       'Endereço':self.endereco, 
                                       'CEP':self.cep, 
                                       'Salário':self.salario, 
                                       'Função':self.funcao, 
                                       'Data Admissional':self.data_admissional, 
                                       'Data Admissional por Extenso':DockCreate.converter_por_extenso(self.data_admissional)
                                       }
            
            self._guardar_backup(self.dados_funcionarios)
            
            self.contador = 1            
            messagebox.showinfo('Concluído', f'Dados de {self.nome} foram salvos.')
            
            
        ask = messagebox.askyesno('Atenção','Deseja criar os arquivos com os dados atuais?')
        if ask is True:
            print('teste 1')
            
            with open('BackupFolder/DataBackup.txt', 'r', encoding='utf-8') as file:
                dados = file.readlines()
            
            dados = dados[-1]
            dados = dados.split(';')    
            
            
            self.campo_nome.insert(0, dados[0])
            self.campo_cpf.insert(0, dados[1])
            self.campo_rg.insert(0, dados[2])
            self.campo_ctps_numero.insert(0, dados[3])
            self.campo_ctps_serie.insert(0, dados[4])
            self.campo_endereco.insert(0, dados[5])
            self.campo_cep.insert(0, dados[6])
            self.campo_salario.insert(0, dados[7])
            self.campo_funcao.insert(0, dados[8])
            self.campo_data_admissional.insert(0, dados[9])
            
            self.criar_arquivo()


    def info_anterior(self):
                
        try:
            with open('BackupFolder/DataBackup.txt', 'r', encoding='utf-8') as file:
                dados = file.readlines()
            
            dados_separados = dados[-self.contador]
            dados_tratados = dados_separados.split(';')
            logging.info(f'Dados anteriores puxados: {dados_tratados}')
        
            DockCreate._campo_delete_insert(self.campo_nome, dados_tratados[0])
            DockCreate._campo_delete_insert(self.campo_cpf, dados_tratados[1])
            DockCreate._campo_delete_insert(self.campo_rg, dados_tratados[2])
            DockCreate._campo_delete_insert(self.campo_ctps_numero, dados_tratados[3])
            DockCreate._campo_delete_insert(self.campo_ctps_serie, dados_tratados[4])
            DockCreate._campo_delete_insert(self.campo_endereco, dados_tratados[5])
            DockCreate._campo_delete_insert(self.campo_cep, dados_tratados[6])
            DockCreate._campo_delete_insert(self.campo_salario, dados_tratados[7])
            DockCreate._campo_delete_insert(self.campo_funcao, dados_tratados[8])
            DockCreate._campo_delete_insert(self.campo_data_admissional, dados_tratados[9])
            
            self.contador += 1
            print(self.contador)
        except:
            messagebox.showinfo('Atenção', f'Os últimos dados registrados foram alcançados.')
            
    
    def info_posterior(self):
        try:
            with open('BackupFolder/DataBackup.txt', 'r', encoding='utf-8') as file:
                dados = file.readlines()
            
            self.contador -= 1
            if self.contador <= 0:
                self.contador == 0
                messagebox.showinfo('Atenção', f'Não é possível avançar para obter mais dados.')
            
            else:
                print(self.contador)
                dados_separados = dados[-self.contador]
                dados_tratados = dados_separados.split(';')
                logging.info(f'Dados anteriores puxados: {dados_tratados}')
            
                DockCreate._campo_delete_insert(self.campo_nome, dados_tratados[0])
                DockCreate._campo_delete_insert(self.campo_cpf, dados_tratados[1])
                DockCreate._campo_delete_insert(self.campo_rg, dados_tratados[2])
                DockCreate._campo_delete_insert(self.campo_ctps_numero, dados_tratados[3])
                DockCreate._campo_delete_insert(self.campo_ctps_serie, dados_tratados[4])
                DockCreate._campo_delete_insert(self.campo_endereco, dados_tratados[5])
                DockCreate._campo_delete_insert(self.campo_cep, dados_tratados[6])
                DockCreate._campo_delete_insert(self.campo_salario, dados_tratados[7])
                DockCreate._campo_delete_insert(self.campo_funcao, dados_tratados[8])
                DockCreate._campo_delete_insert(self.campo_data_admissional, dados_tratados[9])
            
            
        except:
            messagebox.showinfo('Atenção', f'Não é possível avançar para obter mais dados.')
        
    
    # para limpar as caixas de texto
    def limpar_caixa_entrada(self):
        
        self.campo_nome.delete(0,tk.END)
        self.campo_cpf.delete(0,tk.END)
        self.campo_rg.delete(0,tk.END)
        self.campo_ctps_numero.delete(0,tk.END)
        self.campo_ctps_serie.delete(0,tk.END)
        self.campo_endereco.delete(0,tk.END)
        self.campo_cep.delete(0,tk.END)
        self.campo_salario.delete(0,tk.END)
        self.campo_funcao.delete(0,tk.END)
        self.campo_data_admissional.delete(0,tk.END)
        
        logging.info('Todas as caixas de entrada foram limpas.')
        self.contador = 1
        

    # usado para verificar se o botão foi pressionado, e após isso, aplicar as validações aos mesmos
    def check_arquivo1(self):
        if self.var_arquivo1.get() == 1:
            logging.info(f"{list(self.dados_validacao.keys())[0]} selecionado")
            self.dados_validacao['Termo de Conhecimento'] = True
        else:
            logging.info(f"{list(self.dados_validacao.keys())[0]} não selecionado")
            self.dados_validacao['Termo de Conhecimento'] = False
    
    
    def check_arquivo2(self):
        if self.var_arquivo2.get() == 1:
            logging.info(f"{list(self.dados_validacao.keys())[1]} selecionado")
            self.dados_validacao['Política de Privacidade'] = True
        else:
            logging.info(f"{list(self.dados_validacao.keys())[1]} não selecionado")
            self.dados_validacao['Política de Privacidade'] = False
   
   
    def check_arquivo3(self):
        if self.var_arquivo3.get() == 1:
            logging.info(f"{list(self.dados_validacao.keys())[2]} selecionado")
            self.dados_validacao['Contrato Indeterminado'] = True
        else:
            logging.info(f"{list(self.dados_validacao.keys())[2]} não selecionado")
            self.dados_validacao['Contrato Indeterminado'] = False
    
    
    def check_arquivo4(self):
        logging.info(f'Evento "{list(self.dados_validacao.keys())[3]}" selecionado')
        caminho_arquivo_selecionado = filedialog.askopenfilename(title='Selecionar Arquivo', initialdir=Path('ArquivosDocumentos'))
        
        logging.info(f"Caminho: {caminho_arquivo_selecionado}")

            
            
    def interface_grafica(self):
        
        # criar uma janela principal
        self.root = tk.Tk()

        # definir o tamanho e a posição da janela principal
        self.root.geometry("800x600+350+100")

        # iconbitmap
        self.root.iconbitmap('utilidades/icon.jpg')
        
        # adicionar o cabeçalho
        header_frame = tk.Frame(self.root, bg="#1F2E46", padx=20, pady=10)
        header_frame.pack(side="top", fill="x")
        

        # adicionar o logotipo da empresa
        logo = ImageTk.PhotoImage(Image.open("utilidades/icon.jpg").resize((100, 100)))
        logo_label = tk.Label(header_frame, image=logo, bg="#1F2E46")
        logo_label.pack(side="left")

        # adicionar o nome da empresa
        nome_empresa = tk.Label(header_frame, text="Dock Brasil - Engenharia e Serviços S.A.", font=("Arial", 24), bg="#1F2E46", fg="white", padx=10, pady=10)
        nome_empresa.pack(side="left")


        ###### Frames
        # adicionar o quadro para os checkboxes
        checkbox_frame = tk.Frame(self.root, padx=0, pady=0, )
        checkbox_frame.pack(side="top")

        # adicionar o quadro para os botões
        buttons_frame = tk.Frame(self.root, padx=20, pady=0)
        buttons_frame.pack(side="right")

        # adicionar as entradas de texto
        fields_frame = tk.Frame(self.root, padx=20, pady=0)
        fields_frame.pack(side="left", fill="both")



        # adicionar os textos e suas entradas de dados
        rotulo_nome = tk.Label(fields_frame, text="Nome:")
        rotulo_nome.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.campo_nome = tk.Entry(fields_frame)
        self.campo_nome.grid(row=0, column=1, padx=10, pady=10)

        rotulo_cpf = tk.Label(fields_frame, text="CPF:")
        rotulo_cpf.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.campo_cpf = tk.Entry(fields_frame)
        self.campo_cpf.grid(row=1, column=1, padx=10, pady=10)

        rotulo_rg = tk.Label(fields_frame, text="RG:")
        rotulo_rg.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.campo_rg = tk.Entry(fields_frame)
        self.campo_rg.grid(row=2, column=1, padx=10, pady=10)

        rotulo_ctps_numero = tk.Label(fields_frame, text="CTPS-Número:")
        rotulo_ctps_numero.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.campo_ctps_numero = tk.Entry(fields_frame)
        self.campo_ctps_numero.grid(row=3, column=1, padx=10, pady=10)

        rotulo_ctps_serie = tk.Label(fields_frame, text="CTPS-Série:")
        rotulo_ctps_serie.grid(row=4, column=0, sticky="w", padx=10, pady=10)
        self.campo_ctps_serie = tk.Entry(fields_frame)
        self.campo_ctps_serie.grid(row=4, column=1, padx=10, pady=10)

        rotulo_endereco = tk.Label(fields_frame, text="Endereço:")
        rotulo_endereco.grid(row=5, column=0, sticky="w", padx=10, pady=10)
        self.campo_endereco = tk.Entry(fields_frame)
        self.campo_endereco.grid(row=5, column=1, padx=10, pady=10)

        rotulo_cep = tk.Label(fields_frame, text="CEP:")
        rotulo_cep.grid(row=6, column=0, sticky="w", padx=10, pady=10)
        self.campo_cep = tk.Entry(fields_frame)
        self.campo_cep.grid(row=6, column=1, padx=10, pady=10)

        rotulo_salario = tk.Label(fields_frame, text="Salário:")
        rotulo_salario.grid(row=7, column=0, sticky="w", padx=10, pady=10)
        self.campo_salario = tk.Entry(fields_frame)
        self.campo_salario.grid(row=7, column=1, padx=10, pady=10)

        rotulo_funcao = tk.Label(fields_frame, text="Função:")
        rotulo_funcao.grid(row=8, column=0, sticky="w", padx=10, pady=10)
        self.campo_funcao = tk.Entry(fields_frame)
        self.campo_funcao.grid(row=8, column=1, padx=10, pady=10)

        rotulo_data_admissional = tk.Label(fields_frame, text="Data Admissional:")
        rotulo_data_admissional.grid(row=9, column=0, sticky="w", padx=10, pady=10)
        self.campo_data_admissional = tk.Entry(fields_frame)
        self.campo_data_admissional.grid(row=9, column=1, padx=10, pady=10)



        # adicionar os botões
        dados_anteriores_button = tk.Button(buttons_frame, text="Dados Anteriores", height=3, width=20, 
                                                    bg='#1F2E46', fg='white', command=self.info_anterior)
        dados_anteriores_button.pack(side="top", padx=10, pady=10)
        
        dados_posteriores_button = tk.Button(buttons_frame, text="Dados Posteriores", height=3, width=20, 
                                                    bg='#1F2E46', fg='white', command=self.info_posterior)
        dados_posteriores_button.pack(side="top", padx=10, pady=10)

        limpar_button = tk.Button(buttons_frame, text="Limpar", height=3, width=20, 
                                                    bg='#1F2E46', fg='white', command=self.limpar_caixa_entrada)
        limpar_button.pack(side="top", padx=10, pady=10)

        salvar_arquivo_button = tk.Button(buttons_frame, text="Salvar Dados", height=3, width=20, 
                                                    bg='#1F2E46', fg='white', command=self.salvar_info)
        salvar_arquivo_button.pack(side="top", padx=10, pady=10)

        criar_arquivo_button = tk.Button(buttons_frame, text="Criar Arquivo", height=3, width=20, 
                                                    bg='#1F2E46', fg='white', command=self.criar_arquivo)
        criar_arquivo_button.pack(side="top", padx=10, pady=10)

        
        
        #Botão para abrir uma nova janela
        imagem_menu = Image.open("utilidades/menu_icon.png")
        image_resized = imagem_menu.resize((40, 40))
        imagem_menu = ImageTk.PhotoImage(image_resized)

        button_abrir_menu = tk.Button(checkbox_frame, image=imagem_menu, bd=0, height=40, width=40 , command=self.abrir_menu)
        button_abrir_menu.pack(side='left', padx=20, pady = 5)


        # usado para verificar se o botão foi selecionado ou não, juntamente à função "check_arquivo[x]()"
        self.var_arquivo1 = tk.IntVar()
        self.var_arquivo2 = tk.IntVar()
        self.var_arquivo3 = tk.IntVar()
        
        # adicionar os checkboxes
        bg_checkbox_field = '#708090'
        
        termo_conhecimento_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[0],variable=self.var_arquivo1,
                                                        command=self.check_arquivo1, height=3, width=20,bg=bg_checkbox_field, indicatoron=False)
        termo_conhecimento_checkbox.pack(side='left', padx=0, pady=5)


        politica_privacidade_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[1],variable=self.var_arquivo2,
                                                        command=self.check_arquivo2, height=3, width=20,bg=bg_checkbox_field, indicatoron=False)
        politica_privacidade_checkbox.pack(side='left', padx=0, pady=5)


        contrato_indeterminado_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[2],variable=self.var_arquivo3,
                                                        command=self.check_arquivo3, height=3, width=20,bg=bg_checkbox_field, indicatoron=False)
        contrato_indeterminado_checkbox.pack(side='left', padx=0, pady=5)

        
        selecionar_arquivo_checkbox = tk.Button(checkbox_frame, text=list(self.dados_validacao.keys())[3], height=3, width=20, 
                                                    bg=bg_checkbox_field, command=self.check_arquivo4)
        selecionar_arquivo_checkbox.pack(side='left', padx=0, pady=5)



        # iniciar o loop de eventos do tkinter
        self.root.mainloop()


      
    def criar_arquivo(self):
        
        substituicoes = {
                        '[NOME]' : self.campo_nome.get().strip(),
                        '[RG]' : self.campo_rg.get().strip(),
                        '[CPF]' : self.campo_cpf.get().strip(),
                        '[CTPS_NUMERO]' : self.campo_ctps_numero.get().strip(),
                        '[CTPS_SERIE]' : self.campo_ctps_serie.get().strip(),
                        '[ENDEREÇO]' : self.campo_endereco.get().strip(),
                        '[CEP]' : self.campo_cep.get().strip(),
                        '[DATA_ADMISSIONAL]' : self.campo_data_admissional.get().strip(),
                        '[FUNCAO]' : self.campo_funcao.get().strip(),
                        '[SALARIO]' : self.campo_salario.get().strip(),
                        }
        

        arquivos = self._encontrar_arquivo()
        
        for i, arquivo in enumerate(arquivos.values()):
            print(arquivo)
            self._editar_arquivo(arquivo, substituicoes, i)
            
        logging.info("Documento(s) criado(s)")
        
        self.notificacao()
        
        self.listagem_arquivos.clear()
        self._nomes_documentos_utilizados.clear()
            

        
    def _encontrar_arquivo(self):
        
        # Verifica se algum documento foi selecionado.
        if not True in self.dados_validacao.values():
            messagebox.showinfo('Alerta','Nenhum documento foi selecionado.')
            
        else:
            pass
        
        
        #verifica os documentos que foram selecionados e o(s) coloca(m) em uma lista para serem tratados.
        for i, item in enumerate(self.dados_validacao.items()):
            key, value = item
            
            if value:
                caminho = Path('ArquivosDocumentos')
                lista_arquivos = caminho.iterdir()
                
                for each in lista_arquivos:
                    
                    if key in str(each):
                        arquivo_base = Path(str(each))
                        arquivo = docx.Document(arquivo_base)
                        self.listagem_arquivos.append(arquivo)
                        self._nomes_documentos_utilizados.append(key)
                        
                        dicionario_arquivos = dict(zip(self._nomes_documentos_utilizados, self.listagem_arquivos))
                        logging.info('Arquivo(s) Definido(s)')
            else:
                pass
        
        return dicionario_arquivos
            
            
    def _editar_arquivo(self, arquivo, substituicao, indice):
        for para in arquivo.paragraphs:
            for key in substituicao:
                # substituir a palavra-chave com seu valor correspondente
                if key in para.text:
                    para.text = para.text.replace(key, substituicao[key])
                    
        arquivo.save(f'DocumentosCriados/{self.campo_nome.get()} {self._nomes_documentos_utilizados[indice]}.docx') 
        logging.info(f'{self._nomes_documentos_utilizados[indice]} Criado')
        
        

class JanelaMenu():
    
    def __init__(self, objeto):
        self.objeto = objeto
        # PEGAR ESTA REFERÊNCIA E FAZER DAQUI EM DIANTE
                
        self.root_janela_menu = None
        self.lista_dados_funcionarios = {}
        
        self.inicializar()
        
        self.objeto.limpar_caixa_entrada()
        

    def _procurar_dados(self):
                    
        for item in self.objeto.planilha_df.index:
            # nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao = item
            # self.lista_dados_funcionarios.update({JanelaMenu._tratar_lista([nome, cpf, funcao, salario, data_admissao]): [nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao]})
            # self.lista_dados_funcionarios.update()
            print(self.objeto.planilha_df[item])
            
            
            pass
            
        


    @staticmethod
    def _tratar_lista(lista):
        dados_tratados = ' - '.join(lista)
        
        return dados_tratados
        
        
    
    @staticmethod
    def _deletar_campo_entrada(var):
            var.delete(0, tk.END)
            
        
        
    def _ao_selecionar(self, event):
        selection = event.widget.curselection()
        self.item = event.widget.get(selection[0])
        
        dados = self.lista_dados_funcionarios[self.item]
        logging.info(f'Selecionado através do Menu: {dados}')
        
        
    def apagar_dados(self):
        
        #apagar linha do BD
        map(JanelaMenu._deletar_campo_entrada(),  'lista aqui' )
        
        print('aa')
        pass
        
    
    def inicializar(self):
        # criar uma nova janela
        self.root_janela_menu = tk.Toplevel(self.objeto.root)
        self.root_janela_menu.geometry("600x550+650+150")
        self.root_janela_menu.title("Menu")

        header_frame = tk.Frame(self.root_janela_menu, bg="#1F2E46", padx=20, pady=10)
        header_frame.pack(side="top", fill="x")
        
        # rótulo na nova janela
        label = tk.Label(header_frame, text="Menu", font=("Arial", 24), bg="#1F2E46", fg="white", padx=10, pady=5)
        label.pack(pady=0)
        
        frame_exclusao = tk.Frame(self.root_janela_menu, padx=0, pady=5)
        frame_exclusao.pack(side="top")
              
        
        imagem_excluir = Image.open("utilidades/excluir_icon.png")
        image_resized = imagem_excluir.resize((20, 20))
        imagem_excluir = ImageTk.PhotoImage(image_resized)

        delete_button = tk.Button(frame_exclusao, image=imagem_excluir, highlightthickness=0, bd=0, command=self.apagar_dados)
        delete_button.pack(side='top', padx=0, pady=0)
      

        options_frame = tk.Frame(self.root_janela_menu)
        options_frame.pack(side="left", padx=10, pady=20)


        options_label = tk.Label(options_frame, text="Colaboradores:")
        options_label.pack(side="top")


        options_listbox = tk.Listbox(options_frame, height=50, width=110)
        options_listbox.pack(side="left")


        options_scrollbar = tk.Scrollbar(options_frame, orient="vertical")
        options_scrollbar.config(command=options_listbox.yview)
        options_scrollbar.pack(side="right", fill="y")


        options_listbox.config(yscrollcommand=options_scrollbar.set)
        options_listbox.bind("<<ListboxSelect>>", self._ao_selecionar)


        self._procurar_dados()
        for option in self.lista_dados_funcionarios.keys():
            options_listbox.insert("end", option)

        self.root_janela_menu.mainloop()



class JanelaSelecionarArquivo():

    def __init__(self):
        pass
    
    
    
    
    
class JanelaBuscaCEP():
    
    def __init__():
        pass
    
    
    
class PreenchimentoInfoFuncionario():
    
    def __init__():
        pass
    

    
    
    
if __name__ == "__main__":
    DockCreate()