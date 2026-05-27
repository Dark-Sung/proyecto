class Credito:
    def __init__(self, propietario, monto, cuotas):
        self.propietario = propietario
        self.capital = float(monto)
        self.cuotas = int(cuotas)
        self.interes = 0.08
        self.deuda = self.capital * (1 + self.interes)
        self.pago_total = 0.0

    def cuota(self):
        if self.cuotas <= 0:
            return 0.0
        return self.deuda / self.cuotas

    def pagar(self, monto):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."
        if monto > self.propietario.disponible:
            return False, "No tiene dinero disponible para pagar el crédito."
        pago = min(monto, self.deuda)
        self.propietario.disponible -= pago
        self.deuda -= pago
        self.pago_total += pago
        if self.deuda <= 0:
            self.deuda = 0.0
            return True, "Crédito completamente pagado."
        return True, f"Pago realizado. Deuda restante: {self.deuda:.2f}"

    def consultar_deuda(self):
        return self.deuda

    def to_dict(self):
        return {
            "capital": self.capital,
            "cuotas": self.cuotas,
            "interes": self.interes,
            "deuda": self.deuda,
            "pago_total": self.pago_total,
        }

    @classmethod
    def from_dict(cls, propietario, data):
        credito = cls(propietario, data["capital"], data["cuotas"])
        credito.interes = float(data.get("interes", 0.08))
        credito.deuda = float(data.get("deuda", credito.deuda))
        credito.pago_total = float(data.get("pago_total", 0.0))
        return credito
