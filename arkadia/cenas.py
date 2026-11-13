import os
import sys
import json
from .itens import adicionar_ao_inventario, remover_do_inventario
from .personagem import ganhar_xp

if getattr(sys, 'frozen', False):
    _base_exe = os.path.dirname(sys.executable)
    _base_meipass = getattr(sys, '_MEIPASS', _base_exe)
    DIRETORIO_DATA = os.path.join(_base_exe, "data")
    if not os.path.exists(DIRETORIO_DATA):
        DIRETORIO_DATA = os.path.join(_base_meipass, "data")
else:
    DIRETORIO_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

ARQUIVO_CENAS = os.path.join(DIRETORIO_DATA, "cenas.json")

_CENAS_CACHE = None

def carregar_cenas():
    global _CENAS_CACHE
    if _CENAS_CACHE is None:
        try:
            with open(ARQUIVO_CENAS, "r", encoding="utf-8") as f:
                _CENAS_CACHE = json.load(f)
        except Exception as e:
            print(f"[Erro] Falha ao carregar cenas: {e}")
            _CENAS_CACHE = {}
    return _CENAS_CACHE

def obter_cena(cena_id):
    cenas = carregar_cenas()
    return cenas.get(cena_id)

def verificar_requisito_opcao(opcao, jogador):
    if not jogador:
        return True

    flags = jogador.get("flags", {})
    inv = jogador.get("inventario", [])

    if "requer_flag" in opcao:
        if not flags.get(opcao["requer_flag"], False):
            return False

    if "bloqueia_flag" in opcao:
        if flags.get(opcao["bloqueia_flag"], False):
            return False

    if "requer_ouro" in opcao:
        if jogador.get("ouro", 0) < opcao["requer_ouro"]:
            return False

    if "requer_reputacao" in opcao:
        if jogador.get("reputacao", 0) < opcao["requer_reputacao"]:
            return False

    if "requer_item" in opcao:
        req = opcao["requer_item"]
        item_id = req.get("item")
        qtd = req.get("quantidade", 1)
        if inv.count(item_id) < qtd:
            return False

    return True

CENAS_REPETIVEIS = {
    "fogueira_descanso",
    "comprar_pocao_vida",
    "comprar_pocao_mana",
    "comprar_antidoto",
    "vender_pele",
    "vender_presa",
    "vender_fragmento",
    "entrega_peles_lobo",
    "recrutar_elora"
}

def executar_efeitos_cena(cena, jogador, cena_id=None):
    if not jogador or "efeitos" not in cena:
        return []

    visitadas = jogador.setdefault("cenas_recompensadas", [])
    if cena_id and cena_id not in CENAS_REPETIVEIS:
        if cena_id in visitadas:
            return []
        visitadas.append(cena_id)

    mensagens = []
    flags = jogador.setdefault("flags", {})

    for ef in cena["efeitos"]:
        if "set_flag" in ef:
            flag_nome = ef["set_flag"]
            flag_val = ef.get("valor", True)
            flags[flag_nome] = flag_val

        if "add_ouro" in ef:
            qtd = ef["add_ouro"]
            jogador["ouro"] = max(0, jogador.get("ouro", 0) + qtd)
            if qtd > 0:
                mensagens.append(f"+{qtd} Moedas de Ouro.")

        if "add_xp" in ef:
            msgs_xp = ganhar_xp(jogador, ef["add_xp"])
            mensagens.extend(msgs_xp)

        if "add_reputacao" in ef:
            jogador["reputacao"] = jogador.get("reputacao", 0) + ef["add_reputacao"]

        if "add_corrupcao" in ef:
            jogador["corrupcao"] = jogador.get("corrupcao", 0) + ef["add_corrupcao"]

        if "add_item" in ef:
            adicionar_ao_inventario(jogador, ef["add_item"], 1)

        if "remover_item" in ef:
            rem = ef["remover_item"]
            remover_do_inventario(jogador, rem.get("item"), rem.get("quantidade", 1))

        if "add_missao" in ef:
            m_id = ef["add_missao"]
            if m_id not in jogador.setdefault("missoes", []):
                jogador["missoes"].append(m_id)

        if "concluir_missao" in ef:
            m_id = ef["concluir_missao"]
            if m_id in jogador.setdefault("missoes", []):
                jogador["missoes"].remove(m_id)
            if m_id not in jogador.setdefault("missoes_concluidas", []):
                jogador["missoes_concluidas"].append(m_id)

        if "add_mana_max" in ef:
            jogador["mana_max_base"] = jogador.get("mana_max_base", 40) + ef["add_mana_max"]
            jogador["mana_max"] = jogador.get("mana_max", 40) + ef["add_mana_max"]

        if "curar_tudo" in ef and ef["curar_tudo"]:
            jogador["vida"] = jogador["vida_max"]
            jogador["mana"] = jogador["mana_max"]
            jogador["status"] = {}

    return mensagens
