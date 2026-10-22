import os
import sys
import json
import random
import pygame
from video_player import VideoCenario

# ============================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================

LARGURA = 960
ALTURA = 640
ALTURA_CENARIO = 380
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SAVE = os.path.join(DIRETORIO_BASE, "save_arkadia.json")
PASTA_ASSETS = os.path.join(DIRETORIO_BASE, "assets")

# Paleta de Cores
COR_FUNDO = (15, 15, 20)
COR_PAINEL = (25, 26, 35)
COR_BORDA = (70, 75, 95)
COR_TEXTO = (220, 225, 235)
COR_TEXTO_MUTED = (140, 145, 165)
COR_DESTAQUE = (235, 180, 55)
COR_BOTAO = (40, 45, 60)
COR_BOTAO_HOVER = (60, 68, 90)
COR_BOTAO_BORDA = (90, 95, 120)

COR_VIDA = (200, 50, 50)
COR_MANA = (50, 120, 220)


# ============================================================
# GERENCIADOR DE ASSETS
# ============================================================

class GerenciadorCenarios:
    EXTENSOES_VIDEO = (".mp4", ".avi", ".mov", ".mkv", ".webm")
    EXTENSOES_IMAGEM = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.texturas = {}
        self.videos = {}

    def _resolver_caminho_video(self, nome_arquivo):
        base, ext = os.path.splitext(nome_arquivo)
        if ext.lower() in self.EXTENSOES_VIDEO:
            caminho = os.path.join(PASTA_ASSETS, nome_arquivo)
            if os.path.exists(caminho):
                return caminho
        for v_ext in self.EXTENSOES_VIDEO:
            caminho = os.path.join(PASTA_ASSETS, base + v_ext)
            if os.path.exists(caminho):
                return caminho
        return None

    def _resolver_caminho_imagem(self, nome_arquivo):
        caminho = os.path.join(PASTA_ASSETS, nome_arquivo)
        if os.path.exists(caminho) and not nome_arquivo.lower().endswith(self.EXTENSOES_VIDEO):
            return caminho
        base, _ = os.path.splitext(nome_arquivo)
        for i_ext in self.EXTENSOES_IMAGEM:
            caminho_alt = os.path.join(PASTA_ASSETS, base + i_ext)
            if os.path.exists(caminho_alt):
                return caminho_alt
        return None

    def obter_cenario(self, nome_arquivo):
        if nome_arquivo in self.videos:
            return self.videos[nome_arquivo]
        if nome_arquivo in self.texturas:
            return self.texturas[nome_arquivo]

        # 1. Prioriza vídeo se existir (ex: menu.mp4 mesmo se pedir menu.png ou menu.mp4)
        caminho_video = self._resolver_caminho_video(nome_arquivo)
        if caminho_video:
            video = VideoCenario(caminho_video, self.largura, self.altura)
            if video.container:
                self.videos[nome_arquivo] = video
                return video

        # 2. Tenta carregar imagem estática
        caminho_img = self._resolver_caminho_imagem(nome_arquivo)
        if caminho_img:
            try:
                img = pygame.image.load(caminho_img).convert()
                img = pygame.transform.scale(img, (self.largura, self.altura))
                self.texturas[nome_arquivo] = img
                return img
            except Exception as e:
                print(f"Erro ao carregar imagem {caminho_img}: {e}")

        # Fallback procedural visual caso a mídia não exista
        superficie_padrao = pygame.Surface((self.largura, self.altura))
        superficie_padrao.fill((30, 32, 42))
        
        # Grid estilizado de fundo provisório
        for x in range(0, self.largura, 40):
            pygame.draw.line(superficie_padrao, (40, 43, 55), (x, 0), (x, self.altura))
        for y in range(0, self.altura, 40):
            pygame.draw.line(superficie_padrao, (40, 43, 55), (0, y), (self.largura, y))

        fonte = pygame.font.SysFont("arial", 20, bold=True)
        texto = fonte.render(f"[ Cenário ausente: {nome_arquivo} ]", True, COR_TEXTO_MUTED)
        retangulo_texto = texto.get_rect(center=(self.largura // 2, self.altura // 2))
        superficie_padrao.blit(texto, retangulo_texto)

        self.texturas[nome_arquivo] = superficie_padrao
        return superficie_padrao

    def renderizar(self, nome_arquivo, tela):
        cenario = self.obter_cenario(nome_arquivo)
        if isinstance(cenario, VideoCenario):
            cenario.atualizar_e_desenhar(tela)
        else:
            tela.blit(cenario, (0, 0))

    def fechar_todos(self):
        for video in self.videos.values():
            video.fechar()
        self.videos.clear()


# ============================================================
# COMPONENTE DE BOTÃO
# ============================================================

class Botao:
    def __init__(self, retangulo, texto, callback, fonte):
        self.retangulo = pygame.Rect(retangulo)
        self.texto = texto
        self.callback = callback
        self.fonte = fonte

    def desenhar(self, superficie, mouse_pos):
        colisao = self.retangulo.collidepoint(mouse_pos)
        cor_base = COR_BOTAO_HOVER if colisao else COR_BOTAO

        pygame.draw.rect(superficie, cor_base, self.retangulo, border_radius=6)
        pygame.draw.rect(superficie, COR_BOTAO_BORDA, self.retangulo, width=2, border_radius=6)

        texto_surf = self.fonte.render(self.texto, True, COR_TEXTO)
        texto_rect = texto_surf.get_rect(center=self.retangulo.center)
        superficie.blit(texto_surf, texto_rect)

    def lidar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.retangulo.collidepoint(evento.pos):
                self.callback()
                return True
        return False


# ============================================================
# ESTRUTURA DO JOGO E MÁQUINA DE ESTADOS
# ============================================================

class JogoArkhor:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("As Crônicas de Arkhor")
        self.clock = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont("georgia", 22, bold=True)
        self.fonte_texto = pygame.font.SysFont("arial", 16)
        self.fonte_ui = pygame.font.SysFont("arial", 14, bold=True)

        self.cenarios = GerenciadorCenarios(LARGURA, ALTURA_CENARIO)
        self.jogador = None
        self.botoes = []

        # Estado da cena narrativa
        self.cenario_atual = "menu.mp4"
        self.titulo_atual = ""
        self.mensagens_dialogo = []
        self.em_combate = False
        self.dados_combate = {}

        self.tela_menu_principal()

    # --- Criação e Manipulação de Personagem ---

    def criar_personagem(self, nome, classe):
        config = {
            "Guerreiro": {"vida": 130, "mana": 30, "ataque": 18, "defesa": 8, "arma": "Espada de Ferro", "armadura": "Cota de Malha"},
            "Mago": {"vida": 90, "mana": 100, "ataque": 10, "defesa": 4, "arma": "Cajado de Aprendiz", "armadura": "Manto Arcano"},
            "Arqueiro": {"vida": 105, "mana": 50, "ataque": 15, "defesa": 6, "arma": "Arco Simples", "armadura": "Couro de Caçador"}
        }[classe]

        return {
            "nome": nome,
            "classe": classe,
            "nivel": 1,
            "xp": 0,
            "xp_proximo": 100,
            "vida": config["vida"],
            "vida_max": config["vida"],
            "mana": config["mana"],
            "mana_max": config["mana"],
            "ataque": config["ataque"],
            "defesa": config["defesa"],
            "ouro": 40,
            "arma": config["arma"],
            "armadura": config["armadura"],
            "inventario": ["Poção", "Poção"],
            "missoes": [],
            "checkpoint": "capitulo_1",
            "historia": {
                "ajudou_vila": False,
                "confia_mago": False,
                "entrou_ruinas": False,
                "conheceu_dragao": False
            }
        }

    # --- Gerenciamento de Interface Narrativa ---

    def definir_cena(self, cenario, titulo, linhas, opcoes):
        self.cenario_atual = cenario
        self.titulo_atual = titulo
        self.mensagens_dialogo = linhas
        self.botoes.clear()

        # Posicionamento dos botões no painel inferior direito
        x_base = 580
        largura_btn = 350
        altura_btn = 36
        espacamento = 8

        # Inicia posicionando os botões de baixo para cima ou empilhados
        y_inicial = ALTURA - 30 - (len(opcoes) * (altura_btn + espacamento))

        for i, (label, callback) in enumerate(opcoes):
            rect = (x_base, y_inicial + i * (altura_btn + espacamento), largura_btn, altura_btn)
            self.botoes.append(Botao(rect, label, callback, self.fonte_ui))

    # --- Fluxo de Cenas e Capítulos ---

    def tela_menu_principal(self):
        self.jogador = None
        self.em_combate = False
        self.definir_cena(
            cenario="menu.mp4",
            titulo="AS CRÔNICAS DE ARKHOR",
            linhas=[
                "Uma antiga profecia está despertando nas terras esquecidas.",
                "Três séculos atrás, o reino de Arkhor desapareceu das crônicas.",
                "Agora, estranhas forças tentam restaurar o trono perdido.",
                "",
                "Escolha uma opção para iniciar sua jornada."
            ],
            opcoes=[
                ("Novo Jogo", self.iniciar_novo_jogo),
                ("Carregar Progresso", self.carregar_jogo),
                ("Sair", self.encerrar_jogo)
            ]
        )

    def iniciar_novo_jogo(self):
        # Seleção de classe direta
        self.definir_cena(
            cenario="menu.mp4",
            titulo="SELEÇÃO DE CLASSE",
            linhas=[
                "Escolha seu caminho e aptidões marciais:",
                "• Guerreiro: Maior resiliência e dano físico direto.",
                "• Mago: Capacidade mágica refinada e feitiços em área.",
                "• Arqueiro: Habilidade equilibrada com ataques perfurantes."
            ],
            opcoes=[
                ("Guerreiro", lambda: self.confirmar_classe("Guerreiro")),
                ("Mago", lambda: self.confirmar_classe("Mago")),
                ("Arqueiro", lambda: self.confirmar_classe("Arqueiro"))
            ]
        )

    def confirmar_classe(self, classe):
        self.jogador = self.criar_personagem("Aventureiro", classe)
        self.capitulo_1()

    def capitulo_1(self):
        self.salvar_checkpoint("capitulo_1")
        self.definir_cena(
            cenario="floresta.png",
            titulo="CAPÍTULO I — O DESPERTAR",
            linhas=[
                "A chuva fria fustiga a copa das árvores coníferas.",
                "Você desperta no solo úmido sem qualquer lembrança recente.",
                "Na palma de sua mão direita, uma estranha runa emite luz tênue.",
                "Ao norte, fumaça se eleva de uma pequena vila florestal.",
                "Ao sul, a mata densa some sob um denso lençol de névoa."
            ],
            opcoes=[
                ("Ir para a Vila Lúmen", self.vila_lumen),
                ("Adentrar a Floresta Profunda", self.floresta_inicial)
            ]
        )

    def vila_lumen(self):
        self.salvar_checkpoint("vila_lumen")
        self.definir_cena(
            cenario="vila.png",
            titulo="VILA LÚMEN",
            linhas=[
                "A vila sofreu um ataque recente. Cabanas ainda soltam fumaça.",
                "Moradores assustados observam por trás de portas barricadas.",
                "Uma moradora vem ao seu encontro com passos hesitantes.",
                "\"Forasteiro... você veio ajudar nossa gente?\""
            ],
            opcoes=[
                ("Ajudar a vila e investigar", self.ajudar_vila),
                ("Seguir direto para a floresta", self.floresta_inicial)
            ]
        )

    def ajudar_vila(self):
        if not self.jogador["historia"].get("ajudou_vila"):
            self.jogador["historia"]["ajudou_vila"] = True
            self.jogador["inventario"].append("Espada Quebrada")
            self.ganhar_xp(25)
        self.salvar_checkpoint("ajudar_vila")
        self.definir_cena(
            cenario="vila.png",
            titulo="VILA LÚMEN — RELATO",
            linhas=[
                "A mulher entrega uma lâmina antiga encontrada após o massacre.",
                "\"As criaturas procuravam alguém... Alguém com a mesma marca",
                "que brilha em sua mão. Elas fugiram em direção às ruínas.\""
            ],
            opcoes=[
                ("Seguir rastros até a floresta", self.floresta_inicial)
            ]
        )

    def floresta_inicial(self):
        self.salvar_checkpoint("floresta_inicial")
        self.iniciar_combate(
            nome_inimigo="Lobo Sombrio",
            vida_max=45 + self.jogador["nivel"] * 5,
            ataque_inimigo=12,
            cenario="floresta.png",
            vitoria_callback=self.pos_combate_lobo
        )

    def pos_combate_lobo(self):
        self.salvar_checkpoint("pos_combate_lobo")
        self.definir_cena(
            cenario="floresta.png",
            titulo="FLORESTA DE ARKHOR — O ENCONTRO",
            linhas=[
                "A criatura tomba sem vida. O silêncio retorna à floresta.",
                "Surgindo por entre os troncos, uma figura encapuzada observa você.",
                "\"Essa marca em sua mão... ela pertencia à linhagem real de Arkhor.\"",
                "\"Se ela despertou, as ruínas ancestrais já sabem de sua volta.\""
            ],
            opcoes=[
                ("Ouvir o conselho do Mago", self.dialogo_mago),
                ("Ignorá-lo e marchar às ruínas", self.ruinas)
            ]
        )

    def dialogo_mago(self):
        if not self.jogador["historia"].get("confia_mago"):
            self.jogador["historia"]["confia_mago"] = True
            self.ganhar_xp(35)
        self.salvar_checkpoint("dialogo_mago")
        self.definir_cena(
            cenario="floresta.png",
            titulo="O MAGO DA FLORESTA",
            linhas=[
                "\"O rei Aurelion selou o castelo antes do cataclismo.\"",
                "\"Tome este pergaminho de proteção. As ruínas na montanha",
                "testarão sua força antes que você alcance os portões.\""
            ],
            opcoes=[
                ("Avançar até as Ruínas de Arkhor", self.ruinas)
            ]
        )

    def ruinas(self):
        self.jogador["historia"]["entrou_ruinas"] = True
        self.salvar_checkpoint("ruinas")
        self.definir_cena(
            cenario="ruinas.png",
            titulo="CAPÍTULO II — AS RUÍNAS DE ARKHOR",
            linhas=[
                "Paredes megalíticas cobertas de hera revelam três passagens.",
                "A energia arcana das pedras ressoa com a marca em seu braço.",
                "Para onde deseja direcionar sua exploração?"
            ],
            opcoes=[
                ("Sala dos Guerreiros", self.sala_guerreiros),
                ("Biblioteca Perdida", self.biblioteca),
                ("Cripta Subterrânea", self.cripta)
            ]
        )

    def sala_guerreiros(self):
        self.salvar_checkpoint("sala_guerreiros")
        self.iniciar_combate(
            nome_inimigo="Guardião de Pedra",
            vida_max=80 + self.jogador["nivel"] * 8,
            ataque_inimigo=18,
            cenario="guerreiros.png",
            vitoria_callback=self.recompensa_guerreiros
        )

    def recompensa_guerreiros(self):
        if self.jogador.get("arma") != "Espada de Arkhor":
            self.jogador["arma"] = "Espada de Arkhor"
            self.jogador["ataque"] += 8
            self.ganhar_xp(80)
        self.salvar_checkpoint("recompensa_guerreiros")
        self.definir_cena(
            cenario="guerreiros.png",
            titulo="SALA DOS GUERREIROS — SAQUE",
            linhas=[
                "O guardião racha e desmorona em blocos de granito.",
                "Em seu pedestal repousava a autêntica Lâmina de Arkhor.",
                "Seu poder de ataque foi permanentemente aprimorado (+8)."
            ],
            opcoes=[
                ("Seguir até a Montanha Negra", self.capitulo_3)
            ]
        )

    def biblioteca(self):
        if self.jogador.get("checkpoint") != "biblioteca":
            self.jogador["mana_max"] += 20
            self.jogador["mana"] = self.jogador["mana_max"]
            self.ganhar_xp(70)
        self.salvar_checkpoint("biblioteca")
        self.definir_cena(
            cenario="biblioteca.png",
            titulo="BIBLIOTECA PERDIDA",
            linhas=[
                "Prateleiras imensas guardam segredos arcanos intocados.",
                "Ao abrir um tomo ilustrado com a runa régia, o fluxo",
                "de energia restaura e expande seu limite de mana (+20)."
            ],
            opcoes=[
                ("Prosseguir para a Montanha Negra", self.capitulo_3)
            ]
        )

    def cripta(self):
        self.salvar_checkpoint("cripta")
        self.iniciar_combate(
            nome_inimigo="Cavaleiro Morto",
            vida_max=100 + self.jogador["nivel"] * 10,
            ataque_inimigo=22,
            cenario="cripta.png",
            vitoria_callback=self.recompensa_cripta
        )

    def recompensa_cripta(self):
        if self.jogador.get("armadura") != "Armadura do Guardião":
            self.jogador["armadura"] = "Armadura do Guardião"
            self.jogador["defesa"] += 7
            self.ganhar_xp(100)
        self.salvar_checkpoint("recompensa_cripta")
        self.definir_cena(
            cenario="cripta.png",
            titulo="CRIPTAS — RELÍQUIA RECUPERADA",
            linhas=[
                "O esqueleto armadurado tomba em definitivo.",
                "Você resgata a couraça de placas intacta do túmulo régio.",
                "Sua defesa física foi ampliada (+7)."
            ],
            opcoes=[
                ("Subir em direção à Montanha Negra", self.capitulo_3)
            ]
        )

    def capitulo_3(self):
        self.salvar_checkpoint("capitulo_3")
        self.definir_cena(
            cenario="ponte.png",
            titulo="CAPÍTULO III — A PONTE DA MONTANHA",
            linhas=[
                "Uma ponte de pedra estreita cruza um abismo sem fundo.",
                "Tempestades elétricas iluminam a silhueta do Castelo Negro.",
                "Sentinelas de armaduras negras bloqueiam a passagem principal."
            ],
            opcoes=[
                ("Enfrentar o Guarda Negro", self.combate_guarda),
                ("Buscar passagem estreita na rocha", self.atalho_ponte)
            ]
        )

    def atalho_ponte(self):
        self.ganhar_xp(60)
        self.capitulo_4()

    def combate_guarda(self):
        self.salvar_checkpoint("combate_guarda")
        self.iniciar_combate(
            nome_inimigo="Guarda Negro",
            vida_max=110,
            ataque_inimigo=25,
            cenario="ponte.png",
            vitoria_callback=self.capitulo_4
        )

    def capitulo_4(self):
        self.jogador["historia"]["conheceu_dragao"] = True
        self.salvar_checkpoint("capitulo_4")
        self.definir_cena(
            cenario="castelo.png",
            titulo="CAPÍTULO IV — O TRONO ANCESTRAL",
            linhas=[
                "Os salões internos do Castelo Negro encontram-se desertos.",
                "No salão abobadado do trono, uma sombra descomunal se ergue.",
                "\"Você veio reivindicar a herança de Aurelion, mortal?\"",
                "O Dragão Ancestral ruge, estalando labaredas pelas presas."
            ],
            opcoes=[
                ("Iniciar Batalha Decisiva", self.batalha_final)
            ]
        )

    def batalha_final(self):
        self.salvar_checkpoint("batalha_final")
        vida_chefe = 220 + self.jogador["nivel"] * 20
        dano_chefe = 35 + self.jogador["nivel"] * 2
        self.iniciar_combate(
            nome_inimigo="DRAGÃO ANCESTRAL",
            vida_max=vida_chefe,
            ataque_inimigo=dano_chefe,
            cenario="castelo.png",
            vitoria_callback=self.vitoria_final
        )

    def vitoria_final(self):
        self.salvar_checkpoint("vitoria_final")
        self.definir_cena(
            cenario="castelo.png",
            titulo="FIM DA CAMPANHA — VITÓRIA",
            linhas=[
                "O Dragão tomba e sua essência dissipa a névoa das terras.",
                "A marca em sua mão brilha intensamente antes de se fundir à pele.",
                "Arkhor está livre, aguardando a reconstrução por seu novo herdeiro.",
                "",
                f"Parabéns! Nível Final alcançado: {self.jogador['nivel']}."
            ],
            opcoes=[
                ("Menu Principal", self.tela_menu_principal)
            ]
        )

    def derrota(self):
        # Permadeath: aplica wipe no arquivo de save e limpa o estado do jogador
        self.wipe_save()
        self.jogador = None
        self.definir_cena(
            cenario="menu.mp4",
            titulo="VOCÊ TOMBOU EM COMBATE",
            linhas=[
                "Seus pontos de vida se esgotaram.",
                "As sombras de Arkhor consumiram sua determinação.",
                "Seu progresso salvo foi perdido para sempre (Wipe).",
                "",
                "Retorne ao menu para iniciar uma nova jornada."
            ],
            opcoes=[
                ("Voltar ao Menu", self.tela_menu_principal)
            ]
        )

    # --- Mecânica de Combate ---

    def iniciar_combate(self, nome_inimigo, vida_max, ataque_inimigo, cenario, vitoria_callback):
        self.em_combate = True
        self.dados_combate = {
            "inimigo": nome_inimigo,
            "vida": vida_max,
            "vida_max": vida_max,
            "ataque": ataque_inimigo,
            "cenario": cenario,
            "vitoria_callback": vitoria_callback,
            "defendendo": False,
            "log": f"Um {nome_inimigo} ameaçador surge à sua frente!"
        }
        self.atualizar_interface_combate()

    def atualizar_interface_combate(self):
        d = self.dados_combate
        custo_esp = 10 if self.jogador["classe"] == "Guerreiro" else (20 if self.jogador["classe"] == "Mago" else 12)
        nome_esp = "Golpe Brutal" if self.jogador["classe"] == "Guerreiro" else ("Bola de Fogo" if self.jogador["classe"] == "Mago" else "Tiro Preciso")

        self.definir_cena(
            cenario=d["cenario"],
            titulo=f"COMBATE CONTRA {d['inimigo'].upper()}",
            linhas=[
                f"Inimigo: {d['inimigo']} [HP: {d['vida']} / {d['vida_max']}]",
                f"Seu Estado: {self.jogador['vida']} HP | {self.jogador['mana']} MP",
                "",
                f"Última ação: {d['log']}"
            ],
            opcoes=[
                ("1. Ataque Padrão", self.acao_ataque_normal),
                (f"2. {nome_esp} ({custo_esp} MP)", self.acao_ataque_especial),
                ("3. Postura Defensiva", self.acao_defender),
                ("4. Usar Poção", self.acao_pocao)
            ]
        )

    def acao_ataque_normal(self):
        d = self.dados_combate
        dano = max(1, random.randint(self.jogador["ataque"] - 3, self.jogador["ataque"] + 5))
        d["vida"] -= dano
        d["log"] = f"Você causou {dano} de dano ao {d['inimigo']}."

        if d["vida"] <= 0:
            self.finalizar_combate(vitoria=True)
        else:
            self.turno_inimigo()

    def acao_ataque_especial(self):
        d = self.dados_combate
        custo = 10 if self.jogador["classe"] == "Guerreiro" else (20 if self.jogador["classe"] == "Mago" else 12)

        if self.jogador["mana"] < custo:
            d["log"] = f"Mana insuficiente para habilidade ({custo} necessária)."
            self.atualizar_interface_combate()
            return

        self.jogador["mana"] -= custo
        dano = random.randint(self.jogador["ataque"] + 12, self.jogador["ataque"] + 25)
        d["vida"] -= dano
        d["log"] = f"Ataque Especial! Dano massivo de {dano} pontos!"

        if d["vida"] <= 0:
            self.finalizar_combate(vitoria=True)
        else:
            self.turno_inimigo()

    def acao_defender(self):
        d = self.dados_combate
        d["defendendo"] = True
        recuperado = random.randint(8, 14)
        self.jogador["mana"] = min(self.jogador["mana_max"], self.jogador["mana"] + recuperado)
        d["log"] = f"Postura defensiva adotada. Recuperou {recuperado} de mana."
        self.turno_inimigo()

    def acao_pocao(self):
        d = self.dados_combate
        if "Poção" in self.jogador["inventario"]:
            self.jogador["inventario"].remove("Poção")
            recup = 40
            self.jogador["vida"] = min(self.jogador["vida_max"], self.jogador["vida"] + recup)
            d["log"] = f"Poção consumida. +{recup} HP restabelecidos."
            self.turno_inimigo()
        else:
            d["log"] = "Você não possui mais poções no inventário."
            self.atualizar_interface_combate()

    def turno_inimigo(self):
        d = self.dados_combate
        dano_bruto = random.randint(d["ataque"] - 4, d["ataque"] + 4)
        dano = max(1, dano_bruto - (self.jogador["defesa"] // 3))

        if d["defendendo"]:
            dano = max(1, dano // 3)
            d["defendendo"] = False
            d["log"] += f" O contra-ataque foi bloqueado! Sofreu apenas {dano} de dano."
        else:
            d["log"] += f" {d['inimigo']} revidou com {dano} de dano."

        self.jogador["vida"] -= dano
        if self.jogador["vida"] <= 0:
            self.finalizar_combate(vitoria=False)
        else:
            self.salvar_progresso()
            self.atualizar_interface_combate()

    def finalizar_combate(self, vitoria):
        self.em_combate = False
        if vitoria:
            cb = self.dados_combate["vitoria_callback"]
            cb()
        else:
            self.derrota()

    # --- Progressão e Salvamento ---

    def ganhar_xp(self, qtd):
        self.jogador["xp"] += qtd
        while self.jogador["xp"] >= self.jogador["xp_proximo"]:
            self.jogador["xp"] -= self.jogador["xp_proximo"]
            self.jogador["nivel"] += 1
            self.jogador["xp_proximo"] = int(self.jogador["xp_proximo"] * 1.35)
            self.jogador["vida_max"] += 15
            self.jogador["vida"] = self.jogador["vida_max"]
            self.jogador["mana_max"] += 10
            self.jogador["mana"] = self.jogador["mana_max"]
            self.jogador["ataque"] += 4
            self.jogador["defesa"] += 2

    def salvar_checkpoint(self, nome_checkpoint):
        if self.jogador:
            self.jogador["checkpoint"] = nome_checkpoint
            self.salvar_progresso()

    def salvar_progresso(self):
        if not self.jogador:
            return
        try:
            with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
                json.dump(self.jogador, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def wipe_save(self):
        try:
            with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print(f"Erro ao limpar save: {e}")

    def carregar_jogo(self):
        if not os.path.exists(ARQUIVO_SAVE) or os.path.getsize(ARQUIVO_SAVE) == 0:
            self.definir_cena(
                cenario="menu.mp4",
                titulo="NENHUM SAVE ENCONTRADO",
                linhas=[
                    "Não há nenhum progresso salvo disponível em save_arkadia.json",
                    "(ou o seu personagem anterior tombou em combate e sofreu Wipe).",
                    "",
                    "Inicie um Novo Jogo para começar sua jornada."
                ],
                opcoes=[
                    ("Novo Jogo", self.iniciar_novo_jogo),
                    ("Voltar ao Menu", self.tela_menu_principal)
                ]
            )
            return

        try:
            with open(ARQUIVO_SAVE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, dict) or "classe" not in dados:
                raise ValueError("Formato de save inválido ou vazio.")
            self.jogador = dados

            checkpoint = self.jogador.get("checkpoint", "capitulo_1")
            mapa_cenas = {
                "capitulo_1": self.capitulo_1,
                "vila_lumen": self.vila_lumen,
                "ajudar_vila": self.ajudar_vila,
                "floresta_inicial": self.floresta_inicial,
                "pos_combate_lobo": self.pos_combate_lobo,
                "dialogo_mago": self.dialogo_mago,
                "ruinas": self.ruinas,
                "sala_guerreiros": self.sala_guerreiros,
                "recompensa_guerreiros": self.recompensa_guerreiros,
                "biblioteca": self.biblioteca,
                "cripta": self.cripta,
                "recompensa_cripta": self.recompensa_cripta,
                "capitulo_3": self.capitulo_3,
                "combate_guarda": self.combate_guarda,
                "capitulo_4": self.capitulo_4,
                "batalha_final": self.batalha_final,
                "vitoria_final": self.vitoria_final,
            }
            destino = mapa_cenas.get(checkpoint, self.capitulo_1)
            destino()
        except Exception as e:
            print(f"Erro ao carregar: {e}")

    def encerrar_jogo(self):
        self.cenarios.fechar_todos()
        pygame.quit()
        sys.exit()

    # --- Renderização Visual ---

    def desenhar_painel_inferior(self, mouse_pos):
        # Caixa de fundo
        rect_painel = pygame.Rect(0, ALTURA_CENARIO, LARGURA, ALTURA - ALTURA_CENARIO)
        pygame.draw.rect(self.tela, COR_PAINEL, rect_painel)
        pygame.draw.line(self.tela, COR_BORDA, (0, ALTURA_CENARIO), (LARGURA, ALTURA_CENARIO), width=3)

        # Divisor vertical entre texto/narrativa e os botões
        pygame.draw.line(self.tela, COR_BORDA, (560, ALTURA_CENARIO), (560, ALTURA), width=2)

        # Barra de Status do Jogador no Topo da Interface Textual
        if self.jogador:
            # HP Bar
            pygame.draw.rect(self.tela, (50, 20, 20), (25, ALTURA_CENARIO + 15, 120, 14), border_radius=3)
            largura_hp = int(120 * (max(0, self.jogador["vida"]) / self.jogador["vida_max"]))
            pygame.draw.rect(self.tela, COR_VIDA, (25, ALTURA_CENARIO + 15, largura_hp, 14), border_radius=3)
            txt_hp = self.fonte_ui.render(f"HP {self.jogador['vida']}/{self.jogador['vida_max']}", True, COR_TEXTO)
            self.tela.blit(txt_hp, (155, ALTURA_CENARIO + 14))

            # MP Bar
            pygame.draw.rect(self.tela, (20, 30, 60), (265, ALTURA_CENARIO + 15, 100, 14), border_radius=3)
            largura_mp = int(100 * (max(0, self.jogador["mana"]) / self.jogador["mana_max"]))
            pygame.draw.rect(self.tela, COR_MANA, (265, ALTURA_CENARIO + 15, largura_mp, 14), border_radius=3)
            txt_mp = self.fonte_ui.render(f"MP {self.jogador['mana']}/{self.jogador['mana_max']}", True, COR_TEXTO)
            self.tela.blit(txt_mp, (375, ALTURA_CENARIO + 14))

        # Título da Cena
        titulo_surf = self.fonte_titulo.render(self.titulo_atual, True, COR_DESTAQUE)
        self.tela.blit(titulo_surf, (25, ALTURA_CENARIO + 45))

        # Linhas narrativas
        y_texto = ALTURA_CENARIO + 80
        for linha in self.mensagens_dialogo:
            txt_surf = self.fonte_texto.render(linha, True, COR_TEXTO)
            self.tela.blit(txt_surf, (25, y_texto))
            y_texto += 22

        # Desenhar Botões de Escolha
        for botao in self.botoes:
            botao.desenhar(self.tela, mouse_pos)

    def executar(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.encerrar_jogo()

                # Dispara cliques apenas no botão pressionado
                for botao in list(self.botoes):
                    if botao.lidar_evento(evento):
                        break

            # 1. Renderiza o cenário (vídeo ou imagem)
            self.cenarios.renderizar(self.cenario_atual, self.tela)

            # 2. Renderiza a interface de escolhas e diálogos
            self.desenhar_painel_inferior(mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    app = JogoArkhor()
    app.executar()
