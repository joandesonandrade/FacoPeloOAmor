import subprocess as sp
from PIL import Image as img
from util import recDigitos as rec #reconhecimento de caracteres usando o metodo OCR(Reconhecimento ótico de caracteres)
from util import dataset
from datetime import date
import os
import tempfile as tmp

class tratar:
    def __init__(self,pdf_local,totalpath,tipo):
        self.pdf_local          = pdf_local
        self.totalpath          = totalpath
        self.layout             = tipo
        self.tipo               = tipo

    def tratamentoDaImagem(self,imagem):
        imagem     = imagem.convert('L')
        imagem     = imagem.point(lambda x: 255 if x > 200 else 0, '1')
        imagem     = imagem.convert('RGB')
        return imagem

    def reconhecimento(self,cis,chassi):
        cis = rec.rec(cis).extrairTexto()[0]
        chassi = rec.rec(chassi).extrairTexto()[0]
        return (cis,chassi)

    def posicoes_xy(self,image, type='y'):

        image = image.convert('RGB')

        posicoes = []
        xx, yy = image.size
        rgb = image.load()

        for c in range(2):

            pos = []
            encontrou = False

            ranger = range(300)

            if type == 'x':
                ranger = reversed(range(xx - 300, xx))

            for pixel in ranger:

                if self.layout == 1:

                    r, g, b = rgb[86, pixel]

                    if c == 1:
                        r, g, b = rgb[1470, pixel]

                else:
                    if type == 'y':
                        r, g, b = rgb[2350,pixel]

                if type == 'x':

                    r, g, b = rgb[pixel, 460]

                if not encontrou:
                    if r == 0:
                        pos.append(pixel)
                        encontrou = True

                else:
                    if r == 255:
                        encontrou = False

                if len(pos) == 3:
                    posicoes.append(pos)
                    break

        return posicoes

    def localiza_margem(self,image):

        diferenca = 0
        image = image.convert('RGB')
        pos = 0
        pos_total = []
        eixos = [tratar.posicoes_xy(self,image, 'x'), tratar.posicoes_xy(self,image,'y')]

        loop = 2

        if self.layout == 2:
            loop = 1

        for p in range(2):

            for p1 in range(loop):

                menor = 0

                for p2 in range(2):

                    if p2 == 0:
                        menor = abs(eixos[p][p1][p2] - eixos[p][p1][p2 + 1])
                        pos = eixos[p][p1][p2]


                    elif menor >= abs(eixos[p][p1][p2] - eixos[p][p1][p2 + 1]):
                        menor = eixos[p][p1][p2] - eixos[p][p1][p2 + 1]
                        pos = eixos[p][p1][p2]

                pos_total.append(pos)

        y_alto = 'right'

        if self.layout == 1:
            pos_final = [max(pos_total[0:2]), min(pos_total[2:4])]
            diferenca = abs(pos_total[2] - pos_total[3])

            if pos_total[3] < pos_total[2]:
                y_alto = 'left'

        else:
            pos_final = [pos_total[0],pos_total[1]]

        # print(pos_total[2], pos_total[3], y_alto)
        # print(pos_final)
        # pos_final = [abs(pos_total[0] - pos_total[1]) / 2 + min(pos_total[0:2]),
        #             abs(pos_total[2] - pos_total[3]) / 2 + min(pos_total[2:4])]

        return pos_final, diferenca, y_alto

    def add_fundo(self,image, escala=800):
        # escala é o tamanho do fundo

        if escala > 5000: escala = 5000
        elif escala < 600: escala = 600

        x, y = escala, int(escala / 2)
        img_fundo = img.new('RGB', (x, y), (255, 255, 255))
        x1, y1 = image.size
        img_fundo.paste(image, (int(x / 2 - x1 / 2), int(y / 2 - y1 / 2)))

        return img_fundo

    def corteCognetivo(self,image,escala=800):
        (x, y), difer, y_alto = tratar.localiza_margem(self,image)
        # difer = 0
        img_copy = image
        #print('Rotation :',y_alto)
        if self.layout == 1:

            if y_alto == 'right':
                corte1 = img_copy.crop((x - 1105 - (difer * 0.05), y + 357 + (difer * 0.55), x - 719 - (difer * 0.05),
                                        y + 445 + (difer * 0.775)))
                img_copy = image
                corte2 = img_copy.crop(
                    (x - 582 - (difer * 0.05), y + 357 + (difer * 1.0), x - 159 - (difer * 0.05), y + 445 + (difer * 0.95)))
            else:
                corte1 = img_copy.crop(
                    (x - 1105 - (difer * 1.2), y + 357 + (difer * 0.7), x - 718 - (difer * 1.25), y + 445 + (difer * 0.9)))
                img_copy = image
                corte2 = img_copy.crop(
                    (x - 582 - (difer * 1), y + 357 + (difer * 0.4), x - 159 - (difer * 1), y + 445 + (difer * 0.48)))

        else:
            corte1 = img_copy.crop((x - 1118, y + 365, x - 718, y + 461))
            img_copy = image
            corte2 = img_copy.crop((x - 600, y + 365, x - 140, y + 458))

        corte1 = tratar.add_fundo(self,corte1, escala)
        corte2 = tratar.add_fundo(self,corte2, escala)

        tmp1 = tmp.NamedTemporaryFile(suffix='.jpg',delete=False)
        tmp2 = tmp.NamedTemporaryFile(suffix='.jpg',delete=False)

        corte1.save(tmp1)
        corte2.save(tmp2)

        #corte1.save('tmp/001-'+str(random.randint(0,9999))+'.jpg')
        #corte2.save('tmp/002-'+str(random.randint(0,9999))+'.jpg')

        return True,tmp1.name,tmp2.name


    def avaliarImagem(self, path):
        extensao = ''
        if os.path.isfile(path+self.pdf_local+'-000.pbm'):
            extensao = 'pbm'
        else:
            extensao = 'jpg'
        nomeArquivoExtraido = path+self.pdf_local+'-000.'+extensao
        img00 = img.open(nomeArquivoExtraido)
        x,y   = img00.size
        img00.save(path+'/'+self.pdf_local+'-000.jpg')
        if x > y and self.pdf_local[0:3] == '001':
            rotatacaoImagem = img00
            #rotatacaoImagem.thumbnail((y,x),img.ANTIALIAS)
            rotatacaoImagem = rotatacaoImagem.rotate(-90,expand=True)
            rotatacaoImagem.save(path+'/'+self.pdf_local+'-000.jpg')
            img00 = rotatacaoImagem
        img00 = tratar.tratamentoDaImagem(self,img00)
        success,tmp1,tmp2 = tratar.corteCognetivo(self,img00,self.tipo)
        return (tmp1,tmp2)

    def reconhecerInformacao(self):
        pathReq = ['producao/','extraido/']
        sp.run(['pdfimages \''+self.totalpath+pathReq[0]+'/layout'+str(self.tipo)+'/'+self.pdf_local+'\' -j \''+str(self.totalpath+pathReq[1]+self.pdf_local)+'\''],shell=True)
        tmp1,tmp2 = tratar.avaliarImagem(self, self.totalpath + pathReq[1])
        cis,chassi = tratar.reconhecimento(self,tmp1,tmp2)
        doc = self.pdf_local.split('.')[0]
        datad = date.today()
        set = dataset.xml()
        erro = 0
        os.unlink(tmp1)
        os.unlink(tmp2)
        if (cis != '') and (chassi != '') and (len(cis) == 7) and (len(chassi) == 7):
            erro = 0
            #print('CIS:'+cis+' | CHASSI:'+chassi)
            #key = set.getPrimaryKey()
            set.criarXML(doc=doc,cis=cis,chassi=chassi)
            set.criarTabelaResult(doc=doc,cis=cis,chassi=chassi,data=str(datad))
            with open(self.totalpath+pathReq[0]+'/layout'+str(self.tipo)+'/'+self.pdf_local,'rb') as r:
                with open('resultado/'+self.pdf_local,'wb') as w:
                    w.write(r.read())
                    w.close()
                r.close()
        else:
            erro = 1
            set.criarTabelaError(doc=doc, cis=cis, chassi=chassi, data=str(datad))
            with open(self.totalpath+pathReq[0]+'/layout'+str(self.tipo)+'/'+self.pdf_local,'rb') as r:
                with open('erros/'+self.pdf_local,'wb') as w:
                    w.write(r.read())
                    w.close()
                r.close()
            #print('OCR não conseguiu reconhecer o os digitos')
        return (True,1)