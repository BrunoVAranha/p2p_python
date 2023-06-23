import socket
import xmlrpc.client
import os
import threading

# Criando um cliente RPC para chamar metodos do servidor
rpc_client = xmlrpc.client.ServerProxy('http://localhost:9000/')
# # Socket que se conecta ao servidor
client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Input que recebe a porta que o cliente usará para se conectar a um peer
port_input = int(input('Insira uma porta para seu cliente se conectar com outro peer: '))
# Input que recebe o caminho dos arquivos que o client possui
folder_path = input('Qual a pasta com seus arquivos? (peer1, peer2...: ')


# Método executado por uma thread em background crianco um socket para receber requisições de outros peers
def peer_server_thread():
    # Criação do socket que enviará o arquivo
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port_input))
    server_socket.listen(3)

    while True:
        try:
            # Aceitar a conexão de outro peer
            client_socket, client_address = server_socket.accept()

            file = client_socket.recv(1024).decode()

            with client_socket:
                # Abrir o arquivo solicitado pelo peer e enviar os bytes
                with open(f'{folder_path}/{file}.mp4', 'rb') as file:
                    sendfile = file.read()
                client_socket.sendall(sendfile)
        except socket.error:
            pass


# Função que formata o nome dos arquivos, removendo o formato '.mp4' do final
def remove_extension(file_list):
    formatted_file_list = []
    for file_name in file_list:
        file_name_without_extension = os.path.splitext(file_name)[0]
        formatted_file_list.append(file_name_without_extension)
    return formatted_file_list


def run_client():
    # Conectar cliente ao servidor
    server_address = ('localhost', 8000)
    client_server_socket.connect(server_address)

    file_list = remove_extension(os.listdir(folder_path))

    # Chamada do método join para se cadastrar no servidor
    join_message = rpc_client.join(port_input, file_list)
    print(join_message)

    # inicio do laço que permite o peer baixar arquivos
    while True:
        # Socket que irá se conectar a outro client(peer) para fazer download
        p2p_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        search_file = input('Insira o nome do arquivo desejado, ou <END> para encerrar a aplicação: ')
        if search_file == '<END>':
            break
        # Chamada do método search para buscar um arquiva na rede de peers
        search_peer = rpc_client.search(search_file, port_input)
        if search_peer is None:
            print('Nenhum peer possui este arquivo.')
            continue
        else:
            print(f'peers com o arquivo solicitado: {search_peer}')
            download = input('Deseja fazer download do arquivo? (Y/N): ')
            if download == 'Y':
                p2p_client_socket.connect(('localhost', search_peer[0]))
                # Enviar o nome do arquivo para ser baixado
                p2p_client_socket.send(search_file.encode())
                # Abrir arquivo para transefir (escrever) bytes
                with p2p_client_socket, open(f'{folder_path}/{search_file}.mp4', 'wb') as file:
                    while True:
                        recvfile = p2p_client_socket.recv(4096)
                        if not recvfile:
                            break
                        file.write(recvfile)
                print(f'Arquivo {search_file} baixado com sucesso na pasta {folder_path}')
                # Atualizar a lista de arquivos
                file_list = remove_extension(os.listdir(folder_path))
                rpc_client.update(port_input, file_list)
                p2p_client_socket.close()
    client_server_socket.close()


# Thread que irá rodar em background para aceitar requisições de download vindas de outro peer
server_thread = threading.Thread(target=peer_server_thread)
server_thread.daemon = True
server_thread.start()

# iniciar o cliente
run_client()
