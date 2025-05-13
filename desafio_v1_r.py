from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero: int, cliente: Cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor: float):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor: float):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = len([
            t for t in self.historico.transacoes
            if t["tipo"] == Saque.__name__
        ])

        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if saques_realizados >= self._limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
Agência:\t{self.agencia}
C/C:\t\t{self.numero}
Titular:\t{self.cliente.nome}
"""


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta: Conta):
        pass


class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

clientes = []

def encontrar_cliente_por_cpf(cpf):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def selecionar_conta(cliente):
    if not cliente.contas:
        print("Este cliente não possui contas.")
        return None

    print("\nContas disponíveis:")
    for i, conta in enumerate(cliente.contas):
        print(f"{i + 1} - Conta {conta.numero}")
    opcao = int(input("Escolha o número da conta: ")) - 1

    if 0 <= opcao < len(cliente.contas):
        return cliente.contas[opcao]

    print("Opção inválida.")
    return None

def menu():
    print("\n=== MENU PRINCIPAL ===")
    print("1 - Cadastrar cliente")
    print("2 - Criar conta para cliente existente")
    print("3 - Realizar depósito")
    print("4 - Realizar saque")
    print("5 - Ver extrato")
    print("6 - Listar clientes e contas")
    print("0 - Sair")
    return input("Escolha uma opção: ")

def main():
    while True:
        opcao = menu()

        if opcao == "1":
            nome = input("Nome: ")
            nascimento = input("Data de nascimento (dd/mm/aaaa): ")
            cpf = input("CPF: ")
            endereco = input("Endereço: ")

            if encontrar_cliente_por_cpf(cpf):
                print("\n@@@ Cliente com este CPF já existe. @@@")
                continue

            cliente = PessoaFisica(nome, nascimento, cpf, endereco)
            clientes.append(cliente)
            print("\n=== Cliente cadastrado com sucesso! ===")

        elif opcao == "2":
            cpf = input("Informe o CPF do cliente: ")
            cliente = encontrar_cliente_por_cpf(cpf)

            if not cliente:
                print("\n@@@ Cliente não encontrado. @@@")
                continue

            numero = len(cliente.contas) + 1
            conta = ContaCorrente.nova_conta(cliente, numero)
            cliente.adicionar_conta(conta)
            print("\n=== Conta criada com sucesso! ===")

        elif opcao in ["3", "4", "5"]:
            cpf = input("Informe o CPF do cliente: ")
            cliente = encontrar_cliente_por_cpf(cpf)

            if not cliente:
                print("\n@@@ Cliente não encontrado. @@@")
                continue

            conta = selecionar_conta(cliente)
            if not conta:
                continue

            if opcao == "3":
                valor = float(input("Valor do depósito: "))
                deposito = Deposito(valor)
                cliente.realizar_transacao(conta, deposito)

            elif opcao == "4":
                valor = float(input("Valor do saque: "))
                saque = Saque(valor)
                cliente.realizar_transacao(conta, saque)

            elif opcao == "5":
                print("\n--- Extrato da Conta ---")
                print(conta)
                if not conta.historico.transacoes:
                    print("Nenhuma transação realizada.")
                else:
                    for transacao in conta.historico.transacoes:
                        print(f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
                    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")

        elif opcao == "6":
            print("\n=== Clientes Cadastrados ===")
            if not clientes:
                print("Nenhum cliente cadastrado.")
                continue
            for cliente in clientes:
                print(f"Nome: {cliente.nome} | CPF: {cliente.cpf}")
                for conta in cliente.contas:
                    print(f"  - Conta {conta.numero} | Agência: {conta.agencia} | Saldo: R$ {conta.saldo:.2f}")

        elif opcao == "0":
            print("Saindo do sistema. Até logo!")
            break

        else:
            print("\n@@@ Opção inválida. Tente novamente. @@@")


if __name__ == "__main__":
    main()
