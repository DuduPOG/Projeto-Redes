import threading
from socket import socket
import psutil
import platform
import json
from models.cliente import Cliente
from models.servidor import Servidor

class UI:

    def menu():
        while True:
            print("\n--- Menu do Servidor ---")
            print("1. Listar clientes conectados")
            print("2. Detalhar cliente por IP")
            print("3. Exibir médias consolidadas")
            print("4. Sair")
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                if not Servidor.get_clientes():
                    print("Nenhum cliente conectado.")
                else:
                    print("\nClientes conectados:")
                    for ip in Servidor.get_clientes().keys():
                        print(f"- {ip}")
            elif escolha == '2':
                ip_cliente = input("Digite o IP do cliente para detalhar: ")
                if ip_cliente in Servidor.get_clientes():
                    Servidor.imprimir_dados_cliente(ip_cliente, Servidor.get_clientes()[ip_cliente])
                else:
                    print("Cliente não encontrado.")
            elif escolha == '3':
                Servidor.calcular_medias()
            elif escolha == '4':
                print("Encerrando o servidor...")
                Servidor.parar()
                break
            else:
                print("Opção inválida. Tente novamente.")

    def iniciar():
        try:
            Servidor.get_socket().bind((Servidor.get_host(), Servidor.get_port()))
            Servidor.get_socket().listen()
            print(f"Servidor iniciado em {Servidor.get_host()}:{Servidor.get_port()}")
            
            menu_thread = threading.Thread(target=Servidor.menu())
            menu_thread.daemon = True
            menu_thread.start()

            while True:
                conexao, endereco = Servidor.get_socket().accept()
                print(f"Conexão recebida de {endereco}")
                thread = threading.Thread(target=Servidor.processar_cliente(), args=(conexao, endereco))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("Servidor encerrado por interrupção do usuário.")
        except Exception as e:
            print(f"Erro no servidor: {e}")
        finally:
            Servidor.get_socket().close()

    def parar(self):
        Servidor.get_socket().close()
    
if __name__ == "__main__":
    servidor_ip = '0.0.0.0' # Aceita conexões de qualquer IP
    porta_servidor = 65432
    
    servidor = Servidor(servidor_ip, porta_servidor)
    servidor.iniciar()