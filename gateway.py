from fastapi import FastAPI, Form, Request, HTTPException, Depends
#from services import NotificationService
from configs.network_config import settings
import uvicorn

app = FastAPI(title="QR Notification Gateway")

#def get_notification_service() -> NotificationService:
#   return NotificationService()

@app.post(settings.notify_route_path)
async def notify_mailbox(
    request: Request,
    owner_id: str,
    nome: str = Form(...),
    #service: NotificationService = Depends(get_notification_service)
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" not in content_type:
         raise HTTPException(status_code=415, detail="Unsupported Media Type")
    #Injetar aqui também a dependência
    #return service.process_notification(owner_id=owner_id, nome=nome)
    #Por enquanto, é apenas uma mensagem que a comunicação foi bem feita.
    return {
            "status": "success",
            "message": "Processamento delegado para a classe NotificationService",
            "data": {
                "owner_id": owner_id,
                "nome_anunciador": nome
            }
        }

if __name__ == "__main__":
    # A infraestrutura agora é injetada pelas configurações de ambiente
    uvicorn.run(
        "gateway:app", 
        host=settings.server_host, 
        port=settings.server_port, 
        reload=(settings.environment == "development")
    )