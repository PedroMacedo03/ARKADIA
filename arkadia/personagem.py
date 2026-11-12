from .itens import recalcular_atributos

TABELA_SKILLS = {
    "Guerreiro": [
        {
            "id": "golpe_brutal",
            "nome": "Golpe Brutal",
            "nivel_req": 1,
            "custo_mp": 10,
            "elemento": "fisico",
            "mult_dano": 1.6,
            "bonus_flat": 14,
            "descricao": "Desfere um golpe devastador causando alto dano físico."
        },
        {
            "id": "postura_ferro",
            "nome": "Postura de Ferro",
            "nivel_req": 2,
            "custo_mp": 12,
            "tipo": "buff",
            "efeito_buff": {"defesa": 10, "duracao": 3},
            "descricao": "Endurece a guarda, aumentando a defesa em +10 por 3 turnos."
        },
        {
            "id": "grito_guerra",
            "nome": "Grito de Guerra",
            "nivel_req": 3,
            "custo_mp": 18,
            "elemento": "fisico",
            "mult_dano": 1.4,
            "bonus_flat": 10,
            "status": "atordoado",
            "duracao_status": 1,
            "descricao": "Bradado intimidador que fere e atordoa o inimigo por 1 rodada."
        }
    ],
    "Mago": [
        {
            "id": "bola_fogo",
            "nome": "Bola de Fogo",
            "nivel_req": 1,
            "custo_mp": 18,
            "elemento": "fogo",
            "mult_dano": 1.8,
            "bonus_flat": 18,
            "status": "queimadura",
            "duracao_status": 3,
            "descricao": "Conjura uma labareda que queima o inimigo por 3 rodadas."
        },
        {
            "id": "escudo_mana",
            "nome": "Escudo de Mana",
            "nivel_req": 2,
            "custo_mp": 15,
            "tipo": "buff",
            "efeito_buff": {"defesa": 12, "duracao": 2, "cura_imediata": 25},
            "descricao": "Cria uma barreira mágica que protege e restaura 25 HP."
        },
        {
            "id": "raio_arcano",
            "nome": "Raio Arcano",
            "nivel_req": 3,
            "custo_mp": 26,
            "elemento": "arcano",
            "mult_dano": 2.4,
            "bonus_flat": 25,
            "ignora_defesa": True,
            "descricao": "Dispara um feixe cósmico puro que ignora a armadura do alvo."
        }
    ],
    "Arqueiro": [
        {
            "id": "tiro_preciso",
            "nome": "Tiro Perfurante",
            "nivel_req": 1,
            "custo_mp": 12,
            "elemento": "fisico",
            "mult_dano": 1.7,
            "bonus_flat": 12,
            "critico_extra": 0.20,
            "descricao": "Disparo fulminante no ponto vital com alta chance crítica."
        },
        {
            "id": "flecha_venenosa",
            "nome": "Flecha Tóxica",
            "nivel_req": 2,
            "custo_mp": 14,
            "elemento": "sombrio",
            "mult_dano": 1.2,
            "bonus_flat": 8,
            "status": "veneno",
            "duracao_status": 3,
            "descricao": "Flecha banhada em veneno que drena vida a cada turno."
        },
        {
            "id": "chuva_flechas",
            "nome": "Tempestade de Flechas",
            "nivel_req": 3,
            "custo_mp": 22,
            "elemento": "fisico",
            "mult_dano": 2.2,
            "bonus_flat": 20,
            "descricao": "Dispara uma saraivada contínua cobrindo o campo de batalha."
        }
    ]
}

def criar_personagem(nome, classe):
    config = {
        "Guerreiro": {
            "vida": 135,
            "mana": 35,
            "ataque": 18,
            "defesa": 8,
            "arma": "espada_ferro",
            "armadura": "cota_malha"
        },
        "Mago": {
            "vida": 95,
            "mana": 105,
            "ataque": 11,
            "defesa": 4,
            "arma": "cajado_aprendiz",
            "armadura": "manto_arcano"
        },
        "Arqueiro": {
            "vida": 110,
            "mana": 55,
            "ataque": 15,
            "defesa": 6,
            "arma": "arco_simples",
            "armadura": "couro_cacador"
        }
    }[classe]

    jogador = {
        "nome": nome,
        "classe": classe,
        "nivel": 1,
        "xp": 0,
        "xp_proximo": 100,
        "vida": config["vida"],
        "vida_max": config["vida"],
        "mana": config["mana"],
        "mana_max": config["mana"],
        "mana_max_base": config["mana"],
        "ataque_base": config["ataque"],
        "defesa_base": config["defesa"],
        "ataque": config["ataque"],
        "defesa": config["defesa"],
        "ouro": 45,
        "reputacao": 0,
        "corrupcao": 0,
        "arma_equipada": config["arma"],
        "armadura_equipada": config["armadura"],
        "inventario": ["pocao_vida", "pocao_vida", "pocao_mana"],
        "status": {},
        "missoes": [],
        "missoes_concluidas": [],
        "checkpoint": "capitulo_1",
        "flags": {
            "ajudou_vila": False,
            "confia_mago": False,
            "entrou_ruinas": False,
            "conheceu_dragao": False,
            "companheiro_ativo": False
        }
    }

    recalcular_atributos(jogador)
    return jogador

def obter_skills_disponiveis(jogador):
    classe = jogador.get("classe", "Guerreiro")
    nivel = jogador.get("nivel", 1)
    skills = TABELA_SKILLS.get(classe, [])
    return [s for s in skills if s["nivel_req"] <= nivel]

def ganhar_xp(jogador, qtd):
    """
    Acrescenta XP e processa subida de nível.
    Retorna uma lista de strings notificando sobre melhorias ou novas skills.
    """
    jogador["xp"] += qtd
    mensagens = [f"+{qtd} XP obtidos."]

    while jogador["xp"] >= jogador["xp_proximo"]:
        jogador["xp"] -= jogador["xp_proximo"]
        jogador["nivel"] += 1
        jogador["xp_proximo"] = int(jogador["xp_proximo"] * 1.35)

        # Incremento de stats base
        jogador["vida_max"] += 15
        jogador["vida"] = jogador["vida_max"]
        jogador["mana_max_base"] += 10
        jogador["ataque_base"] += 4
        jogador["defesa_base"] += 2

        recalcular_atributos(jogador)
        jogador["mana"] = jogador["mana_max"]

        mensagens.append(f"★ NÍVEL {jogador['nivel']} ALCANÇADO! Status ampliados.")

        # Verifica se novas skills foram desbloqueadas
        for skill in TABELA_SKILLS.get(jogador["classe"], []):
            if skill["nivel_req"] == jogador["nivel"]:
                mensagens.append(f"Nova Habilidade Desbloqueada: {skill['nome']}!")

    return mensagens
