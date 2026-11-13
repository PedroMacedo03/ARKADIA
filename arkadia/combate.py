import os
import sys
import json
import random
from .itens import obter_item, adicionar_ao_inventario
from .personagem import ganhar_xp

if getattr(sys, 'frozen', False):
    _base_exe = os.path.dirname(sys.executable)
    _base_meipass = getattr(sys, '_MEIPASS', _base_exe)
    DIRETORIO_DATA = os.path.join(_base_exe, "data")
    if not os.path.exists(DIRETORIO_DATA):
        DIRETORIO_DATA = os.path.join(_base_meipass, "data")
else:
    DIRETORIO_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

ARQUIVO_INIMIGOS = os.path.join(DIRETORIO_DATA, "inimigos.json")

_INIMIGOS_CACHE = None

def carregar_inimigos():
    global _INIMIGOS_CACHE
    if _INIMIGOS_CACHE is None:
        try:
            with open(ARQUIVO_INIMIGOS, "r", encoding="utf-8") as f:
                _INIMIGOS_CACHE = json.load(f)
        except Exception as e:
            print(f"[Erro] Falha ao carregar inimigos: {e}")
            _INIMIGOS_CACHE = {}
    return _INIMIGOS_CACHE

class MotorCombate:
    def __init__(self, jogador, inimigo_id, cenario, vitoria_callback, derrota_callback):
        self.jogador = jogador
        self.inimigo_id = inimigo_id
        self.cenario = cenario
        self.vitoria_callback = vitoria_callback
        self.derrota_callback = derrota_callback

        catalogo = carregar_inimigos()
        dados_base = catalogo.get(inimigo_id, {
            "nome": "Monstro Errante",
            "vida_base": 50,
            "vida_escala": 5,
            "ataque_base": 12,
            "ataque_escala": 1,
            "defesa": 4,
            "elemento": "fisico",
            "fraquezas": [],
            "resistencias": [],
            "xp_base": 50,
            "ouro_min": 10,
            "ouro_max": 20,
            "drops": [],
            "acoes": [{"id": "golpe", "nome": "Golpe", "dano_mult": 1.0, "aviso": "O inimigo prepara um ataque."}]
        })

        nivel = jogador.get("nivel", 1)
        self.inimigo = {
            "id": inimigo_id,
            "nome": dados_base["nome"],
            "vida_max": dados_base["vida_base"] + nivel * dados_base.get("vida_escala", 5),
            "vida": dados_base["vida_base"] + nivel * dados_base.get("vida_escala", 5),
            "ataque": dados_base["ataque_base"] + nivel * dados_base.get("ataque_escala", 1),
            "defesa": dados_base.get("defesa", 4),
            "elemento": dados_base.get("elemento", "fisico"),
            "fraquezas": dados_base.get("fraquezas", []),
            "resistencias": dados_base.get("resistencias", []),
            "xp_base": dados_base.get("xp_base", 50),
            "ouro_min": dados_base.get("ouro_min", 10),
            "ouro_max": dados_base.get("ouro_max", 20),
            "drops": dados_base.get("drops", []),
            "acoes": dados_base.get("acoes", []),
            "fases": dados_base.get("fases", []),
            "status": {},
            "buff_defesa_temp": 0,
            "buff_ataque_temp": 0
        }

        self.defendendo = False
        self.buff_defesa_jogador = 0
        self.duracao_buff_jogador = 0
        self.turno_atual = 1
        self.log_combate = [f"Um terrível {self.inimigo['nome']} se interpõe em seu caminho!"]
        self.intencao_inimiga = self._sortear_intencao()

    def _obter_acoes_disponiveis(self):
        if self.inimigo.get("fases"):
            proporcao_vida = self.inimigo["vida"] / self.inimigo["vida_max"]
            # Encontra a fase correspondente
            for fase in reversed(self.inimigo["fases"]):
                if proporcao_vida <= fase["limiar_hp"]:
                    return fase["acoes"]
        return self.inimigo.get("acoes", [])

    def _sortear_intencao(self):
        acoes = self._obter_acoes_disponiveis()
        if not acoes:
            return {"id": "ataque", "nome": "Investida", "dano_mult": 1.0, "aviso": "O inimigo avança para golpear!"}
        return random.choice(acoes)

    def calcular_multiplicador_elemental(self, elemento_ataque, fraquezas, resistencias):
        mult = 1.0
        if elemento_ataque in fraquezas:
            mult *= 1.50
        elif elemento_ataque in resistencias:
            mult *= 0.50
        return mult

    def acao_ataque_normal(self):
        # Arma equipada
        elemento_arma = "fisico"
        critico = 0.05
        if self.jogador.get("arma_equipada"):
            info = obter_item(self.jogador["arma_equipada"])
            elemento_arma = info.get("elemento", "fisico")
            critico += info.get("critico", 0.0)

        dano_base = random.randint(self.jogador["ataque"] - 3, self.jogador["ataque"] + 4)
        mult_elem = self.calcular_multiplicador_elemental(elemento_arma, self.inimigo["fraquezas"], self.inimigo["resistencias"])
        
        is_critico = random.random() < critico
        if is_critico:
            dano_base = int(dano_base * 1.5)

        defesa_total = self.inimigo["defesa"] + self.inimigo["buff_defesa_temp"]
        dano_final = max(2, int((dano_base * mult_elem) - (defesa_total // 2)))

        self.inimigo["vida"] -= dano_final
        crit_msg = " [GOLPE CRÍTICO!]" if is_critico else ""
        elem_msg = " (SUPER EFICAZ!)" if mult_elem > 1.0 else (" (Resistido)" if mult_elem < 1.0 else "")
        self.log_combate.append(f"Você atacou causando {dano_final} de dano{crit_msg}{elem_msg}.")

        if self.inimigo["vida"] <= 0:
            self.finalizar_combate(vitoria=True)
        else:
            self.turno_inimigo()

    def acao_usar_skill(self, skill):
        custo = skill.get("custo_mp", 10)
        if self.jogador["mana"] < custo:
            self.log_combate.append(f"Mana insuficiente para {skill['nome']} (Requer {custo} MP).")
            return False

        self.jogador["mana"] -= custo

        if skill.get("tipo") == "buff":
            efeito = skill["efeito_buff"]
            self.buff_defesa_jogador = efeito.get("defesa", 10)
            self.duracao_buff_jogador = efeito.get("duracao", 2)
            cura = efeito.get("cura_imediata", 0)
            if cura > 0:
                self.jogador["vida"] = min(self.jogador["vida_max"], self.jogador["vida"] + cura)
            self.log_combate.append(f"Habilidade: {skill['nome']} ativada! +{self.buff_defesa_jogador} Defesa.")
        else:
            elemento = skill.get("elemento", "fisico")
            mult_elem = self.calcular_multiplicador_elemental(elemento, self.inimigo["fraquezas"], self.inimigo["resistencias"])
            mult_dano = skill.get("mult_dano", 1.5)
            bonus_flat = skill.get("bonus_flat", 10)

            dano_base = int(self.jogador["ataque"] * mult_dano) + random.randint(bonus_flat - 3, bonus_flat + 5)
            defesa_inimigo = 0 if skill.get("ignora_defesa") else (self.inimigo["defesa"] + self.inimigo["buff_defesa_temp"])
            dano_final = max(3, int((dano_base * mult_elem) - (defesa_inimigo // 2)))

            self.inimigo["vida"] -= dano_final
            elem_msg = " (SUPER EFICAZ!)" if mult_elem > 1.0 else (" (Resistido)" if mult_elem < 1.0 else "")
            self.log_combate.append(f"{skill['nome']} causou {dano_final} de dano{elem_msg}!")

            # Aplica status se houver
            if "status" in skill:
                st = skill["status"]
                dur = skill.get("duracao_status", 2)
                self.inimigo["status"][st] = dur
                self.log_combate.append(f"O inimigo foi afligido por {st.upper()} por {dur} turnos!")

        if self.inimigo["vida"] <= 0:
            self.finalizar_combate(vitoria=True)
        else:
            self.turno_inimigo()
        return True

    def acao_defender(self):
        self.defendendo = True
        recuperado = random.randint(10, 16)
        self.jogador["mana"] = min(self.jogador["mana_max"], self.jogador["mana"] + recuperado)
        self.log_combate.append(f"Postura defensiva adotada. Recuperou {recuperado} MP.")
        self.turno_inimigo()

    def acao_usar_pocao_vida(self):
        if "pocao_vida" in self.jogador.get("inventario", []):
            self.jogador["inventario"].remove("pocao_vida")
            recup = 45
            self.jogador["vida"] = min(self.jogador["vida_max"], self.jogador["vida"] + recup)
            self.log_combate.append(f"Poção consumida. +{recup} HP restabelecidos.")
            self.turno_inimigo()
            return True
        elif "elixir_arkhor" in self.jogador.get("inventario", []):
            self.jogador["inventario"].remove("elixir_arkhor")
            self.jogador["vida"] = min(self.jogador["vida_max"], self.jogador["vida"] + 80)
            self.jogador["mana"] = min(self.jogador["mana_max"], self.jogador["mana"] + 50)
            self.log_combate.append("Elixir sagrado consumido! +80 HP e +50 MP restaurados.")
            self.turno_inimigo()
            return True
        else:
            self.log_combate.append("Você não possui poções de vida no inventário.")
            return False

    def acao_usar_pocao_mana(self):
        if "pocao_mana" in self.jogador.get("inventario", []):
            self.jogador["inventario"].remove("pocao_mana")
            recup = 35
            self.jogador["mana"] = min(self.jogador["mana_max"], self.jogador["mana"] + recup)
            self.log_combate.append(f"Poção de Mana consumida. +{recup} MP restabelecidos.")
            self.turno_inimigo()
            return True
        else:
            self.log_combate.append("Você não possui poções de mana.")
            return False

    def acao_usar_antidoto(self):
        if "antidoto" in self.jogador.get("inventario", []):
            self.jogador["inventario"].remove("antidoto")
            self.jogador["status"].clear()
            self.log_combate.append("Antídoto aplicado. Todos os status negativos foram curados!")
            self.turno_inimigo()
            return True
        else:
            self.log_combate.append("Você não possui antídotos no inventário.")
            return False

    def processar_status(self):
        # Status do Inimigo
        status_in = list(self.inimigo["status"].keys())
        for st in status_in:
            if st == "veneno":
                dano_dot = max(2, int(self.inimigo["vida_max"] * 0.07))
                self.inimigo["vida"] -= dano_dot
                self.log_combate.append(f"Veneno inflige {dano_dot} de dano contínuo ao inimigo.")
            elif st == "queimadura":
                dano_dot = max(3, int(self.inimigo["vida_max"] * 0.08))
                self.inimigo["vida"] -= dano_dot
                self.log_combate.append(f"Chamas queimam o inimigo causando {dano_dot} de dano!")
            
            self.inimigo["status"][st] -= 1
            if self.inimigo["status"][st] <= 0:
                del self.inimigo["status"][st]

        # Status do Jogador
        status_jog = list(self.jogador.get("status", {}).keys())
        for st in status_jog:
            if st == "veneno":
                dano_dot = 8
                self.jogador["vida"] -= dano_dot
                self.log_combate.append(f"Você sofre {dano_dot} de dano de veneno.")
            elif st == "queimadura":
                dano_dot = 10
                self.jogador["vida"] -= dano_dot
                self.log_combate.append(f"Chamas queimam sua pele causando {dano_dot} de dano!")
            elif st == "sangramento":
                dano_dot = 7
                self.jogador["vida"] -= dano_dot
                self.log_combate.append(f"O sangramento aberto drena {dano_dot} de vida.")

            self.jogador["status"][st] -= 1
            if self.jogador["status"][st] <= 0:
                del self.jogador["status"][st]

    def turno_companheiro(self):
        # Se Elora estiver ativa
        if self.jogador.get("flags", {}).get("companheiro_elora"):
            # 45% chance de curar ou desferir suporte
            if random.random() < 0.45:
                cura = random.randint(18, 30)
                self.jogador["vida"] = min(self.jogador["vida_max"], self.jogador["vida"] + cura)
                self.log_combate.append(f"[Suporte] Elora aplicou ervas curativas! (+{cura} HP)")

    def turno_inimigo(self):
        # Reduz buffs do inimigo
        self.inimigo["buff_defesa_temp"] = 0

        # Processa dano de status
        self.processar_status()

        if self.inimigo["vida"] <= 0:
            self.finalizar_combate(vitoria=True)
            return

        if self.jogador["vida"] <= 0:
            self.finalizar_combate(vitoria=False)
            return

        # Verifica se o inimigo está atordoado
        if self.inimigo["status"].get("atordoado", 0) > 0:
            self.log_combate.append(f"{self.inimigo['nome']} está atordoado e não pôde agir neste turno!")
            self.inimigo["status"]["atordoado"] -= 1
            self.turno_companheiro()
            self.intencao_inimiga = self._sortear_intencao()
            return

        # Executa a intenção que estava telegrafada
        acao = self.intencao_inimiga
        dano_mult = acao.get("dano_mult", 1.0)

        if dano_mult > 0.0:
            dano_bruto = int((self.inimigo["ataque"] + self.inimigo["buff_ataque_temp"]) * dano_mult) + random.randint(-2, 3)
            defesa_total = self.jogador["defesa"] + self.buff_defesa_jogador
            dano_sofrido = max(2, dano_bruto - (defesa_total // 2))

            if self.defendendo:
                dano_sofrido = max(1, int(dano_sofrido * 0.35))
                self.defendendo = False
                self.log_combate.append(f"BLOQUEIO PERFEITO! Você absorveu a maior parte do impacto ({dano_sofrido} sofrido).")
            else:
                self.log_combate.append(f"{self.inimigo['nome']} usou {acao['nome']} causando {dano_sofrido} de dano.")

            self.jogador["vida"] -= dano_sofrido

            # Aplica status ao jogador se houver
            if "status" in acao and random.random() < 0.65:
                st = acao["status"]
                dur = acao.get("duracao_status", 2)
                self.jogador["status"][st] = dur
                self.log_combate.append(f"Atenção: Você foi afetado por {st.upper()} ({dur} turnos)!")
        else:
            if "buff_defesa" in acao:
                self.inimigo["buff_defesa_temp"] = acao["buff_defesa"]
            if "buff_ataque" in acao:
                self.inimigo["buff_ataque_temp"] = acao["buff_ataque"]
            self.log_combate.append(f"{self.inimigo['nome']} executou {acao['nome']}.")

        # Suporte do companheiro
        self.turno_companheiro()

        # Atualiza buff temporário do jogador
        if self.duracao_buff_jogador > 0:
            self.duracao_buff_jogador -= 1
            if self.duracao_buff_jogador == 0:
                self.buff_defesa_jogador = 0

        self.inimigo["buff_ataque_temp"] = 0
        self.turno_atual += 1

        if self.jogador["vida"] <= 0:
            self.finalizar_combate(vitoria=False)
        else:
            # Sorteia a intenção do próximo turno
            self.intencao_inimiga = self._sortear_intencao()

    def finalizar_combate(self, vitoria):
        if vitoria:
            xp_ganho = self.inimigo["xp_base"] + self.jogador["nivel"] * 5
            ouro_ganho = random.randint(self.inimigo["ouro_min"], self.inimigo["ouro_max"])

            self.jogador["ouro"] = self.jogador.get("ouro", 0) + ouro_ganho
            msgs_xp = ganhar_xp(self.jogador, xp_ganho)

            drops_conquistados = []
            for d in self.inimigo.get("drops", []):
                if random.random() <= d.get("chance", 0.5):
                    adicionar_ao_inventario(self.jogador, d["item"], 1)
                    info = obter_item(d["item"])
                    drops_conquistados.append(info.get("nome", d["item"]))

            self.vitoria_callback(drops_conquistados, xp_ganho, ouro_ganho, msgs_xp)
        else:
            self.derrota_callback()
