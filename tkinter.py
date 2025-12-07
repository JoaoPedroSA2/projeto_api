import tkinter as tk
from tkinter import messagebox
import requests

API_URL = "http://127.0.0.1:8000"
token = ""

#----------- config grafica--------------
root = tk.Tk()
root.title("frontend API Tkinter")
root.geometry("600x600")
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
#-----------------------------------------


#------------campo de login ----------------
frame_login = tk.Frame(root)
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
frame_produtos = tk.Frame(root)
#-----------------------------------------------------------

#---------------lista de produtos ----------------
btn_produto = tk.Button(frame_produtos, text="Listar Produtos", command=lista_produto)
btn_produto.pack()

lista = tk.Listbox(frame_produtos, width = 100)
lista.pack(pady=10, padx = 10)

#-----------------------------------------------------------

#------------ campos de produto ----------------
tk.Label(frame_produtos, text="Nome do produto:").pack()
entry_nome = tk.Entry(frame_produtos)
entry_nome.pack()

tk.Label(frame_produtos, text="Preco unitario:").pack()
entry_preco = tk.Entry(frame_produtos)
entry_preco.pack()

tk.Label(frame_produtos, text="Quantidade:").pack()
entry_quantidade = tk.Entry(frame_produtos)
entry_quantidade.pack()

btn_add_produto = tk.Button(frame_produtos, text="Adicionar Produto", command=adicionar_produto)
btn_add_produto.pack(pady=5)
#----------------------------------------------------

#------------ campo de deletar produto ----------------
tk.Label(frame_produtos, text="ID do produto para deletar:").pack()
entry_delete = tk.Entry(frame_produtos)
entry_delete.pack()

tk.Button(frame_produtos, text="Deletar Produto", command=remover_produto).pack(pady=5)
#-----------------------------------------------------------

#------------loop grafico----------------
root.mainloop()
