# Monitoramento de estoque mínimo

O projeto consulta o saldo no Linx DMS (Oracle), atualiza uma planilha Google Sheets e notifica os itens abaixo do estoque mínimo por e-mail e Google Chat.

## Estrutura da planilha

Em cada aba, a primeira linha é cabeçalho. Por padrão: **B Código**, **C Estoque mínimo**, **D Estoque atual**, **E Status** e **F Atualizado em**. Ajuste a numeração das colunas no `.env` se necessário.

## Configuração

1. Instale as dependências: `python -m pip install -r requirements.txt`.
2. Copie `.env.example` para `.env` e preencha os valores. Não versione o `.env`.
3. Salve a chave da conta de serviço Google no caminho definido por `GOOGLE_SERVICE_ACCOUNT_FILE` e compartilhe a planilha com o e-mail dessa conta.
4. Informe `STOCK_QUERY`: ela deve retornar **uma única coluna** (saldo atual) e aceitar os binds Oracle `:codigo` e `:empresa`.
5. Para Google Chat, crie um webhook de entrada no espaço e configure `GOOGLE_CHAT_WEBHOOK_URL`.

Exemplo de contrato da consulta (substitua tabela e campos pelos nomes do Linx DMS):

```sql
SELECT COALESCE(SUM(quantidade_disponivel), 0)
FROM estoque
WHERE codigo_item = :codigo
  AND empresa = :empresa
```

## Execução

```powershell
# Consulta, sem alterar a planilha nem enviar alertas
python main.py --dry-run

# Atualiza a planilha, sem alertas
python main.py --sem-alertas

# Atualiza e envia alertas quando houver itens abaixo do mínimo
python main.py
```

Para automatizar, agende `python main.py` no Agendador de Tarefas do Windows usando uma conta com acesso à rede e ao Oracle Client.
