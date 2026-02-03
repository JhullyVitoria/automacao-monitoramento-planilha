# automacao-monitoramento-planilha

# Notificador de formulários via WhatsApp (WA-HA)

Este projeto foi desenvolvido para automatizar o monitoramento de uma planilha de suporte vinculada a um projeto de extensão universitária.
Diariamente, usuários preenchiam um formulário com dúvidas e sugestões. O fluxo de trabalho exigia que um monitor acessasse a planilha manualmente pelo menos duas vezes ao dia para checar novas entradas. 
A solução foi gerar um script que monitora a planilha em intervalos definidos e notifica a equipe via WhatsApp assim que uma nova demanda é registrada.

## Funcionalidades:
- Lê respostas de uma planilha online
- Identifica novas demandas
- Envia notificações automáticas via WhatsApp
- Evita duplicidade usando controle por log

## Tecnologias
- Python: lógica central
- Pandas: tratamento de dados
- Docker: Utilizado para rodar a infraestrutura da API de forma isolada e rápida, garantindo que o ambiente de envio de mensagens esteja sempre pronto sem precisar de instalações complexas no Windows.
- WA-HA: Atua como o servidor que conecta o script Python ao WhatsApp, permitindo o envio das notificações de forma automatizada.

## Como funciona
1. O script baixa a versão mais recente da planilha
2. O Pandas compara os dados atuais com o arquivo de log
3. Se houver novas entradas, o script formata uma mensagem e dispara via API WA-HA
4. O log é atualizado para evitar duplicidade no próximo ciclo
5. Execução automatizada via Task Scheduler (Agendador de Tarefas do Windows)

## Observação
Este projeto utiliza uma API **não oficial** do WhatsApp, apenas para fins educacionais.
