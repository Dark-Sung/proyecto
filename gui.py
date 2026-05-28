import random
import tkinter as tk
from tkinter import messagebox

from Main import (
    ensure_data_files,
    cargar_cliente,
    guardar_cliente,
    load_all_data,
    obtener_ahorro,
    is_valid_documento,
    is_valid_email,
    is_valid_name,
    is_valid_telefono,
)
from Clases import Ahorro, Bolsillo, Cliente, Credito, Tarjeta


def parse_float(text):
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def parse_int(text):
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


def validate_digits(text):
    return text == "" or text.isdigit()


def validate_numeric(text):
    if text == "":
        return True
    if text.count(".") > 1:
        return False
    return all(ch.isdigit() or ch == "." for ch in text)


class BancoGUI:
    def __init__(self, root):
        self.root = root
        root.title("Banco")
        root.geometry("620x480")
        tk.Label(root, text="Banco", font=(None, 14, "bold")).pack(pady=8)
        self.content = tk.Frame(root)
        self.content.pack(fill="both", expand=True, padx=10, pady=6)

        self.show_main_menu()

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_main_menu(self):
        self.clear_content()
        tk.Label(self.content, text="Banco - Menú", font=(None, 14, "bold")).pack(pady=6)
        tk.Button(self.content, text="Registro", width=30, command=self.open_register).pack(pady=6)
        tk.Button(self.content, text="Iniciar sesión", width=30, command=self.open_login).pack(pady=6)
        tk.Button(self.content, text="Salir", width=30, command=self.root.quit).pack(pady=6)

    def open_register(self):
        self.clear_content()
        RegisterWindow(self)

    def open_login(self):
        self.clear_content()
        LoginWindow(self)


class RegisterWindow:
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame(app.content)
        self.frame.pack(fill="both", expand=True)

        labels = [
            "Nombre",
            "Apellidos",
            "Documento",
            "Teléfono",
            "Correo",
            "Contraseña",
            "Saldo inicial",
        ]
        self.entries = {}
        self.name_validator = self.frame.register(self.validate_name_char)
        self.digits_validator = self.frame.register(validate_digits)
        self.numeric_validator = self.frame.register(validate_numeric)
        self.email_validator = self.frame.register(self.validate_email_char)
        for i, label in enumerate(labels):
            tk.Label(self.frame, text=label).grid(row=i, column=0, padx=10, pady=6, sticky="w")
            if label in ("Nombre", "Apellidos"):
                entry = tk.Entry(
                    self.frame,
                    width=35,
                    validate="key",
                    validatecommand=(self.name_validator, "%P"),
                )
            elif label in ("Documento", "Teléfono"):
                entry = tk.Entry(
                    self.frame,
                    width=35,
                    validate="key",
                    validatecommand=(self.digits_validator, "%P"),
                )
            elif label == "Saldo inicial":
                entry = tk.Entry(
                    self.frame,
                    width=35,
                    validate="key",
                    validatecommand=(self.numeric_validator, "%P"),
                )
            elif label == "Correo":
                entry = tk.Entry(
                    self.frame,
                    width=35,
                    validate="key",
                    validatecommand=(self.email_validator, "%P"),
                )
                entry.bind("<KeyRelease>", self.update_create_button_state)
                self.email_entry = entry
            else:
                entry = tk.Entry(self.frame, width=35, show="*" if label == "Contraseña" else "")
            entry.grid(row=i, column=1, padx=10, pady=6)
            self.entries[label] = entry

        self.create_button = tk.Button(self.frame, text="Crear cuenta", width=20, command=self.create_account, state="disabled")
        self.create_button.grid(row=len(labels), column=0, columnspan=2, pady=14)
        tk.Button(self.frame, text="Volver", width=20, command=self.app.show_main_menu).grid(row=len(labels)+1, column=0, columnspan=2)

    def create_account(self):
        datos = load_all_data()
        nombre = self.entries["Nombre"].get().strip()
        apellidos = self.entries["Apellidos"].get().strip()
        documento = self.entries["Documento"].get().strip()
        telefono = self.entries["Teléfono"].get().strip()
        correo = self.entries["Correo"].get().strip()
        contrasena = self.entries["Contraseña"].get()
        saldo_text = self.entries["Saldo inicial"].get().strip() or "0"

        if not nombre or not apellidos or not documento or not telefono or not correo or not contrasena:
            messagebox.showinfo(
                "Aviso",
                "No puede ingresar un valor vacío. Intente de nuevo o escriba 'cancel' para volver.",
            )
            return
        if not is_valid_name(nombre) or not is_valid_name(apellidos):
            messagebox.showinfo(
                "Aviso",
                "Nombre inválido. Use 2-50 caracteres válidos (letras, números, espacios y .,'-).",
            )
            return
        if not is_valid_documento(documento):
            messagebox.showinfo(
                "Aviso",
                "Documento inválido. Debe contener solo dígitos (6-12 dígitos).",
            )
            return
        if documento in datos.get("clientes", {}):
            messagebox.showinfo("Aviso", "Ya existe un cliente con ese documento.")
            return
        if not is_valid_telefono(telefono):
            messagebox.showinfo(
                "Aviso",
                "Teléfono inválido. Use solo dígitos, opcionalmente con '+' y entre 7 y 15 caracteres.",
            )
            return
        if not is_valid_email(correo):
            messagebox.showinfo(
                "Aviso",
                "Correo inválido. Ingrese un correo con formato válido (ej: usuario@dominio.com).",
            )
            return
        if len(contrasena) < 6 or " " in contrasena:
            messagebox.showinfo(
                "Aviso",
                "La contraseña debe tener al menos 6 caracteres y no contener espacios.",
            )
            return

        saldo = parse_float(saldo_text)
        if saldo is None or saldo < 0:
            messagebox.showinfo("Aviso", "Saldo inicial inválido.")
            return

        cliente = Cliente(nombre.title(), apellidos.title(), documento, telefono, correo.lower(), contrasena)
        cliente.disponible = saldo
        cliente.ahorros.append(Ahorro(cliente, "Ahorro principal", 0.0))
        guardar_cliente(cliente, datos)
        messagebox.showinfo("Éxito", "Cliente creado exitosamente.")
        self.app.show_main_menu()

    def validate_name_char(self, value):
        if value == "":
            return True
        return all(char.isalpha() or char.isspace() for char in value)

    def validate_email_char(self, value):
        if value == "":
            return True
        return all(ch.isalnum() or ch in "@._-+" for ch in value)

    def update_create_button_state(self, event=None):
        correo = self.email_entry.get().strip() if hasattr(self, "email_entry") else ""
        if "@" in correo and correo.count("@") == 1 and correo.index("@") not in (0, len(correo) - 1):
            self.create_button.config(state="normal")
        else:
            self.create_button.config(state="disabled")


class LoginWindow:
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame(app.content)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Documento").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        tk.Label(self.frame, text="Contraseña").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.digits_validator = self.frame.register(validate_digits)
        self.doc_ent = tk.Entry(
            self.frame,
            width=35,
            validate="key",
            validatecommand=(self.digits_validator, "%P"),
        )
        self.doc_ent.grid(row=0, column=1, padx=10, pady=8)
        self.pwd_ent = tk.Entry(self.frame, show="*", width=35)
        self.pwd_ent.grid(row=1, column=1, padx=10, pady=8)

        tk.Button(self.frame, text="Ingresar", width=20, command=self.try_login).grid(
            row=2, column=0, columnspan=2, pady=14
        )
        tk.Button(self.frame, text="Volver", width=20, command=self.app.show_main_menu).grid(row=3, column=0, columnspan=2)

    def try_login(self):
        documento = self.doc_ent.get().strip()
        contrasena = self.pwd_ent.get()

        if not documento or not contrasena:
            messagebox.showinfo(
                "Aviso",
                "No puede ingresar un valor vacío. Intente de nuevo o escriba 'cancel' para volver.",
            )
            return
        if not is_valid_documento(documento):
            messagebox.showinfo("Aviso", "Documento inválido. Verifique e intente de nuevo.")
            return

        datos = load_all_data()
        cliente = cargar_cliente(documento, datos)
        if cliente is None:
            messagebox.showinfo("Aviso", "Documento no encontrado.")
            return
        if not cliente.verificar_contrasena(contrasena):
            messagebox.showinfo("Aviso", "Contraseña incorrecta.")
            return

        messagebox.showinfo("Éxito", f"Inicio de sesión exitoso. Bienvenido, {cliente.nombre}")
        self.app.clear_content()
        AccountWindow(self.app, cliente)


class AccountWindow:
    def __init__(self, app, cliente):
        self.app = app
        self.cliente = cliente
        self.datos = load_all_data()
        self.frame = tk.Frame(self.app.content)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.app.content, text=f"Bienvenido, {cliente.nombre} {cliente.apellidos}", font=(None, 12, "bold")).pack(pady=10)
        self.saldo_var = tk.StringVar()
        self.update_balance()
        tk.Label(self.app.content, textvariable=self.saldo_var).pack(pady=6)

        self.content = tk.Frame(self.app.content)
        self.content.pack(fill="both", expand=True, padx=10, pady=6)

        self.top = self.app.root
        self.show_main_menu()

    def update_balance(self):
        self.saldo_var.set(f"Saldo disponible: {self.cliente.disponible:.2f}")

    def refresh(self):
        datos = load_all_data()
        cliente = cargar_cliente(self.cliente.documento, datos)
        if cliente is not None:
            self.cliente = cliente
            self.datos = datos
            self.update_balance()

    def close_session(self):
        messagebox.showinfo("Aviso", "Se cerró sesión.")
        self.app.show_main_menu()

    def open_tarjetas(self):
        self.clear_content()
        TarjetasWindow(self)

    def open_bolsillos(self):
        self.clear_content()
        BolsillosWindow(self)

    def open_creditos(self):
        self.clear_content()
        CreditosWindow(self)

    def open_ahorros(self):
        self.clear_content()
        AhorrosWindow(self)

    def depositar_dinero(self):
        ventana = MontoWindow(self.top, "Ingrese el monto a depositar en su cuenta:")
        self.top.wait_window(ventana.top)
        if ventana.result is None:
            return
        monto = ventana.result
        if monto <= 0:
            messagebox.showinfo("Aviso", "El monto debe ser mayor que cero.")
            return
        self.cliente.disponible += monto
        guardar_cliente(self.cliente, self.datos)
        self.refresh()
        messagebox.showinfo(
            "Éxito",
            f"Depósito de {monto:.2f} realizado exitosamente. Saldo disponible: {self.cliente.disponible:.2f}",
        )

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_main_menu(self):
        self.clear_content()
        btns = [
            ("Tarjetas", self.open_tarjetas),
            ("Bolsillos", self.open_bolsillos),
            ("Créditos", self.open_creditos),
            ("Ahorros", self.open_ahorros),
            ("Depositar dinero en mi cuenta", self.depositar_dinero),
            ("Transferir dinero a otra cuenta", self.transferir_dinero),
            ("Cerrar sesión", self.close_session),
        ]
        for text, cmd in btns:
            tk.Button(self.content, text=text, width=40, command=cmd).pack(pady=4)

    def transferir_dinero(self):
        ventana = InputWindow(
            self.top,
            "Transferencia",
            ["Ingrese el teléfono del destinatario:", "Ingrese el monto a transferir:"],
        )
        self.top.wait_window(ventana.top)
        if ventana.result is None:
            return
        telefono_destino, monto_text = ventana.result
        if not is_valid_telefono(telefono_destino):
            messagebox.showinfo(
                "Aviso",
                "Teléfono inválido. Use solo dígitos, opcionalmente con '+' y entre 7 y 15 caracteres.",
            )
            return
        monto = parse_float(monto_text)
        if monto is None:
            messagebox.showinfo("Aviso", "Valor inválido. Ingrese un número válido, por ejemplo 123.45.")
            return
        if monto <= 0:
            messagebox.showinfo("Aviso", "El monto debe ser mayor que cero.")
            return

        datos = load_all_data()
        cliente_destino = None
        for doc, cliente_data in datos["clientes"].items():
            if cliente_data.get("telefono") == telefono_destino:
                cliente_destino = cargar_cliente(doc, datos)
                break
        if cliente_destino is None:
            messagebox.showinfo("Aviso", "El número de teléfono no está asociado a una cuenta.")
            return

        confirm = messagebox.askyesno("Confirmación", "¿Desea confirmar la transferencia? (s/n):")
        if not confirm:
            messagebox.showinfo("Aviso", "Transferencia cancelada.")
            return
        if monto > self.cliente.disponible:
            messagebox.showinfo(
                "Aviso",
                "No tiene suficiente saldo disponible para realizar esta transferencia.",
            )
            return

        self.cliente.disponible -= monto
        cliente_destino.disponible += monto
        guardar_cliente(self.cliente, datos)
        guardar_cliente(cliente_destino, datos)
        self.refresh()
        messagebox.showinfo(
            "Éxito",
            f"Transferencia de {monto:.2f} realizada exitosamente.\nSaldo disponible: {self.cliente.disponible:.2f}",
        )


class TarjetasWindow:
    def __init__(self, account_window):
        self.account = account_window
        self.frame = tk.Frame(self.account.content)
        self.frame.pack(fill="both", expand=True)
        self.build()

    def build(self):
        tk.Button(self.frame, text="Crear tarjeta", width=35, command=self.crear_tarjeta).pack(pady=6)
        tk.Button(self.frame, text="Activar tarjeta", width=35, command=self.activar_tarjeta).pack(pady=6)
        tk.Button(self.frame, text="Bloquear tarjeta", width=35, command=self.bloquear_tarjeta).pack(pady=6)
        tk.Button(self.frame, text="Realizar pago con tarjeta", width=35, command=self.realizar_pago).pack(pady=6)
        tk.Button(self.frame, text="Eliminar tarjeta", width=35, command=self.eliminar_tarjeta).pack(pady=6)
        tk.Button(self.frame, text="Volver", width=35, command=self.account.show_main_menu).pack(pady=8)

    def crear_tarjeta(self):
        if len(self.account.cliente.tarjetas) >= self.account.cliente.limit_tarjetas:
            messagebox.showinfo("Aviso", "Ha alcanzado el límite de tarjetas permitidas.")
            return

        tipo = ChoiceWindow(self.account.top, "Tipo de tarjeta", "Seleccione una opción:", ["Débito", "Crédito"]).result
        if tipo is None:
            messagebox.showinfo("Aviso", "Creación de tarjeta cancelada. Volviendo al menú de tarjetas.")
            return

        numero = random.randint(10**15, 10**16 - 1)
        cvc = random.randint(100, 999)
        tarjeta = Tarjeta(self.account.cliente, numero, tipo, cvc)
        self.account.cliente.tarjetas.append(tarjeta)
        guardar_cliente(self.account.cliente, self.account.datos)
        self.account.refresh()
        messagebox.showinfo("Éxito", "Tarjeta creada correctamente.")

    def seleccionar_tarjeta(self):
        if not self.account.cliente.tarjetas:
            messagebox.showinfo("Aviso", "No hay tarjetas creados aún.")
            return None
        labels = [f"{tarjeta.tipo} - {tarjeta.numero}" for tarjeta in self.account.cliente.tarjetas]
        seleccion = SelectionWindow(self.account.top, "Seleccione una tarjeta", labels).result
        if seleccion is None:
            return None
        return self.account.cliente.tarjetas[seleccion]

    def activar_tarjeta(self):
        tarjeta = self.seleccionar_tarjeta()
        if tarjeta is None:
            return
        mensaje = tarjeta.activar()
        guardar_cliente(self.account.cliente, self.account.datos)
        messagebox.showinfo("Aviso", mensaje)

    def bloquear_tarjeta(self):
        tarjeta = self.seleccionar_tarjeta()
        if tarjeta is None:
            return
        mensaje = tarjeta.bloquear()
        guardar_cliente(self.account.cliente, self.account.datos)
        messagebox.showinfo("Aviso", mensaje)

    def realizar_pago(self):
        tarjeta = self.seleccionar_tarjeta()
        if tarjeta is None:
            return
        ventana = MontoWindow(self.account.top, "Ingrese el monto del pago:")
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Pago cancelado.")
            return
        monto = ventana.result
        valido, mensaje = tarjeta.puede_pagar(monto)
        if not valido:
            messagebox.showinfo("Aviso", mensaje)
            return

        if tarjeta.tipo.lower() in ("crédito", "credito"):
            cuotas_text = ChoiceWindow(
                self.account.top,
                "Número de cuotas",
                "Ingrese el número de cuotas (máximo 24):",
                [str(i) for i in range(1, 25)],
            ).result
            if cuotas_text is None:
                messagebox.showinfo("Aviso", "Pago cancelado.")
                return
            cuotas = parse_int(cuotas_text)
            if cuotas is None or cuotas < 1 or cuotas > 24:
                messagebox.showinfo("Aviso", "El número de cuotas debe ser entre 1 y 24.")
                return
            exito, mensaje = tarjeta.realizar_pago(monto)
            messagebox.showinfo("Aviso", mensaje)
            if exito:
                credito = Credito(self.account.cliente, monto, cuotas)
                self.account.cliente.creditos.append(credito)
                guardar_cliente(self.account.cliente, self.account.datos)
                self.account.refresh()
                messagebox.showinfo(
                    "Aviso",
                    f"Crédito creado con {cuotas} cuotas. Deuda total: {credito.deuda:.2f}",
                )
            return
        exito, mensaje = tarjeta.realizar_pago(monto)
        messagebox.showinfo("Aviso", mensaje)
        if exito:
            guardar_cliente(self.account.cliente, self.account.datos)
            self.account.refresh()

    def eliminar_tarjeta(self):
        tarjeta = self.seleccionar_tarjeta()
        if tarjeta is None:
            return
        confirm = messagebox.askyesno(
            "Confirmación",
            f"Confirma eliminar la tarjeta {tarjeta.tipo} {tarjeta.numero}? (s/n):",
        )
        if not confirm:
            messagebox.showinfo("Aviso", "Eliminación cancelada.")
            return
        self.account.cliente.tarjetas.remove(tarjeta)
        guardar_cliente(self.account.cliente, self.account.datos)
        self.account.refresh()
        messagebox.showinfo("Éxito", "Tarjeta eliminada correctamente.")


class BolsillosWindow:
    def __init__(self, account_window):
        self.account = account_window
        self.frame = tk.Frame(self.account.content)
        self.frame.pack(fill="both", expand=True)
        self.build()

    def build(self):
        tk.Button(self.frame, text="Crear bolsillo", width=35, command=self.crear_bolsillo).pack(pady=6)
        tk.Button(self.frame, text="Consultar un bolsillo", width=35, command=self.consultar_bolsillo).pack(pady=6)
        tk.Button(self.frame, text="Volver", width=35, command=self.account.show_main_menu).pack(pady=8)

    def crear_bolsillo(self):
        ventana = CreateBolsilloWindow(self.account.top)
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Creación de bolsillo cancelada. Volviendo al menú de bolsillos.")
            return

        nombre, dinero, color = ventana.result
        if dinero > self.account.cliente.disponible:
            messagebox.showinfo(
                "Aviso",
                "No tiene suficiente dinero disponible; el bolsillo se creará con 0.",
            )
            dinero = 0.0
        else:
            self.account.cliente.disponible -= dinero

        bolsillo = Bolsillo(self.account.cliente, nombre, dinero, color)
        self.account.cliente.bolsillos.append(bolsillo)
        guardar_cliente(self.account.cliente, self.account.datos)
        self.account.refresh()
        messagebox.showinfo("Éxito", "Bolsillo creado correctamente.")

    def seleccionar_bolsillo(self):
        if not self.account.cliente.bolsillos:
            messagebox.showinfo("Aviso", "No hay bolsillos creados aún.")
            return None
        labels = [f"{bolsillo.nombre} ({bolsillo.color})" for bolsillo in self.account.cliente.bolsillos]
        seleccion = SelectionWindow(self.account.top, "Seleccione un bolsillo", labels).result
        if seleccion is None:
            return None
        return self.account.cliente.bolsillos[seleccion]

    def consultar_bolsillo(self):
        bolsillo = self.seleccionar_bolsillo()
        if bolsillo is None:
            return
        self.account.clear_content()
        BolsilloDetailWindow(self.account, bolsillo)


class CreditosWindow:
    def __init__(self, account_window):
        self.account = account_window
        self.frame = tk.Frame(self.account.content)
        self.frame.pack(fill="both", expand=True)
        self.build()

    def build(self):
        tk.Button(self.frame, text="Pagar crédito", width=35, command=self.pagar_credito).pack(pady=6)
        tk.Button(self.frame, text="Cambiar número de cuotas", width=35, command=self.cambiar_cuotas).pack(pady=6)
        tk.Button(self.frame, text="Volver", width=35, command=self.account.show_main_menu).pack(pady=8)

    def seleccionar_credito(self):
        if not self.account.cliente.creditos:
            messagebox.showinfo("Aviso", "No hay créditos creados aún.")
            return None
        labels = [f"Crédito {i + 1} - Deuda {credito.deuda:.2f}" for i, credito in enumerate(self.account.cliente.creditos)]
        seleccion = SelectionWindow(self.account.top, "Seleccione un crédito", labels).result
        if seleccion is None:
            return None
        return self.account.cliente.creditos[seleccion]

    def pagar_credito(self):
        credito = self.seleccionar_credito()
        if credito is None:
            return
        ventana = MontoWindow(self.account.top, "Monto a pagar:")
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Pago cancelado.")
            return
        monto = ventana.result
        exito, mensaje = credito.pagar(monto)
        messagebox.showinfo("Aviso", mensaje)
        if exito:
            guardar_cliente(self.account.cliente, self.account.datos)
            self.account.refresh()

    def cambiar_cuotas(self):
        credito = self.seleccionar_credito()
        if credito is None:
            return
        ventana = MontoWindow(self.account.top, "Ingrese el nuevo número de cuotas (1-24):", integer=True)
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Cambio de cuotas cancelado. Volviendo al menú de créditos.")
            return
        cuotas = ventana.result
        if cuotas < 1 or cuotas > 24:
            messagebox.showinfo("Aviso", "El número de cuotas debe ser entre 1 y 24.")
            return
        credito.cuotas = cuotas
        guardar_cliente(self.account.cliente, self.account.datos)
        self.account.refresh()
        messagebox.showinfo("Éxito", "Número de cuotas actualizado.")


class AhorrosWindow:
    def __init__(self, account_window):
        self.account = account_window
        self.frame = tk.Frame(self.account.content)
        self.frame.pack(fill="both", expand=True)
        self.ahorro = obtener_ahorro(self.account.cliente)
        self.build()

    def build(self):
        self.ahorro.actualizar_interes()
        diario = self.ahorro.incremento_diario()
        tk.Label(self.frame, text=f"Saldo ahorro: {self.ahorro.dinero:.2f}").pack(pady=8)
        tk.Label(self.frame, text=f"Incremento diario: {diario:.2f}").pack(pady=8)
        tk.Button(self.frame, text="Depositar en ahorro", width=35, command=self.depositar).pack(pady=6)
        tk.Button(self.frame, text="Retirar de ahorro", width=35, command=self.retirar).pack(pady=6)
        tk.Button(self.frame, text="Volver", width=35, command=self.account.show_main_menu).pack(pady=8)

    def depositar(self):
        ventana = MontoWindow(self.account.top, "Monto a depositar en ahorro:")
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Depósito cancelado.")
            return
        monto = ventana.result
        exito, mensaje = self.ahorro.depositar(monto)
        messagebox.showinfo("Aviso", mensaje)
        if exito:
            guardar_cliente(self.account.cliente, self.account.datos)
            self.account.refresh()
            self.account.clear_content()
            AhorrosWindow(self.account)

    def retirar(self):
        ventana = MontoWindow(self.account.top, "Monto a retirar del ahorro:")
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Retiro cancelado.")
            return
        monto = ventana.result
        exito, mensaje = self.ahorro.retirar(monto)
        messagebox.showinfo("Aviso", mensaje)
        if exito:
            guardar_cliente(self.account.cliente, self.account.datos)
            self.account.refresh()
            self.account.clear_content()
            AhorrosWindow(self.account)


class InputWindow:
    def __init__(self, master, title, prompts):
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.result = None
        self.entries = []
        for i, prompt in enumerate(prompts):
            tk.Label(self.top, text=prompt).grid(row=i, column=0, sticky="w", padx=10, pady=6)
            entry = tk.Entry(self.top, width=35)
            entry.grid(row=i, column=1, padx=10, pady=6)
            self.entries.append(entry)

        tk.Button(self.top, text="Aceptar", width=20, command=self.on_accept).grid(
            row=len(prompts), column=0, columnspan=2, pady=10
        )
        tk.Button(self.top, text="Cancelar", width=20, command=self.top.destroy).grid(
            row=len(prompts) + 1, column=0, columnspan=2, pady=2
        )

    def on_accept(self):
        values = [entry.get().strip() for entry in self.entries]
        if any(value == "" for value in values):
            messagebox.showinfo(
                "Aviso",
                "No puede ingresar un valor vacío. Intente de nuevo o escriba 'cancel' para volver.",
            )
            return
        self.result = values
        self.top.destroy()


class MontoWindow:
    def __init__(self, master, prompt, integer=False):
        self.top = tk.Toplevel(master)
        self.top.title("Monto")
        self.result = None
        self.integer = integer

        tk.Label(self.top, text=prompt).pack(padx=10, pady=10)
        validator = validate_digits if integer else validate_numeric
        self.value_validator = self.top.register(validator)
        self.entry = tk.Entry(
            self.top,
            width=30,
            validate="key",
            validatecommand=(self.value_validator, "%P"),
        )
        self.entry.pack(padx=10, pady=6)
        tk.Button(self.top, text="Aceptar", width=20, command=self.on_accept).pack(pady=6)
        tk.Button(self.top, text="Cancelar", width=20, command=self.top.destroy).pack()

    def on_accept(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showinfo(
                "Aviso",
                "No puede ingresar un valor vacío. Intente de nuevo o escriba 'cancel' para volver.",
            )
            return
        if self.integer:
            value = parse_int(text)
            if value is None:
                messagebox.showinfo("Aviso", "Valor inválido. Ingrese un número entero válido.")
                return
        else:
            value = parse_float(text)
            if value is None:
                messagebox.showinfo("Aviso", "Valor inválido. Ingrese un número válido, por ejemplo 123.45.")
                return
        self.result = value
        self.top.destroy()


class SelectionWindow:
    def __init__(self, master, title, items):
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.result = None

        tk.Label(self.top, text=title, font=(None, 11, "bold")).pack(pady=8)
        self.listbox = tk.Listbox(self.top, width=60, height=10)
        self.listbox.pack(padx=10, pady=5)
        for item in items:
            self.listbox.insert(tk.END, item)

        tk.Button(self.top, text="Seleccionar", width=20, command=self.on_select).pack(pady=6)
        tk.Button(self.top, text="Cancelar", width=20, command=self.top.destroy).pack()
        self.top.transient(master)
        self.top.grab_set()
        master.wait_window(self.top)

    def on_select(self):
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Selección inválida.")
            return
        self.result = seleccion[0]
        self.top.destroy()


class ChoiceWindow:
    def __init__(self, master, title, prompt, options):
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.result = None

        tk.Label(self.top, text=prompt).pack(padx=10, pady=10)
        self.var = tk.StringVar(value=options[0])
        for option in options:
            tk.Radiobutton(self.top, text=option, variable=self.var, value=option).pack(anchor="w", padx=20)

        tk.Button(self.top, text="Aceptar", width=20, command=self.on_accept).pack(pady=10)
        tk.Button(self.top, text="Cancelar", width=20, command=self.top.destroy).pack()
        self.top.transient(master)
        self.top.grab_set()
        master.wait_window(self.top)

    def on_accept(self):
        self.result = self.var.get()
        self.top.destroy()


class CreateBolsilloWindow:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Crear bolsillo")
        self.top.geometry("420x240")
        self.result = None

        tk.Label(self.top, text="Nombre del bolsillo:").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.nombre = tk.Entry(self.top, width=35)
        self.nombre.grid(row=0, column=1, padx=10, pady=6)

        tk.Label(self.top, text="Dinero inicial:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.money_validator = self.top.register(validate_numeric)
        self.dinero = tk.Entry(
            self.top,
            width=35,
            validate="key",
            validatecommand=(self.money_validator, "%P"),
        )
        self.dinero.grid(row=1, column=1, padx=10, pady=6)

        tk.Label(self.top, text="Color del bolsillo:").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        self.color_var = tk.StringVar(value="Rojo")
        opciones = ["Rojo", "Azul", "Verde", "Amarillo", "Negro"]
        self.color_menu = tk.OptionMenu(self.top, self.color_var, *opciones)
        self.color_menu.grid(row=2, column=1, padx=10, pady=6, sticky="w")

        tk.Button(self.top, text="Crear", width=20, command=self.on_create).grid(row=3, column=0, columnspan=2, pady=12)
        tk.Button(self.top, text="Cancelar", width=20, command=self.top.destroy).grid(row=4, column=0, columnspan=2)

    def on_create(self):
        nombre = self.nombre.get().strip()
        dinero_text = self.dinero.get().strip()
        if not nombre or not dinero_text:
            messagebox.showinfo(
                "Aviso",
                "No puede ingresar un valor vacío. Intente de nuevo o escriba 'cancel' para volver.",
            )
            return
        dinero = parse_float(dinero_text)
        if dinero is None:
            messagebox.showinfo("Aviso", "Valor inválido. Ingrese un número válido, por ejemplo 123.45.")
            return
        if dinero < 0:
            messagebox.showinfo("Aviso", "El valor no puede ser negativo.")
            return
        self.result = (nombre, dinero, self.color_var.get())
        self.top.destroy()


class BolsilloDetailWindow:
    def __init__(self, account_window, bolsillo):
        self.account = account_window
        self.bolsillo = bolsillo
        self.frame = tk.Frame(self.account.content)
        self.frame.pack(fill="both", expand=True)

        color_map = {"Rojo": "red", "Azul": "blue", "Verde": "green", "Amarillo": "yellow", "Negro": "black"}
        color_name = color_map.get(bolsillo.color, bolsillo.color.lower())
        fg = "white" if color_name not in ("yellow",) else "black"
        tk.Label(self.frame, text=f"Bolsillo: {bolsillo.nombre} ({bolsillo.color})", font=(None, 11, "bold"), bg=color_name, fg=fg).pack(fill="x", pady=10)

        self.saldo_var = tk.StringVar(value=f"Saldo: {bolsillo.dinero:.2f}")
        tk.Label(self.frame, textvariable=self.saldo_var).pack(pady=4)
        tk.Button(self.frame, text="Depositar en el bolsillo", width=35, command=self.depositar).pack(pady=6)
        tk.Button(self.frame, text="Retirar del bolsillo", width=35, command=self.retirar).pack(pady=6)
        tk.Button(self.frame, text="Volver", width=35, command=self.account.show_main_menu).pack(pady=8)

    def depositar(self):
        ventana = MontoWindow(self.account.top, "Ingrese el monto a depositar:")
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Depósito cancelado.")
            return
        monto = ventana.result
        exito, mensaje = self.bolsillo.depositar(monto)
        messagebox.showinfo("Aviso", mensaje)
        if exito:
            guardar_cliente(self.account.cliente, self.account.datos)
            self.account.refresh()
            self.saldo_var.set(f"Saldo: {self.bolsillo.dinero:.2f}")

    def retirar(self):
        ventana = MontoWindow(self.account.top, "Ingrese el monto a retirar:")
        self.account.top.wait_window(ventana.top)
        if ventana.result is None:
            messagebox.showinfo("Aviso", "Retiro cancelado.")
            return
        monto = ventana.result
        exito, mensaje = self.bolsillo.retirar(monto)
        messagebox.showinfo("Aviso", mensaje)
        if exito:
            guardar_cliente(self.account.cliente, self.account.datos)
            self.account.refresh()
            self.saldo_var.set(f"Saldo: {self.bolsillo.dinero:.2f}")


def main():
    ensure_data_files()
    root = tk.Tk()
    app = BancoGUI(root)
    root.mainloop()

main()