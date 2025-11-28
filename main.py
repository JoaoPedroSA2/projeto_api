from fastapi import FastAPI
from pydantic import BaseModel
from jose import jwt, JWTError 
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status


app = FastAPI(
    title = "My API",
    description = "This is a sample API"
)

secretkey = "chave_mega_secreta"
algoritmo = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

user_db = {
    "admin" : {
        "username": "admin",
        "password": "1234",
    }
}

class produto(BaseModel):
    nome : str
    preco_unitario : float
    quantidade : int

class token(BaseModel):
    access_token: str
    token_type: str

estoque = []

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, secretkey, algorithms=[algoritmo])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Token inválido",
                headers = {"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token inválido ou expirado",
            headers = {"WWW-Authenticate": "Bearer"},
        )

def criar_token(data: dict,expire_time:timedelta | None = None):
    to_encode = data.copy()
    if expire_time:
        expire = datetime.utcnow() + expire_time
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode["exp"] = expire
    encode_jwt = jwt.encode(to_encode, secretkey, algorithm = algoritmo)
    
    return encode_jwt
    
@app.post("/login", response_model = token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = user_db.get(form.username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    
    if form.password != user["password"]:
        raise HTTPException(status_code=400, detail="Senha incorreta")

    dados_token = {"sub": form.username}
    token_expire = timedelta(minutes = 30)

    access_token = criar_token(data = dados_token, expire_time = token_expire)
    
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/produtos/post")
async def adicionar_produto(produto: produto, token: str = Depends(oauth2_scheme)):
    verificar_token(token)
    
    novo_produto = {
        "nome": produto.nome,
        "preco_unitario": produto.preco_unitario,
        "quantidade": produto.quantidade,
        "id": len(estoque) + 1
    }
    estoque.append(novo_produto)
    
    return {"message": "Produto adicionado com sucesso", "produto": novo_produto}

@app.get("/produtos")
async def read_produtos(token: str = Depends(oauth2_scheme)):
    return estoque

@app.delete("/produto/delete/{produto_id}")
async def deletar_produto(produto_id: int, token: str = Depends(oauth2_scheme)):
    verificar_token(token)

    for produto in estoque:
        if produto["id"] == produto_id:
            estoque.remove(produto)
            return {"message": "Produto removido com sucesso"}
        
    return {"message": "Produto não encontrado"}

