import sys
from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:8000/', allow_none=True) # instancia um objeto proxy que aponta para o servidor XML-RPC

def usage(): # função que será chamada quando o cliente digitar um comando inválido
    print('Commands: add <item>, list, mark <item> <value>, mark_all <value>, remove <item>, total <year> <month>')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage() # se não houver argumentos exibe a mensagem de ajuda e retorna erro
        sys.exit(1)
    cmd = sys.argv[1] # recebe o primeiro argumento do script e verifica a qual comando pertence
    if cmd == 'add':
        print(proxy.add_item(sys.argv[2])) # imprime o resultado da invocação do método remoto
    elif cmd == 'list':
        print(proxy.list_items())
    elif cmd == 'mark':
        print(proxy.mark_item(sys.argv[2], float(sys.argv[3])))
    elif cmd == 'mark_all':
        print(proxy.mark_all(float(sys.argv[2])))
    elif cmd == 'remove':
        print(proxy.remove_item(sys.argv[2]))
    elif cmd == 'total':
        print(proxy.monthly_total(int(sys.argv[2]), int(sys.argv[3])))
    else:
        usage()
