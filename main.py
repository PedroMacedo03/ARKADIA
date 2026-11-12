import os
import sys
import pygame

from video_player import VideoCenario
from arkadia.ui import Botao, desenhar_painel_narrativo
from arkadia.cenas import obter_cena, verificar_requisito_opcao, executar_efeitos_cena
from arkadia.personagem import criar_personagem, obter_skills_disponiveis
from arkadia.combate import MotorCombate
from arkadia.estado import salvar_progresso, carregar_progresso, wipe_save
from arkadia.audio import GerenciadorAudio
from arkadia.itens import obter_nome_item

# ============================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================

LARGURA = 960
ALTURA = 640
ALTURA_CENARIO = 380

if getattr(sys, 'frozen', False):
    DIRETORIO_BASE = os.path.dirname(sys.executable)
else:
    DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_SAVE = os.path.join(DIRETORIO_BASE, "save_arkadia.json")
PASTA_ASSETS = os.path.join(DIRETORIO_BASE, "assets")

# ============================================================
# GERENCIADOR DE ASSETS VISUAIS
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

        # Prioriza vídeo animado se disponível
        caminho_video = self._resolver_caminho_video(nome_arquivo)
        if caminho_video:
            video = VideoCenario(caminho_video, self.largura, self.altura)
            if video.container:
                self.videos[nome_arquivo] = video
                return video

        # Tenta carregar imagem estática
        caminho_img = self._resolver_caminho_imagem(nome_arquivo)
        if caminho_img:
            try:
                img = pygame.image.load(caminho_img).convert()
                img = pygame.transform.scale(img, (self.largura, self.altura))
                self.texturas[nome_arquivo] = img
                return img
            except Exception as e:
                print(f"[Aviso] Erro ao carregar imagem {caminho_img}: {e}")

        # Fallback procedural visual com grid estilizado
        superficie_padrao = pygame.Surface((self.largura, self.altura))
        superficie_padrao.fill((30, 32, 42))
        for x in range(0, self.largura, 40):
            pygame.draw.line(superficie_padrao, (42, 45, 58), (x, 0), (x, self.altura))
        for y in range(0, self.altura, 40):
            pygame.draw.line(superficie_padrao, (42, 45, 58), (0, y), (self.largura, y))

        fonte = pygame.font.SysFont("arial", 20, bold=True)
        texto = fonte.render(f"[ Cenário: {nome_arquivo} ]", True, (140, 145, 165))
        superficie_padrao.blit(texto, texto.get_rect(center=(self.largura // 2, self.altura // 2)))

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
# CONTROLADOR PRINCIPAL DO JOGO
# ============================================================

class JogoArkhor:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("As Crônicas de Arkhor — v1.0")
        self.clock = pygame.time.Clock()

        self.fontes = {
            "titulo": pygame.font.SysFont("georgia", 22, bold=True),
            "texto": pygame.font.SysFont("arial", 16),
            "ui": pygame.font.SysFont("arial", 14, bold=True)
        }

        self.cenarios = GerenciadorCenarios(LARGURA, ALTURA_CENARIO)
        self.audio = GerenciadorAudio(PASTA_ASSETS)

        self.jogador = None
        self.botoes = []
        self.cenario_atual = "menu.mp4"
        self.titulo_atual = ""
        self.mensagens_dialogo = []
        self.id_cena_atual = "menu_principal"

        # Estado de combate
        self.motor_combate = None

        self.ir_para_cena("menu_principal")

    def ir_para_cena(self, cena_id):
        self.id_cena_atual = cena_id
        dados_cena = obter_cena(cena_id)
        if not dados_cena:
            print(f"[Erro] Cena não encontrada: {cena_id}")
            return

        self.cenario_atual = dados_cena.get("cenario", "menu.mp4")
        self.titulo_atual = dados_cena.get("titulo", "")
        self.mensagens_dialogo = list(dados_cena.get("linhas", []))
        self.motor_combate = None

        # Executa efeitos da cena (XP, ouro, itens, flags)
        if self.jogador:
            novos_avisos = executar_efeitos_cena(dados_cena, self.jogador)
            if novos_avisos:
                self.mensagens_dialogo.extend(["", "✦ " + " | ".join(novos_avisos)])

            # Auto-save de checkpoint
            if cena_id not in ("menu_principal", "selecao_classe", "derrota"):
                self.jogador["checkpoint"] = cena_id
                salvar_progresso(self.jogador, ARQUIVO_SAVE)

        # Verifica se é uma cena de combate
        if "combate_inimigo" in dados_cena:
            inimigo_id = dados_cena["combate_inimigo"]
            vitoria_destino = dados_cena.get("vitoria_destino", "capitulo_1")
            self.iniciar_combate(inimigo_id, vitoria_destino)
            return

        # Monta os botões normais de diálogo/escolhas
        self.montar_botoes_cena(dados_cena.get("opcoes", []))

    def montar_botoes_cena(self, opcoes):
        self.botoes.clear()
        x_base = 590
        largura_btn = 345
        altura_btn = 36
        espacamento = 8

        opcoes_validas = []
        for op in opcoes:
            habilitado = verificar_requisito_opcao(op, self.jogador)
            callback = self._criar_callback_opcao(op)
            opcoes_validas.append((op["texto"], callback, habilitado))

        y_inicial = ALTURA - 25 - (len(opcoes_validas) * (altura_btn + espacamento))

        for i, (label, cb, hab) in enumerate(opcoes_validas):
            rect = (x_base, y_inicial + i * (altura_btn + espacamento), largura_btn, altura_btn)
            self.botoes.append(Botao(rect, label, cb, self.fontes["ui"], habilitado=hab))

    def _criar_callback_opcao(self, opcao):
        if "acao_especial" in opcao:
            acao = opcao["acao_especial"]
            if acao == "carregar_jogo":
                return self.carregar_jogo
            elif acao == "sair":
                return self.encerrar_jogo
            elif acao == "escolher_guerreiro":
                return lambda: self.confirmar_classe("Guerreiro")
            elif acao == "escolher_mago":
                return lambda: self.confirmar_classe("Mago")
            elif acao == "escolher_arqueiro":
                return lambda: self.confirmar_classe("Arqueiro")

        if "ir_para" in opcao:
            destino = opcao["ir_para"]
            return lambda: self.ir_para_cena(destino)

        return None

    def confirmar_classe(self, classe):
        self.jogador = criar_personagem("Aventureiro", classe)
        self.ir_para_cena("capitulo_1")

    # ============================================================
    # SISTEMA DE COMBATE
    # ============================================================

    def iniciar_combate(self, inimigo_id, vitoria_destino):
        self.motor_combate = MotorCombate(
            jogador=self.jogador,
            inimigo_id=inimigo_id,
            cenario=self.cenario_atual,
            vitoria_callback=lambda drops, xp, ouro, msgs_xp: self.vitoria_combate(vitoria_destino, drops, xp, ouro, msgs_xp),
            derrota_callback=self.derrota_combate
        )
        self.atualizar_interface_combate()

    def atualizar_interface_combate(self):
        mc = self.motor_combate
        if not mc:
            return

        self.titulo_atual = f"COMBATE CONTRA {mc.inimigo['nome'].upper()}"
        self.mensagens_dialogo = [
            f"Turno {mc.turno_atual}  |  Fraquezas: {', '.join(mc.inimigo['fraquezas']).upper() or 'Nenhuma'}",
            f"Resistências: {', '.join(mc.inimigo['resistencias']).upper() or 'Nenhuma'}",
            ""
        ] + mc.log_combate[-3:]

        # Opções de ação no combate
        self.botoes.clear()
        acoes = [
            ("1. Ataque Normal", mc.acao_ataque_normal, True)
        ]

        # Skills desbloqueadas do personagem
        skills = obter_skills_disponiveis(self.jogador)
        for s in skills:
            tem_mp = self.jogador["mana"] >= s.get("custo_mp", 10)
            acoes.append((
                f"✦ {s['nome']} ({s.get('custo_mp')} MP)",
                lambda sk=s: mc.acao_usar_skill(sk),
                tem_mp
            ))

        # Defesa e poções
        acoes.append(("🛡 Defender (+MP / -65% Dano)", mc.acao_defender, True))

        inv = self.jogador.get("inventario", [])
        qtd_hp = inv.count("pocao_vida") + inv.count("elixir_arkhor")
        qtd_mp = inv.count("pocao_mana")
        qtd_ant = inv.count("antidoto")

        acoes.append((f"🧪 Poção de Vida ({qtd_hp})", mc.acao_usar_pocao_vida, qtd_hp > 0))
        acoes.append((f"🔷 Poção de Mana ({qtd_mp})", mc.acao_usar_pocao_mana, qtd_mp > 0))
        if self.jogador.get("status"):
            acoes.append((f"🌿 Antídoto ({qtd_ant})", mc.acao_usar_antidoto, qtd_ant > 0))

        # Monta os botões na tela
        x_base = 590
        largura_btn = 345
        altura_btn = 34
        espacamento = 6
        y_inicial = ALTURA - 20 - (len(acoes) * (altura_btn + espacamento))

        for i, (label, cb, hab) in enumerate(acoes):
            rect = (x_base, y_inicial + i * (altura_btn + espacamento), largura_btn, altura_btn)
            # Envolve o callback para atualizar a UI pós-ação
            def acao_wrapper(fn=cb):
                fn()
                if self.motor_combate:
                    self.atualizar_interface_combate()
            self.botoes.append(Botao(rect, label, acao_wrapper, self.fontes["ui"], habilitado=hab))

    def vitoria_combate(self, destino, drops, xp, ouro, msgs_xp):
        self.motor_combate = None
        # Salva o progresso após vencer combate
        salvar_progresso(self.jogador, ARQUIVO_SAVE)

        # Monta tela de pós-vitória
        self.titulo_atual = "VITÓRIA GLORIOSA!"
        linhas = [
            f"O inimigo foi derrotado com maestria!",
            f"Recompensas conquistadas:",
            f"• +{xp} Pontos de Experiência",
            f"• +{ouro} Moedas de Ouro"
        ]
        if drops:
            linhas.append(f"• Itens saqueados: {', '.join(drops)}")
        linhas.extend(msgs_xp)

        self.mensagens_dialogo = linhas
        self.botoes.clear()
        rect = (590, ALTURA - 80, 345, 42)
        self.botoes.append(Botao(rect, "Prosseguir Viagem", lambda: self.ir_para_cena(destino), self.fontes["ui"]))

    def derrota_combate(self):
        self.motor_combate = None
        wipe_save(ARQUIVO_SAVE)
        self.jogador = None
        self.ir_para_cena("derrota")

    # ============================================================
    # PERSISTÊNCIA
    # ============================================================

    def carregar_jogo(self):
        dados = carregar_progresso(ARQUIVO_SAVE)
        if not dados:
            self.ir_para_cena("nenhum_save")
            return

        self.jogador = dados
        checkpoint = self.jogador.get("checkpoint", "capitulo_1")
        self.ir_para_cena(checkpoint)

    def encerrar_jogo(self):
        self.cenarios.fechar_todos()
        self.audio.parar_musica()
        pygame.quit()
        sys.exit()

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================

    def executar(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.encerrar_jogo()

                # Processa cliques nos botões
                for botao in list(self.botoes):
                    if botao.lidar_evento(evento):
                        break

            # 1. Renderiza o cenário (vídeo animado em loop ou imagem estática)
            self.cenarios.renderizar(self.cenario_atual, self.tela)

            # 2. Informações de combate se ativo
            intencao = self.motor_combate.intencao_inimiga if self.motor_combate else None
            inimigo_info = self.motor_combate.inimigo if self.motor_combate else None

            # 3. Renderiza o painel inferior (história, barras, intenções e botões)
            desenhar_painel_narrativo(
                tela=self.tela,
                mouse_pos=mouse_pos,
                largura_tela=LARGURA,
                altura_tela=ALTURA,
                altura_cenario=ALTURA_CENARIO,
                titulo=self.titulo_atual,
                linhas=self.mensagens_dialogo,
                botoes=self.botoes,
                jogador=self.jogador,
                fontes=self.fontes,
                intencao_inimiga=intencao,
                inimigo_info=inimigo_info
            )

            pygame.display.flip()
            self.clock.tick(60)

# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    app = JogoArkhor()
    app.executar()
