import socket
import json
import threading

class Servidor:
    def __init__(self, host, port, shift=3):
        self._host = host
        self._port = port
        self._shift = shift
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientes = {}
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._print_func = print
        self._porta_comando = 65433 # Nova porta para comandos

    # ... (os métodos _cifra_cesar permanecem os mesmos) ...

    def _cifra_cesar(self, texto, deslocamento):
        deslocamento = -deslocamento
        resultado = ""
        for char in texto:
            if 'a' <= char <= 'z':
                resultado += chr((ord(char) - ord('a') + deslocamento) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                resultado += chr((ord(char) - ord('A') + deslocamento) % 26 + ord('A'))
            else:
                resultado += char
        return resultado

    def _processar_cliente_seguro(self, conexao, cliente_ip):
        try:
            dados_criptografados = conexao.recv(4096).decode('utf-8')
            dados_descriptografados = self._cifra_cesar(dados_criptografados, self._shift)
            
            dados = json.loads(dados_descriptografados)
            self._print_func(f"Dados recebidos do cliente {cliente_ip}:")
            
            self._clientes[cliente_ip] = dados
            self._imprimir_dados_cliente_seguro(cliente_ip, dados)

        except json.JSONDecodeError:
            self._print_func(f"Erro ao decodificar dados JSON do cliente {cliente_ip}.")
        except Exception as e:
            self._print_func(f"Erro ao processar dados do cliente {cliente_ip}: {e}")
        finally:
            conexao.close()
            self._print_func(f"Conexão com {cliente_ip} fechada.")

    # ... (os métodos _imprimir_dados_cliente_seguro e _calcular_medias_seguro permanecem os mesmos) ...
    def _imprimir_dados_cliente_seguro(self, ip, dados):
        self._print_func("--- Detalhes do Cliente ---")
        self._print_func(f"IP: {ip}")
        self._print_func(f"Processadores: {dados.get('processadores')}")
        self._print_func(f"Memória RAM Livre: {dados.get('ram_livre'):.2f} GB")
        self._print_func(f"Espaço em Disco Livre: {dados.get('disco_livre'):.2f} GB")
        self._print_func("Endereços IP das Interfaces:")
        for interface, endereco in dados.get('enderecos_ip', {}).items():
            self._print_func(f"  - {interface}: {endereco}")
        self._print_func(f"Interfaces Desativadas: {', '.join(dados.get('interfaces_desativadas', []))}")
        self._print_func(f"Portas TCP abertas: {dados.get('portas_tcp')}")
        self._print_func(f"Portas UDP abertas: {dados.get('portas_udp')}")
        self._print_func("----------------------------")

    def _calcular_medias_seguro(self):
        if not self._clientes:
            self._print_func("\nNenhum cliente conectado para calcular a média.")
            return

        total_processadores = 0
        total_ram_livre = 0
        total_disco_livre = 0
        
        for dados in self._clientes.values():
            total_processadores += dados.get('processadores', 0)
            total_ram_livre += dados.get('ram_livre', 0)
            total_disco_livre += dados.get('disco_livre', 0)
        
        num_clientes = len(self._clientes)
        
        media_processadores = total_processadores / num_clientes
        media_ram_livre = total_ram_livre / num_clientes
        media_disco_livre = total_disco_livre / num_clientes

        self._print_func("\n--- Média dos Dados Consolidados ---")
        self._print_func(f"Média de Processadores: {media_processadores:.2f}")
        self._print_func(f"Média de RAM Livre: {media_ram_livre:.2f} GB")
        self._print_func(f"Média de Espaço em Disco Livre: {media_disco_livre:.2f} GB")
        self._print_func("------------------------------------")

    def _enviar_comando(self, cliente_ip, comando):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((cliente_ip, self._porta_comando))
            comando_criptografado = self._cifra_cesar(comando, self._shift)
            s.sendall(comando_criptografado.encode('utf-8'))
            
            resposta_criptografada = s.recv(1024).decode('utf-8')
            resposta = self._cifra_cesar(resposta_criptografada, -self._shift)
            self._print_func(f"Resposta do cliente {cliente_ip}: {resposta}")
        except ConnectionRefusedError:
            self._print_func(f"Erro: O cliente {cliente_ip} não está ouvindo comandos na porta {self._porta_comando}.")
        except Exception as e:
            self._print_func(f"Erro ao enviar comando para {cliente_ip}: {e}")
        finally:
            s.close()
    
    def enviar_comando_desligar(self, cliente_ip):
        self._enviar_comando(cliente_ip, "SHUTDOWN")

    # ... (getters e parar permanecem os mesmos) ...
    def set_print_func(self, func):
        self._print_func = func

    def get_socket(self):
        return self._socket

    def get_host(self):
        return self._host

    def get_port(self):
        return self._port
    
    def get_clientes(self):
        return self._clientes.copy()

    def parar(self):
        self._socket.close()