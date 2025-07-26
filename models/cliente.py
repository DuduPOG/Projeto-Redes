from socket import socket
import psutil
import platform
import json

class Cliente:
    def __init__(self, host, port, shift=3):
        self.__host = host
        self.__port = port
        self.__shift = shift
        self.__socket = socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_host(self, host):
        if host == "":
            raise ValueError("host não pode ser vazio")
        else:
            self.__host = host

    def get_host(self):
        return self.__host
    
    def set_port(self, port):
        if port == "":
            raise ValueError("port não pode ser vazio")
        else:
            self.__port = port

    def get_port(self):
        return self.__port
    
    def set_socket(self, socket):
        if socket == "":
            raise ValueError("socket não pode ser vazio")
        else:
            self.__socket = socket

    def get_socket(self):
        return self.__socket
    
    def set_shift(self, shift):
        if shift == "" or not isinstance(shift, int):
            raise ValueError("shift não pode ser vazio e deve ser um valor inteiro")
        else:
            self.__shift = shift

    def get_shift(self):
        return self.__shift
    
    def cifra_cesar(self, texto, deslocamento):
        resultado = ""
        for char in texto:
            if 'a' <= char <= 'z':
                resultado += chr((ord(char) - ord('a') + deslocamento) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                resultado += chr((ord(char) - ord('A') + deslocamento) % 26 + ord('A'))
            else:
                resultado += char
        return resultado

    def coletar_dados(self):
        dados = {}
        
        # Quantidade de Processadores
        dados['processadores'] = psutil.cpu_count(logical=True)
        
        # Memória RAM Livre
        memoria = psutil.virtual_memory()
        dados['ram_livre'] = memoria.available / (1024 ** 3) # em GB
        
        # Espaço em disco livre
        disco = psutil.disk_usage('/')
        dados['disco_livre'] = disco.free / (1024 ** 3) # em GB
        
        # Endereço IP e interfaces
        interfaces = psutil.net_if_addrs()
        enderecos_ip = {}
        interfaces_desativadas = []
        for nome_interface, enderecos in interfaces.items():
            if psutil.net_if_stats()[nome_interface].isup:
                for endereco in enderecos:
                    if endereco.family == socket.AF_INET:
                        enderecos_ip[nome_interface] = endereco.address
            else:
                interfaces_desativadas.append(nome_interface)

        dados['enderecos_ip'] = enderecos_ip
        dados['interfaces_desativadas'] = interfaces_desativadas
        
        # Portas TCP e UDP abertas
        portas_tcp = []
        portas_udp = []
        conexoes = psutil.net_connections(kind='inet')
        for conexao in conexoes:
            if conexao.status == 'LISTEN':
                if conexao.type == socket.SOCK_STREAM:
                    portas_tcp.append(conexao.laddr.port)
                elif conexao.type == socket.SOCK_DGRAM:
                    portas_udp.append(conexao.laddr.port)
        
        dados['portas_tcp'] = portas_tcp
        dados['portas_udp'] = portas_udp
        
        return dados
    
    def enviar_dados(self):
        try:
            self.__socket.connect((self.__host, self.__port))
            print("Conectado ao servidor.")
            
            dados = self.coletar_dados()
            dados_json = json.dumps(dados)
            dados_criptografados = self.cifra_cesar(dados_json, self.__shift)
            
            self.__socket.sendall(dados_criptografados.encode('utf-8'))
            print("Dados enviados com sucesso.")
        except ConnectionRefusedError:
            print("Erro: A conexão foi recusada. O servidor pode não estar online.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            self.__socket.close()

if __name__ == "__main__":
    # O cliente precisa saber o IP do servidor.
    # Em uma rede local, você pode usar o IP do servidor.
    # Exemplo: '192.168.1.100'
    servidor_ip = '127.0.0.1' # Para testes na mesma máquina
    porta_servidor = 65432
    
    cliente = Cliente(servidor_ip, porta_servidor)
    cliente.enviar_dados()