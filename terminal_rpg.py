import os
import time
import random
import json


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_SAVE = "save_arkadia.json"


# ============================================================
# SISTEMA BÁSICO
# ============================================================

def limpar():
    os.system("cls" if os.name == "nt" else "clear")


def esperar():
    input("\nPressione ENTER para continuar...")


def escrever(texto, velocidade=0.012):
    for letra in texto:
        print(letra, end="", flush=True)
        time.sleep(velocidade)
    print()


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto.center(65))
    print("=" * 65)


def barra(valor, maximo, tamanho=25):
    if maximo <= 0:
        return "[" + "-" * tamanho + "]"

    proporcao = max(0, min(1, valor / maximo))
    preenchido = int(proporcao * tamanho)

    return "[" + "#" * preenchido + "-" * (tamanho - preenchido) + "]"


def barra_mana(mana, mana_max, tamanho=25):
    if mana_max <= 0:
        return "[" + "-" * tamanho + "]"

    proporcao = max(0, min(1, mana / mana_max))
    preenchido = int(proporcao * tamanho)

    return "[" + "#" * preenchido + "-" * (tamanho - preenchido) + "]"


def escolher(pergunta, opcoes):

    while True:

        print("\n" + pergunta)

        for i, opcao in enumerate(opcoes, 1):
            print(f"  [{i}] {opcao}")

        resposta = input("\n> ")

        if resposta.isdigit():

            numero = int(resposta)

            if 1 <= numero <= len(opcoes):
                return numero

        print("Escolha inválida.")


# ============================================================
# ASCII ART
# ============================================================

def arte_cavaleiro():
    print(r"""
                 /\
                /  \
               /____\
              | 0 0 |
              |  /\ |
              | \/ |
               \__/
              /|  |\
             / |  | \
               |  |
              /    \
             /______\
                ||
               /  \
    """)


def arte_floresta():
    print(r"""
               /\                 /\
              /**\               /**\
             /****\             /****\
            /******\           /******\
               ||                 ||
               ||        /\       ||
      /\       ||       /**\      ||
     /**\             /****\      ||
    /****\           /******\     ||
   /******\             ||        ||
      ||                ||
    """)


def arte_vila():
    print(r"""
              /\                 /\
             /  \_______________/  \
            /                     \
           /_______________________\
           |   _     _     _      |
           |  | |   | |   | |     |
           |  |_|   |_|   |_|     |
           |                       |
           |_______________________|

                 VILA LÚMEN
    """)


def arte_castelo():
    print(r"""
                 |>>>>
                 |
            _    |    _
           | |   |   | |
           | |___|___| |
           |           |
           |  []   []  |
           |           |
        ___|_____|_____|___
       |                   |
       |   CASTELO NEGRO   |
       |___________________|
    """)


def arte_dragao():
    print(r"""
                         / \  //\
            |\___/|     /   \//  \\
            /O  O  \__ /    //  | \ \
           /     /  \_/    //   |  \ \
           @___@'    \    //    |   \ \
              |       \_ //     |    \ \
              |        ///      |     \ \
             /|       //       |      \ \
            / |      //        |       \ \
           /  |     //         |        \ \
          /   |    //          |         \ \
         /____|___//___________|__________\_\
    """)


def arte_ruinas():
    print(r"""
             /\        /\
            /  \      /  \
           /____\____/____\
           |              |
           |    RUÍNAS    |
           |              |
        ___|______  ______|___
       |          ||          |
       |          ||          |
       |__________||__________|
    """)


# ============================================================
# PERSONAGEM
# ============================================================

def criar_personagem(nome, classe):

    if classe == "Guerreiro":

        return {
            "nome": nome,
            "classe": classe,

            "nivel": 1,
            "xp": 0,
            "xp_proximo": 100,

            "vida": 130,
            "vida_max": 130,

            "mana": 30,
            "mana_max": 30,

            "ataque": 18,
            "defesa": 8,

            "ouro": 40,

            "arma": "Espada enferrujada",
            "armadura": "Roupa de viajante",

            "inventario": [
                "Poção",
                "Pão"
            ],

            "missoes": [],

            "historia": {
                "ajudou_vila": False,
                "confia_mago": False,
                "entrou_ruinas": False,
                "conheceu_dragao": False
            }
        }

    elif classe == "Mago":

        return {
            "nome": nome,
            "classe": classe,

            "nivel": 1,
            "xp": 0,
            "xp_proximo": 100,

            "vida": 90,
            "vida_max": 90,

            "mana": 100,
            "mana_max": 100,

            "ataque": 10,
            "defesa": 4,

            "ouro": 40,

            "arma": "Cajado de aprendiz",
            "armadura": "Manto simples",

            "inventario": [
                "Poção",
                "Pão",
                "Pergaminho"
            ],

            "missoes": [],

            "historia": {
                "ajudou_vila": False,
                "confia_mago": False,
                "entrou_ruinas": False,
                "conheceu_dragao": False
            }
        }

    else:

        return {
            "nome": nome,
            "classe": classe,

            "nivel": 1,
            "xp": 0,
            "xp_proximo": 100,

            "vida": 105,
            "vida_max": 105,

            "mana": 50,
            "mana_max": 50,

            "ataque": 15,
            "defesa": 6,

            "ouro": 40,

            "arma": "Arco simples",
            "armadura": "Couro de caçador",

            "inventario": [
                "Poção",
                "Pão",
                "Flecha"
            ],

            "missoes": [],

            "historia": {
                "ajudou_vila": False,
                "confia_mago": False,
                "entrou_ruinas": False,
                "conheceu_dragao": False
            }
        }


# ============================================================
# MENU DO PERSONAGEM
# ============================================================

def menu_personagem(jogador):

    while True:

        limpar()

        titulo("STATUS DO PERSONAGEM")

        print(f"""
Nome:       {jogador['nome']}
Classe:     {jogador['classe']}
Nível:      {jogador['nivel']}

❤️ VIDA
{barra(jogador['vida'], jogador['vida_max'])}
{jogador['vida']} / {jogador['vida_max']}

🔵 MANA
{barra_mana(jogador['mana'], jogador['mana_max'])}
{jogador['mana']} / {jogador['mana_max']}

XP:
{jogador['xp']} / {jogador['xp_proximo']}

Ataque:     {jogador['ataque']}
Defesa:     {jogador['defesa']}

Ouro:       {jogador['ouro']}

Arma:       {jogador['arma']}
Armadura:   {jogador['armadura']}
""")

        escolha = escolher(
            "O que deseja consultar?",
            [
                "Inventário",
                "Missões",
                "Histórico da aventura",
                "Voltar ao jogo"
            ]
        )

        if escolha == 1:

            limpar()

            titulo("INVENTÁRIO")

            if jogador["inventario"]:

                for item in jogador["inventario"]:
                    print(f"  • {item}")

            else:
                print("Seu inventário está vazio.")

            esperar()

        elif escolha == 2:

            limpar()

            titulo("MISSÕES")

            if jogador["missoes"]:

                for missao in jogador["missoes"]:
                    print(f"  • {missao}")

            else:
                print("Você ainda não possui missões.")

            esperar()

        elif escolha == 3:

            limpar()

            titulo("HISTÓRICO")

            h = jogador["historia"]

            print("\nAcontecimentos importantes:")

            if h["ajudou_vila"]:
                print("✓ Você ajudou a Vila Lúmen.")

            if h["confia_mago"]:
                print("✓ Você ganhou a confiança do mago.")

            if h["entrou_ruinas"]:
                print("✓ Você explorou as Ruínas de Arkhor.")

            if h["conheceu_dragao"]:
                print("✓ Você encontrou o Dragão Ancestral.")

            if not any(h.values()):
                print("Sua história ainda está começando.")

            esperar()

        else:
            return


# ============================================================
# XP E LEVEL UP
# ============================================================

def ganhar_xp(jogador, quantidade):

    jogador["xp"] += quantidade

    escrever(
        f"\n✨ Você ganhou {quantidade} XP!"
    )

    while jogador["xp"] >= jogador["xp_proximo"]:

        jogador["xp"] -= jogador["xp_proximo"]

        jogador["nivel"] += 1

        jogador["xp_proximo"] = int(
            jogador["xp_proximo"] * 1.35
        )

        jogador["vida_max"] += 15
        jogador["vida"] = jogador["vida_max"]

        jogador["mana_max"] += 10
        jogador["mana"] = jogador["mana_max"]

        jogador["ataque"] += 4
        jogador["defesa"] += 2

        titulo(
            f"VOCÊ SUBIU PARA O NÍVEL {jogador['nivel']}!"
        )

        escrever(
            "Seu corpo e suas habilidades ficaram mais fortes."
        )

        esperar()


# ============================================================
# INVENTÁRIO
# ============================================================

def usar_item(jogador):

    if "Poção" in jogador["inventario"]:

        jogador["inventario"].remove("Poção")

        recuperado = 40

        jogador["vida"] = min(
            jogador["vida"] + recuperado,
            jogador["vida_max"]
        )

        escrever(
            f"\n🧪 Você recuperou {recuperado} de vida."
        )

        return True

    escrever("\nVocê não possui uma poção.")

    return False


# ============================================================
# ATAQUES EXCLUSIVOS DAS CLASSES
# ============================================================

def ataque_especial(jogador):

    classe = jogador["classe"]

    # --------------------------------------------------------
    # GUERREIRO
    # --------------------------------------------------------

    if classe == "Guerreiro":

        custo = 10

        if jogador["mana"] < custo:

            escrever(
                "\n❌ Mana insuficiente para Golpe Brutal!"
            )

            return None

        jogador["mana"] -= custo

        dano = random.randint(
            jogador["ataque"] + 12,
            jogador["ataque"] + 25
        )

        escrever(
            "\n⚔️ GOLPE BRUTAL!"
        )

        escrever(
            f"Você desferiu um golpe devastador causando {dano} de dano!"
        )

        return dano

    # --------------------------------------------------------
    # MAGO
    # --------------------------------------------------------

    elif classe == "Mago":

        custo = 20

        if jogador["mana"] < custo:

            escrever(
                "\n❌ Mana insuficiente para Bola de Fogo!"
            )

            return None

        jogador["mana"] -= custo

        dano = random.randint(
            jogador["ataque"] + 20,
            jogador["ataque"] + 35
        )

        escrever(
            "\n🔥 BOLA DE FOGO!"
        )

        escrever(
            f"As chamas atingiram o inimigo causando {dano} de dano!"
        )

        return dano

    # --------------------------------------------------------
    # ARQUEIRO
    # --------------------------------------------------------

    else:

        custo = 12

        if jogador["mana"] < custo:

            escrever(
                "\n❌ Mana insuficiente para Flecha Perfurante!"
            )

            return None

        jogador["mana"] -= custo

        dano = random.randint(
            jogador["ataque"] + 15,
            jogador["ataque"] + 28
        )

        escrever(
            "\n🏹 FLECHA PERFURANTE!"
        )

        escrever(
            f"A flecha atravessou a defesa causando {dano} de dano!"
        )

        return dano


# ============================================================
# LAYOUT DA BATALHA
# ============================================================

def mostrar_batalha(
    jogador,
    inimigo,
    vida_inimigo,
    vida_inimigo_max
):

    limpar()

    titulo(f"⚔️  BATALHA — {inimigo}")

    print("\n" + " " * 10 + "SEU PERSONAGEM")

    print(
        f"\n❤️ VIDA: {jogador['vida']} / "
        f"{jogador['vida_max']}"
    )

    print(
        barra(
            jogador["vida"],
            jogador["vida_max"]
        )
    )

    print(
        f"\n🔵 MANA: {jogador['mana']} / "
        f"{jogador['mana_max']}"
    )

    print(
        barra_mana(
            jogador["mana"],
            jogador["mana_max"]
        )
    )

    # Mostra claramente o consumo do ataque poderoso
    custo_poderoso = 15

    print(
        f"   Ataque poderoso: "
        f"{custo_poderoso} mana"
    )

    print(
        "   "
        + barra_mana(
            custo_poderoso,
            jogador["mana_max"]
        )
        + f"  <- custo"
    )

    # --------------------------------------------------------

    print("\n" + "-" * 65)

    print("\n" + " " * 10 + "INIMIGO")

    print(
        f"\n👹 VIDA: {vida_inimigo} / "
        f"{vida_inimigo_max}"
    )

    print(
        barra(
            vida_inimigo,
            vida_inimigo_max
        )
    )

    print("\n" + "-" * 65)

    # Habilidade exclusiva
    if jogador["classe"] == "Guerreiro":
        especial = "Golpe Brutal"
        custo_especial = 10

    elif jogador["classe"] == "Mago":
        especial = "Bola de Fogo"
        custo_especial = 20

    else:
        especial = "Flecha Perfurante"
        custo_especial = 12

    print("\n⚔️ HABILIDADES")

    print(
        f"1. Ataque normal"
    )

    print(
        f"2. Ataque poderoso "
        f"[15 mana]"
    )

    print(
        f"3. {especial} "
        f"[{custo_especial} mana]"
    )

    print(
        "4. 🛡️ Defender "
        "[reduz dano + recupera mana]"
    )

    print(
        "5. 🧪 Usar poção"
    )

    print(
        "6. 🏃 Fugir"
    )

    print("\n" + "=" * 65)


# ============================================================
# SISTEMA DE COMBATE
# ============================================================

def combate(
    jogador,
    inimigo,
    vida_inimigo,
    ataque_inimigo
):

    vida_inimigo_max = vida_inimigo

    defendendo = False

    while vida_inimigo > 0 and jogador["vida"] > 0:

        # Sempre mostra o estado atualizado
        mostrar_batalha(
            jogador,
            inimigo,
            vida_inimigo,
            vida_inimigo_max
        )

        escolha = input("\nSua ação > ")

        if not escolha.isdigit():
            continue

        escolha = int(escolha)

        # ====================================================
        # ATAQUE NORMAL
        # ====================================================

        if escolha == 1:

            dano = random.randint(
                jogador["ataque"] - 4,
                jogador["ataque"] + 7
            )

            dano = max(1, dano)

            vida_inimigo -= dano

            limpar()

            titulo("⚔️ ATAQUE")

            escrever(
                f"\nVocê atacou {inimigo}!"
            )

            escrever(
                f"💥 Dano causado: {dano}"
            )

            esperar()

        # ====================================================
        # ATAQUE PODEROSO
        # ====================================================

        elif escolha == 2:

            custo = 15

            if jogador["mana"] < custo:

                limpar()

                titulo("❌ MANA INSUFICIENTE")

                escrever(
                    f"\nVocê precisa de {custo} mana."
                )

                escrever(
                    f"Mana atual: {jogador['mana']}"
                )

                esperar()

                continue

            jogador["mana"] -= custo

            dano = random.randint(
                jogador["ataque"] + 10,
                jogador["ataque"] + 22
            )

            vida_inimigo -= dano

            limpar()

            titulo("💥 ATAQUE PODEROSO")

            print(
                "\nMana consumida:"
            )

            print(
                " " + "#" * custo
            )

            print(
                f" {custo} pontos de mana"
            )

            escrever(
                f"\nVocê causou {dano} de dano!"
            )

            esperar()

        # ====================================================
        # ATAQUE EXCLUSIVO
        # ====================================================

        elif escolha == 3:

            resultado = ataque_especial(jogador)

            if resultado is None:

                esperar()
                continue

            vida_inimigo -= resultado

            esperar()

        # ====================================================
        # DEFENDER
        # ====================================================

        elif escolha == 4:

            defendendo = True

            recuperacao = random.randint(8, 15)

            jogador["mana"] = min(
                jogador["mana"] + recuperacao,
                jogador["mana_max"]
            )

            limpar()

            titulo("🛡️ DEFENDENDO")

            escrever(
                "Você assume uma posição defensiva."
            )

            escrever(
                "O próximo ataque inimigo terá seu dano reduzido."
            )

            escrever(
                f"\n🔵 Você recuperou {recuperacao} de mana."
            )

            esperar()

        # ====================================================
        # POÇÃO
        # ====================================================

        elif escolha == 5:

            limpar()

            titulo("🧪 POÇÃO")

            if not usar_item(jogador):

                esperar()
                continue

            esperar()

            # Usar poção não permite ataque inimigo?
            # Permite, então continua normalmente.

        # ====================================================
        # FUGIR
        # ====================================================

        elif escolha == 6:

            limpar()

            titulo("🏃 FUGA")

            escrever(
                "Você tenta fugir da batalha..."
            )

            if random.random() < 0.45:

                escrever(
                    "\nVocê conseguiu escapar!"
                )

                esperar()

                return False

            escrever(
                "\nO inimigo bloqueou sua fuga!"
            )

            esperar()

        else:

            continue

        # ====================================================
        # INIMIGO DERROTADO
        # ====================================================

        if vida_inimigo <= 0:

            limpar()

            titulo("🏆 VITÓRIA")

            escrever(
                f"{inimigo} foi derrotado!"
            )

            recompensa = random.randint(20, 45)

            jogador["ouro"] += recompensa

            escrever(
                f"\n💰 Você recebeu {recompensa} moedas."
            )

            ganhar_xp(
                jogador,
                random.randint(45, 75)
            )

            esperar()

            return True

        # ====================================================
        # TURNO DO INIMIGO
        # ====================================================

        dano = random.randint(
            max(1, ataque_inimigo - 5),
            ataque_inimigo + 5
        )

        # Defesa normal
        dano_real = max(
            1,
            dano - jogador["defesa"] // 3
        )

        # Defesa especial
        if defendendo:

            dano_real = max(
                1,
                dano_real // 3
            )

            defendendo = False

            limpar()

            titulo("🛡️ DEFESA BEM-SUCEDIDA")

            escrever(
                f"O ataque de {inimigo} foi parcialmente bloqueado!"
            )

            escrever(
                f"\nDano recebido: {dano_real}"
            )

            jogador["vida"] -= dano_real

            esperar()

        else:

            jogador["vida"] -= dano_real

            limpar()

            titulo("👹 ATAQUE INIMIGO")

            escrever(
                f"{inimigo} atacou você!"
            )

            escrever(
                f"\n💔 Você recebeu {dano_real} de dano."
            )

            esperar()

    return jogador["vida"] > 0


# ============================================================
# CAPÍTULO 1
# ============================================================

def capitulo_1(jogador):

    limpar()

    titulo("CAPÍTULO I — O DESPERTAR")

    arte_floresta()

    escrever(
        "A chuva cai sobre a floresta."
    )

    escrever(
        "Você desperta no chão sem saber como chegou ali."
    )

    escrever(
        "Há uma marca estranha brilhando em sua mão."
    )

    escrever(
        "Uma voz distante sussurra seu nome."
    )

    escrever(
        f'"{jogador["nome"]}..."'
    )

    escrever(
        "Você se levanta."
    )

    escrever(
        "Ao norte existe uma vila."
    )

    escrever(
        "Ao sul, uma floresta coberta por névoa."
    )

    escrever(
        "E no horizonte existe uma montanha negra."
    )

    esperar()

    escolha = escolher(
        "Para onde você vai?",
        [
            "Ir para a Vila Lúmen",
            "Explorar a floresta"
        ]
    )

    if escolha == 1:
        vila_lumen(jogador)
    else:
        floresta_inicial(jogador)


# ============================================================
# VILA
# ============================================================

def vila_lumen(jogador):

    limpar()

    arte_vila()

    titulo("VILA LÚMEN")

    escrever(
        "A vila está quase completamente destruída."
    )

    escrever(
        "Casas queimadas."
    )

    escrever(
        "Pessoas escondidas."
    )

    escrever(
        "Guardas mortos nas ruas."
    )

    escrever(
        "Uma mulher corre até você."
    )

    escrever(
        '"Você veio ajudar?"'
    )

    escolha = escolher(
        "O que você responde?",
        [
            "Sim. Quero ajudar.",
            "Não tenho nada a ver com isso.",
            "O que aconteceu aqui?"
        ]
    )

    if escolha == 1:

        jogador["historia"]["ajudou_vila"] = True

        jogador["missoes"].append(
            "Descobrir quem atacou a Vila Lúmen."
        )

        escrever(
            "\nA mulher entrega uma espada quebrada."
        )

        jogador["inventario"].append(
            "Espada quebrada"
        )

        escrever(
            "Ela aponta para a floresta."
        )

        escrever(
            '"Eles vieram de lá."'
        )

        ganhar_xp(jogador, 25)

        esperar()

        floresta_inicial(jogador)

    elif escolha == 2:

        escrever(
            "\nVocê decide seguir sozinho."
        )

        esperar()

        floresta_inicial(jogador)

    else:

        escrever(
            "\nA mulher conta que criaturas atacaram a vila."
        )

        escrever(
            "Mas existe algo ainda mais estranho."
        )

        escrever(
            '"Todas procuravam alguém..."'
        )

        escrever(
            '"Alguém com uma marca na mão."'
        )

        esperar()

        floresta_inicial(jogador)


# ============================================================
# FLORESTA
# ============================================================

def floresta_inicial(jogador):

    limpar()

    arte_floresta()

    titulo("A FLORESTA DE ARKHOR")

    escrever(
        "Você entra na floresta."
    )

    escrever(
        "O ar fica frio."
    )

    escrever(
        "A marca em sua mão começa a brilhar."
    )

    escrever(
        "Então você ouve um rugido."
    )

    esperar()

    venceu = combate(
        jogador,
        "Lobo Sombrio",
        45 + jogador["nivel"] * 5,
        12
    )

    if not venceu:

        game_over(jogador)
        return

    jogador["missoes"].append(
        "Descobrir o significado da marca."
    )

    escrever(
        "\nDepois da batalha, você encontra um homem encapuzado."
    )

    escolha = escolher(
        "O que fazer?",
        [
            "Seguir o homem",
            "Ignorá-lo",
            "Perguntar quem ele é"
        ]
    )

    if escolha == 1:
        mago(jogador)

    elif escolha == 2:
        ruinas(jogador)

    else:

        escrever(
            '\nO homem responde: "Meu nome não importa ainda."'
        )

        escrever(
            '"Mas você precisa chegar às ruínas."'
        )

        jogador["historia"]["confia_mago"] = True

        ganhar_xp(jogador, 30)

        esperar()

        ruinas(jogador)


# ============================================================
# MAGO
# ============================================================

def mago(jogador):

    limpar()

    titulo("O MAGO DA FLORESTA")

    escrever(
        "O homem retira o capuz."
    )

    escrever(
        '"Eu conheço essa marca."'
    )

    escrever(
        '"Ela pertence aos antigos reis de Arkhor."'
    )

    escrever(
        '"Se ela apareceu em você, significa que o reino está acordando."'
    )

    escolha = escolher(
        "O que você deseja perguntar?",
        [
            "Quem era o antigo rei?",
            "Por que a marca está em mim?",
            "Onde fica Arkhor?"
        ]
    )

    if escolha == 1:

        escrever(
            "\nO mago fala sobre um rei chamado Aurelion."
        )

        escrever(
            "Ele desapareceu há trezentos anos."
        )

    elif escolha == 2:

        escrever(
            "\nO mago olha para sua mão."
        )

        escrever(
            '"Você pode ser descendente dele."'
        )

    else:

        escrever(
            "\nO mago aponta para uma montanha distante."
        )

        escrever(
            '"As ruínas estão além daquela montanha."'
        )

    jogador["historia"]["confia_mago"] = True

    jogador["inventario"].append("Pergaminho antigo")

    ganhar_xp(jogador, 40)

    esperar()

    ruinas(jogador)


# ============================================================
# RUÍNAS
# ============================================================

def ruinas(jogador):

    limpar()

    arte_ruinas()

    titulo("CAPÍTULO II — AS RUÍNAS DE ARKHOR")

    jogador["historia"]["entrou_ruinas"] = True

    escrever(
        "Depois de horas caminhando, você encontra enormes ruínas."
    )

    escrever(
        "As pedras possuem o mesmo símbolo da marca em sua mão."
    )

    escrever(
        "No centro existe uma porta."
    )

    escrever(
        "Ela se abre quando você toca nela."
    )

    esperar()

    escolha = escolher(
        "Dentro das ruínas existem três caminhos.",
        [
            "Sala dos guerreiros",
            "Biblioteca antiga",
            "Cripta subterrânea"
        ]
    )

    if escolha == 1:
        sala_guerreiros(jogador)

    elif escolha == 2:
        biblioteca(jogador)

    else:
        cripta(jogador)


# ============================================================
# SALA DOS GUERREIROS
# ============================================================

def sala_guerreiros(jogador):

    limpar()

    titulo("SALA DOS GUERREIROS")

    escrever(
        "Estátuas de antigos cavaleiros cercam a sala."
    )

    escrever(
        "Quando você passa, uma delas se move."
    )

    venceu = combate(
        jogador,
        "Guardião de Pedra",
        80 + jogador["nivel"] * 8,
        18
    )

    if venceu:

        jogador["arma"] = "Espada de Arkhor"

        jogador["ataque"] += 8

        escrever(
            "\nVocê encontrou a Espada de Arkhor!"
        )

        ganhar_xp(jogador, 80)

        esperar()

        capitulo_3(jogador)

    else:

        game_over(jogador)


# ============================================================
# BIBLIOTECA
# ============================================================

def biblioteca(jogador):

    limpar()

    titulo("BIBLIOTECA PERDIDA")

    escrever(
        "Milhares de livros cobrem as paredes."
    )

    escrever(
        "Um deles possui o símbolo da sua marca."
    )

    escolha = escolher(
        "O que você faz?",
        [
            "Ler o livro",
            "Levar o livro",
            "Ignorar e continuar"
        ]
    )

    if escolha == 1:

        jogador["mana_max"] += 20
        jogador["mana"] = jogador["mana_max"]

        escrever(
            "\nVocê aprende uma técnica antiga."
        )

        escrever(
            "Sua mana máxima aumentou."
        )

        ganhar_xp(jogador, 70)

    elif escolha == 2:

        jogador["inventario"].append(
            "Livro de Arkhor"
        )

        escrever(
            "\nVocê guarda o livro."
        )

        ganhar_xp(jogador, 50)

    else:

        escrever(
            "\nVocê decide não tocar no livro."
        )

    esperar()

    capitulo_3(jogador)


# ============================================================
# CRIPTA
# ============================================================

def cripta(jogador):

    limpar()

    titulo("A CRIPTA")

    escrever(
        "Você desce por uma escada."
    )

    escrever(
        "O ar fica pesado."
    )

    escrever(
        "Há dezenas de esqueletos."
    )

    escrever(
        "Então um deles se levanta."
    )

    venceu = combate(
        jogador,
        "Cavaleiro Morto",
        100 + jogador["nivel"] * 10,
        22
    )

    if venceu:

        jogador["armadura"] = "Armadura do Guardião"

        jogador["defesa"] += 7

        escrever(
            "\nVocê encontrou a Armadura do Guardião."
        )

        ganhar_xp(jogador, 100)

        esperar()

        capitulo_3(jogador)

    else:

        game_over(jogador)


# ============================================================
# CAPÍTULO 3
# ============================================================

def capitulo_3(jogador):

    limpar()

    titulo("CAPÍTULO III — A MONTANHA NEGRA")

    escrever(
        "Você deixa as ruínas."
    )

    escrever(
        "No horizonte, uma montanha negra domina o céu."
    )

    escrever(
        "Uma tempestade se forma ao redor dela."
    )

    arte_castelo()

    escrever(
        "No topo existe o Castelo Negro."
    )

    escrever(
        "Antes de chegar até ele, você encontra uma ponte."
    )

    escolha = escolher(
        "O caminho está protegido.",
        [
            "Lutar contra os guardas",
            "Procurar uma passagem secreta",
            "Tentar conversar"
        ]
    )

    if escolha == 1:

        venceu = combate(
            jogador,
            "Guarda Negro",
            110,
            25
        )

        if jogador["vida"] > 0 and venceu:
            capitulo_4(jogador)
        else:
            game_over(jogador)

    elif escolha == 2:

        escrever(
            "\nVocê encontra uma passagem escondida."
        )

        ganhar_xp(jogador, 60)

        capitulo_4(jogador)

    else:

        escrever(
            "\nOs guardas reconhecem sua marca."
        )

        escrever(
            '"Então você finalmente voltou..."'
        )

        escrever(
            "Eles deixam você passar."
        )

        jogador["historia"]["conheceu_dragao"] = True

        ganhar_xp(jogador, 75)

        capitulo_4(jogador)


# ============================================================
# CAPÍTULO 4
# ============================================================

def capitulo_4(jogador):

    limpar()

    titulo("CAPÍTULO IV — O CASTELO NEGRO")

    arte_castelo()

    escrever(
        "Você entra no castelo."
    )

    escrever(
        "Não existem soldados."
    )

    escrever(
        "Não existem moradores."
    )

    escrever(
        "Apenas silêncio."
    )

    escrever(
        "No final do corredor existe uma porta enorme."
    )

    esperar()

    escolha = escolher(
        "Você abre a porta?",
        [
            "Sim",
            "Procurar outra entrada"
        ]
    )

    if escolha == 2:

        escrever(
            "\nVocê encontra uma passagem atrás de uma estátua."
        )

        ganhar_xp(jogador, 80)

    limpar()

    arte_dragao()

    titulo("O DRAGÃO ANCESTRAL")

    escrever(
        "Uma criatura gigantesca abre os olhos."
    )

    escrever(
        '"Finalmente..."'
    )

    escrever(
        '"O portador da marca chegou."'
    )

    jogador["historia"]["conheceu_dragao"] = True

    escolha = escolher(
        "Como você reage?",
        [
            "Atacar o dragão",
            "Perguntar o que ele quer",
            "Perguntar sobre sua origem"
        ]
    )

    if escolha == 1:

        chefe_final(jogador)

    elif escolha == 2:

        escrever(
            '\nO dragão responde:'
        )

        escrever(
            '"Quero impedir que você repita o erro de seus ancestrais."'
        )

        esperar()

        chefe_final(jogador)

    else:

        escrever(
            '\nO dragão encara sua marca.'
        )

        escrever(
            '"Você é descendente de Aurelion."'
        )

        escrever(
            '"E agora precisa decidir o destino de Arkhor."'
        )

        esperar()

        chefe_final(jogador)


# ============================================================
# BATALHA FINAL
# ============================================================

def chefe_final(jogador):

    limpar()

    titulo("CAPÍTULO V — O DESTINO DE ARKHOR")

    arte_dragao()

    escrever(
        "O chão treme."
    )

    escrever(
        "O Dragão Ancestral abre suas asas."
    )

    escrever(
        "O verdadeiro teste começou."
    )

    vida = 220 + jogador["nivel"] * 20

    venceu = combate(
        jogador,
        "DRAGÃO ANCESTRAL",
        vida,
        35 + jogador["nivel"] * 2
    )

    if venceu:
        final_vitoria(jogador)
    else:
        game_over(jogador)


# ============================================================
# FINAL
# ============================================================

def final_vitoria(jogador):

    limpar()

    titulo("FIM DA PRIMEIRA CAMPANHA")

    arte_dragao()

    escrever(
        "O dragão cai."
    )

    escrever(
        "A tempestade desaparece."
    )

    escrever(
        "A marca em sua mão começa a desaparecer."
    )

    escrever(
        "Você olha para o horizonte."
    )

    escrever(
        "A Vila Lúmen ainda precisa ser reconstruída."
    )

    escrever(
        "As ruínas escondem segredos."
    )

    escrever(
        "E você sabe que existem outros reinos além das montanhas."
    )

    ganhar_xp(jogador, 250)

    titulo("VOCÊ TERMINOU A PRIMEIRA CAMPANHA")

    escrever(
        f"Herói: {jogador['nome']}"
    )

    escrever(
        f"Nível alcançado: {jogador['nivel']}"
    )

    escrever(
        "Sua história, porém, ainda não terminou..."
    )

    esperar()


def game_over(jogador):

    limpar()

    titulo("VOCÊ MORREU")

    print(r"""
                    .-.
                   (   )
                    | |
                 ___| |___
                /         \
               /    RIP    \
               \           /
                \_________/
    """)

    escrever(
        f"{jogador['nome']} caiu durante a aventura."
    )

    escrever(
        "Seu destino terminou aqui."
    )

    esperar()


# ============================================================
# SALVAR / CARREGAR
# ============================================================

def salvar(jogador):

    with open(
        ARQUIVO_SAVE,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            jogador,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    escrever(
        "\n💾 Jogo salvo!"
    )


def carregar():

    if not os.path.exists(ARQUIVO_SAVE):
        return None

    try:

        with open(
            ARQUIVO_SAVE,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except:

        return None


# ============================================================
# MENU PRINCIPAL
# ============================================================

def novo_jogo():

    limpar()

    titulo("AS CRÔNICAS DE ARKHOR")

    arte_cavaleiro()

    escrever(
        "Uma antiga profecia está despertando."
    )

    escrever(
        "Três séculos atrás, o reino de Arkhor desapareceu."
    )

    escrever(
        "Agora alguém está tentando trazê-lo de volta."
    )

    nome = input(
        "\nDigite o nome do seu personagem: "
    )

    classe_escolhida = escolher(
        "Escolha sua classe:",
        [
            "Guerreiro — muita vida e defesa",
            "Mago — muita mana e habilidades",
            "Arqueiro — equilíbrio entre ataque e defesa"
        ]
    )

    classes = [
        "Guerreiro",
        "Mago",
        "Arqueiro"
    ]

    jogador = criar_personagem(
        nome,
        classes[classe_escolhida - 1]
    )

    limpar()

    escrever(
        f"Então está decidido, {nome}."
    )

    escrever(
        "Sua aventura começa agora."
    )

    esperar()

    capitulo_1(jogador)

    return jogador


def jogo():

    while True:

        limpar()

        titulo("AS CRÔNICAS DE ARKHOR")

        escolha = escolher(
            "Menu principal",
            [
                "Novo jogo",
                "Carregar jogo",
                "Sair"
            ]
        )

        if escolha == 1:

            jogador = novo_jogo()

        elif escolha == 2:

            jogador = carregar()

            if jogador is None:

                print(
                    "\nNenhum jogo salvo encontrado."
                )

                esperar()

                continue

            escrever(
                f"\nBem-vindo de volta, {jogador['nome']}!"
            )

            esperar()

            capitulo_3(jogador)

        else:

            print(
                "\nAté a próxima, aventureiro!"
            )

            break


# ============================================================
# INÍCIO
# ============================================================

if __name__ == "__main__":
    jogo()
