import json
from pathlib import Path
from Clases import Cliente, Ahorro, Bolsillo, Credito, Tarjeta
import random

BASE_DIR = Path(__file__).parent
DATA_FILES = {
    "clientes": BASE_DIR / "Datos" / "clientes.json",
    "tarjetas": BASE_DIR / "Datos" / "tarjetas.json",
    "bolsillos": BASE_DIR / "Datos" / "bolsillos.json",
    "creditos": BASE_DIR / "Datos" / "creditos.json",
    "ahorros": BASE_DIR / "Datos" / "ahorros.json",
}

class CancelOperation(Exception):
    pass


def ensure_data_files():
    for path in DATA_FILES.values():
        if not path.exists():
            path.write_text("{}", encoding="utf-8")


def load_json(key):
    path = DATA_FILES[key]
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_json(key, data):
    path = DATA_FILES[key]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_all_data():
    return {
        key: load_json(key)
        for key in DATA_FILES
    }


def cargar_cliente(documento, datos):
    if documento not in datos["clientes"]:
        return None
    cliente = Cliente.from_dict(datos["clientes"][documento])
    for tarjeta_data in datos["tarjetas"].get(documento, []):
        cliente.tarjetas.append(Tarjeta.from_dict(cliente, tarjeta_data))
    for bolsillo_data in datos["bolsillos"].get(documento, []):
        cliente.bolsillos.append(Bolsillo.from_dict(cliente, bolsillo_data))
    for credito_data in datos["creditos"].get(documento, []):
        cliente.creditos.append(Credito.from_dict(cliente, credito_data))
    for ahorro_data in datos["ahorros"].get(documento, []):
        cliente.ahorros.append(Ahorro.from_dict(cliente, ahorro_data))
    if not cliente.ahorros:
        cliente.ahorros.append(Ahorro(cliente, "Ahorro principal", 0.0))
    return cliente


def obtener_ahorro(cliente):
    if not cliente.ahorros:
        cliente.ahorros.append(Ahorro(cliente, "Ahorro principal", 0.0))
    return cliente.ahorros[0]


def guardar_cliente(cliente, datos):
    documento = cliente.documento
    datos["clientes"][documento] = cliente.to_dict()
    datos["tarjetas"][documento] = [tarjeta.to_dict() for tarjeta in cliente.tarjetas]
    datos["bolsillos"][documento] = [bolsillo.to_dict() for bolsillo in cliente.bolsillos]
    datos["creditos"][documento] = [credito.to_dict() for credito in cliente.creditos]
    ahorro = obtener_ahorro(cliente)
    datos["ahorros"][documento] = [ahorro.to_dict()]
    for key, value in datos.items():
        save_json(key, value)


def input_nonempty(prompt):
    while True:
        valor = input(prompt).strip()
        if valor.lower() in ("cancel", "skip"):
            raise CancelOperation()
        if valor == "":
            print("No puede ingresar un valor vacío. Intente de nuevo o escriba 'cancel' para volver.")
            continue
        return valor


# Validadores estrictos y versiones con rango de los inputs
import re


def input_float(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = float(input_nonempty(prompt))
        except ValueError:
            print("Valor inválido. Ingrese un número válido, por ejemplo 123.45.")
            continue
        if min_val is not None and val < min_val:
            print(f"El valor debe ser mayor o igual a {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"El valor debe ser menor o igual a {max_val}.")
            continue
        return val


def input_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input_nonempty(prompt))
        except ValueError:
            print("Valor inválido. Ingrese un número entero válido.")
            continue
        if min_val is not None and val < min_val:
            print(f"El valor debe ser mayor o igual a {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"El valor debe ser menor o igual a {max_val}.")
            continue
        return val


# Validadores para nombre, documento, teléfono, correo y contraseña
def is_valid_name(name: str) -> bool:
    return re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$", name) is not None


def input_name(prompt):
    while True:
        try:
            nombre = input_nonempty(prompt)
        except CancelOperation:
            raise
        if not is_valid_name(nombre):
            print("Nombre inválido. Use 2-50 caracteres válidos (letras, números, espacios y .,'-).")
            continue
        return nombre.strip().title()


def is_valid_documento(doc: str) -> bool:
    return re.match(r"^\d{6,12}$", doc) is not None


def input_documento(prompt, datos=None):
    while True:
        try:
            doc = input_nonempty(prompt)
        except CancelOperation:
            raise
        if not is_valid_documento(doc):
            print("Documento inválido. Debe contener solo dígitos (6-12 dígitos).")
            continue
        if datos and doc in datos.get("clientes", {}):
            print("Ya existe un cliente con ese documento.")
            continue
        return doc


def is_valid_telefono(tel: str) -> bool:
    return re.match(r"^\+?\d{7,15}$", tel) is not None


def input_telefono(prompt, datos=None, allow_existing=False):
    while True:
        try:
            tel = input_nonempty(prompt)
        except CancelOperation:
            raise
        if not is_valid_telefono(tel):
            print("Teléfono inválido. Use solo dígitos, opcionalmente con '+' y entre 7 y 15 caracteres.")
            continue
        if datos and not allow_existing:
            for doc, cliente_data in datos.get("clientes", {}).items():
                if cliente_data.get("telefono") == tel:
                    print("El teléfono ya está asociado a otro cliente.")
                    tel = None
                    break
            if tel is None:
                continue
        return tel


def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email) is not None


def input_email(prompt):
    while True:
        try:
            correo = input_nonempty(prompt)
        except CancelOperation:
            raise
        if not is_valid_email(correo):
            print("Correo inválido. Ingrese un correo con formato válido (ej: usuario@dominio.com).")
            continue
        return correo.lower()


def input_password(prompt, min_length=6):
    while True:
        try:
            pwd = input_nonempty(prompt)
        except CancelOperation:
            raise
        if len(pwd) < min_length or " " in pwd:
            print(f"La contraseña debe tener al menos {min_length} caracteres y no contener espacios.")
            continue
        return pwd


def seleccionar_item(items, describe):
    if not items:
        print(f"No hay {describe} creados aún.")
        return None
    for index, item in enumerate(items, start=1):
        if hasattr(item, "tipo"):
            label = f"{item.tipo} - {item.numero}"
        elif hasattr(item, "nombre"):
            label = item.nombre
        elif hasattr(item, "capital"):
            label = f"Crédito {index} - Deuda {item.deuda:.2f}"
        else:
            label = str(item)
        print(f"{index}. {label}")
    try:
        seleccion = input_int("Seleccione un número: ")
    except CancelOperation:
        return None
    if 1 <= seleccion <= len(items):
        return seleccion - 1
    print("Selección inválida.")
    return None


def crear_tarjeta(cliente, datos):
    if len(cliente.tarjetas) >= cliente.limit_tarjetas:
        print("Ha alcanzado el límite de tarjetas permitidas.")
        return
    try:
        opciones = {"1": "Débito", "2": "Crédito"}
        while True:
            eleccion = input_nonempty("Tipo de tarjeta:\n1. Débito\n2. Crédito\nSeleccione una opción: ")
            if eleccion in opciones:
                tipo = opciones[eleccion]
                break
            print("Opción no válida.")
    except CancelOperation:
        print("Creación de tarjeta cancelada. Volviendo al menú de tarjetas.")
        return
    numero = random.randint(10**15, 10**16 - 1)
    cvc = random.randint(100, 999)
    tarjeta = Tarjeta(cliente, numero, tipo, cvc)
    cliente.tarjetas.append(tarjeta)
    guardar_cliente(cliente, datos)
    print("Tarjeta creada correctamente.")


def gestionar_tarjetas(cliente, datos):
    while True:
        print("\n--- Menú de Tarjetas ---")
        print("1. Crear tarjeta")
        print("2. Activar tarjeta")
        print("3. Bloquear tarjeta")
        print("4. Realizar pago con tarjeta")
        print("5. Eliminar tarjeta")
        print("6. Volver")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú anterior.")
            break
        if opcion == "1":
            crear_tarjeta(cliente, datos)
        elif opcion == "2":
            indice = seleccionar_item(cliente.tarjetas, "tarjetas")
            if indice is not None:
                print(cliente.tarjetas[indice].activar())
                guardar_cliente(cliente, datos)
        elif opcion == "3":
            indice = seleccionar_item(cliente.tarjetas, "tarjetas")
            if indice is not None:
                print(cliente.tarjetas[indice].bloquear())
                guardar_cliente(cliente, datos)
        elif opcion == "4":
            indice = seleccionar_item(cliente.tarjetas, "tarjetas")
            if indice is not None:
                tarjeta = cliente.tarjetas[indice]
                try:
                    monto = input_float("Ingrese el monto del pago: ", min_val=0.01)
                except CancelOperation:
                    print("Pago cancelado.")
                    continue
                valido, mensaje = tarjeta.puede_pagar(monto)
                if not valido:
                    print(mensaje)
                    continue
                if tarjeta.tipo.lower() in ("crédito", "credito"):
                    try:
                        cuotas = input_int("Ingrese el número de cuotas (1-24): ", min_val=1, max_val=24)
                    except CancelOperation:
                        print("Pago cancelado.")
                        continue
                    exito, mensaje = tarjeta.realizar_pago(monto)
                    print(mensaje)
                    if exito:
                        credito = Credito(cliente, monto, cuotas)
                        cliente.creditos.append(credito)
                        guardar_cliente(cliente, datos)
                        print(f"Crédito creado con {cuotas} cuotas. Deuda total: {credito.deuda:.2f}")
                else:
                    exito, mensaje = tarjeta.realizar_pago(monto)
                    print(mensaje)
                    if exito:
                        guardar_cliente(cliente, datos)
        elif opcion == "5":
            indice = seleccionar_item(cliente.tarjetas, "tarjetas")
            if indice is not None:
                tarjeta = cliente.tarjetas[indice]
                try:
                    confirmacion = input_nonempty(f"Confirma eliminar la tarjeta {tarjeta.tipo} {tarjeta.numero}? (s/n): ").lower()
                except CancelOperation:
                    print("Operación cancelada.")
                    continue
                if confirmacion == "s":
                    cliente.tarjetas.pop(indice)
                    guardar_cliente(cliente, datos)
                    print("Tarjeta eliminada correctamente.")
                else:
                    print("Eliminación cancelada.")
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")


def crear_bolsillo(cliente, datos):
    try:
        nombre = input_name("Nombre del bolsillo: ")
        dinero = input_float("Dinero inicial: ", min_val=0)
        if dinero > cliente.disponible:
            print("No tiene suficiente dinero disponible; el bolsillo se creará con 0.")
            dinero = 0.0
        else:
            cliente.disponible -= dinero
        color_opciones = {"1": "Rojo", "2": "Azul", "3": "Verde", "4": "Amarillo", "5": "Negro"}
        while True:
            color = input_nonempty("Color del bolsillo:\n1. Rojo\n2. Azul\n3. Verde\n4. Amarillo\n5. Negro\nSeleccione una opción: ")
            if color in color_opciones:
                color = color_opciones[color]
                break
            print("Opción no válida.")
    except CancelOperation:
        print("Creación de bolsillo cancelada. Volviendo al menú de bolsillos.")
        return
    bolsillo = Bolsillo(cliente, nombre, dinero, color)
    cliente.bolsillos.append(bolsillo)
    guardar_cliente(cliente, datos)
    print("Bolsillo creado correctamente.")


def gestionar_bolsillo_individual(cliente, datos, indice):
    bolsillo = cliente.bolsillos[indice]
    while True:
        print(f"\n--- Bolsillo: {bolsillo.nombre} ({bolsillo.color}) ---")
        print(f"Saldo: {bolsillo.dinero:.2f}")
        print("1. Depositar en el bolsillo")
        print("2. Retirar del bolsillo")
        print("3. Volver")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú de bolsillos.")
            break
        if opcion == "1":
            try:
                monto = input_float("Ingrese el monto a depositar: ", min_val=0.01)
            except CancelOperation:
                print("Depósito cancelado.")
                continue
            exito, mensaje = bolsillo.depositar(monto)
            print(mensaje)
            if exito:
                guardar_cliente(cliente, datos)
        elif opcion == "2":
            try:
                monto = input_float("Ingrese el monto a retirar: ", min_val=0.01)
            except CancelOperation:
                print("Retiro cancelado.")
                continue
            exito, mensaje = bolsillo.retirar(monto)
            print(mensaje)
            if exito:
                guardar_cliente(cliente, datos)
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")


def gestionar_bolsillos(cliente, datos):
    while True:
        print("\n--- Menú de Bolsillos ---")
        print("1. Crear bolsillo")
        print("2. Consultar un bolsillo")
        print("3. Volver")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú anterior.")
            break
        if opcion == "1":
            crear_bolsillo(cliente, datos)
        elif opcion == "2":
            indice = seleccionar_item(cliente.bolsillos, "bolsillos")
            if indice is not None:
                gestionar_bolsillo_individual(cliente, datos, indice)
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")


def cambiar_cuotas_credito(cliente, datos):
    indice = seleccionar_item(cliente.creditos, "créditos")
    if indice is None:
        return
    credito = cliente.creditos[indice]
    print(f"Cuotas actuales: {credito.cuotas}")
    try:
        cuotas = input_int("Ingrese el nuevo número de cuotas (1-24): ", min_val=1, max_val=24)
    except CancelOperation:
        print("Cambio de cuotas cancelado. Volviendo al menú de créditos.")
        return
    credito.cuotas = cuotas
    guardar_cliente(cliente, datos)
    print("Número de cuotas actualizado.")


def gestionar_creditos(cliente, datos):
    while True:
        total_deuda = sum(credito.deuda for credito in cliente.creditos)
        print("\n+-----------------------------+")
        print(f"| Deuda total: {total_deuda:10.2f}     |")
        print("+-----------------------------+")
        print("1. Pagar crédito")
        print("2. Cambiar número de cuotas")
        print("3. Volver")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú anterior.")
            break
        if opcion == "1":
            indice = seleccionar_item(cliente.creditos, "créditos")
            if indice is not None:
                try:
                    monto = input_float("Monto a pagar: ", min_val=0.01)
                except CancelOperation:
                    print("Pago cancelado.")
                    continue
                exito, mensaje = cliente.creditos[indice].pagar(monto)
                print(mensaje)
                if exito:
                    guardar_cliente(cliente, datos)
        elif opcion == "2":
            cambiar_cuotas_credito(cliente, datos)
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")


def crear_ahorro(cliente, datos):
    nombre = input_name("Nombre del ahorro: ")
    dinero = input_float("Dinero inicial: ", min_val=0)
    if dinero > cliente.disponible:
        print("No tiene suficiente saldo disponible; el ahorro se creará con 0.")
        dinero = 0.0
    else:
        cliente.disponible -= dinero
    ahorro = Ahorro(cliente, nombre, dinero)
    cliente.ahorros.append(ahorro)
    guardar_cliente(cliente, datos)
    print("Ahorro creado correctamente.")


def gestionar_ahorros(cliente, datos):
    ahorro = obtener_ahorro(cliente)
    while True:
        ahorro.actualizar_interes()
        diario = ahorro.incremento_diario()
        print("\n+---------------------------------------------+")
        print(f"| Saldo ahorro: {ahorro.dinero:12.2f}                  |")
        print(f"| Incremento diario: {diario:9.2f}                |")
        print("+---------------------------------------------+")
        print("1. Depositar en ahorro")
        print("2. Retirar de ahorro")
        print("3. Volver")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú anterior.")
            break
        if opcion == "1":
            try:
                monto = input_float("Monto a depositar en ahorro: ", min_val=0.01)
            except CancelOperation:
                print("Depósito cancelado.")
                continue
            exito, mensaje = ahorro.depositar(monto)
            print(mensaje)
            if exito:
                guardar_cliente(cliente, datos)
        elif opcion == "2":
            try:
                monto = input_float("Monto a retirar del ahorro: ", min_val=0.01)
            except CancelOperation:
                print("Retiro cancelado.")
                continue
            exito, mensaje = ahorro.retirar(monto)
            print(mensaje)
            if exito:
                guardar_cliente(cliente, datos)
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")


def depositar_dinero(cliente, datos):
    try:
        monto = input_float("Ingrese el monto a depositar en su cuenta: ", min_val=0.01)
        cliente.disponible += monto
        guardar_cliente(cliente, datos)
        print(f"Depósito de {monto:.2f} realizado exitosamente. Saldo disponible: {cliente.disponible:.2f}")
    except CancelOperation:
        print("Depósito cancelado.")


def transferir_dinero(cliente, datos):
    try:
        telefono_destino = input_telefono("Ingrese el teléfono del destinatario: ", datos=None, allow_existing=True)
        cliente_destino = None
        for doc, cliente_data in datos["clientes"].items():
            if cliente_data["telefono"] == telefono_destino:
                cliente_destino = cargar_cliente(doc, datos)
                break
        if cliente_destino is None:
            print("El número de teléfono no está asociado a una cuenta.")
            return
        print(f"\n--- Confirmación de Transferencia ---")
        print(f"Destinatario: {cliente_destino.nombre} {cliente_destino.apellidos}")
        print(f"Teléfono: {cliente_destino.telefono}")
        monto = input_float("Ingrese el monto a transferir: ", min_val=0.01)
        if monto <= 0:
            print("El monto debe ser mayor que cero.")
            return
        if monto > cliente.disponible:
            print("No tiene suficiente saldo disponible para realizar esta transferencia.")
            return
        confirmacion = input_nonempty("¿Desea confirmar la transferencia? (s/n): ").lower()
        if confirmacion != "s":
            print("Transferencia cancelada.")
            return
        cliente.disponible -= monto
        cliente_destino.disponible += monto
        guardar_cliente(cliente, datos)
        guardar_cliente(cliente_destino, datos)
        print(f"Transferencia de {monto:.2f} realizada exitosamente.")
        print(f"Saldo disponible: {cliente.disponible:.2f}")
    except CancelOperation:
        print("Transferencia cancelada.")


def menu_cliente(cliente, datos):
    while True:
        disponible = cliente.disponible
        print(f"\nBienvenido, {cliente.nombre} {cliente.apellidos}")
        print("+-------------------------------------------+")
        print(f"| Saldo disponible: {disponible:10.2f}              |")
        print("+-------------------------------------------+")
        print("1. Tarjetas")
        print("2. Bolsillos")
        print("3. Créditos")
        print("4. Ahorros")
        print("5. Depositar dinero en mi cuenta")
        print("6. Transferir dinero a otra cuenta")
        print("7. Cerrar sesión")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú principal.")
            break
        if opcion == "1":
            gestionar_tarjetas(cliente, datos)
        elif opcion == "2":
            gestionar_bolsillos(cliente, datos)
        elif opcion == "3":
            gestionar_creditos(cliente, datos)
        elif opcion == "4":
            gestionar_ahorros(cliente, datos)
        elif opcion == "5":
            depositar_dinero(cliente, datos)
        elif opcion == "6":
            transferir_dinero(cliente, datos)
        elif opcion == "7":
            print("Se cerró sesión.")
            break
        else:
            print("Opción no válida.")


def crear_cliente(datos):
    try:
        nombre = input_name("Ingrese el nombre del cliente: ")
        apellidos = input_name("Ingrese los apellidos del cliente: ")
        documento = input_documento("Ingrese el documento del cliente: ", datos)
        telefono = input_telefono("Ingrese el teléfono del cliente: ", datos, allow_existing=False)
        correo = input_email("Ingrese el correo del cliente: ")
        contrasena = input_password("Ingrese una contraseña para la cuenta: ")
        cliente = Cliente(nombre, apellidos, documento, telefono, correo, contrasena)
        cliente.disponible = input_float("Ingrese el dinero disponible para el cliente: ", min_val=0)
        cliente.ahorros.append(Ahorro(cliente, "Ahorro principal", 0.0))
        guardar_cliente(cliente, datos)
        print("Cliente creado exitosamente.")
    except CancelOperation:
        print("Creación de cliente cancelada. Volviendo al menú principal.")


def iniciar_sesion(datos):
    try:
        documento = input_nonempty("Ingrese el documento del cliente para iniciar sesión: ")
        if not is_valid_documento(documento):
            print("Documento inválido. Verifique e intente de nuevo.")
            return
        cliente = cargar_cliente(documento, datos)
        if cliente is None:
            print("Documento no encontrado.")
            return
        contrasena = input_password("Ingrese su contraseña: ")
        if not cliente.verificar_contrasena(contrasena):
            print("Contraseña incorrecta.")
            return
        print(f"Inicio de sesión exitoso. Bienvenido, {cliente.nombre}")
        menu_cliente(cliente, datos)
    except CancelOperation:
        print("Inicio de sesión cancelado. Volviendo al menú principal.")


def main():
    ensure_data_files()
    datos = load_all_data()
    while True:
        print("\n--- Banco Básico ---")
        print("1. Registro")
        print("2. Iniciar sesión")
        print("3. Salir")
        try:
            opcion = input_nonempty("Seleccione una opción: ")
        except CancelOperation:
            print("Operación cancelada. Volviendo al menú principal.")
            continue
        if opcion == "1":
            crear_cliente(datos)
        elif opcion == "2":
            iniciar_sesion(datos)
        elif opcion == "3":
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
