import concurrent.futures
import requests
import time

def disparar_requisicao(thread_id: int, owner_id: str) -> int:
    """
    Função unitária executada por cada thread.
    """
    url = f"http://127.0.0.1:8080/v2/webhook/mailbox/{owner_id}"
    payload = {"nome": f"Cliente_Teste_{thread_id}"}
    
    try:
        response = requests.post(url, data=payload, timeout=5)
        return response.status_code
    except requests.exceptions.RequestException:
        return 0

def executar_teste_paralelo(total_requisicoes: int, owner_id: str):
    """
    Gera um pool de threads para executar disparos paralelos contra o Gateway.
    """
    print(f"[*] Iniciando bateria de testes: {total_requisicoes} requisições simultâneas.")
    inicio = time.time()
    
    # O ThreadPoolExecutor gerencia a criação e destruição das threads do sistema operacional
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Submete as tarefas para o pool e armazena os objetos "Future"
        futuros = [
            executor.submit(disparar_requisicao, i, owner_id) 
            for i in range(total_requisicoes)
        ]
        
        # Coleta os resultados à medida que as threads terminam
        for futuro in concurrent.futures.as_completed(futuros):
            resultados.append(futuro.result())

    fim = time.time()
    tempo_total = fim - inicio
    
    sucessos = resultados.count(200)
    falhas = len(resultados) - sucessos
    
    print(f"\n[+] Teste Concluído em {tempo_total:.2f} segundos.")
    print(f"[+] Requerimentos bem-sucedidos (HTTP 200): {sucessos}")
    print(f"[-] Falhas (Timeouts/Erros): {falhas}")

if __name__ == "__main__":
    ALVO_ID = "123e4567-e89b-12d3-a456-426614174000"
    
    # Simula 100 usuários lendo o QR Code simultaneamente
    executar_teste_paralelo(total_requisicoes=100, owner_id=ALVO_ID)