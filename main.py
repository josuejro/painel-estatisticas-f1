import sqlite3
import requests
from datetime import datetime

URL_BASE = 'https://api.openf1.org/v1'
BANCO = 'f1.db'
ANO_ATUAL = datetime.today().year

def inicializar_banco():

    db = sqlite3.connect('f1.db')
    cursor = db.cursor()
    db.execute('PRAGMA foreign_keys = ON')

    tabelas = '''
    CREATE TABLE IF NOT EXISTS pilotos(
        numero_piloto INTEGER PRIMARY KEY,
        sigla         TEXT,
        nome_completo TEXT,
        equipe        TEXT
    );

    CREATE TABLE IF NOT EXISTS sessoes(
        session_key   INTEGER PRIMARY KEY,
        nome          TEXT,
        tipo          TEXT,
        data          TEXT,
        pais          TEXT,
        circuito      TEXT
    );

    CREATE TABLE IF NOT EXISTS resultados(
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        session_key   INTEGER,
        numero_piloto INTEGER,
        posicao       INTEGER,
        FOREIGN KEY (session_key) REFERENCES sessoes(session_key),
        FOREIGN KEY (numero_piloto) REFERENCES pilotos(numero_piloto)
    );
    '''

    cursor.executescript(tabelas)
    db.commit()
    db.close()

def buscar_pilotos_api():
    print('Buscando pilotos...')

    try:
        resposta = requests.get(URL_BASE + '/drivers?session_key=latest')

        if resposta.status_code != 200:
            print(f'Erro ao buscar pilotos. Código: {resposta.status_code}')
            return
        
        dados = resposta.json()

        if dados is None:
            print('Nenhum piloto retornado pela API')
            return
        
        db = sqlite3.connect('f1.db')
        cursor = db.cursor()
        db.execute('PRAGMA foreign_keys = ON')

        cont = 0

        for piloto in dados:
            numero = piloto['driver_number']
            nome = piloto['full_name']
            sigla = piloto['name_acronym']
            equipe = piloto['team_name']

            cursor.execute('SELECT numero_piloto FROM pilotos WHERE numero_piloto = ?', (numero,))
            resultado = cursor.fetchone()

            if resultado is None:
                cursor.execute('INSERT INTO pilotos VALUES (?, ?, ?, ?)', (numero, nome, sigla, equipe))
                cont += 1
            else:
                cursor.execute('UPDATE pilotos SET equipe = ? WHERE numero_piloto = ?', (equipe, numero))
        
        db.commit()
        db.close()
        print()
        print(f'{cont} piloto(s) novo(s) adicionado(s)')

    except ConnectionError:
        print('Sem conexão com a internet')

def buscar_sessoes_api():
    print(f'Buscando sessões da temporada {ANO_ATUAL}...')

    try:
        params = {'year': ANO_ATUAL}
        resposta = requests.get(URL_BASE + '/sessions', params=params)

        if resposta.status_code != 200:
            print(f'Erro ao buscar sessões. Código: {resposta.status_code}')
        
        dados = resposta.json()

        if dados is None:
            print('Nenhuma sessção retornada pela API')
            return
        
        db = sqlite3.connect('f1.db')
        cursor = db.cursor()

        cont = 0

        for sessao in dados:
            key = sessao['session_key']
            nome = sessao['session_name']
            tipo = sessao['session_type']
            data = sessao['date_start']
            pais = sessao['country_name']
            circuito = sessao['circuit_short_name']

            cursor.execute('SELECT session_key FROM sessoes WHERE session_key = ?', (key,))
            resultado = cursor.fetchone()

            if resultado is None:
                cursor.execute('INSERT INTO sessoes VALUES (?, ?, ?, ?, ?, ?)', (key, nome, tipo, data, pais, circuito))
                cont += 1
        
        db.commit()
        db.close()
        print()
        print(f'{cont} sessão(ões) nova(s) adicionada(s)')

    except ConnectionError:
        print('Sem conexão com a internet.')

def buscar_resultado_sessao(session_key):
    print(f'Buscando resultado da sessão {session_key}...')

    try:
        params = {'session_key': session_key}
        resposta = requests.get(URL_BASE + '/position', params=params)

        if resposta.status_code != 200:
            print(f'Erro ao buscar os resultados. Código: {resposta.status_code}')
        
        dados = resposta.json()

        if dados is None:
            print('Nenhuma posição retornada para essa sessão')
            return
        
        dicionario_posicoes_finais = {}

        for registro in dados:
            numero = registro['driver_number']
            dicionario_posicoes_finais[numero] = registro['position']

        db = sqlite3.connect('f1.db')
        cursor = db.cursor()
        db.execute('PRAGMA foreign_keys = ON')

        cursor.execute('SELECT id FROM resultados WHERE session_key = ?', (session_key,))
        resultado = cursor.fetchone()

        if resultado is not None:
            print('Os resultados dessa sessão já foram salvos')
            db.close()
            return
        
        for numero_piloto, posicao in dicionario_posicoes_finais.items():
            cursor.execute('INSERT INTO resultados (session_key, numero_piloto, posicao) VALUES (?, ?, ?)', (session_key, numero_piloto, posicao))
        
        db.commit()
        db.close()
        print()
        print('Resultados salvos com sucesso!')

    except ConnectionError:
        print('Sem conexão com a internet')
        
def listar_sessoes():
    db = sqlite3.connect('f1.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sessoes ORDER BY data ASC')
    resultado = cursor.fetchall()
    db.close()

    if not resultado:
        print('Nenhuma sessão no banco. Use a opção 1 para atualizar.')
        return
    
    print('KEY  | PAÍS          | CIRCUITO   | TIPO        | DATA')
    print('-----+---------------+------------+-------------+----------')
    
    for session_key, nome, tipo, data, pais, circuito in resultado:
        print(f'{session_key} | {pais} | {circuito} | {tipo} | {data}')

def ver_resultado(session_key):
    db = sqlite3.connect('f1.db')
    cursor = db.cursor()
    cursor.execute(
        '''
        SELECT resultados.posicao, pilotos.nome_completo, pilotos.sigla, pilotos.equipe 
        FROM resultados
        JOIN pilotos ON resultados.numero_piloto = pilotos.numero_piloto 
        WHERE resultados.session_key = ? 
        ORDER BY posicao ASC
        ''', (session_key,))
    resultado = cursor.fetchall()
    
    if not resultado:
        print('Nenhum resultado salvo para essa sessão.')
        print('Use a opção 3 para buscar e salvar os resultados primeiro.')
        return
    
    cursor.execute('SELECT nome, pais, data FROM sessoes WHERE session_key = ?', (session_key,))
    sessao = cursor.fetchone()
    nome_sessao, pais, data = sessao

    db.close()

    print(f'Resultado: {nome_sessao}  | {pais}         | {data}')
    print('--------------------------+----------------+-------------')

    for posicao, nome_completo, sigla, equipe in resultado:
        print(f'{posicao}º | {sigla} | {nome_completo} | {equipe}')

def ver_piloto():
    db = sqlite3.connect('f1.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM pilotos ORDER BY numero_piloto ASC')
    resultado = cursor.fetchall()
    db.close()

    if not resultado:
        print('Nenhum piloto no banco. Use a opção 1 para atualizar.')
        return
    
    print('N°   | SIGLA         | NOME COMPLETO            | EQUIPE')
    print('-----+---------------+--------------------------+-------------')

    for numero, sigla, nome_completo, equipe in resultado:
        print(f'{numero} | {sigla} | {nome_completo} | {equipe}')

def menu_principal():
    while True:
        print()
        print(f"===== PAINEL F1 {ANO_ATUAL} =====")
        print("1. Atualizar dados da temporada")
        print("2. Ver sessões disponíveis")
        print("3. Ver resultado de uma sessão")
        print("4. Ver pilotos")
        print("0. Sair")
        print("=================================")     

        opc = input('Digite uma opção: ')

        if opc == '1':
            buscar_pilotos_api()
            buscar_sessoes_api()
        elif opc == '2':
            listar_sessoes()
        elif opc == '3':
            listar_sessoes()
            nova_opc = int(input('Digite o session_key da sessão desejada: '))

            try:
                buscar_resultado_sessao(nova_opc)
                ver_resultado(nova_opc)
            except ValueError:
                print('session_key inválido, digite apenas números')
        elif opc == '4':
            ver_piloto()
        elif opc == '0':
            print('Encerrando...')
            break
        else:
            print('Opção Inválida. Digite um número entre 0 e 4.')


inicializar_banco()
menu_principal()
