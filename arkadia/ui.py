import pygame

# Paleta de Cores
COR_FUNDO = (15, 15, 20)
COR_PAINEL = (24, 25, 34)
COR_PAINEL_TOPO = (32, 34, 46)
COR_BORDA = (65, 70, 90)
COR_BORDA_DESTAQUE = (210, 160, 45)
COR_TEXTO = (225, 230, 240)
COR_TEXTO_MUTED = (145, 150, 170)
COR_DESTAQUE = (240, 190, 50)
COR_BOTAO = (38, 42, 58)
COR_BOTAO_HOVER = (58, 66, 92)
COR_BOTAO_BORDA = (85, 92, 120)
COR_BOTAO_DESATIVADO = (25, 26, 32)
COR_TEXTO_DESATIVADO = (80, 85, 100)

COR_VIDA = (210, 50, 50)
COR_VIDA_FUNDO = (60, 20, 20)
COR_MANA = (50, 125, 225)
COR_MANA_FUNDO = (20, 35, 65)
COR_OURO = (245, 205, 65)

COR_INTENCAO_FUNDO = (40, 30, 35)
COR_INTENCAO_BORDA = (180, 70, 70)
COR_INTENCAO_TEXTO = (255, 180, 180)

class Botao:
    def __init__(self, retangulo, texto, callback, fonte, habilitado=True):
        self.retangulo = pygame.Rect(retangulo)
        self.texto = texto
        self.callback = callback
        self.fonte = fonte
        self.habilitado = habilitado

    def desenhar(self, superficie, mouse_pos):
        colisao = self.retangulo.collidepoint(mouse_pos)
        
        if not self.habilitado:
            cor_base = COR_BOTAO_DESATIVADO
            cor_borda = (50, 52, 65)
            cor_txt = COR_TEXTO_DESATIVADO
        else:
            cor_base = COR_BOTAO_HOVER if colisao else COR_BOTAO
            cor_borda = COR_DESTAQUE if colisao else COR_BOTAO_BORDA
            cor_txt = (255, 255, 255) if colisao else COR_TEXTO

        pygame.draw.rect(superficie, cor_base, self.retangulo, border_radius=6)
        pygame.draw.rect(superficie, cor_borda, self.retangulo, width=2, border_radius=6)

        texto_surf = self.fonte.render(self.texto, True, cor_txt)
        texto_rect = texto_surf.get_rect(center=self.retangulo.center)
        superficie.blit(texto_surf, texto_rect)

    def lidar_evento(self, evento):
        if not self.habilitado:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.retangulo.collidepoint(evento.pos):
                if self.callback:
                    self.callback()
                return True
        return False

def desenhar_barra(superficie, x, y, largura, altura, atual, maximo, cor_frente, cor_fundo, texto="", fonte=None):
    pygame.draw.rect(superficie, cor_fundo, (x, y, largura, altura), border_radius=4)
    proporcao = max(0.0, min(1.0, atual / max(1, maximo)))
    largura_preenchida = int(largura * proporcao)
    if largura_preenchida > 0:
        pygame.draw.rect(superficie, cor_frente, (x, y, largura_preenchida, altura), border_radius=4)
    pygame.draw.rect(superficie, COR_BORDA, (x, y, largura, altura), width=1, border_radius=4)

    if texto and fonte:
        txt_surf = fonte.render(texto, True, COR_TEXTO)
        txt_rect = txt_surf.get_rect(center=(x + largura // 2, y + altura // 2))
        superficie.blit(txt_surf, txt_rect)

def desenhar_painel_narrativo(
    tela,
    mouse_pos,
    largura_tela,
    altura_tela,
    altura_cenario,
    titulo,
    linhas,
    botoes,
    jogador,
    fontes,
    intencao_inimiga=None,
    inimigo_info=None
):
    fonte_titulo = fontes["titulo"]
    fonte_texto = fontes["texto"]
    fonte_ui = fontes["ui"]

    # Fundo do painel inferior
    rect_painel = pygame.Rect(0, altura_cenario, largura_tela, altura_tela - altura_cenario)
    pygame.draw.rect(tela, COR_PAINEL, rect_painel)
    pygame.draw.line(tela, COR_BORDA, (0, altura_cenario), (largura_tela, altura_cenario), width=3)

    # Faixa superior de status
    rect_topo = pygame.Rect(0, altura_cenario, largura_tela, 38)
    pygame.draw.rect(tela, COR_PAINEL_TOPO, rect_topo)
    pygame.draw.line(tela, COR_BORDA, (0, altura_cenario + 38), (largura_tela, altura_cenario + 38), width=1)

    # Divisor vertical entre história e botões
    x_divisor = 580
    pygame.draw.line(tela, COR_BORDA, (x_divisor, altura_cenario + 38), (x_divisor, altura_tela), width=2)

    # Exibição dos dados do jogador no topo
    if jogador:
        # HP
        desenhar_barra(tela, 20, altura_cenario + 11, 140, 16, jogador["vida"], jogador["vida_max"], COR_VIDA, COR_VIDA_FUNDO, f"HP {jogador['vida']}/{jogador['vida_max']}", fonte_ui)

        # MP
        desenhar_barra(tela, 175, altura_cenario + 11, 120, 16, jogador["mana"], jogador["mana_max"], COR_MANA, COR_MANA_FUNDO, f"MP {jogador['mana']}/{jogador['mana_max']}", fonte_ui)

        # Ouro e Nível
        txt_info = fonte_ui.render(f"Nív {jogador.get('nivel', 1)}  |  Ouro: {jogador.get('ouro', 0)}  |  Rep: {jogador.get('reputacao', 0)}", True, COR_OURO)
        tela.blit(txt_info, (310, altura_cenario + 11))

        # Companheiro ativo
        if jogador.get("flags", {}).get("companheiro_elora"):
            txt_comp = fonte_ui.render("✦ Suporte: Elora", True, (130, 220, 140))
            tela.blit(txt_comp, (480, altura_cenario + 11))

        # Status ativos do jogador
        if jogador.get("status"):
            tags = " ".join([f"[{st.upper()}]" for st in jogador["status"].keys()])
            txt_st = fonte_ui.render(tags, True, (255, 100, 100))
            tela.blit(txt_st, (680, altura_cenario + 11))

    # Título da cena
    titulo_surf = fonte_titulo.render(titulo, True, COR_DESTAQUE)
    tela.blit(titulo_surf, (25, altura_cenario + 50))

    # Intenção do inimigo (se estiver em combate)
    y_offset = altura_cenario + 85
    if inimigo_info:
        # Barra de vida do inimigo
        desenhar_barra(tela, 25, y_offset, 250, 18, inimigo_info["vida"], inimigo_info["vida_max"], (200, 40, 90), (60, 20, 30), f"{inimigo_info['nome']} [{inimigo_info['vida']}/{inimigo_info['vida_max']}]", fonte_ui)
        y_offset += 24

    if intencao_inimiga:
        rect_int = pygame.Rect(25, y_offset, 530, 26)
        pygame.draw.rect(tela, COR_INTENCAO_FUNDO, rect_int, border_radius=4)
        pygame.draw.rect(tela, COR_INTENCAO_BORDA, rect_int, width=1, border_radius=4)
        aviso = intencao_inimiga.get("aviso", "")
        txt_int = fonte_ui.render(f"Intenção: {aviso}", True, COR_INTENCAO_TEXTO)
        tela.blit(txt_int, (32, y_offset + 5))
        y_offset += 32

    # Linhas de texto narrativo
    for linha in linhas:
        txt_surf = fonte_texto.render(linha, True, COR_TEXTO)
        tela.blit(txt_surf, (25, y_offset))
        y_offset += 22

    # Desenhar os botões de ação
    for botao in botoes:
        botao.desenhar(tela, mouse_pos)
