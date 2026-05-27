from Clases import Cliente  
class Tarjeta:
    def __init__(self, propietario, numero, tipo, cvc):
        self.propietario = propietario
        self.numero = str(numero)
        self.tipo = tipo.strip().title()
        self.cvc = str(cvc)
        self.saldo = 0.0
        self.activa = True

    def activar(self):
        self.activa = True
        return "Tarjeta activada."

    def bloquear(self):
        self.activa = False
        return "Tarjeta bloqueada."

    def puede_pagar(self, monto):
        if not self.activa:
            return False, "La tarjeta está bloqueada."
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."
        tipo = self.tipo.lower()
        if tipo in ("débito", "debito"):
            if monto > self.propietario.disponible:
                return False, "No hay suficiente saldo disponible."
            return True, ""
        if tipo == "crédito":
            disponible_credito = self.propietario.cupo_credito - self.saldo
            if monto > disponible_credito:
                return False, "No hay suficiente cupo de crédito disponible."
            return True, ""
        return False, "Tipo de tarjeta desconocido."

    def realizar_pago(self, monto):
        valido, mensaje = self.puede_pagar(monto)
        if not valido:
            return False, mensaje
        if self.tipo.lower() in ("débito", "debito"):
            self.propietario.disponible -= monto
            return True, "Pago con tarjeta de débito realizado."
        self.saldo += monto
        return True, "Pago con tarjeta de crédito realizado."

    def to_dict(self):
        return {
            "numero": self.numero,
            "tipo": self.tipo,
            "cvc": self.cvc,
            "saldo": self.saldo,
            "activa": self.activa,
        }

    @classmethod
    def from_dict(cls, propietario, data):
        tarjeta = cls(propietario, data["numero"], data["tipo"], data["cvc"])
        tarjeta.saldo = float(data.get("saldo", 0.0))
        tarjeta.activa = bool(data.get("activa", True))
        return tarjeta
