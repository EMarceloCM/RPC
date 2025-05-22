import json
from datetime import datetime
import threading
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

DATA_FILE = 'shopping_list.json'
lock = threading.Lock() # usado nos métodos que modificam a lista, garantindo exclusão mútua pois as threads compartilham o mesmo espaço de memória (self.items).
# se duas threads modificarem essa lista ao mesmo tempo, podem ocorrer itens duplicados, atualizações errdas etc.

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError: # retorna lista vazia se não houver arquivo (primeira execução)
        return []

def save_data(items):
    with open(DATA_FILE, 'w') as f:
        json.dump(items, f) # substitui o conteúdo do arquivo persistente

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): # Servidor herda de ThreadingMixIn (Cria uma nova thread para cada requisição) e SimpleXMLRPCServer (Recebe conexões XML-RPC)
    pass

class ShoppingListService:
    def __init__(self): # ao instanciar, carrega a lista existente em self.items
        self.items = load_data()

    def add_item(self, name):
        with lock: # lock garante que duas threads não insiram simultaneamente
            for i in self.items:
                if i['name'] == name and not i['purchased']:
                    return False # evita duplicata de item ainda não comprado
            self.items.append({
                'name': name,
                'purchased': False,
                'value': 0.0,
                'date': None
            })
            save_data(self.items) # persiste no arquivo json
            return True

    def list_items(self):
        return self.items

    def mark_item(self, name, value):
        with lock:
            for i in self.items:
                if i['name'] == name and not i['purchased']:
                    i['purchased'] = True
                    i['value'] = value
                    i['date'] = datetime.now().isoformat()
                    save_data(self.items)
                    return True
            return False

    def mark_all(self, value):
        with lock:
            updated = False
            for i in self.items:
                if not i['purchased']:
                    i['purchased'] = True
                    i['value'] = value # atualiza todos os itens da lista com o mesmo valor
                    i['date'] = datetime.now().isoformat()
                    updated = True
            if updated:
                save_data(self.items) # só persiste os dados se tiver havido alguma alteração
            return updated

    def remove_item(self, name):
        with lock:
            before = len(self.items) # salva cópia da lista completa
            self.items = [i for i in self.items if i['name'] != name ] # filtra a lista original com os itens que não atendem ao nome
            if len(self.items) < before:
                save_data(self.items) # se houver diferença persiste os dados no json sem os itens que batem com o nome informado
                return True
            return False

    def monthly_total(self, year, month):
        total = 0.0
        for i in self.items:
            if i['purchased'] and i['date']: # pega os itens já comprados
                d = datetime.fromisoformat(i['date'])
                if d.year == year and d.month == month: # se a data bater com o mês e ano informados, soma o valor
                    total += i['value']
        return total

if __name__ == '__main__':
    server = ThreadedXMLRPCServer(('0.0.0.0', 8000), allow_none=True) # instancia o RPC e ele escuta em todas as interfaces na porta 8000
    svc = ShoppingListService() # instancia o servidor de lista de compras
    server.register_instance(svc) # torna cada método público do ShoppingListService disponível via RPC
    print('RPC Shopping List server running on port 8000')
    server.serve_forever() # entra em loop bloqueante, atendendo requisições indefinidamente
