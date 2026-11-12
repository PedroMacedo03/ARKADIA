# 🛡️ ARKADIA — As Crônicas de Arkhor

RPG narrativo e estratégico em turnos desenvolvido em **Python**. Ambientado em um reino sombrio esquecido após o cataclismo do Rei Aurelion, o jogador desperta com uma runa arcana brilhando em sua mão e precisa decidir o destino das terras de Arkhor.

---

## 🎮 Versões do Jogo

O projeto conta com duas edições completas:

1. **Versão Gráfica com Vídeos de Fundo (v1.0 - Atual)**:
   - Interface visual renderizada em **Pygame**.
   - Cenários dinâmicos animados em vídeo loop `.mp4` (decodificação otimizada via FFmpeg / PyAV).
   - Combate tático por turnos com fraquezas elementais, intenções telegrafadas do inimigo e status (*veneno, queimadura, sangramento, atordoamento*).
   - Sistema de classes (Guerreiro, Mago, Arqueiro) com árvore de habilidades por nível.
   - Povoado de Vila Lúmen como Hub com mercador, descanso na fogueira e suporte da companheira Elora.
   - Três finais distintos (*Restauração, Selo Eterno e Soberano Sombrio*).
   - Mecânica de Auto-Save com *Permadeath* (Wipe automático do save em caso de derrota).
   - **Arquivo:** `main.py`

2. **Versão Clássica de Terminal (v0.5)**:
   - Executada puramente no terminal de comandos.
   - Arte em ASCII para todos os cenários e chefes.
   - Sistema clássico de escolhas e combate direto.
   - **Arquivo:** `terminal_rpg.py`

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10 ou superior
- Instalar as dependências:
```bash
pip install -r requirements.txt
```

### Iniciar o Jogo

**No Windows (PowerShell):**
```powershell
Set-Location "F:\PEDRO\Estudos\ESTÁCIO\SEGUNDO PERIODO\PARADIGMAS EM PYTHON\Jogo RPG"; python main.py
```

**No Git Bash / Linux / macOS:**
```bash
python main.py
```

*(Para jogar a versão de terminal, execute `python terminal_rpg.py`)*

---

## 📂 Estrutura do Projeto

```
Jogo RPG/
├── main.py               # Ponto de entrada da versão gráfica
├── video_player.py       # Decodificador de vídeos MP4 em tempo real (PyAV)
├── terminal_rpg.py       # Versão clássica puramente em terminal
├── requirements.txt      # Dependências do projeto
├── save_arkadia.json     # Arquivo de save do jogador
├── assets/               # Vídeos em loop de todos os cenários
│   ├── menu.mp4
│   ├── floresta.mp4
│   ├── vila.mp4
│   ├── ruinas.mp4
│   ├── guerreiros.mp4
│   ├── biblioteca.mp4
│   ├── cripta.mp4
│   ├── ponte.mp4
│   └── castelo.mp4
├── data/                 # Arquitetura orientada a dados (JSON)
│   ├── cenas.json        # Árvore de cenas, diálogos, opções e efeitos
│   ├── inimigos.json     # Atributos, fraquezas, intenções e fases
│   ├── itens.json        # Catálogo de armas, armaduras e consumíveis
│   └── missoes.json      # Missões primárias e secundárias
└── arkadia/              # Pacote modular do jogo
    ├── cenas.py          # Interpretador e executor de cenas
    ├── combate.py        # Motor de combate tático por turnos
    ├── estado.py         # Save, load, migração e permadeath wipe
    ├── itens.py          # Gestão de inventário e equipamentos
    ├── personagem.py     # Criação, atributos e skills por classe
    ├── ui.py             # Componentes de interface e botões
    └── audio.py          # Gerenciador tolerante de som
```

---

## ⚔️ Mecânicas de Profundidade

- **Intenções Telegrafadas**: Em combate, os inimigos avisam a sua próxima ação (ex.: *"O Dragão estala as mandíbulas incandescentes..."*). O jogador deve usar essa informação para decidir entre atacar com tudo ou usar a **Postura Defensiva** (-65% dano sofrido).
- **Fraquezas Elementais**: O Guardião de Pedra é resistente a cortes físicos, mas fraco contra magia arcana; o Cavaleiro Morto e o Lobo Sombrio sofrem mais dano por fogo.
- **Economia e Hub**: Venda peles de lobo e fragmentos rúnicos para o mercador de Vila Lúmen e compre poções e elixires.
- **Companheira de Suporte**: Ajude a vila e recrute Elora para receber curas e unguentos periódicos durante as batalhas mais difíceis.
- **Múltiplos Finais**: O desfecho da história dependerá de suas escolhas morais perante o trono de Aurelion.
