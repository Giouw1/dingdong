#the logic is for this to requests to test our architecture,
#This is the ultimate abstraction of it all
import requests

def simular_leitura_qr_code(owner_id: str, nome_anunciador: str) -> None:
    """
    Simula a emissão da requisição HTTP gerada pela leitura de um QR code.
    """
    url = f"http://127.0.0.1:8080/v2/webhook/mailbox/{owner_id}"
    
    # O dicionário 'data' é serializado automaticamente pela biblioteca requests
    # como 'application/x-www-form-urlencoded'
    payload = {
        "nome": nome_anunciador
    }
    
    try:
        print(f"[*] Enviando POST para: {url}")
        print(f"[*] Payload: {payload}")
        
        response = requests.post(url, data=payload, timeout=5)
        
        print(f"[+] Status Code: {response.status_code}")
        print(f"[+] Resposta do Servidor: {response.json()}\n")
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Erro de conexão: {e}\n")

if __name__ == "__main__":
    # Teste 1: Requisição padrão
    simular_leitura_qr_code(owner_id="123e4567-e89b-12d3-a456-426614174000", nome_anunciador="ClienteA")


#curl -X POST "http://127.0.0.1:8000/api/v1/mailbox/123e4567/notify" \
     #-H "Content-Type: application/x-www-form-urlencoded" \
    # -d "nome=ClienteA"