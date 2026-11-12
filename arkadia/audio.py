import os
import pygame

class GerenciadorAudio:
    def __init__(self, pasta_assets):
        self.pasta_assets = pasta_assets
        self.habilitado = False
        self.sons = {}
        self.musica_atual = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.habilitado = True
        except Exception as e:
            print(f"[Aviso] Sistema de áudio desabilitado: {e}")
            self.habilitado = False

    def tocar_musica(self, nome_arquivo, loop=-1, volume=0.5):
        if not self.habilitado:
            return
        caminho = os.path.join(self.pasta_assets, nome_arquivo)
        if not os.path.exists(caminho):
            # Procura em subpasta audio/ se houver
            caminho = os.path.join(self.pasta_assets, "audio", nome_arquivo)
        if os.path.exists(caminho):
            try:
                if self.musica_atual != caminho:
                    pygame.mixer.music.load(caminho)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(loop)
                    self.musica_atual = caminho
            except Exception:
                pass

    def parar_musica(self):
        if self.habilitado:
            try:
                pygame.mixer.music.stop()
                self.musica_atual = None
            except Exception:
                pass

    def tocar_sfx(self, nome_arquivo, volume=0.6):
        if not self.habilitado:
            return
        if nome_arquivo in self.sons:
            try:
                self.sons[nome_arquivo].play()
            except Exception:
                pass
            return

        caminho = os.path.join(self.pasta_assets, nome_arquivo)
        if not os.path.exists(caminho):
            caminho = os.path.join(self.pasta_assets, "audio", nome_arquivo)

        if os.path.exists(caminho):
            try:
                snd = pygame.mixer.Sound(caminho)
                snd.set_volume(volume)
                self.sons[nome_arquivo] = snd
                snd.play()
            except Exception:
                pass
