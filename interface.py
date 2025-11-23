import customtkinter as ctk
from tkinter import messagebox
import json
import os
import unicodedata
from datetime import date

# ---------------- CONFIGURAÇÕES DE APARÊNCIA ----------------
ctk.set_appearance_mode("dark")  # "system" / "dark" / "light"
ctk.set_default_color_theme("dark-blue")  # temas disponíveis

# ---------------- FUNÇÕES AUXILIARES ----------------
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.replace("_", " ").replace("-", " ").replace("/", " ")
    texto = ' '.join(texto.split())
    return texto.strip()

def garantir_pastas():
    os.makedirs('json', exist_ok=True)
    os.makedirs('dados_funcionario', exist_ok=True)

garantir_pastas()

# ---------------- ARQUIVO DE CARGOS ----------------
caminho_cargos = 'json/cargos_salarios.json'
if not os.path.exists(caminho_cargos):
    exemplo = {
        "Operacional_Rodoviario": {
            "Motorista Carreteiro": 2583,
            "Motorista Truck": 2583,
            "Motorista Toco": 2500,
            "Motorista VUC": 2300,
            "Motorista de Coleta e Entrega": 2300,
            "Motorista Bi-trem / Rodotrem": 3000,
            "Motorista Munck": 3200,
            "Motorista Operador": 3200,
            "Ajudante de Motorista": 1600,
            "Ajudante de Carga e Descarga": 1600
        }
    }
    with open(caminho_cargos, "w", encoding="utf-8") as f:
        json.dump(exemplo, f, indent=4, ensure_ascii=False)

with open(caminho_cargos, 'r', encoding='utf-8') as f:
    cargos_salarios = json.load(f)

cargos_normalizados = {}
cargos_display = []
for categoria, cargos in cargos_salarios.items():
    for cargo, salario in cargos.items():
        cargos_normalizados[normalizar(cargo)] = salario
        cargos_display.append(cargo)
cargos_display = sorted(list(dict.fromkeys(cargos_display)))

def obter_salario(cargo: str):
    return cargos_normalizados.get(normalizar(cargo))

def calcular_idade(dia: int, mes: int, ano: int) -> int:
    hoje = date.today()
    idade = hoje.year - ano
    if (hoje.month, hoje.day) < (mes, dia):
        idade -= 1
    return idade

# ---------------- PERMISSÕES DE CARGA ----------------
PERMISSOES_CARGA = {
    "leve": ["motorista vuc","motorista toco","motorista truck","motorista de coleta e entrega","motorista operador"],
    "pesada": ["motorista truck","motorista carreteiro","motorista munck","motorista operador"],
    "bi trem": ["motorista bi trem  rodotrem","motorista carreteiro"],
    "rodo trem": ["motorista bi trem  rodotrem","motorista carreteiro"]
}
PERMISSOES_CARGA_NORM = {k:[normalizar(x) for x in v] for k,v in PERMISSOES_CARGA.items()}

# ---------------- FUNÇÕES DE DADOS ----------------
def salvar_funcionario_json(dados: dict):
    nome_arquivo = normalizar(dados["nome"]).replace(" ", "_")
    with open(f'dados_funcionario/{nome_arquivo}.json','w',encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_todos_funcionarios():
    lista = []
    for arq in os.listdir('dados_funcionario'):
        if arq.endswith('.json'):
            with open(os.path.join('dados_funcionario', arq),'r',encoding='utf-8') as f:
                try: lista.append(json.load(f))
                except: continue
    return lista

def carregar_funcionario_por_nome(nome: str):
    nome_arquivo = normalizar(nome).replace(" ","_")
    caminho = f'dados_funcionario/{nome_arquivo}.json'
    if os.path.exists(caminho):
        with open(caminho,'r',encoding='utf-8') as f:
            return json.load(f)
    return None

# ---------------- APLICAÇÃO ----------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Transportes — Gestão de Funcionários")
        self.geometry("950x650")
        self.minsize(820,560)

        # Layout
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self,width=220,corner_radius=0)
        self.sidebar.grid(row=0,column=0,sticky="nswe")
        self.sidebar.grid_rowconfigure(6,weight=1)
        ctk.CTkLabel(self.sidebar,text="TRANSPORTES",font=ctk.CTkFont(size=20,weight="bold")).grid(padx=20,pady=(20,8),row=0,column=0)
        ctk.CTkLabel(self.sidebar,text="Gestão de Motoristas",font=ctk.CTkFont(size=12)).grid(padx=20,pady=(0,16),row=1,column=0)

        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=0,column=1,sticky="nswe",padx=12,pady=12)
        for tab in ["Cadastro","Listar","Buscar","Locar Caminhão"]:
            self.notebook.add(tab)

        self.tab_cadastro = self.notebook.tab("Cadastro")
        self.tab_listar = self.notebook.tab("Listar")
        self.tab_buscar = self.notebook.tab("Buscar")
        self.tab_locar = self.notebook.tab("Locar Caminhão")

        # Sidebar buttons
        btns = [("Cadastrar",self.tab_cadastro),
                ("Listar",self.tab_listar),
                ("Buscar",self.tab_buscar),
                ("Locar Caminhão",self.tab_locar)]
        for i,(txt,tab) in enumerate(btns,start=2):
            ctk.CTkButton(self.sidebar,text=txt,command=lambda t=tab:self.notebook.set(t)).grid(row=i,column=0,padx=20,pady=6,sticky="we")

        # Constroi abas
        self._construir_cadastro(self.tab_cadastro)
        self._construir_listar(self.tab_listar)
        self._construir_buscar(self.tab_buscar)
        self._construir_locar(self.tab_locar)
        self.notebook.set("Cadastro")

    # ---------------- CADASTRO ----------------
    def _construir_cadastro(self,parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True,fill="both",padx=12,pady=12)
        # Left
        left = ctk.CTkFrame(frame)
        left.pack(side="left",fill="both",expand=True,padx=(0,8))
        right = ctk.CTkFrame(frame)
        right.pack(side="right",fill="both",expand=True,padx=(8,0))

        # Inputs
        self.input_nome = ctk.CTkEntry(left,placeholder_text="Nome completo")
        self.input_nome.pack(fill="x",padx=10,pady=6)
        self.input_dia = ctk.CTkEntry(left,placeholder_text="Dia")
        self.input_dia.pack(fill="x",padx=10,pady=6)
        self.input_mes = ctk.CTkEntry(left,placeholder_text="Mês")
        self.input_mes.pack(fill="x",padx=10,pady=6)
        self.input_ano = ctk.CTkEntry(left,placeholder_text="Ano")
        self.input_ano.pack(fill="x",padx=10,pady=6)
        self.input_sexo = ctk.CTkEntry(left,placeholder_text="Sexo M/F")
        self.input_sexo.pack(fill="x",padx=10,pady=6)
        self.input_cpf = ctk.CTkEntry(left,placeholder_text="CPF")
        self.input_cpf.pack(fill="x",padx=10,pady=6)

        # Right
        self.cargo_option = ctk.CTkOptionMenu(right,values=cargos_display)
        self.cargo_option.pack(fill="x",padx=10,pady=6)
        self.input_cargo_manual = ctk.CTkEntry(right,placeholder_text="Ou digite cargo manualmente")
        self.input_cargo_manual.pack(fill="x",padx=10,pady=6)
        self.btn_cadastrar = ctk.CTkButton(right,text="Cadastrar",fg_color="#1f6aa5",command=self.action_cadastrar)
        self.btn_cadastrar.pack(pady=18,padx=10,fill="x")

    def action_cadastrar(self):
        nome = self.input_nome.get().strip().title()
        try:
            dia,mes,ano=int(self.input_dia.get()),int(self.input_mes.get()),int(self.input_ano.get())
        except: messagebox.showerror("Erro","Data inválida"); return
        sexo=self.input_sexo.get().strip().upper()
        cpf=self.input_cpf.get().strip()
        cargo=self.input_cargo_manual.get().strip() or self.cargo_option.get()
        if not nome: messagebox.showerror("Erro","Nome obrigatório"); return
        salario=obter_salario(cargo) or 0
        idade=calcular_idade(dia,mes,ano)
        dados={"nome":nome,"nascimento":f"{dia:02d}/{mes:02d}/{ano}","idade":idade,"sexo":sexo,"cpf":cpf,"cargo":cargo.title(),"salario":salario}
        salvar_funcionario_json(dados)
        messagebox.showinfo("Sucesso",f"Funcionário {nome} cadastrado.")
        self._limpar_campos_cadastro()
        self.atualizar_lista()

    def _limpar_campos_cadastro(self):
        for e in [self.input_nome,self.input_dia,self.input_mes,self.input_ano,self.input_sexo,self.input_cpf,self.input_cargo_manual]:
            e.delete(0,"end")

    # ---------------- LISTAR ----------------
    def _construir_listar(self,parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both",expand=True,padx=12,pady=12)
        self.frame_lista=frame
        self.atualizar_lista()

    def atualizar_lista(self):
        for w in self.frame_lista.winfo_children(): w.destroy()
        dados=carregar_todos_funcionarios()
        if not dados: ctk.CTkLabel(self.frame_lista,text="Nenhum funcionário cadastrado").pack(pady=10); return
        for f in sorted(dados,key=lambda x:normalizar(x.get("nome",""))):
            card = ctk.CTkFrame(self.frame_lista,corner_radius=8)
            card.pack(fill="x",padx=8,pady=6)
            ctk.CTkLabel(card,text=f"{f.get('nome','')} — {f.get('cargo','')}",font=ctk.CTkFont(weight="bold")).pack(anchor="w",padx=8,pady=(4,0))
            txt = f"Idade:{f.get('idade','-')} | Nasc:{f.get('nascimento','-')} | CPF:{f.get('cpf','-')} | Salário:R${f.get('salario',0)}"
            ctk.CTkLabel(card,text=txt,anchor="w").pack(anchor="w",padx=8,pady=(2,4))

    # ---------------- BUSCAR ----------------
    def _construir_buscar(self,parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both",expand=True,padx=12,pady=12)
        self.input_busca_nome = ctk.CTkEntry(frame,placeholder_text="Digite nome")
        self.input_busca_nome.pack(fill="x",padx=10,pady=6)
        ctk.CTkButton(frame,text="Buscar",command=self.action_buscar).pack(pady=6)
        self.resultado_busca = ctk.CTkTextbox(frame,width=700,height=300)
        self.resultado_busca.pack(fill="both",expand=True,padx=6,pady=6)

    def action_buscar(self):
        nome=self.input_busca_nome.get().strip()
        self.resultado_busca.delete("0.0","end")
        if not nome: messagebox.showerror("Erro","Digite um nome"); return
        dados=carregar_funcionario_por_nome(nome)
        if not dados: self.resultado_busca.insert("0.0","Funcionário não encontrado"); return
        self.resultado_busca.insert("0.0",json.dumps(dados,indent=4,ensure_ascii=False))

    # ---------------- LOCAR CAMINHÃO ----------------
    def _construir_locar(self,parent):
        frame=ctk.CTkFrame(parent)
        frame.pack(fill="both",expand=True,padx=12,pady=12)
        self.input_loc_nome = ctk.CTkEntry(frame,placeholder_text="Nome do Motorista")
        self.input_loc_nome.pack(fill="x",padx=10,pady=6)
        self.option_carga = ctk.CTkOptionMenu(frame,values=["leve","pesada","bi trem","rodo trem"])
        self.option_carga.pack(fill="x",padx=10,pady=6)
        self.input_num_caminhao = ctk.CTkEntry(frame,placeholder_text="Número do Caminhão")
        self.input_num_caminhao.pack(fill="x",padx=10,pady=6)
        ctk.CTkButton(frame,text="Locar",fg_color="#1f6aa5",command=self.action_locar).pack(pady=12,padx=6,anchor="e")

    def action_locar(self):
        nome=self.input_loc_nome.get().strip()
        if not nome: messagebox.showerror("Erro","Digite o motorista"); return
        dados=carregar_funcionario_por_nome(nome)
        if not dados: messagebox.showerror("Erro","Funcionário não encontrado"); return
        cargo_norm=normalizar(dados.get("cargo",""))
        if not cargo_norm.startswith("motorista"): messagebox.showerror("Erro","Não é motorista"); return
        carga=self.option_carga.get(); numero=self.input_num_caminhao.get().strip()
        if not carga or not numero: messagebox.showerror("Erro","Preencha todos os campos"); return
        permissoes=PERMISSOES_CARGA_NORM.get(carga.lower(),[])
        if cargo_norm not in permissoes:
            messagebox.showerror("Sem permissão",f"O motorista {dados.get('nome')} não pode '{carga}'\nPermitidos: "+", ".join([p.title() for p in permissoes]))
            return
        messagebox.showinfo("Sucesso",f"Caminhão {numero} locado para {dados.get('nome')} ({carga})")
        # grava histórico
        hist_file="json/historico_locacoes.json"
        hist=[]
        if os.path.exists(hist_file):
            try: hist=json.load(open(hist_file,'r',encoding='utf-8'))
            except: hist=[]
        hist.append({"motorista":dados.get("nome"),"cargo":dados.get("cargo"),"carga":carga,"caminhao":numero,"data":date.today().isoformat()})
        with open(hist_file,'w',encoding='utf-8') as f: json.dump(hist,f,indent=4,ensure_ascii=False)

# ---------------- RODAR APLICAÇÃO ----------------
if __name__=="__main__":
    app=App()
    app.mainloop()
