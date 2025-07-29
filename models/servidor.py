import socket
import json
import threading

class Servidor:
    def __init__(self, host, port, shift=3):
        self.__host = host
        self.__port = port
        self.__shift = shift
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clientes = {}
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
    
    def get_clientes(self):
        return self.__clientes
    
    @staticmethod
    def cifra_cesar(texto, deslocamento):
        deslocamento = -deslocamento # Para descriptografar
        resultado = ""
        for char in texto:
            if 'a' <= char <= 'z':
                resultado += chr((ord(char) - ord('a') + deslocamento) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                resultado += chr((ord(char) - ord('A') + deslocamento) % 26 + ord('A'))
            else:
                resultado += char
        return resultado

    @staticmethod
    def processar_cliente(self, conexao, endereco):
        try:
            dados_criptografados = conexao.recv(4096).decode('utf-8')
            dados_descriptografados = self.cifra_cesar(dados_criptografados, self.__shift)
            
            dados = json.loads(dados_descriptografados)
            print(f"Dados recebidos do cliente {endereco}:")
            
            self.__clientes[endereco[0]] = dados
            self.imprimir_dados_cliente(endereco[0], dados)

        except json.JSONDecodeError:
            print(f"Erro ao decodificar dados JSON do cliente {endereco}.")
        except Exception as e:
            print(f"Erro ao processar dados do cliente {endereco}: {e}")
        finally:
            conexao.close()
            print(f"Conexão com {endereco} fechada.")

    @staticmethod
    def imprimir_dados_cliente(ip, dados):
        print("--- Detalhes do Cliente ---")
        print(f"IP: {ip}")
        print(f"Processadores: {dados.get('processadores')}")
        print(f"Memória RAM Livre: {dados.get('ram_livre'):.2f} GB")
        print(f"Espaço em Disco Livre: {dados.get('disco_livre'):.2f} GB")
        print("Endereços IP das Interfaces:")
        for interface, endereco in dados.get('enderecos_ip', {}).items():
            print(f"  - {interface}: {endereco}")
        print(f"Interfaces Desativadas: {', '.join(dados.get('interfaces_desativadas', []))}")
        print(f"Portas TCP abertas: {dados.get('portas_tcp')}")
        print(f"Portas UDP abertas: {dados.get('portas_udp')}")
        print("----------------------------")

    def calcular_medias(self):
        if not self.__clientes:
            print("\nNenhum cliente conectado para calcular a média.")
            return

        total_processadores = 0
        total_ram_livre = 0
        total_disco_livre = 0
        
        for dados in self.__clientes.values():
            total_processadores += dados.get('processadores', 0)
            total_ram_livre += dados.get('ram_livre', 0)
            total_disco_livre += dados.get('disco_livre', 0)
        
        num_clientes = len(self.__clientes)
        
        media_processadores = total_processadores / num_clientes
        media_ram_livre = total_ram_livre / num_clientes
        media_disco_livre = total_disco_livre / num_clientes

        print("\n--- Média dos Dados Consolidados ---")
        print(f"Média de Processadores: {media_processadores:.2f}")
        print(f"Média de RAM Livre: {media_ram_livre:.2f} GB")
        print(f"Média de Espaço em Disco Livre: {media_disco_livre:.2f} GB")
        print("------------------------------------")
pass