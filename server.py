import json
from datetime import datetime
import threading
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

DATA_FILE = 'shopping_list.json'
lock = threading.Lock()

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(items):
    with open(DATA_FILE, 'w') as f:
        json.dump(items, f)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class ShoppingListService:
    def __init__(self):
        self.items = load_data()

    def add_item(self, name):
        with lock:
            for i in self.items:
                if i['name'] == name and not i['purchased']:
                    return False
            self.items.append({
                'name': name,
                'purchased': False,
                'value': 0.0,
                'date': None
            })
            save_data(self.items)
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
                    i['value'] = value
                    i['date'] = datetime.now().isoformat()
                    updated = True
            if updated:
                save_data(self.items)
            return updated

    def remove_item(self, name):
        with lock:
            before = len(self.items)
            self.items = [i for i in self.items if i['name'] != name]
            if len(self.items) < before:
                save_data(self.items)
                return True
            return False

    def monthly_total(self, year, month):
        total = 0.0
        for i in self.items:
            if i['purchased'] and i['date']:
                d = datetime.fromisoformat(i['date'])
                if d.year == year and d.month == month:
                    total += i['value']
        return total

if __name__ == '__main__':
    server = ThreadedXMLRPCServer(('0.0.0.0', 8000), allow_none=True)
    svc = ShoppingListService()
    server.register_instance(svc)
    print('RPC Shopping List server running on port 8000')
    server.serve_forever()