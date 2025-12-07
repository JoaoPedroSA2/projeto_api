from fastapi import FastAPI
from pydantic import BaseModel
from jose import jwt, JWTError 
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import String
from typing import List

#------------config basica do FastAPI----------------
app = FastAPI(
    title = "My API",
    description = "This is a sample API"
)

secretkey = "chave_mega_secreta"
algoritmo = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
##------------------------

##---------------- banco de dados ------------------
dataurl = "sqlite:///./bancodados.db"  

engine = create_engine(dataurl, connect_args={"check_same_thread": False})

sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

##--------------------------

##--------------Modelo do banco ---------------
Base = declarative_base()

class produtodb(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    preco_unitario = Column(Float)
    quantidade = Column(Integer)

Base.metadata.create_all(bind=engine)
## ------------------------------------

##------------Modelo pydantic ----------------
class produto(BaseModel):
    nome: str
    preco_unitario: float
    quantidade: int

class produtoresponse(BaseModel):
    id: int
    nome : str
    preco_unitario: float
    quantidade: int

    class config:
        orm_mode = True

class ProdutoCriadoResponse(BaseModel):
    msg: str
    produto : produtoresponse

class token(BaseModel):
    access_token: str
    token_type: str
#_-------------------------------


#--------Funções de autenticação e segurança ---------
def hash_senha(senha):
    senha = senha[:72]
    hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  

def verify_senha(plain_senha, hashed_senha):
    plain_senha = plain_senha[:72]
    return bcrypt.checkpw(plain_senha.encode('utf-8'), hashed_senha.encode('utf-8'))

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

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
    
#--------------------------------------------------

#-----------------Usuário e autenticação ---------------
user_db = {
    "admin" : {
        "username": "admin",
        "password": hash_senha("1234"),
        "role": "admin"
    }
}
#-------------------------------------------

#------------------Rotas FastAPI-------------------
@app.post("/login", response_model = token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = user_db.get(form.username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    
    if not verify_senha(form.password, user["password"]):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    dados_token = {
        "sub": form.username,
        "role": user["role"]
    }

    token_expire = timedelta(minutes = 30)

    access_token = criar_token(data = dados_token, expire_time = token_expire)
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/produtos/post", response_model = ProdutoCriadoResponse)
async def adicionar_produto(produto: produto, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    verificar_token(token)
    
    novo = produtodb(
        nome = produto.nome,
        preco_unitario = produto.preco_unitario,
        quantidade = produto.quantidade,
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    
    return {"msg": "Produto adicionado com sucesso", "produto": novo}

@app.put("/produtos/{produto_id}")
async def atualizar_produto(produto_id : int, produto: produto, db : Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    verificar_token(token)

    produto_db = db.query(produtodb).filter(produtodb.id == produto_id).first()

    if not produto_db:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    produto_db.nome = produto.nome
    produto_db.preco_unitario = produto.preco_unitario
    produto_db.quantidade = produto.quantidade

    db.commit()
    db.refresh(produto_db)

    return {"message": "Produto atualizado com sucesso","produto" : produto_db}

@app.get("/produtos", response_model = List[produtoresponse])
async def read_produtos(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verificar_token(token)
    produtos = db.query(produtodb).all()
    return produtos

@app.delete("/produto/delete/{produto_id}")
async def deletar_produto(produto_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verificar_token(token)
    
    produto = db.query(produtodb).filter(produtodb.id == produto_id).first()
        
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db.delete(produto)
    db.commit()
    return {"message": "Produto deletado com sucesso"}

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

