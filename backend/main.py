from app.infrastructure.inmemorymailbox import InMemoryMailbox, get_main_mailbox
from app.infrastructure.inmemoryownerrepo import InMemoryOwnerRepo, MockID_Generator, get_owner_repo, get_id_generator
from app.infrastructure.sqllitemailbox import SQLite3Mailbox
from app.infrastructure.sqlliteownerrepo import SQLite3OwnerRepo, SQLite3IDGenerator
from app.infrastructure.sqlite3adapter import Sqlite3Adapter
from app.infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store
from app.owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases
from app.owner_path.owner_gateway import router as owner_router
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.notification_path.notif_gateway import notif_router
from app.notification_path.notif_use_cases import Notificator_UseCases, get_notifier_use_cases
from configs.config import get_db_settings, get_network_settings, get_log_settings, get_env_settings

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


db_settings = get_db_settings()
network_settings = get_network_settings()
env_settings = get_env_settings()
app = FastAPI()
#Parte de CORS, verificar e usar nas configurações antes de jogar a público.
origins = [
"*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Allows specified domains
    allow_credentials=True,         # Allows cookies and credentials
    allow_methods=["*"],            # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],            # Allows all request headers
)
if db_settings.IN_MEMORY:
    main_repo_instance = InMemoryMailbox()
    owner_repo_instance = InMemoryOwnerRepo()
    id_generator_instance = MockID_Generator(owner_repo_instance)
else:
    main_repo_instance = SQLite3Mailbox(db_path=db_settings.DB_PATH)
    owner_repo_instance = SQLite3OwnerRepo(db_path=db_settings.DB_PATH)
    id_generator_instance = SQLite3IDGenerator(repository=owner_repo_instance)
    
token_store_instance = OpaqueTokenStore()
owner_use_cases = OwnerUseCases(notifmailbox=main_repo_instance, ownermailbox=owner_repo_instance, id_generator=id_generator_instance)
notificator_use_cases = Notificator_UseCases(ownermailbox=owner_repo_instance,notifmailbox=main_repo_instance)

app.dependency_overrides[get_notifier_use_cases] = lambda: notificator_use_cases
app.dependency_overrides[get_opaque_token_store] = lambda: token_store_instance
app.dependency_overrides[get_owner_use_cases] = lambda: owner_use_cases
app.dependency_overrides[get_env_settings] = lambda: env_settings
app.include_router(router=owner_router, prefix=network_settings.OWNER_ROUTE_PATH, tags=["Owners"])
app.include_router(router=notif_router,prefix=network_settings.NOTIF_ROUTE_PATH,tags=["Notifications"])

@app.get("/", status_code=status.HTTP_200_OK, response_class=FileResponse, tags=["Frontend"])
async def return_html_page():
    file_path = FRONTEND_DIR / "frontend.html"
    return FileResponse(path=file_path, media_type="text/html")

@app.get("/notify", status_code=status.HTTP_200_OK, response_class=FileResponse, tags=["Frontend"])
@app.get("/notify.html", status_code=status.HTTP_200_OK, response_class=FileResponse, tags=["Frontend"])
async def return_notify_page():
    file_path = FRONTEND_DIR / "notify.html"
    return FileResponse(path=file_path, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=network_settings.SERVER_HOST, port=network_settings.SERVER_PORT, reload=not (env_settings.IS_PRODUCTION))
