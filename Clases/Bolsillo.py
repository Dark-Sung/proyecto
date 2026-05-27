class Bolsillo:
    def __init__(self, propietario, nombre, dinero, color):
        self.propietario = propietario
        self.nombre = nombre
        self.dinero = float(dinero)
        self.color = color

    def depositar(self, monto):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."
        if monto > self.propietario.disponible:
            return False, "No tiene dinero disponible para depositar en el bolsillo."
        self.dinero += monto
        self.propietario.disponible -= monto
        return True, "Depósito realizado."

    def retirar(self, monto):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."
        if monto > self.dinero:
            return False, "No tiene suficiente dinero en el bolsillo para retirar esa cantidad."
        self.dinero -= monto
        self.propietario.disponible += monto
        return True, "Retiro realizado."

    def consultar_saldo(self):
        return self.dinero

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "dinero": self.dinero,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, propietario, data):
        return cls(propietario, data["nombre"], data["dinero"], data["color"])
