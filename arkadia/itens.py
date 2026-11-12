import json
import os

DIRETORIO_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ARQUIVO_ITENS = os.path.join(DIRETORIO_DATA, "itens.json")

_ITENS_CACHE = None

def carregar_catalogo_itens():
    global _ITENS_CACHE
    if _ITENS_CACHE is None:
        try:
            with open(ARQUIVO_ITENS, "r", encoding="utf-8") as f:
                _ITENS_CACHE = json.load(f)
        except Exception as e:
            print(f"[Aviso] Falha ao carregar {ARQUIVO_ITENS}: {e}")
            _ITENS_CACHE = {}
    return _ITENS_CACHE

def obter_item(item_id):
    catalogo = carregar_catalogo_itens()
    return catalogo.get(item_id, {
        "nome": item_id,
        "tipo": "comum",
        "descricao": "Item desconhecido."
    })

def obter_nome_item(item_id):
    item = obter_item(item_id)
    return item.get("nome", item_id)

def adicionar_ao_inventario(jogador, item_id, quantidade=1):
    """
    Adiciona itens ao inventário do jogador.
    Retorna (True, mensagem) se bem-sucedido, ou (False, mensagem) se cheio.
    """
    if "inventario" not in jogador:
        jogador["inventario"] = []

    # Itens de missão e materiais sempre podem ser carregados
    info = obter_item(item_id)
    tipo = info.get("tipo", "comum")
    
    LIMITE_SLOTS = 16
    if tipo not in ("missao", "material") and len(jogador["inventario"]) >= LIMITE_SLOTS:
        return False, "Inventário cheio!"

    for _ in range(quantidade):
        jogador["inventario"].append(item_id)
    
    nome = obter_nome_item(item_id)
    return True, f"+{quantidade}x {nome} adicionado ao inventário."

def remover_do_inventario(jogador, item_id, quantidade=1):
    if "inventario" not in jogador:
        return False
    
    removidos = 0
    for _ in range(quantidade):
        if item_id in jogador["inventario"]:
            jogador["inventario"].remove(item_id)
            removidos += 1
        else:
            break
    return removidos == quantidade

def equipar_item(jogador, item_id):
    info = obter_item(item_id)
    tipo = info.get("tipo")
    if tipo == "arma":
        # Guarda arma antiga no inventário se houver
        if jogador.get("arma_equipada"):
            jogador["inventario"].append(jogador["arma_equipada"])
        jogador["arma_equipada"] = item_id
        if item_id in jogador["inventario"]:
            jogador["inventario"].remove(item_id)
        recalcular_atributos(jogador)
        return True, f"Você empunhou {info.get('nome')}."
    elif tipo == "armadura":
        if jogador.get("armadura_equipada"):
            jogador["inventario"].append(jogador["armadura_equipada"])
        jogador["armadura_equipada"] = item_id
        if item_id in jogador["inventario"]:
            jogador["inventario"].remove(item_id)
        recalcular_atributos(jogador)
        return True, f"Você vestiu {info.get('nome')}."
    return False, "Este item não pode ser equipado."

def recalcular_atributos(jogador):
    """
    Recalcula o Ataque e a Defesa somando os bônus base com equipamentos.
    """
    atk_base = jogador.get("ataque_base", 15)
    def_base = jogador.get("defesa_base", 6)
    mana_max_base = jogador.get("mana_max_base", 50)

    bonus_atk = 0
    bonus_def = 0
    bonus_mana = 0

    if jogador.get("arma_equipada"):
        arma = obter_item(jogador["arma_equipada"])
        bonus_atk += arma.get("ataque", 0)
        bonus_mana += arma.get("mana_max", 0)

    if jogador.get("armadura_equipada"):
        armadura = obter_item(jogador["armadura_equipada"])
        bonus_def += armadura.get("defesa", 0)
        bonus_mana += armadura.get("mana_max", 0)

    jogador["ataque"] = atk_base + bonus_atk
    jogador["defesa"] = def_base + bonus_def
    jogador["mana_max"] = mana_max_base + bonus_mana
    jogador["mana"] = min(jogador["mana"], jogador["mana_max"])

def usar_consumivel(jogador, item_id):
    if item_id not in jogador.get("inventario", []):
        return False, "Você não possui este item."

    info = obter_item(item_id)
    if info.get("tipo") != "consumivel":
        return False, "Este item não é consumível."

    mensagens = []
    if "cura_vida" in info:
        cura = info["cura_vida"]
        jogador["vida"] = min(jogador["vida_max"], jogador["vida"] + cura)
        mensagens.append(f"+{cura} HP")

    if "cura_mana" in info:
        recup = info["cura_mana"]
        jogador["mana"] = min(jogador["mana_max"], jogador["mana"] + recup)
        mensagens.append(f"+{recup} MP")

    if "cura_status" in info and "status" in jogador:
        for st in info["cura_status"]:
            if st in jogador["status"]:
                del jogador["status"][st]
                mensagens.append(f"Curou {st.capitalize()}")

    jogador["inventario"].remove(item_id)
    return True, f"Usou {info.get('nome')}: " + ", ".join(mensagens)
