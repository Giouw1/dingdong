#Dependências à serem injetadas pelo main nas rotas
from app.infrastructure.inmemoryownerrepo import InMemoryOwnerRepo, get_owner_repo, get_id_generator, MockID_Generator
from app.infrastructure.inmemorymailbox import InMemoryMailbox, get_main_mailbox
from app.owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases, RegistrationError,ResourceNotFoundError, AuthenticationError
from app.infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store
from app.infrastructure.inmemoryeventbus import get_main_event_bus
from app.domain.event_bus import EventBusInterface

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Response, Cookie
import asyncio
from fastapi.responses import StreamingResponse

  
from dataclasses import is_dataclass, asdict
from typing import List, Any, Dict
from pydantic import BaseModel
import logging
from configs.config import get_env_settings, EnvSettings
import json

router = APIRouter()
security = HTTPBasic()



@router.post("/register", status_code=status.HTTP_204_NO_CONTENT, tags=["Registro de usuário"])
async def register(userdata: HTTPBasicCredentials = Depends(security),
                usecases: OwnerUseCases = Depends(get_owner_use_cases)):
    try:
        username_extraido = userdata.username
        password_extraido = userdata.password
        id = usecases.register(username=username_extraido,password=password_extraido)
    except RegistrationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,   
        )


@router.post("/login", response_model=str|None, tags=["Rota de login"])
async def login(response: Response,
                userdata: HTTPBasicCredentials = Depends(security),
                store: OpaqueTokenStore = Depends(get_opaque_token_store),
                usecases: OwnerUseCases = Depends(get_owner_use_cases),
                settings: EnvSettings = Depends(get_env_settings)
                ):
    try:
        username_extraido = userdata.username
        password_extraida = userdata.password
        owner_id = usecases.login(username=username_extraido, password=password_extraida)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="There isn't such User."
        )
    opaque_token = store.generate_and_store(owner_id)
    response.set_cookie(
        key="session_id",
        value=opaque_token,
        path="/",
        httponly=True,  # Forbids JavaScript access (mitigates XSS)
        secure=settings.IS_PRODUCTION,    # Mandates transmission strictly over HTTPS
        samesite="none" if settings.IS_PRODUCTION else "lax" , # Mitigates Cross-Site Request Forgery (CSRF)
        max_age=3600    # Hard expiration in seconds (1 hour)
    )
    try:
        nickname = usecases.retrieve_nickname(owner_id=owner_id)
        return nickname
    except ResourceNotFoundError:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 



@router.get("/notifications", response_model=List[Any]|None, tags=["Verificar notificações"])
async def get_notifications(response: Response,
                            opaque_owner_id: str = Cookie(..., alias="session_id"),
                            msg_amount: int = Query(default=1, description="Message amount", ge=1),
                            offset: int = Query(default=0, description="Message 'offset'", ge=0),
                            store: OpaqueTokenStore = Depends(get_opaque_token_store),
                            usecases: OwnerUseCases = Depends(get_owner_use_cases)):
    if len(opaque_owner_id) != 43:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Invalid credential format{opaque_owner_id}")
    token = store.get_token(opaque_token=opaque_owner_id) 
    if (token == None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not logged in: session expired."
        )
    try:
        return usecases.get_notifications(owner_id=token, msg_amount=msg_amount, offset=offset)
    except ResourceNotFoundError:
        response.status_code = status.HTTP_204_NO_CONTENT

@router.get("/stream_notifications", status_code=status.HTTP_200_OK, tags= ["SSE stream de dados"])
async def notification_event_stream(opaque_owner_id:str=Cookie(..., alias="session_id"),
                                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                                    settings: EnvSettings = Depends(get_env_settings),
                                    event_bus: EventBusInterface = Depends(get_main_event_bus),
                                    ):
    #Get true owner id and validate it
    owner_id= store.get_token(opaque_token=opaque_owner_id)
    if owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in: session expired."
        )
    #subscribe to the bus
    queue = event_bus.subscribe(topic=owner_id)
    #Initial stream handshake
    
    # 3. Define the generator that yields events as they arrive
    async def event_generator():
        yield ": connected\n\n"

        try:
            while True:
                # stops until queue gets something
                notification = await queue.get()
                if store.get_token(opaque_token=opaque_owner_id):       
                    # I have to do this whole checking to do the "StreamingResponse"
                    if is_dataclass(notification):
                        payload_str = json.dumps(asdict(notification), default=str)
                    elif isinstance(notification, str):
                        payload_str = notification
                    else:
                        payload_str = json.dumps(notification, default=str)

                      # SSE protocol format requires 'data: <content>\n\n'
                    yield f"data: {payload_str}\n\n"
                else:
                    break
        except asyncio.CancelledError:
            # If client disconnects, cancels
            pass
        finally:
            # Guarantees that when the connection drops, this queue is cleaned up from RAM
            event_bus.unsubscribe(owner_id, queue)
            # 4. Return the streaming response
    return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disables buffering if you use Nginx in production
            }
        )

  

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["Logout de usuário"])
async def logout(response: Response,
                opaque_owner_id: str = Cookie(..., alias="session_id"),
                store: OpaqueTokenStore = Depends(get_opaque_token_store),
                settings: EnvSettings = Depends(get_env_settings),
                ):
    removal = store.remove_token(opaque_token=opaque_owner_id)
    if removal == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session already expired, logged out smoothly."
)
    
    response.delete_cookie(
        key="session_id",
        path="/",
        httponly=True,
        secure=settings.IS_PRODUCTION,     
        samesite="lax"   
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.post("/nickname/register", status_code=status.HTTP_204_NO_CONTENT, tags=["Registro de nickname"])
async def create_nick(opaque_owner_id: str = Cookie(..., alias='session_id'),
                    nickname: str = Query(..., alias="Nickname", description="Include in the URL the nickname"),
                    usecases: OwnerUseCases = Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    if owner_id == None:
        logging.error("User not authenticated tried to log in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired, log in again."

        )
    try:
        usecases.register_nickname(owner_id=owner_id, nickname=nickname)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except RegistrationError as e:
        if str(e) == "There is already such nickname":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Try to choose another nickname")
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/nickname/change", status_code=status.HTTP_204_NO_CONTENT, tags=["Mudar nickname"])
async def change_nick(opaque_owner_id: str = Cookie(..., alias="session_id"),
                    nickname: str = Query(..., alias="Nickname", description="Include in the URL the nickname"),
                    usecases: OwnerUseCases = Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    if owner_id == None:
        logging.error("User not authenticated tried to log in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired, log in again."
        )
    try:
        usecases.change_nickname(owner_id=owner_id, nickname=nickname)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except RegistrationError as e:
        if str(e) == "There is already such nickname":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Try to choose another nickname")
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/nickname/retrieve", response_model=str, tags=["Obter nickname"])
async def retrieve_nick(opaque_owner_id: str = Cookie(..., alias="session_id"),
                    usecases: OwnerUseCases = Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    if owner_id == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
        )
    try:
        return usecases.retrieve_nickname(owner_id=owner_id)
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no nickname attached to the user: please register one")

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, tags=["Deletar usuário"])
async def delete_user(userdata: HTTPBasicCredentials = Depends(security),
                    opaque_owner_id: str = Cookie(..., alias="session_id"),
                    usecases: OwnerUseCases = Depends(get_owner_use_cases),
                    store: OpaqueTokenStore = Depends(get_opaque_token_store),
                    ):
    owner_id = store.get_token(opaque_owner_id)
    username = userdata.username
    password = userdata.password
    if owner_id == None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
    )
    try:
        retrieval = usecases.delete_user(username=username,password=password,owner_id=owner_id)
        store.remove_token(opaque_token=opaque_owner_id)
        return retrieval
    except AuthenticationError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot exclude a login different than yours")
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "You cannot exclude a non existant user")