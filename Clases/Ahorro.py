import time

class Ahorro:
    def __init__(self, propietario, nombre, dinero):
        self.propietario = propietario
        self.nombre = nombre
        self.dinero = float(dinero)
        self.tasa = 0.05
        self.ultimo_calculo = time.time()

    def actualizar_interes(self):
        ahora = time.time()
        segundos_transcurridos = ahora - self.ultimo_calculo
        dias_completos = int(segundos_transcurridos // 86400)
        if dias_completos <= 0:
            return

        self.dinero *= (1 + self.tasa) ** dias_completos
        self.ultimo_calculo += dias_completos * 86400

    def depositar(self, monto):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."
        self.actualizar_interes()
        if monto > self.propietario.disponible:
            return False, "No tiene dinero disponible para depositar en el ahorro."
        self.propietario.disponible -= monto
        self.dinero += monto
        return True, "Depósito realizado."

    def retirar(self, monto):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."
        self.actualizar_interes()
        if monto > self.dinero:
            return False, "No tiene suficiente dinero en el ahorro para retirar esa cantidad."
        self.dinero -= monto
        self.propietario.disponible += monto
        return True, "Retiro realizado."

    def consultar_saldo(self):
        self.actualizar_interes()
        return self.dinero

    def incremento_diario(self):
        self.actualizar_interes()
        return self.dinero * (self.tasa / 365)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "dinero": self.dinero,
            "tasa": self.tasa,
            "ultimo_calculo": self.ultimo_calculo,
        }

    @classmethod
    def from_dict(cls, propietario, data):
        ahorro = cls(propietario, data["nombre"], data["dinero"])
        ahorro.tasa = float(data.get("tasa", 0.05))
        ahorro.ultimo_calculo = float(data.get("ultimo_calculo", time.time()))
        return ahorro
