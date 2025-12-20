import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import customtkinter as ctk
import csv

API_URL = "http://127.0.0.1:8000"
token = ""

#----------- config grafica--------------
root = tk.Tk()
root.configure(bg="darkgray")
root.title("frontend API Tkinter")
root.geometry("1000x1200")
#-----------------------------------------

#------------ funcao api---------------
def login():
    global token, entry_user, entry_pass

    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
        return

    try:
        resp = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return  
    
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token","")

        messagebox.showinfo("Sucesso", "Login bem-sucedido!")
        
        frame_login.pack_forget()  # esconde o frame de login
        frame_produtos.pack(fill="both", expand=True)  # mostra o frame de produtos

    else:
        erro = resp.text
        messagebox.showerror("Erro", f"Falha no login: {erro}")
#-------------------------------------


#----------funcoes------------
def lista_produto():
    if not token:
        messagebox.showwarning("Aviso", "Por favor, faça login primeiro.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{API_URL}/produtos", headers=headers)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return
    
    if resp.status_code == 200:
        produtos = resp.json()
    
        for item in tabela.get_children():
            tabela.delete(item)

        for p in produtos:
            tabela.insert("","end",values=(p["id"],p["nome"],p["preco_unitario"],p["quantidade"])) 
    else:
        erro = resp.text
        messagebox.showwarning("Aviso", f"Erro ao buscar produtos:{erro}")


def adicionar_produto():
    if not token:
        messagebox.showwarning("Aviso", "Por favor, faça login primeiro.")
        return
    global caminho_imagem
    
    nome = entry_nome.get()
    preco = entry_preco.get()
    quantidade = entry_quantidade.get()

    if not nome or not preco or not quantidade:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos do produto.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.post(
            f"{API_URL}/produtos/post",
            json={
                "nome": nome,
                "preco_unitario": float(preco),
                "quantidade": int(quantidade)
            },
            headers=headers
        )  
    except Exception as e: 
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return
    
    if resp.status_code == 200 or resp.status_code == 201:
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
        lista_produto() #att lista
        try:
            dados = resp.json()
            produto_id = dados["produto"]["id"]
        except Exception:
            messagebox.showwarning("Aviso", "Falha ao obter o ID do produto.")
            lista_produto()
            caminho_imagem = None
            return

        if caminho_imagem:
            try:
                import os
                os.makedirs("imagens", exist_ok=True)

                with open(caminho_imagem, "rb") as f:
                    files = {"imagem": f}
                    resp_img = requests.post(f"{API_URL}/produto/{produto_id}/imagem", files=files, headers = {"Authorization": f"Bearer {token}"})
                    if resp_img.status_code != 200:
                        messagebox.showwarning("Aviso", "Falha ao enviar imagem do produto.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao enviar imagem: {e}")
    else:
        try:
            erro = resp.json().get("detail",resp.text)
        except:
            erro = resp.text
            messagebox.showerror("Erro", f"Falha ao adicionar produto: {erro}")
    
    caminho_imagem = None
    lista_produto()



def remover_produto():
    if not token:
        messagebox.showwarning("Aviso", "Por favor, faça login primeiro.")
        return
    
    id_produto = entry_delete.get()
    
    if not id_produto:
        messagebox.showwarning("Aviso", "Por favor, insira o ID do produto para deletar.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.delete(f"{API_URL}/produto/delete/{id_produto}", headers=headers)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return
    
    if resp.status_code == 200:
        messagebox.showinfo("Sucesso", "Produto deletado com sucesso!")
        lista_produto()
    else:
        erro = resp.text
        messagebox.showerror("Erro", f"Falha ao deletar produto: {erro}")

def logout():
    global token
    token = ""

    entry_user.delete(0, tk.END)
    entry_pass.delete(0, tk.END)

    frame_produtos.pack_forget() # esconde o frame de produtos
    frame_login.pack(fill="both", expand=True) # mostra o frame de login

def toggle_senha():
    if entry_pass.cget("show") == "":
        entry_pass.config(show="*")
    else:
        entry_pass.config(show="")

def editar_produto():
    global caminho_imagem
    caminho_imagem = None

    item = tabela.focus()
    valores = tabela.item(item, "values")
    
    if not valores:
        messagebox.showwarning("Aviso", "Por favor, selecione um produto para editar.")
        return

    id_ = valores[0]
    nome = valores[1]
    preco = valores[2]
    quantidade = valores[3]

    global produto_id_editado
    produto_id_editado = id_

    entry_nome.delete(0, tk.END)
    entry_nome.insert(0, nome)

    entry_preco.delete(0, tk.END)
    entry_preco.insert(0, preco)

    entry_quantidade.delete(0, tk.END)
    entry_quantidade.insert(0, quantidade)

    messagebox.showinfo("Sucesso", "Edite os campos e clique em SALVAR")
    
def salvar_edicao():
    novo_nome = entry_nome.get()
    novo_preco = entry_preco.get()
    novo_quantidade = entry_quantidade.get()

    if not novo_nome or not novo_preco or not novo_quantidade:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos do produto.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.put(
            f"{API_URL}/produtos/{produto_id_editado}",
            json={
                "nome": novo_nome,
                "preco_unitario": float(novo_preco),
                "quantidade": int(novo_quantidade)
            },
            headers= headers
        )
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return
    
    if resp.status_code == 200:
            if caminho_imagem:
                try:
                    with open(caminho_imagem, "rb") as f:
                        files = {"imagem": f}
                        resp_img = requests.post(
                            f"{API_URL}/produto/{produto_id_editado}/imagem",
                            files=files,
                            headers={"Authorization": f"Bearer {token}"}
                        )
                        if resp_img.status_code != 200:
                            messagebox.showwarning("Aviso", "Falha ao enviar imagem do produto.")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao enviar imagem: {e}")
                    return
            messagebox.showinfo("Sucesso", "Produto editado com sucesso!")
            lista_produto()
    else:
        erro = resp.text
        messagebox.showerror("Erro", f"Falha ao editar produto: {erro}")

def buscar_produto():
    termo = entry_buscar.get().lower()
    
    for item in tabela.get_children():
        tabela.delete(item)

    if not termo:
        messagebox.showwarning("Aviso", "Por favor, insira um termo para buscar.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(f"{API_URL}/produtos", headers=headers)

        if resp.status_code == 200:
            produtos = resp.json()
            for p in produtos:
                if termo in p['nome'].lower() or termo == str(p['id']):
                    tabela.insert("","end", values = (p["id"], p["nome"], p["preco_unitario"], p["quantidade"]))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return
    
def esconde_sugestao():
    listbox_autocomplete.place_forget()

def selecionar_sugestao(event):
    try:
        item = listbox_autocomplete.get(listbox_autocomplete.curselection())
    except:
        return 
    entry_buscar.delete(0, tk.END)
    entry_buscar.insert(0, item)
    esconde_sugestao()

def autocomplete(event):
    termo = entry_buscar.get().lower()
    listbox_autocomplete.delete(0,tk.END)

    if not termo:
        esconde_sugestao()
        return
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(f"{API_URL}/produtos", headers=headers)
        if resp.status_code != 200:
            esconde_sugestao()
            return
        produtos = resp.json()
    except:
        esconde_sugestao()
        return

    sugestoes = [p['nome'] for p in produtos if p['nome'].lower().startswith(termo)]

    if not sugestoes:
        esconde_sugestao()
        return
    for s in sugestoes:
        listbox_autocomplete.insert(tk.END, s)

    offset = 10
    x = entry_buscar.winfo_rootx() - offset
    y = entry_buscar.winfo_y() + entry_buscar.winfo_height()
    w = entry_buscar.winfo_width()

    listbox_autocomplete.place(x=x, y=y, width=w)

def click_fora(event):
        if event.widget not in (entry_buscar, listbox_autocomplete):
            esconde_sugestao()

caminho_imagem = None

def selecionar_imagem():
    global caminho_imagem

    caminho_imagem = filedialog.askopenfilename(title="Selecione a imagem",filetypes=[("Imagens", "*.jpg;*.png;*.jpeg")])

    if caminho_imagem:
        messagebox.showinfo("Sucesso", "Imagem selecionada com sucesso!")

def mostrar_imagem(event):
    item = tabela.identify_row(event.y)
    if not item:
        return
    
    tabela.selection_set(item)
    
    valores = tabela.item(item, "values")

    if not valores:
        return
    
    id_produto = valores[0]

    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(f"{API_URL}/produto/{id_produto}/imagem", headers=headers)

        if resp.status_code == 404:
            messagebox.showwarning("Aviso", "Imagem não encontrada para este produto.")
            return

        if resp.status_code != 200:
            return

        img_data = BytesIO(resp.content)
        img = Image.open(img_data)
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)

        win = tk.Toplevel()
        win.title(f"Imagem do produto {id_produto}")

        label = tk.Label(win, image=img_tk)
        label.image = img_tk
        label.pack()

        root.wait_window(win)
        
    except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir imagem: {e}")

def exportar_csv():
    if not token:
        messagebox.showwarning("Aviso", "Por favor, faça login primeiro.")
        return
    
    headers = {"Authorization": f"Bearer {token}"} 

    try:
        resp = requests.get(f"{API_URL}/produtos", headers=headers)
        if resp.status_code != 200:
            messagebox.showerror("Aviso","Não foi possivel obter dados da API")
            return
        produtos = resp.json()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return 
    
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar relatorio de Estoque"
    )
    if not caminho_arquivo:
        return
    
    try:
        with open(caminho_arquivo,mode = "w",newline="", encoding= "utf-8-sig") as f:
            escritor = csv.writer(f, delimiter= ";")

            escritor.writerow(["ID","Nome do Produto", "Preço Unitario", "Quantidade", "Valor em Estoque"])

            for p in produtos:
                valor_estoque = p["preco_unitario"] * p["quantidade"]
                escritor.writerow([[
                    p["id"],
                    p["nome"],
                    f"{p["preco_unitario"]:.2f}".replace(".","."),
                    p["quantidade"],
                    f"{valor_estoque:.2f}".replace(".", ".")
                ]])
        messagebox.showinfo("Sucesso", "Relatorio exportado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar relatorio: {e}")  

#-----------------------------------------

#------------campo de login ----------------
frame_login = tk.Frame(root, bg = "darkgray")
frame_login.pack(fill = "both", expand = True)

tk.Label(frame_login, text="Usuario:").pack()
entry_user = tk.Entry(frame_login)
entry_user.pack()

tk.Label(frame_login, text="Senha:").pack()
entry_pass = tk.Entry(frame_login, show="*")
entry_pass.pack()

btn_login = tk.Button(frame_login, text="Login", command=login)
btn_login.pack(pady=10)
#-----------------------------------------------------------

#------------frame de produtos ----------------
frame_produtos = tk.Frame(root, bg = "darkgray")
#-----------------------------------------------------------

#------------------listbox autocomplete-----------
listbox_autocomplete = tk.Listbox(frame_produtos, height=5, bg = "white")
listbox_autocomplete.place_forget()  # Inicialmente, esconde a listbox
#--------------------------------------------------

#---------------lista de produtos ----------------
btn_produto = tk.Button(frame_produtos, text="Listar Produtos", fg = "green", command=lista_produto)
btn_produto.pack(anchor = "nw", pady=10, padx = 10)

colunas = ("ID", "Nome", "Preço", "Quantidade")

tabela = ttk.Treeview(frame_produtos, columns=colunas, show="headings")

tabela.heading("ID", text="ID")
tabela.heading("Nome", text="Nome")
tabela.heading("Preço", text="Preço")
tabela.heading("Quantidade", text="Quantidade")

tabela.column("ID", width=50)
tabela.column("Nome", width=200)
tabela.column("Preço", width=120)
tabela.column("Quantidade", width=120)

tabela.pack(pady=10, padx=10, anchor="nw")

scrollbar = ttk.Scrollbar(frame_produtos, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tabela.bind("<Double-1>", mostrar_imagem)
#-----------------------------------------------------------

#------------ campos de produto ----------------
tk.Label(frame_produtos, text="Nome do produto:").pack(anchor="sw")
entry_nome = tk.Entry(frame_produtos)
entry_nome.pack(anchor = "sw")

tk.Label(frame_produtos, text="Preco unitario:").pack(anchor="sw")
entry_preco = tk.Entry(frame_produtos)
entry_preco.pack(anchor = "sw")

tk.Label(frame_produtos, text="Quantidade:").pack(anchor="sw")
entry_quantidade = tk.Entry(frame_produtos)
entry_quantidade.pack(anchor="sw")

btn_imagem = tk.Button(frame_produtos, text="Selecionar Imagem", fg = "green", command=selecionar_imagem)
btn_imagem.pack(pady=5, anchor="sw")

btn_add_produto = tk.Button(frame_produtos, text="Adicionar Produto", fg = "green", command=adicionar_produto)
btn_add_produto.pack(pady=5, anchor="sw")

#----------------------------------------------------

#------------ campo de deletar produto ----------------
tk.Label(frame_produtos, text="ID do produto para deletar:").pack(anchor="sw")
entry_delete = tk.Entry(frame_produtos)
entry_delete.pack(anchor="sw")

tk.Button(frame_produtos, text="Deletar Produto", fg = "red", command=remover_produto).pack(pady=5, anchor="sw")
#-----------------------------------------------------------

#------------ botao mostrar senha ----------------
chk_senha = tk.Checkbutton(frame_login, text = "Mostrar senha", bg = "darkgray", fg = "white", command=toggle_senha)
chk_senha.pack()
#-----------------------------------------------------------

#------------ botao editar produto ----------------
tk.Label(frame_produtos, text="Editar Produto:").pack(anchor="sw")

btn_editar = tk.Button(frame_produtos, text = "Editar produto", fg = "green", command = editar_produto)
btn_editar.pack(pady = 5, anchor = "sw")

#--------------------------------------------------------

#---------------- Salvar ------------------
btn_salvar = tk.Button(frame_produtos, text="Salvar",fg = "green", command=salvar_edicao)
btn_salvar.pack(pady=5, anchor="sw")

#------------ campo de buscar produto ----------------
tk.Label(frame_produtos, text="Buscar produto:").pack(anchor="sw")
entry_buscar = tk.Entry(frame_produtos)
entry_buscar.place(x= 5, y = 680, width=250)

btn_buscar = tk.Button(frame_produtos, text = "Buscar produto",fg = "green", command = buscar_produto)
btn_buscar.place(x = 270,y = 680)
#--------------------------------------------------

#------------ botao logout ----------------
btn_logout = tk.Button(frame_produtos, text="Logout", bg = "red", fg = "white",command=logout)
btn_logout.pack(pady=10, anchor="se")
#--------------------------------------------------------------

#------------ botao exportar csv ----------------
btn_exportar = tk.Button(frame_produtos, text="Exportar CSV", fg = "green", command=exportar_csv)
btn_exportar.pack(pady=10, anchor="nw", padx= 10)

#------------------binds autocomplete----------------------
entry_buscar.bind("<KeyRelease>", autocomplete)
listbox_autocomplete.bind("<<ListboxSelect>>", selecionar_sugestao)
root.bind("<Button-1>", lambda e: esconde_sugestao() if e.widget not in (entry_buscar, listbox_autocomplete) else None)
#--------------------------------------------

#------------loop grafico----------------
root.mainloop()
