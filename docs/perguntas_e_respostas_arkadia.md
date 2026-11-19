# Perguntas e Respostas — Apresentação: As Crônicas de Arkhor

> Documento de apoio com possíveis perguntas do professor e respostas estruturadas para a apresentação de **Paradigmas em Python**.
> *(Este arquivo será atualizado conforme novas perguntas forem feitas.)*

---

## 1. Por que usar o `pygame` ao invés do `tkinter`?

**Resposta curta para falar em sala:**
> "Tkinter foi feito para aplicativos com formulários, como cadastro, botões e campos de texto. Pygame foi feito para jogos: ele redesenha a tela 60 vezes por segundo, o que eu precisava para os vídeos de cenário, as barras de vida e o combate em tempo real."

### Os 4 motivos principais

1. **Controle do Game Loop:**
   Um jogo precisa redesenhar a tela o tempo todo, mesmo sem nenhum clique, porque o vídeo do fundo continua rodando. No `pygame`, o código controla o loop diretamente (`main.py`):
   ```python
   while True:
       for evento in pygame.event.get(): ...   # lê cliques
       self.cenarios.renderizar(...)           # desenha o vídeo
       desenhar_painel_narrativo(...)          # desenha o painel
       pygame.display.flip()
       self.clock.tick(60)                     # 60 FPS
   ```
   No `tkinter`, quem controla o loop é o próprio framework (`mainloop()`), e a tela só muda quando ocorre um evento. Para animar vídeos, seria necessário agendar quadros com `root.after()`, o que é um improviso para esse tipo de aplicação.

2. **Renderização direta dos vídeos de fundo:**
   Cada quadro decodificado pelo PyAV vira uma `Surface` do `pygame` em apenas uma linha (`video_player.py`):
   ```python
   self.surface_atual = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
   ```
   No `tkinter`, seria necessário converter cada quadro usando Pillow (`ImageTk.PhotoImage`) e trocar a imagem de um `Label` 24 vezes por segundo — mais lento e complexo.

3. **Liberdade visual (UI customizada):**
   Todos os elementos da interface foram desenhados do zero: botões arredondados com efeito *hover*, barras proporcionais de HP/MP, caixa de intenção do inimigo e painel narrativo sobreposto ao vídeo. Widgets do `tkinter` seguem a aparência nativa do sistema operacional e são difíceis de estilizar nesse nível.

4. **Áudio integrado:**
   O `pygame` já inclui o módulo `pygame.mixer` para música de fundo e efeitos sonoros (`arkadia/audio.py`). O `tkinter` não possui suporte nativo a áudio, exigindo bibliotecas externas adicionais.

### O que o `pygame` custou (pontos de troca / *trade-offs*)

| Desvantagem do `pygame` | Como foi resolvida no projeto |
|---|---|
| Não possui botões prontos | Criada a classe `Botao` com `desenhar()` e `lidar_evento()` (`arkadia/ui.py`) |
| Não faz quebra de linha automática | Implementada a função `quebrar_texto()` (`arkadia/ui.py`) |
| Não gerencia layout responsivo sozinho | Cálculo manual de coordenadas, como o `x_dinamico` na barra de status |
| Exige instalação (`pip install pygame`) | Empacotado em executável standalone `.exe` via PyInstaller |

**Fechamento para a banca:**
> "Se fosse um sistema de cadastro, eu usaria Tkinter. Como é um jogo com animação contínua, vídeo e áudio, o Pygame era a ferramenta certa. E construir os botões e a quebra de texto manualmente permitiu aplicar mais conceitos de orientação a objetos, como na classe `Botao`."

---

## 2. Onde fica o começo? A base de onde sai todo o resto do código?

**Resposta curta para falar em sala:**
> "O ponto de partida de todo o programa fica no arquivo `main.py`. É lá que o Python começa a rodar, cria a janela, instancia o controlador `JogoArkhor`, carrega a primeira cena do JSON (`menu_principal`) e entra no loop infinito que mantém o jogo vivo a 60 FPS."

### A sequência exata de inicialização (em 4 passos)

1. **Porta de entrada (`if __name__ == "__main__":`) — final do [main.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/main.py):**
   ```python
   if __name__ == "__main__":
       app = JogoArkhor()   # 1. Prepara o jogo
       app.executar()       # 2. Liga o loop principal
   ```
   O `if __name__ == "__main__":` garante que o jogo só inicie quando `main.py` for executado diretamente (e não quando for importado por outro arquivo, como `test_verificacao.py`).

2. **Configuração de ambiente e caminhos — topo do [main.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/main.py#L18-L28):**
   Antes mesmo de criar a janela, o `main.py` define a resolução (`960x640`) e descobre onde estão as pastas `assets/` e `save_arkadia.json` (funcionando tanto via `python main.py` quanto compilado em `.exe`).

3. **Montagem dos sistemas no `JogoArkhor.__init__()` ([main.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/main.py#L123-L150)):**
   Ao instanciar `app = JogoArkhor()`, o construtor:
   - Inicializa o Pygame e cria a janela (`pygame.display.set_mode`);
   - Carrega as fontes;
   - Cria por **composição** os gerenciadores de cenário (`GerenciadorCenarios`) e áudio (`GerenciadorAudio`);
   - Chama `self.ir_para_cena("menu_principal")`, que lê o `data/cenas.json`, prepara o vídeo `menu.mp4` e monta os primeiros botões (*Novo Jogo*, *Carregar Progresso*, *Sair*).

4. **O coração que mantém tudo rodando (`app.executar()`) ([main.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/main.py#L370)):**
   A partir daí, o jogo entra no `while True:` (60 vezes por segundo). Tudo o que acontece depois — trocar de cena, criar personagem (`personagem.py`), entrar em combate (`MotorCombate`), salvar/carregar (`estado.py`) — é disparado a partir dos cliques capturados dentro desse loop.

```
python main.py
   └── __main__
         ├── 1. JogoArkhor() ──► abre janela + cria gerenciadores + ir_para_cena("menu_principal")
         └── 2. app.executar() ──► while True (60 FPS): lê cliques ──► dispara cenas / combate / save
```

---

## 3. Por que no arquivo `main.py` tem tantos `imports`? Essas são classes que foram criadas para o jogo ou são bibliotecas que vocês usaram?

**Resposta curta para falar em sala:**
> "Temos os dois tipos: apenas **três** são bibliotecas do Python ou externas (`os`, `sys` e `pygame`), e as outras **oito linhas** são módulos, classes e funções que **nós mesmos criamos** dentro da pasta `arkadia/`. Existem vários `imports` justamente por causa da **modularização**: em vez de colocar todo o código do jogo num único arquivo gigante, dividimos cada responsabilidade no seu próprio arquivo e o `main.py` apenas importa e conecta tudo."

### Divisão exata das 12 linhas de `import` do [main.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/main.py#L1-L12)

1. **Bibliotecas Nativas do Python (já vêm com o Python):**
   ```python
   import os    # Para montar caminhos de pastas e verificar se arquivos existem
   import sys   # Para fechar o programa (sys.exit) e detectar se está rodando como .exe
   ```

2. **Biblioteca Externa (instalada com `pip`):**
   ```python
   import pygame  # Motor gráfico: cria a janela, desenha na tela, lê cliques e toca som
   ```
   *(A outra biblioteca externa usada no projeto é a `av` / PyAV, que fica importada dentro do [video_player.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/video_player.py#L2)).*

3. **Código criado por nós para o jogo (Pacote `arkadia/` + `video_player.py`):**
   Misturamos **Classes** (Orientação a Objetos) e **Funções** (Paradigma Procedural), todas de autoria do projeto:

   | Linha de import no `main.py` | O que foi importado? | É Classe ou Função nossa? |
   |---|---|---|
   | `from video_player import VideoCenario` | `VideoCenario` | **Classe nossa** (reproduz o vídeo `.mp4` em loop) |
   | `from arkadia.ui import Botao, desenhar_painel_narrativo` | `Botao` / `desenhar_painel_narrativo` | **1 Classe** (botão clicável) e **1 Função** (desenha o painel) |
   | `from arkadia.cenas import obter_cena, verificar_requisito_opcao, executar_efeitos_cena` | Buscador e leitor de cenas | **3 Funções nossas** (leem o `cenas.json` e aplicam efeitos) |
   | `from arkadia.personagem import criar_personagem, obter_skills_disponiveis` | Criação do herói e skills | **2 Funções nossas** |
   | `from arkadia.combate import MotorCombate` | `MotorCombate` | **Classe nossa** (controla os turnos da batalha) |
   | `from arkadia.estado import salvar_progresso, carregar_progresso, wipe_save` | Sistema de Save / Load / Wipe | **3 Funções nossas** (gravam e leem `save_arkadia.json`) |
   | `from arkadia.audio import GerenciadorAudio` | `GerenciadorAudio` | **Classe nossa** (controla músicas e efeitos sonoros) |
   | `from arkadia.itens import obter_nome_item` | Consulta de item no catálogo | **1 Função nossa** |

### Comparação com a versão inicial do projeto
- Na primeira versão ([terminal_rpg.py](file:///F:/PEDRO/Estudos/ESTÁCIO/SEGUNDO%20PERIODO/PARADIGMAS%20EM%20PYTHON/EXERCICIOS/Jogo%20RPG/terminal_rpg.py)), tudo ficava num arquivo único de **2.078 linhas**.
- Na versão final (`v1.0`), aplicamos **modularização e separação de responsabilidades**: cada assunto virou um arquivo dentro do pacote `arkadia/`, e o `main.py` ficou com apenas **396 linhas**, servindo como o controlador que importa as peças.
