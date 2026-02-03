import pandas as pd
import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# --- CONFIGURAÇÕES VIA ENV ---
PLANILHA_NOME = os.getenv("PLANILHA_NOME")
PLANILHA_URL = os.getenv("PLANILHA_URL")

MEU_TELEFONE_PESSOAL = os.getenv("MEU_TELEFONE_PESSOAL")

WAHA_URL = os.getenv("WAHA_URL")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")
WAHA_SESSION = os.getenv("WAHA_SESSION")

LOG_PATH = os.getenv("LOG_PATH", "logs.txt")

headers = {
    "X-Api-Key": WAHA_API_KEY,
    "Content-Type": "application/json"
}

# --- LOG ---
def registrar_log(texto):
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] {texto}\n")

# --- ENVIO WHATSAPP ---
def enviar_mensagem(mensagem):
    chat_id = f"{MEU_TELEFONE_PESSOAL}@c.us"
    payload = {
        "session": WAHA_SESSION,
        "chatId": chat_id,
        "text": mensagem
    }
    try:
        response = requests.post(WAHA_URL, json=payload, headers=headers, timeout=15)
        return response.status_code in (200, 201)
    except Exception as e:
        registrar_log(f"ERRO API WAHA: {e}")
        return False

# --- CONTROLE DE DUPLICIDADE ---
def ids_ja_enviados():
    if not os.path.exists(LOG_PATH):
        return set()
    with open(LOG_PATH, "r", encoding="utf-8") as log:
        return set(l.strip() for l in log if l.strip())

def registrar_id_enviado(id_pergunta):
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"{id_pergunta}\n")

# --- DOWNLOAD PLANILHA ---
def baixar_planilha():
    arquivo_temp = "planilha_temp.xlsx"
    try:
        r = requests.get(PLANILHA_URL, timeout=30)
        r.raise_for_status()
        with open(arquivo_temp, "wb") as f:
            f.write(r.content)
        return arquivo_temp
    except Exception as e:
        registrar_log(f"ERRO ao baixar planilha: {e}")
        return None

# --- PROCESSAMENTO ---
def processa_planilha():
    arquivo_excel = baixar_planilha()
    if not arquivo_excel:
        return

    ids_enviados = ids_ja_enviados()

    try:
        df = pd.read_excel(arquivo_excel, sheet_name=PLANILHA_NOME, engine="openpyxl")
    except Exception as e:
        registrar_log(f"Erro ao abrir Excel: {e}")
        return

    for _, row in df.iterrows():
        id_pergunta = str(row.get("ID", "")).strip()
        duvida = str(row.get("Detalhe, por favor, a dúvida.", "")).strip()

        if not id_pergunta or id_pergunta.lower() == "nan":
            continue
        if id_pergunta in ids_enviados:
            continue
        if not duvida or duvida.lower() == "nan":
            continue

        nome = row.get("Nome1", "Não informado")
        municipio = row.get("Nome do Município", "Não informado")
        telefone = row.get("Telefone Celular / WhatsApp (com DDD e somente números)", "")
        email = row.get("E-mail", "")
        meio = str(row.get("Como gostaria de ser contactada/o para resposta?", "")).lower()

        if "email" in meio:
            contato = email
        elif "whatsapp" in meio:
            contato = telefone
        else:
            registrar_log(f"ID {id_pergunta} ignorado (meio inválido)")
            continue

        mensagem = (
            f"*NOVA DEMANDA (ID: {id_pergunta})*\n\n"
            f"*Nome:* {nome}\n"
            f"*Município:* {municipio}\n"
            f"*Contato:* {contato}\n\n"
            f"*Dúvida:*\n{duvida}"
        )

        if enviar_mensagem(mensagem):
            registrar_id_enviado(id_pergunta)
            print(f"Enviado ID {id_pergunta}")
            time.sleep(2)

if __name__ == "__main__":
    processa_planilha()
