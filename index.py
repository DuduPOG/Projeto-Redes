import threading
import socket 

from models.cliente import Cliente
from models.servidor import Servidor

class UI:
    _print_lock = threading.Lock()

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
                # Usa o método _processar_cliente_seguro que utiliza a função de print sincronizada
                thread = threading.Thread(target=servidor_instance._processar_cliente_seguro, args=(conexao, cliente_ip))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            UI._print_sincronizado("\nServidor encerrado por interrupção do usuário.")
        except Exception as e:
            UI._print_sincronizado(f"Erro no servidor: {e}")
        finally:
            # Garante que o socket seja fechado mesmo em caso de erro
            servidor_instance.get_socket().close()

    @staticmethod
    def menu(servidor_instance):
        """Exibe o menu de interação com o servidor."""
        while True:
            UI._print_sincronizado("\n--- Menu do Servidor ---")
            UI._print_sincronizado("1. Listar IPs de clientes conectados")
            UI._print_sincronizado("2. Detalhar cliente por IP")
            UI._print_sincronizado("3. Exibir médias consolidadas")
            UI._print_sincronizado("4. Enviar dados do cliente local (para teste)")
            UI._print_sincronizado("5. Sair")
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
                    # Chama o método de impressão seguro do servidor
                    servidor_instance._imprimir_dados_cliente_seguro(ip_cliente_para_detalhar, dados_cliente)
                else:
                    UI._print_sincronizado(f"Cliente com IP '{ip_cliente_para_detalhar}' não encontrado.")
            elif escolha == '3':
                # Chama o método de cálculo de médias seguro do servidor
                servidor_instance._calcular_medias_seguro()
            elif escolha == '4':
                UI._print_sincronizado("Enviando dados do cliente local...")
                servidor_ip_cliente = '127.0.0.1' 
                porta_servidor_cliente = 65432
                cliente_local = Cliente(servidor_ip_cliente, porta_servidor_cliente)
                # Passa a função de print sincronizado para o cliente
                cliente_local.enviar_dados_seguro(UI._print_sincronizado) 
            elif escolha == '5':
                UI._print_sincronizado("Encerrando o servidor e saindo...")
                servidor_instance.parar()
                break
            else:
                UI._print_sincronizado("Opção inválida. Tente novamente.")
    
if __name__ == "__main__":
    servidor_host = '0.0.0.0'
    porta_servidor = 65432
    
    servidor = Servidor(servidor_host, porta_servidor)
    # INJETAR A FUNÇÃO DE PRINT SINCRONIZADA NO SERVIDOR
    servidor.set_print_func(UI._print_sincronizado)
    
    servidor_thread = threading.Thread(target=UI._iniciar_servidor_thread, args=(servidor,))
    servidor_thread.daemon = True
    servidor_thread.start()

    UI.menu(servidor)
    servidor_thread.join()
    UI._print_sincronizado("Aplicação finalizada.")