class Cliente:
    def __init__(self, nombre, apellidos, documento, telefono, correo, contrasena):
        self.nombre = nombre
        self.apellidos = apellidos
        self.documento = documento
        self.telefono = telefono
        self.correo = correo
        self.contrasena = contrasena
        self.disponible = 0.0
        self.cupo_credito = 500000.0
        self.limit_tarjetas = 2
        self.tarjetas = []
        self.bolsillos = []
        self.creditos = []
        self.ahorros = []

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "documento": self.documento,
            "telefono": self.telefono,
            "correo": self.correo,
            "contrasena": self.contrasena,
            "disponible": self.disponible,
            "cupo_credito": self.cupo_credito,
        }

    @classmethod
    def from_dict(cls, data):
        cliente = cls(
            data["nombre"],
            data["apellidos"],
            data["documento"],
            data["telefono"],
            data["correo"],
            data.get("contrasena", ""),
        )
        cliente.disponible = float(data.get("disponible", 0.0))
        cliente.cupo_credito = float(data.get("cupo_credito", 500000.0))
        return cliente

    def verificar_contrasena(self, contrasena):
        return self.contrasena == contrasena

    def consultar_saldo_total(self):
        total = self.disponible
        total += sum(b.dinero for b in self.bolsillos)
        total += sum(a.dinero for a in self.ahorros)
        return total
