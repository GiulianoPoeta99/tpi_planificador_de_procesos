from typing import List
from interfaces import PlanificadorDeProcesos, ProcesoEnEjecucion, ProcesoFinalizado, ResultadoPlanificador, Proceso, EstadoSistema
from executors.ejecutor_base import EjecutorProcesosStrategy
from common import ejecutar_un_tick_cpu, ejecutar_un_tick_idle, ejecutar_un_tick_io, ejecutar_un_tick_tcp, ejecutar_un_tick_tfp, ejecutar_un_tick_tip

class EjecutorRR(EjecutorProcesosStrategy):
    def __init__(self, planificador: PlanificadorDeProcesos):
        super().__init__(planificador)
        self.unidad_de_tiempo = 0
        self.cola_listos: List[ProcesoEnEjecucion] = []
        self.cola_bloqueados_por_io: List[ProcesoEnEjecucion] = []
        self.ultimo_proceso_ejecutado_id = -1
        self.resultado = ResultadoPlanificador(
            historial_estados=[],
            procesos_finalizados=[],
            tiempo_retorno_tanda=0,
            tiempo_medio_retorno_tanda=0,
            tiempo_cpu_desocupada=0,
            tiempo_cpu_con_so=0
        )
        self.quantum_counter = 1
        self.actualizar_cola_bloqueados_por_io()
        self.actualizar_cola_listos()

    def avanzar_una_unidad_de_tiempo(self):
        self.unidad_de_tiempo += 1

    def actualizar_cola_listos(self):
        for proceso in self.planificador.procesos:
            if proceso.tiempo_de_arribo == self.unidad_de_tiempo:
                self.cola_listos.append(ProcesoEnEjecucion(
                    **proceso.__dict__,
                    ya_ejecuto_su_tip=self.planificador.tip == 0,
                    rafaga_cpu_pendiente_en_ejecucion=proceso.duracion_rafaga_cpu,
                    rafaga_io_pendiente_en_ejecucion=proceso.duracion_rafaga_io,
                    tiempo_servicio=0,
                    tiempo_espera_listo=0,
                    cantidad_de_rafagas_cpu=proceso.cantidad_de_rafagas_cpu - 1 if proceso.cantidad_de_rafagas_cpu > 0 else 0
                ))

    def actualizar_cola_bloqueados_por_io(self):
        procesos_bloqueados_revisados = 0
        while procesos_bloqueados_revisados < len(self.cola_bloqueados_por_io):
            proceso = self.cola_bloqueados_por_io[procesos_bloqueados_revisados]
            if proceso.rafaga_io_pendiente_en_ejecucion > 0:
                ejecutar_un_tick_io(proceso, self.resultado.historial_estados, self.unidad_de_tiempo)

            if proceso.rafaga_io_pendiente_en_ejecucion == 0:
                if proceso.cantidad_de_rafagas_io > 0:
                    proceso.cantidad_de_rafagas_io -= 1
                    proceso.rafaga_io_pendiente_en_ejecucion = proceso.duracion_rafaga_io

                self.cola_listos.append(proceso)
                self.cola_bloqueados_por_io.pop(procesos_bloqueados_revisados)
            else:
                procesos_bloqueados_revisados += 1

    def ejecutar(self) -> ResultadoPlanificador:
        while len(self.resultado.procesos_finalizados) < len(self.planificador.procesos):
            if len(self.cola_listos) == 0:
                ejecutar_un_tick_idle(self.resultado.historial_estados, self.unidad_de_tiempo)
                self.resultado.tiempo_cpu_desocupada += 1
                self.avanzar_una_unidad_de_tiempo()
                self.actualizar_cola_bloqueados_por_io()
                self.actualizar_cola_listos()
            else:
                proceso_actual = self.cola_listos[0]
                if self.ultimo_proceso_ejecutado_id != proceso_actual.id and self.ultimo_proceso_ejecutado_id != -1 and proceso_actual.ya_ejecuto_su_tip:
                    for _ in range(self.planificador.tcp):
                        ejecutar_un_tick_tcp(proceso_actual, self.resultado.historial_estados, self.unidad_de_tiempo)
                        self.resultado.tiempo_cpu_con_so += 1
                        self.avanzar_una_unidad_de_tiempo()
                        self.actualizar_cola_bloqueados_por_io()
                        self.actualizar_cola_listos()
                    self.ultimo_proceso_ejecutado_id = proceso_actual.id
                elif self.ultimo_proceso_ejecutado_id != proceso_actual.id and not proceso_actual.ya_ejecuto_su_tip:
                    for _ in range(self.planificador.tip):
                        ejecutar_un_tick_tip(proceso_actual, self.resultado.historial_estados, self.unidad_de_tiempo)
                        self.resultado.tiempo_cpu_con_so += 1
                        self.avanzar_una_unidad_de_tiempo()
                        self.actualizar_cola_bloqueados_por_io()
                        self.actualizar_cola_listos()
                    proceso_actual.ya_ejecuto_su_tip = True
                    self.ultimo_proceso_ejecutado_id = proceso_actual.id
                else:
                    if proceso_actual.rafaga_cpu_pendiente_en_ejecucion > 0:
                        ejecutar_un_tick_cpu(proceso_actual, self.resultado.historial_estados, self.unidad_de_tiempo)
                        proceso_actual.tiempo_servicio += 1
                        for i in range(1, len(self.cola_listos)):
                            self.cola_listos[i].tiempo_espera_listo += 1
                        self.ultimo_proceso_ejecutado_id = proceso_actual.id
                        self.avanzar_una_unidad_de_tiempo()
                        self.actualizar_cola_bloqueados_por_io()
                        self.actualizar_cola_listos()

                        # Reviso si se completó el quantum de RR para pasar el proceso al final de la cola de listos
                        if self.quantum_counter % self.planificador.quantum == 0:
                            self.cola_listos.append(self.cola_listos.pop(0))
                        self.quantum_counter += 1

                    if proceso_actual.rafaga_cpu_pendiente_en_ejecucion == 0 and proceso_actual.cantidad_de_rafagas_cpu > 0:
                        proceso_actual.cantidad_de_rafagas_cpu -= 1
                        proceso_actual.rafaga_cpu_pendiente_en_ejecucion = proceso_actual.duracion_rafaga_cpu
                        self.cola_bloqueados_por_io.append(proceso_actual)
                        self.cola_listos.pop(0)
                        self.quantum_counter = 1
                    elif proceso_actual.rafaga_cpu_pendiente_en_ejecucion == 0 and proceso_actual.cantidad_de_rafagas_cpu == 0:
                        for _ in range(self.planificador.tfp):
                            ejecutar_un_tick_tfp(proceso_actual, self.resultado.historial_estados, self.unidad_de_tiempo)
                            self.resultado.tiempo_cpu_con_so += 1
                            self.avanzar_una_unidad_de_tiempo()
                            self.actualizar_cola_bloqueados_por_io()
                            self.actualizar_cola_listos()

                        self.resultado.procesos_finalizados.append(ProcesoFinalizado(
                            **proceso_actual.__dict__,
                            instante_retorno=self.unidad_de_tiempo,
                            tiempo_retorno=self.unidad_de_tiempo - proceso_actual.tiempo_de_arribo,
                            tiempo_retorno_normalizado=(self.unidad_de_tiempo - proceso_actual.tiempo_de_arribo) / proceso_actual.tiempo_servicio
                        ))
                        self.cola_listos.pop(0)
                        self.quantum_counter = 1

        self.resultado.procesos_finalizados.sort(key=lambda x: x.id)
        self.resultado.tiempo_retorno_tanda = self.unidad_de_tiempo
        self.resultado.tiempo_medio_retorno_tanda = sum(p.tiempo_retorno for p in self.resultado.procesos_finalizados) / len(self.resultado.procesos_finalizados)
        return self.resultado