import os
import json
from .itens import recalcular_atributos

def migrar_save_legado(dados):
    """
    Garante que saves de versões antigas (v0.5 ou v0.9 original) continuem
    100% funcionais no formato da v1.0.
    """
    if not isinstance(dados, dict):
        return None

    # Mapeamento de armas antigas em texto puro para IDs do catálogo
    mapa_armas = {
        "Espada de Ferro": "espada_ferro",
        "Cajado de Aprendiz": "cajado_aprendiz",
        "Arco Simples": "arco_simples",
        "Espada de Arkhor": "espada_arkhor",
        "Lâmina de Arkhor": "espada_arkhor"
    }

    mapa_armaduras = {
        "Cota de Malha": "cota_malha",
        "Manto Arcano": "manto_arcano",
        "Couro de Caçador": "couro_cacador",
        "Armadura do Guardião": "armadura_guardiao"
    }

    mapa_itens = {
        "Poção": "pocao_vida",
        "Pão": "pocao_vida",
        "Espada Quebrada": "espada_quebrada",
        "Pergaminho": "pergaminho_antigo"
    }

    # Converte arma/armadura
    if "arma_equipada" not in dados:
        arma_antiga = dados.get("arma", "")
        dados["arma_equipada"] = mapa_armas.get(arma_antiga, "espada_ferro")

    if "armadura_equipada" not in dados:
        armadura_antiga = dados.get("armadura", "")
        dados["armadura_equipada"] = mapa_armaduras.get(armadura_antiga, "cota_malha")

    # Converte inventário
    novo_inv = []
    for it in dados.get("inventario", []):
        novo_inv.append(mapa_itens.get(it, it))
    dados["inventario"] = novo_inv

    # Converte historia -> flags
    if "flags" not in dados:
        dados["flags"] = dados.get("historia", {})

    dados.setdefault("ouro", 40)
    dados.setdefault("reputacao", 0)
    dados.setdefault("corrupcao", 0)
    dados.setdefault("status", {})
    dados.setdefault("missoes", [])
    dados.setdefault("missoes_concluidas", [])
    dados.setdefault("checkpoint", "capitulo_1")

    # Garante stats base
    dados.setdefault("ataque_base", dados.get("ataque", 15))
    dados.setdefault("defesa_base", dados.get("defesa", 6))
    dados.setdefault("mana_max_base", dados.get("mana_max", 40))

    recalcular_atributos(dados)
    return dados

def salvar_progresso(jogador, caminho_arquivo):
    if not jogador:
        return False
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(jogador, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Erro] Falha ao salvar jogo em {caminho_arquivo}: {e}")
        return False

def carregar_progresso(caminho_arquivo):
    if not os.path.exists(caminho_arquivo) or os.path.getsize(caminho_arquivo) == 0:
        return None
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return migrar_save_legado(dados)
    except Exception as e:
        print(f"[Erro] Falha ao carregar save de {caminho_arquivo}: {e}")
        return None

def wipe_save(caminho_arquivo):
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write("")
        return True
    except Exception as e:
        print(f"[Erro] Falha ao realizar wipe em {caminho_arquivo}: {e}")
        return False
