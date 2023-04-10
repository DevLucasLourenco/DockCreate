
import time
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
        
        self.root = None
        
        self.contador = 1
        
        self.listagem_arquivos = []
        self._nomes_documentos_utilizados = []
        self.dados_validacao = {'Termo de Conhecimento': False, 'Política de Privacidade': False, 
                                'Contrato Indeterminado':False, 'Contrato Intermitente': False}
        
        logging.info("{:=^50}".format("Software Inicializado"))
        
        

        Path('EventFolder').mkdir(exist_ok=True)
        Path('DocumentosCriados').mkdir(exist_ok=True)
        Path('BackupFolder').mkdir(exist_ok=True)
        
        
        self.interface_grafica()
        
    
    @staticmethod
    def _guardar_backup(dados):

        try:
            with open(Path('BackupFolder/DataBackup.txt'), 'r', encoding='utf-8') as file:
                arquivo_preenchido = file.read()
            
            with open(Path('BackupFolder/DataBackup.txt'), 'w', encoding='utf-8') as file:
                file.write(arquivo_preenchido + '\n')
                file.write(dados)
                
        except Exception:
            with open(Path('BackupFolder/DataBackup.txt'), 'w', encoding='utf-8') as file:
                file.write(dados)
                
            
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
    
    
    def abrir_menu(self):     
        
        janela2 = JanelaSecundaria(self.root, self.campo_nome, self.campo_cpf, self.campo_rg, self.campo_ctps_numero, self.campo_ctps_serie, 
                                    self.campo_endereco, self.campo_cep, self.campo_salario, self.campo_funcao, self.campo_data_admissional)


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
        self.cpf = DockCreate._formatar_cpf(self.campo_cpf.get())
        self.rg = DockCreate._formatar_rg(self.campo_rg.get())
        self.ctps_numero = self.campo_ctps_numero.get()
        self.ctps_serie = self.campo_ctps_serie.get()
        self.endereco = self.campo_endereco.get().strip()
        self.cep = DockCreate._formatar_cep(self.campo_cep.get())
        self.salario = self._formatar_moeda(self.campo_salario.get())
        self.funcao = DockCreate._formatar_funcao(self.campo_funcao.get())
        self.data_admissional = self.campo_data_admissional.get()
        
        
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
            
            DockCreate._guardar_backup(self.dados_funcionarios)
            
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
        if self.var_arquivo4.get() == 1:
            logging.info(f"{list(self.dados_validacao.keys())[3]} selecionado")
            self.dados_validacao['Contrato Intermitente'] = True
        else:
            logging.info(f"{list(self.dados_validacao.keys())[3]} não selecionado")
            self.dados_validacao['Contrato Intermitente'] = False
            

    
    def interface_grafica(self):
        
        # criar uma janela principal
        self.root = tk.Tk()


        # definir o tamanho e a posição da janela principal
        self.root.geometry("800x600+350+100")

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
        fields_frame.pack(side="left", fill="both", expand=True)



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
        self.var_arquivo4 = tk.IntVar()
        
        # adicionar os checkboxes
        termo_conhecimento_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[0],variable=self.var_arquivo1,
                                                        command=self.check_arquivo1, height=3, width=20,bg='#708090' , indicatoron=False)
        termo_conhecimento_checkbox.pack(side='left', padx=0, pady=5)


        politica_privacidade_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[1],variable=self.var_arquivo2,
                                                        command=self.check_arquivo2, height=3, width=20,bg='#708090' , indicatoron=False)
        politica_privacidade_checkbox.pack(side='left', padx=0, pady=5)


        contrato_indeterminado_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[2],variable=self.var_arquivo3,
                                                        command=self.check_arquivo3, height=3, width=20,bg='#708090' , indicatoron=False)
        contrato_indeterminado_checkbox.pack(side='left', padx=0, pady=5)


        contrato_intermitente_checkbox = tk.Checkbutton(checkbox_frame, text=list(self.dados_validacao.keys())[3],variable=self.var_arquivo4,
                                                        command=self.check_arquivo4, height=3, width=20,bg='#708090' , indicatoron=False)
        contrato_intermitente_checkbox.pack(side='left', padx=0, pady=5)



        # iniciar o loop de eventos do tkinter
        self.root.mainloop()


   
   ########################################################################################################################################################
   
    def criar_arquivo(self):
        
        substituicoes = {
                        '[NOME]' : self.campo_nome.get(),
                        '[RG]' : self.campo_rg.get(),
                        '[CPF]' : self.campo_cpf.get(),
                        '[CTPS_NUMERO]' : self.campo_ctps_numero.get(),
                        '[CTPS_SERIE]' : self.campo_ctps_serie.get(),
                        '[ENDEREÇO]' : self.campo_endereco.get(),
                        '[CEP]' : self.campo_cep.get(),
                        '[DATA_ADMISSIONAL]' : self.campo_data_admissional.get(),
                        '[FUNCAO]' : self.campo_funcao.get(),
                        '[SALARIO]' : self.campo_salario.get(),
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
        
################################################



class JanelaSecundaria():
    
    def __init__(self, objeto, nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao): 
        self.root = objeto 
        self.lista_dados_funcionarios = None
        
        self.nome, self.cpf, self.rg, self.ctps_numero, self.ctps_serie, self.endereco, self.cep, self.salario, self.funcao, self.data_admissional = nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao
        
        self.inicializar()
        
        
        
    @staticmethod
    def _procurar_dados():
        lista_dados = []
        
        with open('BackupFolder/DataBackup.txt', 'r', encoding='utf-8') as file:
            dados = file.readlines()
            
        for item in dados:
            item = item.split(';')
            nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao = item

            lista_dados.append([[nome, cpf, funcao, salario, data_admissao], [nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao]])
            
        return lista_dados
    
        
    def on_select(self, event):
        selected_item = event.widget.get(event.widget.curselection())
        listagem = [item[0] for item in self.lista_dados_funcionarios]
        print('aaa',listagem)
        nome, cpf, rg, ctps_num, ctps_serie, endereco, cep, salario, funcao, data_admissao = listagem
        self.nome.insert(0, nome)

        
    def inicializar(self):
        # criar uma nova janela
        nova_janela = tk.Toplevel(self.root)
        nova_janela.geometry("600x550+450+150")
        nova_janela.title("Menu")

        header_frame = tk.Frame(nova_janela, bg="#1F2E46", padx=20, pady=10)
        header_frame.pack(side="top", fill="x")
        
        # adicionar um rótulo na nova janela
        label = tk.Label(header_frame, text="Menu", font=("Arial", 24), bg="#1F2E46", fg="white", padx=10, pady=5)
        label.pack(pady=0)
        
        options_frame = tk.Frame(nova_janela)
        options_frame.pack(side="left", padx=10, pady=20)

        options_label = tk.Label(options_frame, text="Opções:")
        options_label.pack(side="top")

        options_listbox = tk.Listbox(options_frame, height=50, width=110)
        options_listbox.pack(side="left")

        options_scrollbar = tk.Scrollbar(options_frame, orient="vertical")
        options_scrollbar.config(command=options_listbox.yview)
        options_scrollbar.pack(side="right", fill="y")

        options_listbox.config(yscrollcommand=options_scrollbar.set)
        options_listbox.bind("<<ListboxSelect>>", self.on_select)

        self.lista_dados_funcionarios = JanelaSecundaria._procurar_dados()
        
        for option in self.lista_dados_funcionarios:
            option = ' - '.join(option[0])
            options_listbox.insert("end", option)

        nova_janela.mainloop()

# continuar em janela secundaria preencher primária