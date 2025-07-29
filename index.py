import threading
from socket import socket
import psutil
import platform
import json
from models.cliente import Cliente
from models.servidor import Servidor

class UI:

    @staticmethod
    def menu(servidor):
        while True:
            print("\n--- Menu do Servidor ---")
            print("1. Listar clientes conectados")
            print("2. Detalhar cliente por IP")
            print("3. Exibir médias consolidadas")
            print("4. Sair")
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                if not servidor.get_clientes():
                    print("Nenhum cliente conectado.")
                else:
                    print("\nClientes conectados:")
                    for ip in servidor.get_clientes().keys():
                        print(f"- {ip}")
            elif escolha == '2':
                ip_cliente = input("Digite o IP do cliente para detalhar: ")
                if ip_cliente in servidor.get_clientes():
                    servidor.imprimir_dados_cliente(ip_cliente, servidor.get_clientes()[ip_cliente])
                else:
                    print("Cliente não encontrado.")
            elif escolha == '3':
                servidor.calcular_medias()
            elif escolha == '4':
                print("Encerrando o servidor...")
                UI.parar(servidor)
                break
            else:
                print("Opção inválida. Tente novamente.")

    @staticmethod
    def iniciar(servidor):
        try:
            servidor.get_socket().bind((servidor.get_host(), servidor.get_port()))
            servidor.get_socket().listen()
            print(f"Servidor iniciado em {servidor.get_host()}:{servidor.get_port()}")
            
            menu_thread = threading.Thread(target=UI.menu(servidor), args=(servidor,))
            menu_thread.daemon = True
            menu_thread.start()

            while True:
                conexao, endereco = servidor.get_socket().accept()
                print(f"Conexão recebida de {endereco}")
                thread = threading.Thread(target=servidor.processar_cliente(), args=(conexao, endereco))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("Servidor encerrado por interrupção do usuário.")
        except Exception as e:
            print(f"Erro no servidor: {e}")
        finally:
            servidor.get_socket().close()

    def parar(servidor):
        servidor.get_socket().close()
    
if __name__ == "__main__":
    servidor_ip = '0.0.0.0' # Aceita conexões de qualquer IP
    porta_servidor = 65432
    
    servidor = Servidor(servidor_ip, porta_servidor)
    UI.iniciar(servidor)