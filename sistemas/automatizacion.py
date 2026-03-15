from sistemas.tareas import TipoTarea


class SistemaAutomatizacion:
    def decidir_tarea(self, pinguino, colonia) -> TipoTarea:
        if pinguino.energia < 20:
            return TipoTarea.VOLVER_BASE

        if pinguino.inventario["pez"] >= pinguino.capacidad_inventario:
            return TipoTarea.VOLVER_BASE

        return TipoTarea.PESCAR