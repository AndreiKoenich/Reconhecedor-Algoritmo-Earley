# RECONHECEDOR DE PALAVRAS GERADAS POR GRAMATICA LIVRE DE CONTEXTO COM ALGORITMO DE EARLEY
# Autor: Andrei Pochmann Koenich

# O programa a seguir recebe um arquivo de entrada contendo uma Gramatica Livre de Contexto (GLC) de acordo com uma sintaxe e uma palavra, e informa
# ao usuario se a palavra inserida pode ser gerada pela GLC do arquivo de entrada, por meio da utilização do algoritmo de Earley, com a aplicacao
# do algoritmo sendo demonstrada passo a passo.

# Referencias:
# https://pt.wikipedia.org/wiki/Algoritmo_Earley
# https://www.youtube.com/watch?v=7u03UcbM-qU&feature=youtu.be
# https://www.youtube.com/watch?v=WkmV_a9q5Qw

import os
import sys

SIMBOLOMARCADOR = bytes([254]).decode('cp437')[0] # Constante representando o simbolo marcador do algoritmo de Earley.
DELIMITADOR_ESQ = bytes([179]).decode('cp437')[0] # Constante para demarcar o caractere da palavra sendo analisado.
DELIMITADOR_DIR = bytes([179]).decode('cp437')[0] # Constante para demarcar o caractere da palavra sendo analisado.
INICIOLADODIREITO = 5                             # Constante para indicar o ponto em que inicia o lado direito da producao no arquivo de entrada.

class InfoGLC: # Classe para armazenar todas as informacoes relevantes da GLC do arquivo de entrada.
    def __init__(self, nome_gramatica, variaveis, terminais, nome_producoes, inicial, producoes):
        self.nome_GLC = nome_gramatica
        self.var = variaveis
        self.ter = terminais
        self.nome_prod = nome_producoes
        self.ini = inicial
        self.lista_producoes = producoes # Armazena todas as producoes antes do inicio da aplicacao do algoritmo de Earley.

class regra_producao: # Classe para armazenar todos os objetos que representam uma regra de producao, que sera embutidos em uma lista.
    def __init__(self, esquerdo, direito, marcador, conj_inicio, conj_mostrou, operacao):
        self.esq = esquerdo             # Lado esquerdo da regra de producao.
        self.dir = direito              # Lado direito da regra de producao.
        self.marca = marcador           # Posicao do marcador no lado direito da producao.
        self.inicio = conj_inicio          # Numero do conjunto D no qual a producao foi inicializada.
        self.aparicao = conj_mostrou    # Numero do conjunto D no qual ocorreu a impressao da regra de producao.
        self.op = operacao              # Indica qual das tres operacoes (scan, predict ou complete) foi utilizada para obter a producao.

class info_operacao: # Classe para armazenar as informacoes de uma operacao de "predict" ou "complete", do algoritmo de Earley.
    def __init__(self,producoes,aumento):
        self.prods = producoes
        self.aumentou = aumento

def encontra_indice(palavra, caractere, nth): # Retorna o indice da n-esima ocorrencia de uma substring.
    inicio = palavra.find(caractere)
    while inicio >= 0 and nth > 1:
        inicio = palavra.find(caractere, inicio + len(caractere))
        nth -= 1
    return inicio

def erro_primeira(): # Informa ao usuario que ha erro na primeira linha do arquivo de entrada.
    print('\nErro de sintaxe na primeira linha do arquivo contendo a GLC. Fim do programa.\n')
    os.system("PAUSE")
    sys.exit()

def erro_segunda(): # Informa ao usuario que ha erro na segunda linha do arquivo de entrada.
    print('\nErro na segunda linha do arquivo contendo a GLC (nome das regras de producao). Fim do programa.\n')
    os.system("PAUSE")
    sys.exit()

def erro_producoes(numero_linha): # Informa ao usuario que ha erro em alguma das regras de producao no arquivo de entrada.
    print('\nErro na regra de producao da linha', numero_linha, '. Fim do programa.\n')
    os.system("PAUSE")
    sys.exit()

def acha_erros(linha): # Controle de sintaxe da primeira linha do arquivo.
    posicao_igual = linha.find('=')

    if posicao_igual == -1 or posicao_igual == 0:
        erro_primeira()

    elif linha.count('{') != 2 or linha.count('}') != 2:
        erro_primeira()

    elif linha.count('(') != linha.count(')'):
        erro_primeira()

    elif linha[posicao_igual + 1] != '(' or linha[posicao_igual + 2] != '{':
        erro_primeira()

    elif linha[linha.find('}')+1] != ',' or linha[linha.find('}')+2] != '{':
        erro_primeira()

    indice_aux = encontra_indice(linha,'}', 2)

    if linha[indice_aux+1] != ',' or linha[indice_aux+2] == ')':
        erro_primeira()

    elif linha[len(linha)-2] != ')':
        erro_primeira()

    elif linha[len(linha)-4] != ',':
        erro_primeira()

def obtem_informacoes(linha, indice): # Obtem as informacoes da GLC no arquivo de entrada.
    lista_info = [] # Inicializa a lista de variaveis ou terminais a ser retornada pela funcao.

    while linha[indice] != '}': # Iteracao para inserir todas as variaveis na lista de variaveis.
        if linha[indice+1] != ',' and linha[indice+1] != '}':
            erro_primeira()

        elif linha[indice+1] == ',' and linha[indice+2] == '}':
            erro_primeira()

        else:
            lista_info.append(linha[indice])

        if linha[indice+1] != '}':
            indice += 2

        else:
            indice += 1

    return lista_info

def controla_primeiralinha(arquivo_GLC): # Obtem e controla a sintaxe das informacoes da primeira linha do arquivo com a GLC.
    informacoes = InfoGLC('','','','','',[]) # Inicializa o objeto contendo as informacoes da GLC.
    lista_variaveis = [] # Inicializa a lista de variaveis.
    lista_terminais = [] # Inicializa a lista de terminais.
    nome_producao = [] # Inicializa a lista contendo o nome da producao.

    linha = arquivo_GLC.readline()
    acha_erros(linha) # Realiza controle de sintaxe da primeira linha do arquivo.

    nome_GLC = linha.split('=')[0] # Obtem o nome da GLC inserida pelo usuario.

    indice = linha.find('{')+1 # Obtem as variaveis.
    lista_variaveis = obtem_informacoes(linha,indice)

    indice = linha.find('}')+3 # Obtem os terminais.
    lista_terminais = obtem_informacoes(linha,indice)

    indice = encontra_indice(linha,'}', 2)+2 # Obtem o nome das regras de producoes.
    while linha[indice] != ',':
        if not linha[indice].isalnum():
            erro_primeira()
        nome_producao.append(linha[indice])
        indice += 1

    var_inicial = linha[indice+1]

    informacoes.nome_GLC = nome_GLC # Atualiza a estrutura contendo todas as informacoes da GLC obtidas.
    informacoes.var = lista_variaveis
    informacoes.ter = lista_terminais
    informacoes.nome_prod = ''.join(nome_producao)
    informacoes.ini = var_inicial

    return informacoes # Retorna a estrutura contendo as informacoes da GLC.

def controla_segundalinha(arquivo_GLC, informacoes): # Obtem e controla a sintaxe da informacao da segunda linha do arquivo com a GLC.
    nome_prod = arquivo_GLC.readline()

    if (nome_prod[len(nome_prod)-1] != '\n'):
        erro_segunda()

    nome_prod = nome_prod.split('\n')[0]

    if (nome_prod != informacoes.nome_prod): # Verifica se o nome da segunda linha corresponde ao nome das producoes na primeira linha.
        erro_segunda()

def controla_producao(informacoes, producao, numero_linha): # Controla a sintaxe das informacoes de uma regra de producao.
    if not producao.esq in informacoes.var:
        erro_producoes(numero_linha)

    elif not producao.dir: # Verifica se a string referente a producao do lado direito e vazia.
        erro_producoes(numero_linha)

    for i in list(producao.dir):
        if (not i in informacoes.var) and (not i in informacoes.ter):
            erro_producoes(numero_linha)

        elif (i in informacoes.var) and (i in informacoes.ter):
            erro_producoes(numero_linha)

def obtem_producao(linha, numero_linha): # Obtem e controla todas as regras de producao a partir da terceira linha.
    producao = regra_producao('','', 0, 0, -1, '')

    if not (linha[1] == ' ' and linha[2] == '-' and linha[3] == '>'):
        erro_producoes(numero_linha)

    elif linha[4] != ' ' and linha[4] != '\n':
        erro_producoes(numero_linha)

    producao.esq = linha[0] # Armazena o lado esquerdo da regra de producao da linha.

    indice = INICIOLADODIREITO
    lado_direito = [] # Inicializa a lista contendo os caracteres do lado direito da producao.

    while (linha[indice] != '\n' and indice < len(linha)-1):
        lado_direito.append(linha[indice]) # Armazena o lado direito da regra de producao da linha.
        indice += 1

    lado_direito = list(linha.split(' -> ')[1])
    if lado_direito[-1] == '\n':
        lado_direito.pop() # Remocao da quebra de linha da lista contendo o lado direito da producao.

    producao.dir = ''.join(lado_direito) # Converte a lista em uma string, para armazenar a informacao.

    return producao

def imprime_earley(producao): # Imprime uma regra de producao durante a aplicacao do algoritmo de Earley.
    print(producao.esq, end='') # Impressao do lado esquerdo da regra de producao.
    print(' -> ' , end='')

    j = 0
    for i in list(producao.dir): # Impressao do lado direito da regra de producao.
        if (producao.marca == j):
            print(SIMBOLOMARCADOR, end='') # Imprime o simbolo marcador na posicao corrente, no lado direito da producao.
        j += 1
        print(i, end='')

    if (producao.marca >= len(producao.dir)): # Imprime o simbolo marcador no final da producao, se necessario.
        print(SIMBOLOMARCADOR, end='')

    print(' /', producao.inicio, end='')# Imprime o conjunto no qual a regra de producao foi inicializada.

def imprime_lista_earley(lista_producoes, numero_conjunto): # Imprime uma lista com varias regras de producao durante a aplicacao do algoritmo de Earley.
    for i in lista_producoes:
        if (i.aparicao == numero_conjunto):
            imprime_earley(i)
            print(i.op)

def imprime_D0(informacoes): # Imprime todas as regras de producao do conjunto inicial D0, no inicio da aplicacao do algoritmo.
    uteis = []
    print('CONJUNTO D0:')

    for i in informacoes.lista_producoes:
        if (i.esq == informacoes.ini): # Verifica quais producoes partem do simbolo inicial.
            i.aparicao = 0
            uteis.append(i)

    uteis = predict_earley(informacoes,uteis,0)

    for i in uteis:
        imprime_earley(i)
        print()

    print('')
    return uteis

def scan_earley(uteis,caractere,numero_conjunto):
    producoes = uteis
    nova_producao = regra_producao('', '', 0, 0, -1, '')

    for i in uteis: # Operacao de scan: avanca o marcador para reconhecer um terminal (caractere da palavra).
        if (i.marca < len(i.dir) and i.dir[i.marca] == caractere and (i.aparicao == numero_conjunto-1)):
            nova_producao = i
            nova_producao.marca += 1
            nova_producao.aparicao = numero_conjunto
            nova_producao.op = ' --- SCAN'
            nova_producao = regra_producao('', '', 0, 0, -1, '')
            producoes.append(nova_producao)

    return producoes

def verifica_contem(producoes, nova_producao): # Verifica se uma lista de producoes contem uma determinada producao.
    for i in producoes:
        if (i.esq == nova_producao.esq) and (i.dir == nova_producao.dir):
            if (i.marca == nova_producao.marca) and (i.inicio == nova_producao.inicio):
                if (i.aparicao == nova_producao.aparicao):
                    return True

    return False

def aux_predict(informacoes,numero_conjunto,InfoPredict): # Aplica a operacao de predict segundo o algoritmo de Earley.
    nova_producao = regra_producao('', '', 0, 0, -1, '')  # Reinicia a variavel auxiliar ao fim da iteracao.
    inicializados = []
    tamanho_atual = len(InfoPredict.prods)

    for i in InfoPredict.prods: # Operacao de predict: inicializa as novas producoes necessarias, em razao do marcador ter encostado em uma variavel.
        if (i.marca < len(i.dir)) and (i.dir[i.marca] in informacoes.var) and (i.aparicao == numero_conjunto):
            for j in informacoes.lista_producoes:
                if (j.esq == i.dir[i.marca]) and (j.inicio == 0):
                    nova_producao.esq = j.esq
                    nova_producao.dir = j.dir
                    nova_producao.marca = 0
                    nova_producao.inicio = numero_conjunto
                    nova_producao.aparicao = numero_conjunto
                    nova_producao.op = ' --- PREDICT'
                    if (not verifica_contem(InfoPredict.prods, nova_producao)):
                        inicializados.append(nova_producao)
                    nova_producao = regra_producao('', '', 0, 0, -1, '') # Reinicia a variavel auxiliar ao fim da iteracao.

    InfoPredict.prods += inicializados
    novo_tamanho = len(InfoPredict.prods)

    if novo_tamanho == tamanho_atual: # Verifica se a cardinalidade do conjunto foi aumentada ou nao.
        InfoPredict.aumentou = 0

    else:
        InfoPredict.aumentou = 1

    return InfoPredict # Retorna as producoes atualizadas, contendo as obtidas com as operacoes de predict.

def predict_earley(informacoes,uteis,numero_conjunto): # Aplica a operacao de predict ate o conjunto de producoes nao aumentar mais.
    InfoPredict = info_operacao(uteis,1) # Armazena as producoes atuais na variavel auxiliar.

    while InfoPredict.aumentou == 1: # Aplica a operacao de predict enquanto a cardinalidade do conjunto seguir aumentando.
        InfoPredict = aux_predict(informacoes,numero_conjunto,InfoPredict) # Atualiza a variavel auxiliar apos cada operacao de predict.

    return InfoPredict.prods # Retorna as producoes atualizadas, contendo as obtidas com as operacoes de predict.

def aux_complete(numero_conjunto,InfoComplete): # Aplica a operacao de complete segundo o algoritmo de Earley.
    InfoComplete.aumentou = 0

    atualizados = []
    nova_producao = regra_producao('', '', 0, 0, -1, '')  # Reinicia a variavel auxiliar ao fim da iteracao.

    for i in InfoComplete.prods: # Inicializa as novas producoes necessarias, em razao do marcador ter encostado em uma variavel.
        if (i.marca == len(i.dir)) and (i.aparicao == numero_conjunto): # Verifica se a producao de uma variavel foi completada.
            for j in InfoComplete.prods:
                if (j != i) and (i.inicio == j.aparicao) and (j.marca < len(j.dir)) and (j.dir[j.marca] == i.esq):
                    nova_producao.esq = j.esq
                    nova_producao.dir = j.dir
                    nova_producao.marca = j.marca+1
                    nova_producao.inicio = j.inicio
                    nova_producao.aparicao = numero_conjunto
                    nova_producao.op = ' --- COMPLETE'
                    atualizados.append(nova_producao)
                    nova_producao = regra_producao('', '', 0, 0, -1, '')  # Reinicia a variavel auxiliar ao fim da iteracao.

        for j in atualizados:
            if (not verifica_contem(InfoComplete.prods, j)):
                InfoComplete.aumentou = 1
                InfoComplete.prods.append(j)

    return InfoComplete # Retorna as producoes atualizadas, contendo as obtidas com as operacoes de complete.

def complete_earley(uteis,numero_conjunto): # Aplica a operacao de complete ate o conjunto de producoes nao aumentar mais.
    InfoComplete = info_operacao(uteis,1)

    while InfoComplete.aumentou == 1: # Aplica a operacao de complete enquanto a cardinalidade do conjunto seguir aumentando.
        InfoComplete = aux_complete(numero_conjunto,InfoComplete)

    return InfoComplete.prods # Retorna as producoes atualizadas, contendo as obtidas com as operacoes de complete.

def remove_repetidos(uteis): # Remove producoes repetidas de uma lista de producoes.
    nova_lista = []

    for i in uteis:
        if (not verifica_contem(nova_lista,i)):
            nova_lista.append(i)

    return nova_lista # Retorna a nova lista sem repeticoes.

def analise_earley(informacoes,uteis,palavra,numero_conjunto): # Aplica a operacao

    caractere = palavra[numero_conjunto - 1]
    tamanho_antes_scan = len(uteis)
    # Atualiza as producoes, por meio das operacoes de scan.
    uteis = scan_earley(uteis,caractere,numero_conjunto)
    tamanho_depois_scan = len(uteis)

    if tamanho_antes_scan != tamanho_depois_scan: # Caso o scan tenha sido realizado com sucesso, imprime os conjuntos.
        print('CONJUNTO D',numero_conjunto,': ', sep='',end='') # Imprime o numero do conjunto da vez.

        for i in range(len(palavra)): # Imprime a palavra sendo analisada, destacando o caractere em analise.
            if (i != numero_conjunto-1):
                print(palavra[i], end='')
            else:
                print(DELIMITADOR_ESQ,end='')
                print(caractere,end='')
                print(DELIMITADOR_DIR,end='')
        print()

    else: # Casos em que a palavra sera rejeitada, por nao ser possivel executar a operacao de scan no conjunto.
        print('RESULTADO FINAL:')
        print('A palavra NAO PODE ser gerada pela GLC inserida.\nNenhuma operacao de SCAN pode ser realizada no conjunto D', numero_conjunto, sep='', end='.\n')
        print('\n')
        os.system("PAUSE")
        sys.exit() # Encerra a execucao do programa, pois a palavra foi rejeitada.

    tamanho_antes = -1
    tamanho_depois = -2

    while (tamanho_antes != tamanho_depois):
        tamanho_antes = len(uteis)
        # Atualiza as producoes, por meio das operacoes de predict e complete.
        uteis = predict_earley(informacoes,uteis,numero_conjunto)
        uteis = complete_earley(uteis,numero_conjunto)
        tamanho_depois = len(uteis)

    uteis = remove_repetidos(uteis) # Remove eventuais producoes repetidas.
    imprime_lista_earley(uteis,numero_conjunto) # Imprime todas as producoes referentes ao conjunto da vez.

    print()
    return uteis # Retorna a lista com as producoes atualizadas.

def earley(informacoes, palavra):
    numero_conjunto = 0
    aceitou = 0
    uteis = imprime_D0(informacoes) # Obtem o primeiro conjunto de producoes para iniciar as operacoes.

    while numero_conjunto < len(palavra): # Aplica o algoritmo de Earley com cada caractere da palavra de entrada.
        numero_conjunto += 1
        uteis = analise_earley(informacoes,uteis,palavra,numero_conjunto)

    for i in uteis:  # Imprime as producoes que garantem a aceitacao da palavra.
        if (i.marca == len(i.dir) and (i.inicio == 0) and (i.aparicao == numero_conjunto)):
            aceitou = 1

    print('RESULTADO FINAL:') # Indica ao usuario se a palavra pode ou nao ser gerada pela GLC inserida.

    if (aceitou == 1):
        print('A palavra PODE ser gerada pela GLC inserida.\nOs marcadores das producoes inicializadas em D0 mostradas abaixo atingiram o final.\n')
        for i in uteis:  # Imprime as producoes que garantem a aceitacao da palavra.
            if (i.marca == len(i.dir) and (i.inicio == 0) and (i.aparicao == numero_conjunto)):
                imprime_earley(i)
                print()

    else:
        print('A palavra NAO PODE ser gerada pela GLC inserida.\nNenhuma producao inicializada em D0 foi percorrida pelo seu marcador.\n')

    print()

def leitura_arquivo(arquivo_GLC):
    informacoes = controla_primeiralinha(arquivo_GLC) # Obtem as informacoes da GLC da primeira linha.
    controla_segundalinha(arquivo_GLC, informacoes) # Obtem o nome das regras de producao na segunda linha.

    todas_producoes = []

    numero_linha = 3
    linha = arquivo_GLC.readline()

    while linha != '': # Iteracao para percorrer todas as linhas do arquivo texto com a GLC.
        producao = obtem_producao(linha, numero_linha)
        controla_producao(informacoes, producao, numero_linha)
        numero_linha += 1

        if not (producao in todas_producoes): # Armazena todas as producoes em uma lista, evitando repeticoes.
            todas_producoes.append(producao)

        linha = arquivo_GLC.readline() # Realiza a leitura de cada linha em cada iteracao.

    print('')

    palavra = input('Digite a palavra a ser analisada com o algoritmo de Earley:\n')
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa o conteudo da tela.

    print('Producoes:') # Imprime todas as producoes da GLC na tela, antes do inicio da aplicacao do algoritmo.
    for i in todas_producoes:
        print(i.esq, ' -> ', i.dir)
    print()

    informacoes.lista_producoes = todas_producoes # Armazena todas as producoes do arquivo de entrada.
    earley(informacoes, palavra) # Inicia a aplicao do algoritmo de Earley.

def inicia_programa():
    print('RECONHECEDOR DE PALAVRAS COM ALGORITMO DE EARLEY')
    print('\nAutor: Andrei Pochmann Koenich\n')

    nomearquivo_GLC = input('Digite o nome do arquivo texto de entrada contendo a GLC:\n')
    arquivo_GLC = open(nomearquivo_GLC,'r') # Abertura do arquivo de entrada para leitura.
    leitura_arquivo(arquivo_GLC) # Inicia a leitura do arquivo contendo a GLC.
    arquivo_GLC.close() # Fechamento do arquivo de entrada.

def main():
    inicia_programa()
    os.system("PAUSE")

main()