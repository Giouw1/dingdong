## Pontos de desenvolvimento
# Atual:
Gateway da notificação.
Mudar os retornos dos gateways de user-- Sem "Sucessful alguma coisa mais"
Fazer os configs corretamente
# RoadMAP
Fazer Javascript
Logging válido, em um file específico
Com isso feito, temos tudo feito, mudar as estruturas de dados(isso vai me ajudar com a integridade referencial: teste dos user_id), os mutexes. melhorar a estrutura de logging para dev e prod, e ser capaz de dar "nomes" de erros melhores. Usar cookies para lidar com os tokens de autorização, Hashear a senha lógico, e lidar com tratamento de strings, futuro problema

Jogar a semântica de erro para os casos de uso, como deveria ser (e não é)
Número de notificações vai ser interessante no use cases do owner (funciona bem para a aplicação), diferenciando entre read e unread. 
Limpar meu código: Lista:
 
Resolver o anti pattern do Dependency Injection levando à muitos factories.
# Dúvidas estruturais
# Futuro
Docker, plataforma de CI/CD bem estruturada (github actions).
HTML com javascript dps
Lidar com criação de contas infinitamente depois
Lidar com a mudança de username/password, com corrupção de dicionário
Hashing do password
Mexer com a leitura: sliding window com offset, lidas e não lidas: para otimizar a leitura