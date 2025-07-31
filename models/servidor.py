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
        # print_func será injetado pela UI para garantir a sincronização
        self._print_func = print 

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

    # Renomeando para 'seguro' para indicar que usa o print sincronizado
    def _processar_cliente_seguro(self, conexao, cliente_ip):
        try:
            dados_criptografados = conexao.recv(4096).decode('utf-8')
            dados_descriptografados = self._cifra_cesar(dados_criptografados, self._shift)
            
            dados = json.loads(dados_descriptografados)
            self._print_func(f"Dados recebidos do cliente {cliente_ip}:")
            
            self._clientes[cliente_ip] = dados
            self._imprimir_dados_cliente_seguro(cliente_ip, dados) # Chamada para o método seguro

        except json.JSONDecodeError:
            self._print_func(f"Erro ao decodificar dados JSON do cliente {cliente_ip}.")
        except Exception as e:
            self._print_func(f"Erro ao processar dados do cliente {cliente_ip}: {e}")
        finally:
            conexao.close()
            self._print_func(f"Conexão com {cliente_ip} fechada.")

    # Renomeando para 'seguro'
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

    # Renomeando para 'seguro'
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
    
    # Adicionando um setter para a função de impressão
    def set_print_func(self, func):
        self._print_func = func

    # Getters permanecem os mesmos
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