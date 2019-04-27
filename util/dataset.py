class xml:

    def setPrimaryKey(self,id):
        a = int(id) + 1
        with open('ckey.key','wt') as f:
            f.write(str(a))
            f.close()
        return a

    def getPrimaryKey(self):
        with open('ckey.key','rt') as f:
            r = f.read()
            f.close()
        return r

    def getModelXML(self):
        with open('dataset/model.xml') as f:
            r = f.read()
            f.close()
        return r.replace('\n','')


    def criarXML(self,doc,cis,chassi):
        qxml = xml.getModelXML(self).format(tipo='Fichas SRDQ',chassi=chassi,cis=cis,documento=doc+str('.pdf'),paginas=str(4),breakline='\n')
        with open('resultado/'+doc+'.xml','w') as f:
            f.write(qxml)
            f.close()

    def criarTabelaResult(self,doc,cis,chassi,data):
        qtable = str(doc)+'.pdf,'+cis+','+chassi+','+data+'\n'
        with open('dataset/resultados.csv', 'a') as f:
            f.write(qtable)
            f.close()

    def criarTabelaError(self,doc,cis,chassi,data):
        qtable = str(doc)+'.pdf,'+cis+','+chassi+','+data+'\n'
        with open('dataset/erros.csv', 'a') as f:
            f.write(qtable)
            f.close()