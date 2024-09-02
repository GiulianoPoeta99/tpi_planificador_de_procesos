from dataclasses import dataclass
from typing import List, Literal

@dataclass
class Proceso:
    id: int
    nombre: str
    tiempo_de_arribo: int
    cantidad_de_rafagas_cpu: int
    duracion_rafaga_cpu: int
    cantidad_de_rafagas_io: int
    duracion_rafaga_io: int
    prioridad: int

@dataclass
class PlanificadorDeProcesos:
    politica: Literal['fcfs', 'rr', 'spn', 'srtn', 'pe']
    procesos: List[Proceso]
    tip: int
    tfp: int
    tcp: int
    quantum: int

@dataclass
class EstadoSistema:
    orden: int
    tarea: Literal['ejecutando_cpu', 'esperando_io', 'esperando_idle', 'ejecutando_tip', 'ejecutando_tcp', 'ejecutando_tfp']
    proceso_id: int = None
    proceso_nombre: str = None

@dataclass
class ProcesoEnEjecucion(Proceso):
    ya_ejecuto_su_tip: bool
    rafaga_cpu_pendiente_en_ejecucion: int
    rafaga_io_pendiente_en_ejecucion: int
    tiempo_servicio: int
    tiempo_espera_listo: int

@dataclass
class ProcesoFinalizado(ProcesoEnEjecucion):
    instante_retorno: int
    tiempo_retorno: int
    tiempo_retorno_normalizado: float

@dataclass
class ResultadoPlanificador:
    historial_estados: List[EstadoSistema]
    procesos_finalizados: List[ProcesoFinalizado]
    tiempo_retorno_tanda: int
    tiempo_medio_retorno_tanda: float
    tiempo_cpu_desocupada: int
    tiempo_cpu_con_so: int