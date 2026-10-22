import time
import av
import pygame

class VideoCenario:
    def __init__(self, caminho_arquivo, largura, altura):
        self.caminho = caminho_arquivo
        self.largura = largura
        self.altura = altura
        self.container = None
        self.stream = None
        self.gerador_frames = None
        self.surface_atual = pygame.Surface((largura, altura))
        self.fps = 24.0
        self.intervalo_frame = 1.0 / 24.0
        self.ultimo_tempo = 0.0
        
        self._carregar()

    def _carregar(self):
        try:
            self.container = av.open(self.caminho)
            self.stream = self.container.streams.video[0]
            # Desativa decodificação de áudio para poupar CPU/GPU
            self.stream.thread_type = "AUTO"
            if self.stream.average_rate:
                self.fps = float(self.stream.average_rate)
                if self.fps > 0:
                    self.intervalo_frame = 1.0 / self.fps
            self.gerador_frames = self.container.decode(self.stream)
            self._proximo_frame()
            self.ultimo_tempo = time.perf_counter()
        except Exception as e:
            print(f"Erro ao carregar vídeo {self.caminho}: {e}")
            self.container = None

    def _proximo_frame(self):
        if not self.container:
            return

        try:
            frame = next(self.gerador_frames)
        except (StopIteration, av.FFmpegError, EOFError):
            # Chegou ao fim do vídeo: reseta para o início (Loop infinito)
            try:
                self.container.seek(0)
                self.gerador_frames = self.container.decode(self.stream)
                frame = next(self.gerador_frames)
            except Exception:
                return

        # Redimensiona e converte o frame diretamente via FFmpeg (muito mais rápido)
        frame_redimensionado = frame.reformat(width=self.largura, height=self.altura, format="rgb24")
        rgb_frame = frame_redimensionado.to_ndarray()
        
        # Converte o array para Surface do Pygame (transpondo largura/altura)
        self.surface_atual = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))

    def atualizar_e_desenhar(self, tela):
        if self.container:
            agora = time.perf_counter()
            if agora - self.ultimo_tempo >= self.intervalo_frame:
                self._proximo_frame()
                self.ultimo_tempo = agora
        tela.blit(self.surface_atual, (0, 0))

    def fechar(self):
        if self.container:
            self.container.close()
            self.container = None
