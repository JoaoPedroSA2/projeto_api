import tkinter as tk
from tkinter import messagebox
import requests

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
        lista.delete(0,tk.END)

        for p in produtos:
            lista.insert(tk.END, f"ID: {p['id']} - Nome: {p['nome']} - Preço: {p['preco_unitario']} - Quantidade: {p['quantidade']}")
    else:
        erro = resp.text
        messagebox.showwarning("Aviso", f"Erro ao buscar produtos:{erro}")


def adicionar_produto():
    if not token:
        messagebox.showwarning("Aviso", "Por favor, faça login primeiro.")
        return
    
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
    else:
        erro = resp.text
        messagebox.showerror("Erro", f"Falha ao adicionar produto: {erro}")


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
    try:
        selected = lista.get(lista.curselection()) #pega item selecionado
        id_produto = selected.split(" - ")[0].replace("ID: ", "") #pega id do produto
    except:
        messagebox.showwarning("Aviso", "Por favor, selecione um produto para editar.")
        return
    
    partes = selected.split(" - ")

    id_ = partes[0].replace("ID: ", "") 
    nome = partes[1].replace("Nome: ", "")
    preco = partes[2].replace("Preço: ", "")
    quantidade = partes[3].replace("Quantidade: ", "")

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
            messagebox.showinfo("Sucesso", "Produto editado com sucesso!")
            lista_produto()
    else:
        erro = resp.text
        messagebox.showerror("Erro", f"Falha ao editar produto: {erro}")

def buscar_produto():
    termo = entry_buscar.get().lower()
    lista.delete(0, tk.END)

    if not termo:
        messagebox.showwarning("Aviso", "Por favor, insira um termo para buscar.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(f"{API_URL}/produtos", headers=headers)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à API: {e}")
        return

    if resp.status_code == 200:
        produtos = resp.json()
        for p in produtos:
            if termo in p['nome'].lower() or termo == str(p['id']):
                lista.insert(tk.END, f"ID: {p['id']} - Nome: {p['nome']} - Preço: {p['preco_unitario']} - Quantidade: {p['quantidade']}")
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

#---------------lista de produtos ----------------
btn_produto = tk.Button(frame_produtos, text="Listar Produtos", command=lista_produto)
btn_produto.pack(anchor = "nw", pady=10, padx = 10)

scrollbar = tk.Scrollbar(frame_produtos)
scrollbar.pack(side = "right", fill= "y")

lista = tk.Listbox(frame_produtos, width = 100,yscrollcommand=scrollbar.set)
lista.pack(pady=10, padx = 10, anchor = "nw")
scrollbar.config(command=lista.yview)

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

btn_add_produto = tk.Button(frame_produtos, text="Adicionar Produto", command=adicionar_produto)
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

btn_editar = tk.Button(frame_produtos, text = "Editar produto", command = editar_produto)
btn_editar.pack(pady = 5, anchor = "sw")

#--------------------------------------------------------

#---------------- Salvar ------------------
btn_salvar = tk.Button(frame_produtos, text="Salvar", command=salvar_edicao)
btn_salvar.pack(pady=5, anchor="sw")

#------------ campo de buscar produto ----------------
tk.Label(frame_produtos, text="Buscar produto:").pack(anchor="sw")
entry_buscar = tk.Entry(frame_produtos)
entry_buscar.pack(pady = 5, anchor="sw")

btn_buscar = tk.Button(frame_produtos, text = "Buscar produto", command = buscar_produto)
btn_buscar.pack(pady = 5, anchor = "sw")
#--------------------------------------------------

#------------ botao logout ----------------
btn_logout = tk.Button(frame_produtos, text="Logout", bg = "red", fg = "white",command=logout)
btn_logout.pack(pady=10, anchor="se")
#--------------------------------------------------------------

#------------loop grafico----------------
root.mainloop()
