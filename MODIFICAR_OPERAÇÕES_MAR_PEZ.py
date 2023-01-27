import tkinter
from tkinter import filedialog
import os
import re


########################################################################################################################
#VER SE EXISTE ABA
def ContarAbrirAba(info):
    try:
        lista_open = []
        n_open = 0
        indice = info.index('[OPEN]\n') + 1
        while '[' not in info[indice] and indice < len(info):
            # checar se nao eh linha vazia
            if (info[indice]) == 1 or info[indice].startswith('LIV'):
                n_open = n_open
            else:
                info_open = info[indice].split(' ')
                while '' in info_open:
                    info_open.remove('')

                lista_open.append(info_open)
            indice += 1

        n_open = len(lista_open) #Rev. .01.01
        return str(n_open)
    except:
        log_erros.write('Posicao ' + posicao + ' erro contabilizar dobras. Verifique CAM pode estar fora do padrao! ' + '\n')
        return '0'

# VER SE EXISTE DOBRA:
def contar_dobras(ver, info):
    try:
        n_dobras = 0
        d_dobras = []
        indice = info.index('[FOLD]\n') + 1
        while '[' not in info[indice] and indice < len(info):
            # checar se nao eh linha vazia
            if (info[indice]) == 1 or info[indice].startswith('LIV'):
                n_dobras = n_dobras
            else:
                l_dobras = info[indice]
                l_dobras = l_dobras.rstrip('\n')
                l_dobras = l_dobras.split(' ')
                while '' in l_dobras:
                    l_dobras.remove('')
                for i in range(len(l_dobras)):
                    l_dobras[i] = abs(float(l_dobras[i]))

                if l_dobras not in d_dobras:
                    d_dobras.append(l_dobras)
            indice += 1
        n_dobras = len(d_dobras)
        if ver == 'novo':
            return str(n_dobras)
        if ver == 'antigo':
            return str(n_dobras/3)
    except:
        log_erros.write('Posicao ' + posicao + ' erro contabilizar dobras. Verifique CAM pode estar fora do padrao! ' + '\n')
        return '0'

#VER SE EXISTE CHANFRO
def existe_chanfro(info):
    try:
        chanfro = ''
        indice = info.index('[CUTTER]\n') +1
        if indice>=len(info): # revisao 01
            return chanfro    # revisao 01
        while '[' not in info[indice] and indice < len(info):
            # checar se nao eh linha vazia
            if (info[indice]) == 1:
                chanfro = ''
            else:
                chanfro = 'X'
                return chanfro
            indice += 1
            if indice>=len(info): # revisao 01
                return chanfro    # revisao 01
        return chanfro
    except:
        log_erros.write('Posicao ' + posicao + ' erro ao procurar chanfro. Verifique CAM pode estar fora do padrao! ' + '\n')
        return ''

# funcao para determinar se o ponto pertence a uma reta
def det(x1, y1, x2, y2, ptx, pty):
    d = ((x2 - x1) * (pty - y1)) - ((ptx - x1) * (y2 - y1))
    if d <= 0.0001 and d >= -0.0001:
        return True
    else:
        return False


# extrai aba e espessura
def aba_esp(texto, ver):
    if ver == 'novo':
        if 'X' in texto:  # revisao .02
            c = texto.split(' ')
            if 'L' in c:
                c.remove('L')
                c.remove('X')
            if 'BC' in c:  # Rev. 1.07
                c.remove('BC')  # Rev. 1.07
                c.remove('X')  # Rev. 1.07
            if 'U' in c:  # Rev. 1.08
                c.remove('U')  # Rev. 1.08
                c.remove('X')  # Rev. 1.08
                c.remove('X')  # Rev. 1.08
            return c

        if '*' in texto:
            c = texto.split(' ')
            c = c[1].split('*')
            return c

    if ver == 'antigo':
        c = texto.split(' ')
        c.remove('L')
        c.remove('X')
        return c


def search_for_file_path():
    currdir = os.getcwd()
    tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
    return tempdir

#CABEÇALHO
def cabecalho(info, titulo):
    for i in info:
        if re.search(titulo, i):
            valor = i.split(':')[1]
            valor = valor.strip()
    return valor

#VERSAO
def versao_cam(cam):
    if str(cam) == '[ENTITY4]\n':
        return 'novo'
    else:
        return 'antigo'


# quantidade de recortes - revisado 12/05/14 para reduzir qtde recortes caso haja mais de um recorte em um mesmo vertice
def contar_recortes(ver, info, tipo):
    try:
        n_recortes = 0
        if ver == 'novo' or ver == 'antigo':
            # cantoneiras
            if tipo == 'D':

                # contar pelo OUTLINE
                bito_cam = cabecalho(info, 'NOM_PRO:')
                out = []
                indice = info.index('[OUTLINE]\n') + 2
                while 'LIV' not in info[indice] and indice < len(info):
                    # obter linha OUTLINE
                    info_out = info[indice].rstrip('\n')
                    info_out = info[indice].split(' ')
                    while '' in info_out:
                        info_out.remove('')
                    out.append(info_out)
                    indice += 1
                while ['\n'] in out:
                    out.remove(['\n'])
                # verificar se existe raio identificar linha anterior e posterior
                ind = 0
                for i in out:
                    if float(i[3]) != 0.0:
                        out[ind - 1].append('XXX')
                        out[ind + 1].append('XXX')
                    ind += 1

                novo_out = []
                for i in out:
                    if i[-1] == 'XXX' or i in novo_out:
                        pass
                    else:
                        novo_out.append(i)

                # verif se a ultima coord eh igual a primeira
                if [novo_out[0][0], novo_out[0][1]] != [novo_out[-1][0], novo_out[-1][1]]:
                    novo_out.append(novo_out[0])

                # contorno LIV1
                pt1 = [0.0, 0.0]
                pt2 = [float(cabecalho(info, 'LUN_PRO:')), 0.0]
                pt3 = [float(cabecalho(info, 'LUN_PRO:')), -float(aba_esp(bito_cam, ver)[0])]
                pt4 = [0.0, -float(aba_esp(bito_cam, ver)[0])]

                # verifica segmentos
                ind = 0
                while ind <= len(novo_out) - 2:
                    if [novo_out[ind][0], novo_out[ind][1]] != [novo_out[ind + 1][0], novo_out[ind + 1][1]]:
                        mid_x = (float(novo_out[ind][0]) + float(novo_out[ind + 1][0])) / 2.0
                        mid_y = (float(novo_out[ind][1]) + float(novo_out[ind + 1][1])) / 2.0

                        if det(pt1[0], pt1[1], pt2[0], pt2[1], mid_x, mid_y) == True or \
                                det(pt2[0], pt2[1], pt3[0], pt3[1], mid_x, mid_y) == True or \
                                det(pt3[0], pt3[1], pt4[0], pt4[1], mid_x, mid_y) == True or \
                                det(pt4[0], pt4[1], pt1[0], pt1[1], mid_x, mid_y) == True:
                            n_recortes = n_recortes
                        else:
                            n_recortes += 1
                            # se for vertical ou horizontal passa
                            # if float(novo_out[ind][0]) == float(novo_out[ind + 1][0]) or float(novo_out[ind][1]) == float(novo_out[ind + 1][1]):
                            if float(novo_out[ind][0]) == float(novo_out[ind + 1][0]):
                                n_recortes -= 1
                            else:
                                # se for recorte duplo
                                if ((float(novo_out[ind][0]) == 0. and float(novo_out[ind + 1][1]) == 0.) or \
                                    (float(novo_out[ind][1]) == 0. and float(novo_out[ind + 1][0]) == 0.)) or \
                                        ((float(novo_out[ind][0]) == float(cabecalho(info, 'LUN_PRO:')) and float(
                                            novo_out[ind + 1][1]) == 0.) or \
                                         (float(novo_out[ind][1]) == 0. and float(novo_out[ind + 1][0]) == float(
                                             cabecalho(info, 'LUN_PRO:')))):
                                    n_recortes += 1
                    ind += 1

                # Ler LIV2
                out = []
                indice += 1
                while 'LIV' not in info[indice] and indice < len(info):
                    # obter linha OUTLINE
                    info_out = info[indice].rstrip('\n')
                    info_out = info[indice].split(' ')
                    while '' in info_out:
                        info_out.remove('')
                    out.append(info_out)
                    indice += 1
                while ['\n'] in out:
                    out.remove(['\n'])
                # verificar se existe raio identificar linha anterior e posterior
                ind = 0
                for i in out:
                    if float(i[3]) != 0.0:
                        out[ind - 1].append('XXX')
                        out[ind + 1].append('XXX')
                    ind += 1

                novo_out = []
                for i in out:
                    if i[-1] == 'XXX' or i in novo_out:
                        pass
                    else:
                        novo_out.append(i)

                # verif se a ultima coord eh igual a primeira
                if [novo_out[0][0], novo_out[0][2]] != [novo_out[-1][0], novo_out[-1][2]]:
                    novo_out.append(novo_out[0])

                # contorno
                pt1 = [0.0, 0.0]
                pt2 = [float(cabecalho(info, 'LUN_PRO:')), 0.0]
                pt3 = [float(cabecalho(info, 'LUN_PRO:')), -float(aba_esp(bito_cam, ver)[0])]
                pt4 = [0.0, -float(aba_esp(bito_cam, ver)[0])]

                # verifica segmentos
                ind = 0
                while ind <= len(novo_out) - 2:
                    if [novo_out[ind][0], novo_out[ind][2]] != [novo_out[ind + 1][0], novo_out[ind + 1][2]]:
                        mid_x = (float(novo_out[ind][0]) + float(novo_out[ind + 1][0])) / 2.0
                        mid_y = (float(novo_out[ind][2]) + float(novo_out[ind + 1][2])) / 2.0

                        if det(pt1[0], pt1[1], pt2[0], pt2[1], mid_x, mid_y) == True or \
                                det(pt2[0], pt2[1], pt3[0], pt3[1], mid_x, mid_y) == True or \
                                det(pt3[0], pt3[1], pt4[0], pt4[1], mid_x, mid_y) == True or \
                                det(pt4[0], pt4[1], pt1[0], pt1[1], mid_x, mid_y) == True:
                            n_recortes = n_recortes
                        else:
                            n_recortes += 1
                            # se for vertical ou horizontal passa
                            # if float(novo_out[ind][0]) == float(novo_out[ind + 1][0]) or float(novo_out[ind][2]) == float(novo_out[ind + 1][2]):
                            if float(novo_out[ind][0]) == float(novo_out[ind + 1][0]):
                                n_recortes -= 1
                            else:
                                # se for recorte duplo
                                if ((float(novo_out[ind][0]) == 0. and float(novo_out[ind + 1][2]) == 0.) or \
                                    (float(novo_out[ind][2]) == 0. and float(novo_out[ind + 1][0]) == 0.)) or \
                                        ((float(novo_out[ind][0]) == float(cabecalho(info, 'LUN_PRO:')) and float(
                                            novo_out[ind + 1][2]) == 0.) or \
                                         (float(novo_out[ind][2]) == 0. and float(novo_out[ind + 1][0]) == float(
                                             cabecalho(info, 'LUN_PRO:')))):
                                    n_recortes += 1
                    ind += 1

                return str(n_recortes)

            # chapas
            if tipo == 'R' or tipo == 'Y':  # Rev. 1.07
                # modificada 2014-09-23
                out = []
                indice = info.index('[OUTLINE]\n') + 2
                while 'LIV' not in info[indice] and indice < len(info):
                    # obter linha OUTLINE
                    info_out = info[indice].rstrip('\n')
                    info_out = info[indice].split(' ')
                    while '' in info_out:
                        info_out.remove('')
                    out.append(info_out)
                    indice += 1
                if ['\n'] in out:
                    out.remove(['\n'])
                # verificar se existe raio identificar linha anterior e posterior
                indice = 0
                for i in out:
                    if float(i[3]) != 0.0:
                        out[indice - 1].append('XXX')
                        out[indice + 1].append('XXX')
                    indice += 1

                novo_out = []
                for i in out:
                    if i[-1] == 'XXX':
                        pass
                    else:
                        novo_out.append(i)

                # verif se a ultima coord eh igual a primeira
                if [novo_out[0][0], novo_out[0][1]] != [novo_out[-1][0], novo_out[-1][1]]:
                    novo_out.append(novo_out[0])

                # contorno chapa
                pt1 = [0.0, 0.0]
                pt2 = [float(cabecalho(info, 'LUN_PRO:')), 0.0]
                pt3 = [float(cabecalho(info, 'LUN_PRO:')), -float(cabecalho(info, 'LAR_PRO:'))]
                pt4 = [0.0, -float(cabecalho(info, 'LAR_PRO:'))]

                # verifica segmentos
                indice = 0
                while indice <= len(novo_out) - 2:
                    if [novo_out[indice][0], novo_out[indice][1]] != [novo_out[indice + 1][0], novo_out[indice + 1][1]]:
                        mid_x = (float(novo_out[indice][0]) + float(novo_out[indice + 1][0])) / 2.0
                        mid_y = (float(novo_out[indice][1]) + float(novo_out[indice + 1][1])) / 2.0

                        if det(pt1[0], pt1[1], pt2[0], pt2[1], mid_x, mid_y) == True or \
                                det(pt2[0], pt2[1], pt3[0], pt3[1], mid_x, mid_y) == True or \
                                det(pt3[0], pt3[1], pt4[0], pt4[1], mid_x, mid_y) == True or \
                                det(pt4[0], pt4[1], pt1[0], pt1[1], mid_x, mid_y) == True:
                            n_recortes = n_recortes
                        else:
                            n_recortes += 1
                    indice += 1

                return str(n_recortes)

            if tipo == 'A' or tipo == 'N' or tipo == 'G':
                return str(n_recortes)  # Rev. 1.06

    except:
        log_erros.write(
            'Posicao ' + posicao + ' erro contabilizar recortes. Verifique CAM pode estar fora do padrao! ' + '\n')
        return '0'

########################################################################################################################
#CAMINHO
root = tkinter.Tk()
root.withdraw()
caminho = search_for_file_path()

# loop paara abrir arquivos
for filename in os.listdir(caminho):
    recortes = 0
    f = os.path.join(caminho, filename)
    # checking if it is a file
    if os.path.isfile(f):

        #ABRINDO ARQUIVO E FECHANDO PARA PEGAR AS LINHAS EM UMA LISTA!!!
        linhas = open(f, 'r')
        info = linhas.readlines()
        linhas.close()

        #DEFINDO CABEÇALHO E VERSAO PARA CONTINUAR AS FUNÇÕES
        tipo_cam = cabecalho(info, 'TIP_PRO:')
        versao = versao_cam(info[0])

        ################################################################################################################

        #DEFINIR OPERAÇÕES
        chanf = existe_chanfro(info)
        recortes = int(contar_recortes(versao, info, tipo_cam))
        dobra = int(contar_dobras(versao,info))
        aba = int(ContarAbrirAba(info))

        ############################################# OPERAÇÕES ########################################################

        #GAL
        if tipo_cam == 'D' and chanf == '' and recortes == 0 and dobra == 0 and aba == 0:
            for i, j in enumerate(info):
                if 'MAR_PEZ' in j:
                    b = i
                    info[i] = 'MAR_PEZ:GAL' + '\n'

        #RECORTE COM QUANTIDADE
        if tipo_cam == 'D' and recortes > 0:
            for i, j in enumerate(info):
                if 'MAR_PEZ' in j:
                    b = i
                    info[i] = 'MAR_PEZ:REC' + str(recortes) + '\n'

        #CHANFRO
        if tipo_cam == 'D' and recortes == 0 and chanf == 'X':
            for i, j in enumerate(info):
                if 'MAR_PEZ' in j:
                    b = i
                    info[i] = 'MAR_PEZ:' + 'CHANF' + '\n'

        #ABA
        if tipo_cam == 'D' and recortes == 0 and chanf == '' and aba > 0:
            for i, j in enumerate(info):
                if 'MAR_PEZ' in j:
                    b = i
                    info[i] = 'MAR_PEZ:' + 'ABA' + '\n'

        #DOBRA
        if tipo_cam == 'D' and recortes == 0 and chanf == '' and aba == 0 and int(dobra) > 0:
            for i, j in enumerate(info):
                if 'MAR_PEZ' in j:
                    b = i
                    info[i] = 'MAR_PEZ:' + 'DB' + '\n'

        ################################################################################################################


        #ABRINDO EM ESCRITA PARA SALVAR OQUE FOI EDITADO COM AS INFOS CORRETAS
        with open(f, 'w') as final:
            for linha in info:
                final.write(linha)

