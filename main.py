# CEOGAME Automation System
# Author: Zeki
# Version: 1.4.1
# Description: System created to automatically manage your companies in CEOGAME, a business simulation game
#   just like a real world CEO you gotta find the best solutions to your business, that's why I created this
#   app to manage my companies for me. Some may call this cheating, I call this being smarter than competition.

# Changelog:
# - Added .env file to configure your Authorization key easily

# More information can be found in the Wiki at our Github repo (https://github.com/EzequielDM/ceogame-manager)

# I'll ask for your forgiveness in advance, I'm not a Python developer and I was too bored to make a C++ application
# to do these tasks, so I stuck with Python for now and I'm kind of having a hard time because of syntax and
# functions not having the same names as in most other languages.
# For example, the fact that Array.length isn't a property and instead you have a len() function which returns the
# property, like... fr?!?!? But I'm dealing with this and knowledge is never enough, so, one more programming
# language down the list.


from requests import status_codes
import json
import requests
import os
import math
from dotenv import load_dotenv

load_dotenv()   # loads the .env file


headers = {
    # Do remember that the authorization currently needs to be gathered from a proxy like Postman.
    'authorization': os.getenv("AUTH"),
    'content-type': 'text/json; charset=utf-8',
    'content-length': '45',
    'host': 'api.ceogame.com.br',
    'connection': 'Keep-Alive',
    'accept-encoding': 'gzip',
    'user-agent': 'okhttp/3.12.6',
    'Cookie': 'AWSALB=YxSFHjL3UrBNWZqyxpTMxsXNwgdpDOMiuQTFe6XcVwohr0OBo7As2Lk//VsQvTS1WwgAzmk6k+RMcCWRwQoBfDbcRRhg4NsStMNiw860qylvxOe1v8HeZt4stuzm; AWSALBCORS=YxSFHjL3UrBNWZqyxpTMxsXNwgdpDOMiuQTFe6XcVwohr0OBo7As2Lk//VsQvTS1WwgAzmk6k+RMcCWRwQoBfDbcRRhg4NsStMNiw860qylvxOe1v8HeZt4stuzm; PHPSESSID=1kssq59m3lhlr37ah8od14qfbi'
}

turnos = 0


def refreshToken():
    url = "http://api.ceogame.com.br/game/tryRefreshToken"

    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def getDadosPersonagem():
    url = "http://api.ceogame.com.br/game/getDadosPersonagem"
    payload = "{\"email\":\"guest616d3db18d4ef@ceogame.com.br\"}"
    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code != requests.codes.ok):
        print(f"Error: {response.status_code} - {response.reason}")
        return False

    return response.json()


def getRedesEmpresas():
    url = "http://api.ceogame.com.br/game/getPersonagemRedesEmpresas"
    payload = "{\"email\":\"guest616d3db18d4ef@ceogame.com.br\"}"
    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code != requests.codes.ok):
        print(f"Error: {response.status_code} - {response.reason}")
        return False
    return response.json()


def getEmpresasIds():
    url = "http://api.ceogame.com.br/game/getPersonagemRedesEmpresas"
    payload = "{\"email\":\"guest616d3db18d4ef@ceogame.com.br\"}"
    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code != requests.codes.ok):
        print(f"Error: {response.status_code} - {response.reason}")
        return False

    response = response.json()
    empresas = []

    for e in response["redes"]:
        for c in e["empresas"]:
            empresas.append(int(c["id_empresa"]))

    return empresas


def getValorEmpresas():
    empresas = getRedesEmpresas()["redes"]
    valor = 0
    for rede in empresas:
        for empresa in rede["empresas"]:
            valor += float(empresa["dinheiro"])

    return valor


def getTotalValue():
    dadosPersonagem = getDadosPersonagem()
    patrimonio = float(dadosPersonagem["personagem"]["patrimonio"])
    dinheiro = float(dadosPersonagem["personagem"]["dinheiro"])
    empresas = getValorEmpresas()
    total = math.floor(empresas + patrimonio + dinheiro)
    return total


def payBills(round):
    if(round < 146 & round > 1000):
        print("Rodada inválida")
        return
    empresas = getEmpresasIds()
    dados = "{\"email\":\"guest616d3db18d4ef@ceogame.com.br\",\"rodada_vencto\":" + \
        str(round) + ",\"contas_selecionadas\":[1,2,3,4]}"
    for empresa in empresas:
        url = f"http://api.ceogame.com.br/game/pagarTipoContaEmpresaAssistente/{empresa}"
        res = requests.request(
            "POST", f"http://api.ceogame.com.br/game/pagarTipoContaEmpresaAssistente/{empresa}", headers=headers, data=dados)
        if(res.status_code != requests.codes.ok):
            print(
                f"Falha ao pagar contas da empresa de ID {empresa} | {res.reason}")
            continue

        res = res.json()
        dinheiro = res["dinheiro"]
        turnos = res["turnos"]
        print(
            f"Conta paga para empresa {empresa}\nSaldo: {dinheiro}\nTurnos: {turnos}")

    print(f"\nTodas as solicitações foram enviadas.")
    return


def pagarMarketing():
    empresas = getEmpresasIds()
    for empresa in empresas:
        url = f"http://api.ceogame.com.br/game/pagarPublicidadesEmpresaAssistente/{empresa}"
        payload = {"email": "guest616d3db18d4ef@ceogame.com.br",
                   "servicos_selecionados": [3, 4, 7, 8]}
        payload = json.dumps(payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        if(response.status_code != requests.codes.ok):
            print(
                f"Erro ao pagar marketing da empresa {empresa}\n  {response.text}")
            continue
        print(response.json if response.json else "Error while gathering response.json")


def updateTurnos():
    global turnos
    if(getDadosPersonagem() == False):
        print(f"Token inválido ou expirado! 401 - UNAUTHORIZED\n")
        quit()
    turnos = getDadosPersonagem()['personagem']['turnos']
    return


def main():
    cmd = input("Command: ")

    # Check command
    if(cmd == "valor"):
        print(f"Valor total do seu patrimônio: R${getTotalValue():,}.00")
        return
    if(cmd == "pagar"):
        rodada = input("Rodada: ")
        payBills(int(rodada))
        return
    if(cmd == "marketing"):
        pagarMarketing()
        return
    if(cmd == "exit" or cmd == "close" or cmd == "fechar"):
        quit()
    if(cmd == "nempresas" or cmd == "number"):
        count = getDadosPersonagem()['qtde_empresas']
        plural = "empresa" if count == 1 else "empresas"
        print(f"Você tem {count} {plural}")
        return
    if(cmd == "rodada"):
        rodada = getDadosPersonagem()['rodada']
        print(f"O jogo está na rodada {rodada}")
        return
    if(cmd == "emails" or cmd == "email"):
        emails = getDadosPersonagem()['emails_nao_lidos']
        plural = "email" if emails == 1 else "emails"
        plural2 = "lido" if emails == 1 else "lidos"
        print(f"Você tem {emails} {plural} não {plural2}")
        return
    if(cmd == "turnos"):
        plural = "turno" if turnos == 1 else "turnos"
        plural2 = "disponível" if turnos == 1 else "disponíveis"
        return print(f"{turnos} {plural} {plural2}")

    if(cmd == "dev"):
        a = input("Fill in function name: ")
        if(a == "getDados" or a == "getDadosPersonagem"):
            print(str(getDadosPersonagem()))
            return


while True:
    updateTurnos()
    main()
    os.system("pause")
