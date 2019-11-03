# Função que recebe um valor inteiro e um tamanho
#e retorna uma string de numero binario
def integerToBinary(value, size):
    binario = bin(value)[2:]
    return binario.zfill(size)

#Função que retorna o tipo da instrução que será traduzida
def instructionType(opcodesB,opcodesI,opcodesJ,opcodesR,value):
    if value in opcodesB.keys():
        return 'b'
    elif value in opcodesI.keys():
        return 'i'
    elif value in opcodesJ.keys():
        return 'j'
    elif value in opcodesR.keys():
        return 'r'

# Fução que faz a verificação se após a linha de
#código existe um comentário e retira o mesmo
def tratarComentarios(lista):
    cont = 0
    for i in lista:
        if '#' in i:
            while len(lista)!= cont:
                del lista[cont]
        cont += 1
# Função que procura as labels de função
#para que se possa referenciar em binário
#na instrução
def acharLabel(label, size):
    cont = 0
    with open("code.s") as f:
        for line in f:
            cont+=1
            instrucao = line.split()
            if label in instrucao[0]:
                return integerToBinary(cont,size)            

# Dicionarios com os opcodes, o campo funct da instrução
#do tipo R e os registradores
opcodesB = {}
opcodesI = {}
opcodesJ = {}
opcodesR = {}
functR = {}
registradores = {}

# Função que preenche o dicionário com as intruções de branch
#foi separado dessa forma de acordo com a sintaxe
with open("opcodesB.txt") as f:
    for line in f:
        (key,val) = line.split()
        opcodesB[key] = val

# Função que preenche o dicionário com as instruções do tipo I
with open("opcodesI.txt") as f:
    for line in f:
        (key,val) = line.split()
        opcodesI[key] = val

# Função que preenche o dicionário com as instruções do tipo J
with open("opcodesJ.txt") as f:
    for line in f:
        (key,val) = line.split()
        opcodesJ[key] = val

# Função que preenche o dicionário com as instruções do tipo R
with open("opcodesR.txt") as f:
    for line in f:
        (key,val) = line.split()
        opcodesR[key] = val

# Função que preenche o dicionário com o campo funct
with open("functR.txt") as f:
    for line in f:
        (key,val) = line.split()
        functR[key] = val

# Função que preenche o dicionário com os registradores
with open("registers.txt") as f:
    for line in f:
        (key,val) = line.split()
        registradores[key] = val

# Criação do arquivo que vai receber o código traduzido
arquivo_maquina = open("codigo_maquina.txt","w+")

# Lendo o arquivo e fazendo a tradução
with open("code.s") as f:
    for line in f:
        # Replace para tirar as virgulas e por um espaço
        #para que se possa fazer o split e se obter uma lista
        line = line.replace(',',' ').replace('(',' ').replace(')','').split()
        
        # Verificar caso a linha seja um comentário para que
        #seja ignorado na tradução
        if line[0][0] == '#':
            continue
        
        if len(line) == 1:
            continue
        
        # If para verificar se o campo começa com label
        #caso comece o campo é ignorado e a instrução retante
        #será traduzida
        if ':' in line[0]:
            del line[0]
            
            # Função que trata comentários na linha após o código
            tratarComentarios(line)
        

        #Tipo da instrução que ocorrerá
        instrucao = instructionType(opcodesB,opcodesI,opcodesJ,opcodesR,line[0])

        # Função que trata comentários na linha após o código
        tratarComentarios(line)

        # Operacação de tradução da operação branch
        #opcode + registrador1 + registrador 2 + label de salto
        if instrucao == 'b':
            linha = opcodesB[line[0]] + registradores[line[1]] + registradores[line[2]] + acharLabel(line[3]+':',16)
            arquivo_maquina.write(linha)
            arquivo_maquina.write('\n')
        
        # Operação para instrução do tipo I (Memória)
        #opcode + registrador 1 + registrador 2 + offset
        elif instrucao == 'i':
            linha = opcodesI[line[0]] + registradores[line[1]] + integerToBinary(int(line[2]),16) + registradores[line[3]] 
            arquivo_maquina.write(linha)
            arquivo_maquina.write('\n')
        
        # Operação do tipo J (Salto)
        #opcode + label de salto
        elif instrucao == 'j':
            if line[0] == 'jr':
                linha = opcodesJ[line[0]] + registradores[line[1]].zfill(26)
                arquivo_maquina.write(linha)
                arquivo_maquina.write('\n')
            else:
                linha = opcodesJ[line[0]] + acharLabel(line[1]+':',26)
                arquivo_maquina.write(linha)
                arquivo_maquina.write('\n')

        # Operação do tipo R (Aritmética)
        elif instrucao == 'r':
            # Tratamento para operações que são realizadas através de immediate,
            #ou seja, usando um valor ao inves de um regitrador
            if line[0][-1:] == 'i' or line[0][-2:] == 'iu':
                linha = opcodesR[line[0]] + registradores[line[1]] + registradores[line[2]] + integerToBinary(int(line[3]),16)
                arquivo_maquina.write(linha)
                arquivo_maquina.write('\n')

            # Operações que não usam immediate
            else:
                # Tratamento para operações de Shift de bits
                #corpo especial por não usar o primeiro regitrador e o campo
                #shampt recebe valor do deslocamento
                if line[0] == 'sll' or line[0] == 'srl' or line[0] == 'sra':
                    linha = opcodesR[line[0]] + '00000' + registradores[line[1]] + registradores[line[2]] + integerToBinary(int(line[3]),5) + functR[line[0]]
                    arquivo_maquina.write(linha)
                    arquivo_maquina.write('\n')

                # Operações comuns do tipo R
                else:
                    linha = opcodesR[line[0]] + registradores[line[1]] + registradores[line[2]] + registradores[line[3]] + '00000' + functR[line[0]]
                    arquivo_maquina.write(linha)
                    arquivo_maquina.write('\n')

        else:
            print("Instrução não reconhecida")
            break