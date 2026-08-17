"""
    A ideia é que esse Gateway vai receber as requisições do usuário de REGISTRAR, LOGAR, LER
    
    """
#Dependências à serem injetadas pelo main nas rotas
from infrastructure.ownerrepo import InMemoryOwnerRepo, get_owner_repo, get_id_generator, MockID_Generator
from infrastructure.mailbox import InMemoryMailbox, get_main_mailbox
from owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases, RegistrationError,ResourceNotFoundError, AuthenticationError
from infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import APIRouter, Depends, HTTPException,status, Header, Query, Response, Cookie
from domain.entities import UserData,NotificationPayload, OwnerID, Nickname
from typing import List, Any, Dict
import logging
from hashlib import  md5
from configs.config import get_overall_settings, OverallSettings

router = APIRouter()
security = HTTPBasic()

@router.post("/register",response_model=str,tags=["Registro de usuário"])
async def register(userdata: HTTPBasicCredentials = Depends(security),
                usecases: OwnerUseCases = Depends(get_owner_use_cases),):
    try:
        username_extraido = userdata.username
        password_extraido = userdata.password
        true_user_data = UserData(username=username_extraido,password=password_extraido)
        id = usecases.register(user_data=true_user_data)
        #Errado, a cripto deve ser feita internamente   
        usecases.register_nickname(owner_id=id, nickname=md5((str(username_extraido)+str(password_extraido)).encode("utf-8")).hexdigest())
        return "Successful registration"
    except RegistrationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,   
        )

@router.post("/login",response_model=Nickname,tags=["Rota de login"])
async def login(response:Response,
                userdata: HTTPBasicCredentials = Depends(security),
                store: OpaqueTokenStore = Depends(get_opaque_token_store),
                usecases: OwnerUseCases = Depends(get_owner_use_cases),
                settings: OverallSettings = Depends(get_overall_settings)
                ):
    #Depois averiguar problemas com esse login aqui, possivelmente perigos de login
    try:
        username_extraido = userdata.username
        password_extraida = userdata.password
        owner_id = usecases.login(user_data=UserData(username=username_extraido,password=password_extraida))
        nickname = usecases.retrieve_nickname(owner_id=owner_id)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="There isn't such User."
        )
    opaque_token = store.generate_and_store(owner_id)
    response.set_cookie(
        key="session_id",
        value=opaque_token,
        httponly=True,  # Forbids JavaScript access (mitigates XSS)
        secure=settings.IS_PRODUCTION,    # Mandates transmission strictly over HTTPS
        samesite="lax", # Mitigates Cross-Site Request Forgery (CSRF)
        max_age=3600    # Hard expiration in seconds (1 hour)
    )
    return nickname

@router.get("/notifications",response_model= List[NotificationPayload]|List[Any], tags=["Verificar notificações"])
async def get_notifications(opaque_owner_id: str = Cookie(..., alias="session_id"),
                            msg_amount:int= Query(default=1, description="Message amount",ge=1),
                            offset:int=Query(default=0, description="Message 'offset'",ge=0),
                            store: OpaqueTokenStore = Depends(get_opaque_token_store),
                            usecases: OwnerUseCases = Depends(get_owner_use_cases)):
    if len(opaque_owner_id) != 43:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Invalid credential format{opaque_owner_id}")
    token = store.get_token(opaque_token=opaque_owner_id) 
    if (token == None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED    , 
            detail="User not logged in: session expired"
        )
    try:
        return usecases.get_notifications(owner_id=token,msg_amount=msg_amount,offset=offset)
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="There isn't such User."
        )

@router.post("/logout",response_model=str,tags=["Logout de usuário"])
async def logout(response:Response,
                opaque_owner_id: str = Cookie(..., alias="session_id"),
                store: OpaqueTokenStore = Depends(get_opaque_token_store),
                settings: OverallSettings = Depends(get_overall_settings)
                ):
    removal = store.remove_token(opaque_token=opaque_owner_id)
    if removal == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    response.delete_cookie(
        key="session_id",
        path="/",
        httponly=True,
        secure=settings.IS_PRODUCTION,     
        samesite="lax"   
    )
    return "Successful logout"




@router.post("/nickname/register",response_model=str,tags=["Registro de nickname"])
async def create_nick(opaque_owner_id: str = Cookie(..., alias='session_id'),
                    nickname:str = Query(...,alias="Nickname", description="Include in the URL the nickname"),
                    usecases:OwnerUseCases =Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    if owner_id == None:
        logging.error("User not authenticated tried to log in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
        )
    try:
        usecases.register_nickname(owner_id=owner_id,nickname=nickname)
        return "Sucessful register"
    except RegistrationError as e:
        if str(e) == "There is already such nickname":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= "Try to choose another nickname")
    except ResourceNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
@router.post("/nickname/change",response_model=str,tags=["Mudar nickname"])
async def change_nick(opaque_owner_id: str = Cookie(..., alias="session_id"),
                    nickname:str = Query(...,alias="Nickname", description="Include in the URL the nickname"),
                    usecases:OwnerUseCases =Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    if owner_id == None:
        logging.error("User not authenticated tried to log in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
        )
    try:
        usecases.change_nickname(owner_id=owner_id,nickname=nickname)
        return "Sucessful registration"
    except RegistrationError as e:
        if str(e) == "There is already such nickname":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= "Try to choose another nickname")
    except ResourceNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@router.get("/nickname/retrieve",response_model=str,tags=["Obter nickname"])
async def retrieve_nick(opaque_owner_id: str = Cookie(..., alias="session_id"),
                    usecases:OwnerUseCases =Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    if owner_id == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
        )
    try:
        return usecases.retrieve_nickname(owner_id=owner_id)
    except ResourceNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details="There is no user/nickname attached to the user")

