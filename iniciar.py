# -*-coding:utf-8-*-

import sys

'''

'''

from util import tratamentoImagem as tratar, dataset
import os
from progressbar import Percentage,Bar,ProgressBar,ETA
from multiprocessing import Process

from datetime import date
from util import dataset

class runInMultiProcess(object):
    def __init__(self,tipodelayout,fullPath):
        self.tipodelayout = tipodelayout
        self.fullPath = fullPath
        self.error = 0

    def erroNoDocumento(self,arquivo,tipo):
        set = dataset.xml()
        datad = date.today()
        doc = arquivo.split('.')[0]
        set.criarTabelaError(doc=doc, cis='', chassi='', data=str(datad))
        with open(self.fullPath + 'producao/layout' + str(tipo) + '/' + arquivo, 'rb') as r:
            with open('erros/' + arquivo, 'wb') as w:
                w.write(r.read())
                w.close()
            r.close()


    def __call__(self,arquivo,fullPath,tipodelayout):
        try:
            tratador = tratar.tratar(arquivo,fullPath, int(tipodelayout))
            sucesso, self.error = tratador.reconhecerInformacao()
            return self.error
        except:
            runInMultiProcess.erroNoDocumento(self,arquivo,tipodelayout)
            print('erro')

banner = ('='*100)+'\n\n' \
    'python3 executavel.py (1|2) \n'\
    'Para iniciar o processo de extração de informações coloque os documentos dentro da pasta \n'\
    'producao/layout1|producao/layout2 e expecifique o tipo de layout se é 1 ou 2 \n' \
    'apois o fim do processo, o relatório ficará salvo em dataset, e os resultados em resultado.' \
    '\n\n' \
    ''+('='*100)+''

print(banner)

try:
    tipodelayout = sys.argv[1]
except IndexError:
    print(banner)
    exit()

#tipodelayout  = input('Tipo do layout do documento (1/2)> ').lower()
#if tipodelayout == '':
#    raise Exception('Expecifique o tipo de layout do documento.')
#if not tipodelayout.isnumeric():
#    raise Exception('Valor expecificado não é um número válido.')



if (tipodelayout != '') and (tipodelayout != ''):
    if (tipodelayout!= '1') and (tipodelayout!='2'):
        tipodelayout = '1'

path = 'producao/layout'+str(tipodelayout)+'/'

arquivos = []
for r, d, f in os.walk(path):
    for file in f:
        if '.pdf' in file:
            arquivos.append(file)

for r, d, f in os.walk('erros'):
    for file in f:
        if '.pdf' in file:
            os.unlink('erros/'+file)

fullPath = os.path.dirname(__file__)
arquivos_processados = []
banner = ['Processando arquivos ', Percentage(), ' ', Bar(),' - ',ETA()]
bar = ProgressBar(widgets=banner, maxval=len(arquivos)).start()

th = []
progresso = 0
erros = []
media = 0
totalerro = 0
totalresolvido = 0
totalprocessado = 0
print('Iniciando multiplas Threads...')

run = runInMultiProcess(tipodelayout=tipodelayout, fullPath=fullPath)

for arq in arquivos:
    progresso += 1
    bar.update(progresso)
    processo = Process(target=run, args=(arq,fullPath,tipodelayout))
    processo.start()
    processo.join()
bar.finish()

for r, d, f in os.walk('erros'):
    for file in f:
        if '.pdf' in file:
            erros.append(1)

for erro in erros:
    totalerro+=erro

if totalerro == 0:
    divisor = 1
else:
    divisor = totalerro

totalresolvido  = len(arquivos) - totalerro

media = (totalresolvido * 100) / len(arquivos)

print('{0} ERROS | {1} RESOLVIDO | {2}% DE ACERTO'.format(totalerro,totalresolvido,int(media)))
