#Agora a ideia é criar o gateway do usuário?
#Main is going to set universal variables, as mailboxes db's, for example.


#Aqui instanciar as factories

from infrastructure.mailbox import InMemoryMailbox, get_main_mailbox
from infrastructure.ownerrepo import InMemoryOwnerRepo, MockID_Generator, get_owner_repo, get_id_generator
from infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store
from owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases
from owner_path.owner_gateway import router as owner_router
from fastapi import FastAPI
from configs.config import get_overall_settings
overallsettings = get_overall_settings()
app = FastAPI()
main_repo_instance = InMemoryMailbox()
owner_repo_instance = InMemoryOwnerRepo()
id_generator_instance = MockID_Generator(owner_repo_instance)
token_store_instance = OpaqueTokenStore()
owner_use_cases = OwnerUseCases(notifmailbox=main_repo_instance, ownermailbox=owner_repo_instance, id_generator=id_generator_instance)

app.dependency_overrides[get_opaque_token_store] = lambda: token_store_instance
app.dependency_overrides[get_owner_use_cases] = lambda: owner_use_cases
app.dependency_overrides[get_overall_settings] = lambda:overallsettings
app.include_router(owner_router, prefix="/owner", tags=["Owners"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
