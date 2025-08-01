import socket
import psutil
import platform
import json
import os
from datetime import datetime
import threading

class Cliente:
    def __init__(self, host, port, shift=3):
        self._host = host
        self._port = port
        self._shift = shift
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_ouvinte = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._print_lock = threading.Lock()
    
    def _print_sincronizado(self, *args, **kwargs):
        """Imprime no console de forma sincronizada."""
        with self._print_lock:
            print(*args, **kwargs)

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
    
    def enviar_dados(self):
        try:
            self._socket.connect((self._host, self._port))
            self._print_sincronizado("Conectado ao servidor.")
            
            dados = self._coletar_dados()
            dados_json = json.dumps(dados)
            dados_criptografados = self._cifra_cesar(dados_json, self._shift)
            
            self._socket.sendall(dados_criptografados.encode('utf-8'))
            self._print_sincronizado("Dados enviados com sucesso.")
        except ConnectionRefusedError:
            self._print_sincronizado("Erro: A conexão foi recusada. O servidor pode não estar online.")
        except Exception as e:
            self._print_sincronizado(f"Ocorreu um erro ao enviar dados: {e}")
        finally:
            self._socket.close()
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _executar_comando(self, conexao, comando):
        resposta = ""
        try:
            if comando == "SHUTDOWN":
                if platform.system() == "Windows":
                    os.system("shutdown /s /t 1")
                elif platform.system() == "Linux" or platform.system() == "Darwin":
                    os.system("sudo shutdown -h now")
                resposta = "Comando de desligamento executado."
            else:
                resposta = f"Comando desconhecido: {comando}"
        except Exception as e:
            resposta = f"Erro ao executar o comando {comando}: {e}"
        finally:
            resposta_criptografada = self._cifra_cesar(resposta, self._shift)
            conexao.sendall(resposta_criptografada.encode('utf-8'))

    def ouvir_comandos(self, porta_comando):
        try:
            self._socket_ouvinte.bind(('0.0.0.0', porta_comando))
            self._socket_ouvinte.listen(1)
            self._print_sincronizado(f"Cliente ouvindo comandos na porta {porta_comando}...")
            while True:
                conexao, endereco = self._socket_ouvinte.accept()
                try:
                    comando_criptografado = conexao.recv(1024).decode('utf-8')
                    comando = self._cifra_cesar(comando_criptografado, -self._shift)
                    
                    self._print_sincronizado(f"Comando recebido de {endereco[0]}: {comando}")
                    
                    # Usa uma nova thread para executar o comando e não bloquear o socket
                    thread_comando = threading.Thread(target=self._executar_comando, args=(conexao, comando))
                    thread_comando.daemon = True
                    thread_comando.start()

                except Exception as e:
                    self._print_sincronizado(f"Erro ao processar comando: {e}")
                finally:
                    conexao.close()
        except OSError as e:
            self._print_sincronizado(f"Erro ao ligar o socket de comando: {e}. A porta pode já estar em uso.")
        except Exception as e:
            self._print_sincronizado(f"Erro no loop de escuta de comandos: {e}")
        finally:
            self._socket_ouvinte.close()
    
    def parar_ouvinte(self):
        self._socket_ouvinte.close()
        
    def get_socket(self):
        return self._socket

    def get_host(self):
        return self._host

    def get_port(self):
        return self._port
    
    def get_shift(self):
        return self._shift

# Adicione este bloco de execução no final do arquivo models/cliente.py
"""if __name__ == "__main__":
    servidor_ip = '127.0.0.1' 
    porta_servidor = 65432
    porta_comando = 65433
    
    cliente = Cliente(servidor_ip, porta_servidor)
    
    # Inicia a thread que ouve comandos
    comando_thread = threading.Thread(target=cliente.ouvir_comandos, args=(porta_comando,))
    comando_thread.daemon = True # Garante que a thread termine com o programa principal
    comando_thread.start()
    
    # Envia os dados do cliente para o servidor uma vez
    cliente.enviar_dados()

    # Mantém o script rodando para a thread de comandos continuar ativa
    try:
        comando_thread.join() # O join() aqui fará com que o script principal espere a thread de comandos
    except KeyboardInterrupt:
        cliente.parar_ouvinte()
        print("Cliente encerrado pelo usuário.")"""