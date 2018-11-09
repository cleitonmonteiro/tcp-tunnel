import ctypes as ct
import sys

class Pacote:
    def __init__(self):
        pass
    def mostradados(self):
        lista = [self.seq,
                self.ack,
                self.con,
                self.opcoes,
                self.dados
        ]
        return lista
    def contruir_pacote(self,seq,ack,con,opcoes,dados=""):
        self.seq = ct.c_int(seq)
        self.ack = ct.c_int(ack)
        self.con = ct.c_short(con)
        self.opcoes = ct.c_short(opcoes)
        self.dados = dados.encode("utf-8")
    def para_rede(self):
        return bytes(self.seq) + \
         bytes(self.ack) + \
         bytes(self.con) + \
         bytes(self.opcoes) + \
         self.dados

        
    def desfazer_pacote(self, internet_pacote):
        self.seq = int.from_bytes(internet_pacote[:4],sys.byteorder)
        self.ack = int.from_bytes(internet_pacote[4:8],sys.byteorder)
        self.con = int.from_bytes(internet_pacote[8:10],sys.byteorder)
        self.opcoes = int.from_bytes(internet_pacote[10:12],sys.byteorder)
        self.dados = (internet_pacote[12:].decode("utf-8"))
    

