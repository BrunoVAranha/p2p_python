import socket
from xmlrpc.server import SimpleXMLRPCServer

# Criar socket ocm padrão TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Informações do server
server_address = ('localhost', 8000)
# Linkar o server às informações acima
server_socket.bind(server_address)
# Definir quantas conexões o servidor aceita ao mesmo tempo
server_socket.listen(5)
# Socket que conecta ao cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Dicionario que irá armazenar qual peer contém quais arquivos
client_data = {}


# Método responsável por conectar um cliente ao servidor, e listar quais arquivos ele possui
def join(port_input, files):
    global client_socket
    client_socket, addr = server_socket.accept()
    client_data[port_input] = files
    join_ok = f'Sou peer {port_input} com arquivos : {client_data[port_input]}'
    return join_ok


# Método responsável por buscar um arquivo no catálogo de peer -> arquivos
def search(file):
    keys = []
    for key, values in client_data.items():
        if file in values:
            keys.append(key)
    if not keys:
        return None
    return keys


# Método responsável por atualizar o dicionário de peer -> arquivos
def update(port, file_list):
    client_data[port] = file_list


def run_server():
    print('Server is running. Listening for connections...')

    # Criar o server RPC, que irá lidar com as requisições remotas
    rpc_server = SimpleXMLRPCServer(('localhost', 9000), allow_none=True)

    # registrando no servidor os métodos de chamada remota
    rpc_server.register_function(join, 'join')
    rpc_server.register_function(search, 'search')
    rpc_server.register_function(update, 'update')

    # inicar o servidor e mantê-lo rodando
    while True:
        rpc_server.handle_request()


run_server()
