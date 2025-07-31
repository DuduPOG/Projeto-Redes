import socket
import psutil
import platform
import json

class Cliente:
    def __init__(self, host, port, shift=3):
        self._host = host
        self._port = port
        self._shift = shift
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def _cifra_cesar(self, texto, deslocamento):
        resultado = ""
        for char in texto:
            if 'a' <= char <= 'z':
                resultado += chr((ord(char) - ord('a') + deslocamento) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                resultado += chr((ord(char) - ord('A') + deslocamento) % 26 + ord('A'))
            else:
                resultado += char
        return resultado

    def _coletar_dados(self):
        dados = {}
        dados['processadores'] = psutil.cpu_count(logical=True)
        memoria = psutil.virtual_memory()
        dados['ram_livre'] = memoria.available / (1024 ** 3) # em GB
        disco = psutil.disk_usage('/')
        dados['disco_livre'] = disco.free / (1024 ** 3) # em GB
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
    
    def enviar_dados_seguro(self, print_func):
        """Envia dados usando uma função de impressão segura."""
        try:
            self._socket.connect((self._host, self._port))
            print_func("Conectado ao servidor.")
            
            dados = self._coletar_dados()
            dados_json = json.dumps(dados)
            dados_criptografados = self._cifra_cesar(dados_json, self._shift)
            
            self._socket.sendall(dados_criptografados.encode('utf-8'))
            print_func("Dados enviados com sucesso.")
        except ConnectionRefusedError:
            print_func("Erro: A conexão foi recusada. O servidor pode não estar online.")
        except Exception as e:
            print_func(f"Ocorreu um erro ao enviar dados: {e}")
        finally:
            self._socket.close()
            # Reabre o socket para futuras conexões (importante se você criar uma nova instância de Cliente para cada envio)
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)