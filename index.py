import threading
import socket 

from models.cliente import Cliente
from models.servidor import Servidor

class UI:
    _print_lock = threading.Lock()
    _cliente_local_thread = None
    _cliente_local_instancia = None

    @staticmethod
    def _print_sincronizado(*args, **kwargs):
        """Imprime no console de forma sincronizada."""
        with UI._print_lock:
            print(*args, **kwargs)

    @staticmethod
    def _iniciar_servidor_thread(servidor_instance):
        """Função interna para iniciar o servidor em uma thread."""
        try:
            servidor_instance.get_socket().bind((servidor_instance.get_host(), servidor_instance.get_port()))
            servidor_instance.get_socket().listen()
            UI._print_sincronizado(f"Servidor iniciado em {servidor_instance.get_host()}:{servidor_instance.get_port()}")
            
            while True:
                conexao, endereco = servidor_instance.get_socket().accept()
                UI._print_sincronizado(f"Conexão recebida de {endereco}")
                cliente_ip = endereco[0]
                thread = threading.Thread(target=servidor_instance._processar_cliente_seguro, args=(conexao, cliente_ip))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            UI._print_sincronizado("\nServidor encerrado por interrupção do usuário.")
        except Exception as e:
            UI._print_sincronizado(f"Erro no servidor: {e}")
        finally:
            servidor_instance.get_socket().close()

    @staticmethod
    def menu(servidor_instance):
        """Exibe o menu de interação com o servidor."""
        global _cliente_local_thread, _cliente_local_instancia
        
        while True:
            UI._print_sincronizado("\n--- Menu do Servidor ---")
            UI._print_sincronizado("1. Listar IPs de clientes conectados")
            UI._print_sincronizado("2. Detalhar cliente por IP")
            UI._print_sincronizado("3. Exibir médias consolidadas")
            UI._print_sincronizado("4. Enviar dados do cliente local (para teste)")
            UI._print_sincronizado("5. Desligar um cliente")
            UI._print_sincronizado("6. Sair")
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                clientes_ips = servidor_instance.get_clientes().keys()
                if not clientes_ips:
                    UI._print_sincronizado("Nenhum cliente conectado.")
                else:
                    UI._print_sincronizado("\nIPs de clientes conectados:")
                    for ip in clientes_ips:
                        UI._print_sincronizado(f"- {ip}")
            elif escolha == '2':
                ip_cliente_para_detalhar = input("Digite o IP do cliente para detalhar: ")
                dados_cliente = servidor_instance.get_clientes().get(ip_cliente_para_detalhar)
                if dados_cliente:
                    servidor_instance._imprimir_dados_cliente_seguro(ip_cliente_para_detalhar, dados_cliente)
                else:
                    UI._print_sincronizado(f"Cliente com IP '{ip_cliente_para_detalhar}' não encontrado.")
            elif escolha == '3':
                servidor_instance._calcular_medias_seguro()
            elif escolha == '4':
                if UI._cliente_local_thread and UI._cliente_local_thread.is_alive():
                    UI._print_sincronizado("O cliente local já está em execução. Os dados serão enviados automaticamente.")
                else:
                    UI._print_sincronizado("Iniciando cliente local para envio de dados e escuta de comandos...")
                    servidor_ip_cliente = '127.0.0.1' 
                    porta_servidor_cliente = 65432
                    porta_comando_cliente = 65433
                    
                    UI._cliente_local_instancia = Cliente(servidor_ip_cliente, porta_servidor_cliente)
                    
                    # Inicia a thread que ouve comandos
                    UI._cliente_local_thread = threading.Thread(target=UI._cliente_local_ouvir_e_enviar, 
                                                                 args=(UI._cliente_local_instancia, porta_comando_cliente))
                    UI._cliente_local_thread.daemon = True
                    UI._cliente_local_thread.start()
            elif escolha == '5':
                ip_cliente_alvo = input("Digite o IP do cliente para desligar: ")
                if ip_cliente_alvo in servidor_instance.get_clientes():
                    servidor_instance.enviar_comando_desligar(ip_cliente_alvo)
                else:
                    UI._print_sincronizado("Cliente não encontrado. Verifique o IP.")
            elif escolha == '6':
                UI._print_sincronizado("Encerrando o servidor e saindo...")
                if UI._cliente_local_instancia:
                    UI._cliente_local_instancia.parar_ouvinte()
                servidor_instance.parar()
                break
            else:
                UI._print_sincronizado("Opção inválida. Tente novamente.")
    
    @staticmethod
    def _cliente_local_ouvir_e_enviar(cliente_instancia, porta_comando):
        """Função para ser executada na thread do cliente local."""
        cliente_instancia.enviar_dados()
        cliente_instancia.ouvir_comandos(porta_comando)

if __name__ == "__main__":
    servidor_host = '0.0.0.0'
    porta_servidor = 65432
    
    servidor = Servidor(servidor_host, porta_servidor)
    servidor.set_print_func(UI._print_sincronizado)
    
    servidor_thread = threading.Thread(target=UI._iniciar_servidor_thread, args=(servidor,))
    servidor_thread.daemon = True
    servidor_thread.start()

    UI.menu(servidor)
    servidor_thread.join()
    UI._print_sincronizado("Aplicação finalizada.")