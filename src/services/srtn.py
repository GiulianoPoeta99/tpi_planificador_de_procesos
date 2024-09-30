from typing import List
from models import RunningProcess, FinishedProcess, SchedulerResult, ProcessScheduler
from .policy_strategy import PolicyStrategy
from tools.logger import CustomLogger
from system import System

class SRTN(PolicyStrategy):
	def __init__(self, scheduler: ProcessScheduler, logger: CustomLogger):
		self.scheduler = scheduler
		self.logger = logger
		self.time_unit = 0
		self.ready_queue: List[RunningProcess] = []
		self.io_blocked_queue: List[RunningProcess] = []
		self.last_executed_process = None
		self.result = SchedulerResult(
			state_history=[],
			finished_processes=[],
			batch_return_time=0,
			average_batch_return_time=0,
			idle_cpu_time=0,
			os_cpu_time=0
		)
		self.system_executor = System()
		self.update_io_blocked_queue()
		self.update_ready_queue()
		self.sort_ready_queue()

	def advance_time_unit(self):
		self.logger.log_ws()
		self.time_unit += 1
		

	def sort_ready_queue(self):
		self.ready_queue.sort(key=lambda process: process.pending_cpu_burst_in_execution)
		self.logger.info(self.time_unit, '-', f"Ready Queue sorted by remaining time: {[p.id for p in self.ready_queue]}")


	def update_io_blocked_queue(self):
		# contador de procesos revisados
		processes_reviewed = 0
		# se ejecuta hasta que los procesos revisados sean iguales a los totales bloqueados
		while processes_reviewed < len(self.io_blocked_queue):
			process = self.io_blocked_queue[processes_reviewed]
			# si le quedan rafagas de bloque pendiente las realizamos.
			if process.pending_io_burst_in_execution > 0:
				# ejecucion de sistema para resumen
				self.system_executor.execute_io_tick(process, self.time_unit)
				self.logger.info(self.time_unit, 'BLOCKED', f"Process '{process.name}' (pid: {process.id}) executing I/O")

			# si ya no tiene rafagas lo movemos a la cola de listos
			if process.pending_io_burst_in_execution == 0:
				if process.io_burst_count > 0:
					process.io_burst_count -= 1
					process.pending_io_burst_in_execution = process.io_burst_duration
				process.burst_in_execution_finish = False
				self.ready_queue.append(process)
				self.io_blocked_queue.pop(processes_reviewed)
				self.logger.info(self.time_unit, 'BLOCKED', f"Process '{process.name}' (pid: {process.id}) moved from I/O to Ready Queue")
			else:
				processes_reviewed += 1

	def update_ready_queue(self):
		# verificamos que no hayan llegado nuevos procesos y si llegan los agregamos al final de la cola
		for process in self.scheduler.processes:
			if process.arrival_time == self.time_unit:
				self.ready_queue.append(RunningProcess(
					id=process.id,
					name=process.name,
					arrival_time=process.arrival_time,
					cpu_burst_duration=process.cpu_burst_duration,
					io_burst_duration=process.io_burst_duration,
					priority=process.priority,
					tip_already_executed=self.scheduler.tip == 0,
					burst_in_execution=False,
					burst_in_execution_finish=False,
					pending_cpu_burst_in_execution=process.cpu_burst_duration,
					pending_io_burst_in_execution=process.io_burst_duration,
					service_time=0,
					ready_wait_time=0,
					cpu_burst_count=process.cpu_burst_count - 1 if process.cpu_burst_count > 0 else 0,
					io_burst_count=process.io_burst_count
				))
				self.logger.info(self.time_unit, 'READY', f"Process '{process.name}' (pid: {process.id}) arrived and added to Ready Queue")

	def execute(self):
		# ejecutar la simulacion hasta que los procesos finalizados sean iguales a los procesoso totales
		while len(self.result.finished_processes) < len(self.scheduler.processes):
			# si no hay procesos en la cola de listos la cpu esta inactiva si los hay hay que ejecutarlos.
			if len(self.ready_queue) == 0:
				# ejecutamos estadisticas de para el resumen
				self.system_executor.execute_idle_tick(self.time_unit)
				self.result.idle_cpu_time += 1
				# avanzamos el tiempo de la simulacion
				self.advance_time_unit()
				self.logger.info(self.time_unit, '-', "CPU Idle")
				# actualizamos los bloqueados
				self.update_io_blocked_queue()
				# actualizamos la cola de listos
				self.update_ready_queue()
				# ordenamos la cola de listos
				self.sort_ready_queue()
			else:
				# sacamos el siguiente proceso de la cola
				process = self.ready_queue[0]
				if (
					process != self.last_executed_process and 
					self.last_executed_process != None and 
					self.last_executed_process.burst_in_execution):
					# ejecutamos el tcp porque se interrumpio el proceso anterior
					for _ in range(self.scheduler.tcp):
						# ejecutamos estadisticas de para el resumen
						self.system_executor.execute_tcp_tick(self.last_executed_process, self.time_unit)
						self.result.os_cpu_time += 1
						# avanzamos el tiempo de la simulacion
						self.advance_time_unit()
						self.logger.info(self.time_unit, 'RUNNING', f"Process '{self.last_executed_process.name}' (pid: {self.last_executed_process.id}) executing TCP")
						# actualizamos los bloqueados ejecutando y moviendolos a listo
						self.update_io_blocked_queue()
						# revisamos que no hayan procesos nuevos
						self.update_ready_queue()
					# cambiamos el id del ultimo proceso ejeutado
					self.logger.info(self.time_unit, 'RUNNING', f"Process '{self.last_executed_process.name}' (pid: {self.last_executed_process.id}) was interrupted by process '{process.name}' (pid: {process.id})")
					self.last_executed_process = process
				else:
					# si el ultimo proceso ejecutado es el mismo que el actual y no se ejecuto su tip lo ejecuto si no se ejecuta de manera normal
					if not process.tip_already_executed:
						# ejecutamos la cantidad tip que diga en los parametros.
						for _ in range(self.scheduler.tip):
							# ejecucion de sistema para resumen
							self.system_executor.execute_tip_tick(process, self.time_unit)
							self.result.os_cpu_time += 1
							# avanzamos el tiempo de la simulacion
							self.advance_time_unit()
							self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) executing TIP")
							# actualizamos la cola de bloqueadaos para que se ejecute el io y se muevan a la cola de listos
							self.update_io_blocked_queue()
							# revisamos que no hayan aprecido nuevos procesos
							self.update_ready_queue()
						# informamos que se ejecuto el tip
						process.tip_already_executed = True
						# cambiamos el id del ultimo proceso ejeutado
						self.last_executed_process = process
						# ordenamos la cola de listos
						self.sort_ready_queue()
					else:
						# preguntamos si le quedan rafagas pendientes al proceso actual
						if process.pending_cpu_burst_in_execution > 0:
							# ejecutamos estadisticas de para el resumen
							self.system_executor.execute_cpu_tick(process, self.time_unit)
							# ejecutamos la rafaga del proceso
							process.service_time += 1
							for i in range(1, len(self.ready_queue)):
								self.ready_queue[i].ready_wait_time += 1
							process.burst_in_execution = True
							# cambiamos la info del ultimo proceso ejecutado
							self.last_executed_process = process
							# avanzamos el tiempo de la simulacion
							self.advance_time_unit()
							self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) executing CPU burst")
							# actualizamos los bloqueados ejecutando y moviendolos
							self.update_io_blocked_queue()
							# revisamos que no hayan procesos nuevos
							self.update_ready_queue()
							# ordenamos la cola de listos
							self.sort_ready_queue()

						# pregunamos si ya no le queda mas ejecucion de la rafaga actual
						if process.pending_cpu_burst_in_execution == 0:
							# preguntaos si le quedan mas bloques de rafagas pendientes
							if process.cpu_burst_count > 0:
								process.cpu_burst_count -= 1
								process.pending_cpu_burst_in_execution = process.cpu_burst_duration
								process.burst_in_execution = False
								process.burst_in_execution_finish = True
								# ejecutamos el tcp porque el proceso termino su rafaga y pasa a la cola de bloqueados
								for _ in range(self.scheduler.tcp):
									# ejecutamos estadisticas de para el resumen
									self.system_executor.execute_tcp_tick(process, self.time_unit)
									self.result.os_cpu_time += 1
									# avanzamos el tiempo de la simulacion
									self.advance_time_unit()
									self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) executing TCP")
									# actualizamos los bloqueados ejecutando y moviendolos a listo
									self.update_io_blocked_queue()
									# revisamos que no hayan procesos nuevos
									self.update_ready_queue()
								# una vez que termina el tcp movemos el proceso a la cola de bloqueados
								self.io_blocked_queue.append(process)
								# y sacamos el proceso de la cola
								self.ready_queue.remove(process)
								self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) moved to I/O Blocked Queue")
								# ordenamos la cola de listos
								self.sort_ready_queue()
							elif process.cpu_burst_count == 0:
								process.burst_in_execution = False
								process.burst_in_execution_finish = True
								# ejecutamos el tfp porque ya no hay rafagas pendientes
								for _ in range(self.scheduler.tfp):
									# ejecutamos estadisticas de para el resumen
									self.system_executor.execute_tfp_tick(process, self.time_unit)
									self.result.os_cpu_time += 1
									# avanzamos el tiempo de la simulacion
									self.advance_time_unit()
									self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) executing TFP")
									# actualizamos los bloqueados ejecutando y moviendolos a listo
									self.update_io_blocked_queue()
									# revisamos que no hayan procesos nuevos
									self.update_ready_queue()
								# finalizamos el proceso agragandolo a la cola de finalizados
								self.result.finished_processes.append(FinishedProcess(
									**process.__dict__,
									return_instant=self.time_unit,
									return_time=self.time_unit - process.arrival_time,
									normalized_return_time=(self.time_unit - process.arrival_time) / process.service_time
								))
								# lo sacamos de la cola de listos
								self.ready_queue.remove(process)
								self.logger.info(self.time_unit, 'FINISHED', f"Process '{process.name}' (pid: {process.id}) finished")
						

		# una vez que termina la simulacion ordenamos la lista de finalizados por el pid y agregamso varios parametros para el resultado final de la misma
		self.result.finished_processes.sort(key=lambda x: x.id)
		self.result.batch_return_time = self.time_unit
		self.result.average_batch_return_time = sum(p.return_time for p in self.result.finished_processes) / len(self.result.finished_processes)
		self.result.state_history = self.system_executor.get_history()
		return self.result
