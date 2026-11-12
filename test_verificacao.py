import os
import sys

# Força driver de vídeo dummy para rodar testes sem janela gráfica
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
pygame.init()

from arkadia.personagem import criar_personagem, ganhar_xp, obter_skills_disponiveis
from arkadia.itens import (
    obter_item, adicionar_ao_inventario, remover_do_inventario,
    equipar_item, recalcular_atributos, usar_consumivel
)
from arkadia.estado import salvar_progresso, carregar_progresso, wipe_save
from arkadia.cenas import obter_cena, verificar_requisito_opcao, executar_efeitos_cena
from arkadia.combate import MotorCombate
import main

def testar_personagem_e_skills():
    print("[1/6] Testando criação de personagem e skills por nível...")
    p = criar_personagem("Herói", "Guerreiro")
    assert p["vida"] == 135
    assert p["classe"] == "Guerreiro"
    assert p["arma_equipada"] == "espada_ferro"
    
    # Skills nível 1
    skills_nv1 = obter_skills_disponiveis(p)
    assert len(skills_nv1) == 1
    assert skills_nv1[0]["id"] == "golpe_brutal"

    # Ganha XP para subir de nível
    msgs = ganhar_xp(p, 150)
    assert p["nivel"] == 2
    skills_nv2 = obter_skills_disponiveis(p)
    assert len(skills_nv2) == 2
    assert any(s["id"] == "postura_ferro" for s in skills_nv2)

    ganhar_xp(p, 300)
    assert p["nivel"] >= 3
    skills_nv3 = obter_skills_disponiveis(p)
    assert any(s["id"] == "grito_guerra" for s in skills_nv3)
    print("  -> OK!")

def testar_itens_e_inventario():
    print("[2/6] Testando itens, inventário e equipamentos...")
    p = criar_personagem("Guerreiro", "Guerreiro")
    atk_inicial = p["ataque"]

    # Adicionar e equipar arma superior
    adicionar_ao_inventario(p, "espada_arkhor", 1)
    sucesso, msg = equipar_item(p, "espada_arkhor")
    assert sucesso
    assert p["ataque"] > atk_inicial

    # Teste de consumíveis
    p["vida"] = 50
    sucesso, msg = usar_consumivel(p, "pocao_vida")
    assert sucesso
    assert p["vida"] == 95
    print("  -> OK!")

def testar_cenas_e_efeitos():
    print("[3/6] Testando catálogo de cenas, condições e efeitos...")
    c_menu = obter_cena("menu_principal")
    assert c_menu is not None
    assert len(c_menu["opcoes"]) >= 3

    p = criar_personagem("Viajante", "Mago")
    c_ajuda = obter_cena("ajudar_vila")
    avisos = executar_efeitos_cena(c_ajuda, p)
    assert p["flags"].get("ajudou_vila") is True
    assert "espada_quebrada" in p["inventario"]
    assert p["reputacao"] > 0

    # Teste de requisito
    op_elora = {"texto": "Falar", "requer_flag": "ajudou_vila"}
    assert verificar_requisito_opcao(op_elora, p) is True
    op_bloqueada = {"texto": "Secreto", "requer_ouro": 9999}
    assert verificar_requisito_opcao(op_bloqueada, p) is False
    print("  -> OK!")

def testar_combate_tatica():
    print("[4/6] Testando motor de combate tático, fraquezas e intenções...")
    p = criar_personagem("Arqueiro", "Arqueiro")
    vitoria_flag = [False]
    derrota_flag = [False]

    def on_vit(drops, xp, ouro, msgs):
        vitoria_flag[0] = True

    def on_der():
        derrota_flag[0] = True

    mc = MotorCombate(p, "lobo_sombrio", "floresta.mp4", on_vit, on_der)
    assert mc.inimigo["vida"] > 0
    assert mc.intencao_inimiga is not None

    # Ataque normal
    vida_antiga = mc.inimigo["vida"]
    mc.acao_ataque_normal()
    assert mc.inimigo["vida"] < vida_antiga

    # Postura defensiva
    mana_antiga = p["mana"]
    mc.acao_defender()
    assert p["mana"] >= mana_antiga
    print("  -> OK!")

def testar_save_migracao_wipe():
    print("[5/6] Testando persistência, migração e permadeath wipe...")
    caminho_teste = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teste_save.json")
    p = criar_personagem("HeroiSave", "Guerreiro")
    p["ouro"] = 88
    salvar_progresso(p, caminho_teste)

    # Carrega e valida
    carregado = carregar_progresso(caminho_teste)
    assert carregado is not None
    assert carregado["nome"] == "HeroiSave"
    assert carregado["ouro"] == 88

    # Wipe
    wipe_save(caminho_teste)
    assert carregar_progresso(caminho_teste) is None
    if os.path.exists(caminho_teste):
        os.remove(caminho_teste)
    print("  -> OK!")

def testar_smoke_jogo_principal():
    print("[6/6] Smoke test da aplicação JogoArkhor completa...")
    app = main.JogoArkhor()
    assert app.cenario_atual == "menu.mp4"
    app.ir_para_cena("selecao_classe")
    app.confirmar_classe("Guerreiro")
    assert app.jogador["classe"] == "Guerreiro"
    app.ir_para_cena("capitulo_1")
    app.ir_para_cena("vila_lumen")
    app.ir_para_cena("ajudar_vila")
    assert app.jogador["flags"]["ajudou_vila"] is True
    app.cenarios.fechar_todos()
    print("  -> OK!")

if __name__ == "__main__":
    print("=== INICIANDO BATERIA DE TESTES DE ARKADIA ===")
    testar_personagem_e_skills()
    testar_itens_e_inventario()
    testar_cenas_e_efeitos()
    testar_combate_tatica()
    testar_save_migracao_wipe()
    testar_smoke_jogo_principal()
    print("=== TODOS OS 6 TESTES PASSARAM COM SUCESSO! ===")
