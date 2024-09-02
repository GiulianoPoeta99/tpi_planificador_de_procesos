from interfaces import ProcesoEnEjecucion, EstadoSistema
from typing import List

def ejecutar_un_tick_cpu(proceso: ProcesoEnEjecucion, historial: List[EstadoSistema], unidad_de_tiempo: int):
    proceso.rafaga_cpu_pendiente_en_ejecucion -= 1
    historial.append(EstadoSistema(
        orden=unidad_de_tiempo,
        tarea='ejecutando_cpu',
        proceso_id=proceso.id,
        proceso_nombre=proceso.nombre
    ))

def ejecutar_un_tick_io(proceso: ProcesoEnEjecucion, historial: List[EstadoSistema], unidad_de_tiempo: int):
    proceso.rafaga_io_pendiente_en_ejecucion -= 1
    historial.append(EstadoSistema(
        orden=unidad_de_tiempo - 1,
        tarea='esperando_io',
        proceso_id=proceso.id,
        proceso_nombre=proceso.nombre
    ))

def ejecutar_un_tick_tip(proceso: ProcesoEnEjecucion, historial: List[EstadoSistema], unidad_de_tiempo: int):
    historial.append(EstadoSistema(
        orden=unidad_de_tiempo,
        tarea='ejecutando_tip',
        proceso_id=proceso.id,
        proceso_nombre=proceso.nombre
    ))

def ejecutar_un_tick_tcp(proceso: ProcesoEnEjecucion, historial: List[EstadoSistema], unidad_de_tiempo: int):
    historial.append(EstadoSistema(
        orden=unidad_de_tiempo,
        tarea='ejecutando_tcp',
        proceso_id=proceso.id,
        proceso_nombre=proceso.nombre
    ))

def ejecutar_un_tick_tfp(proceso: ProcesoEnEjecucion, historial: List[EstadoSistema], unidad_de_tiempo: int):
    historial.append(EstadoSistema(
        orden=unidad_de_tiempo,
        tarea='ejecutando_tfp',
        proceso_id=proceso.id,
        proceso_nombre=proceso.nombre
    ))

def ejecutar_un_tick_idle(historial: List[EstadoSistema], unidad_de_tiempo: int):
    historial.append(EstadoSistema(
        orden=unidad_de_tiempo,
        tarea='esperando_idle'
    ))