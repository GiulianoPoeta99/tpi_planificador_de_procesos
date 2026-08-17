import os
from html import escape
from typing import Iterable, List, Tuple

from enums import Task
from models import ProcessScheduler, SchedulerResult, SystemState


class SimulationVisualizer:
    """Genera un resumen SVG autocontenido de una simulación."""

    TASK_COLORS = {
        Task.EXECUTING_CPU: "#2563EB",
        Task.WAITING_IO: "#06B6D4",
        Task.WAITING_IDLE: "#CBD5E1",
        Task.EXECUTING_TIP: "#F59E0B",
        Task.EXECUTING_TCP: "#8B5CF6",
        Task.EXECUTING_TFP: "#EF4444",
    }
    TASK_LABELS = {
        Task.EXECUTING_CPU: "CPU",
        Task.WAITING_IO: "E/S",
        Task.WAITING_IDLE: "Inactiva",
        Task.EXECUTING_TIP: "TIP",
        Task.EXECUTING_TCP: "TCP",
        Task.EXECUTING_TFP: "TFP",
    }

    def generate(
        self,
        scheduler: ProcessScheduler,
        result: SchedulerResult,
        output_dir: str,
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "simulation_summary.svg")
        svg = self._build_svg(scheduler, result)
        with open(output_path, "w", encoding="utf-8") as image_file:
            image_file.write(svg)
        return output_path

    def _build_svg(self, scheduler: ProcessScheduler, result: SchedulerResult) -> str:
        processes = scheduler.processes
        finished_by_id = {process.id: process for process in result.finished_processes}
        total_time = max(
            result.batch_return_time,
            max((state.order + 1 for state in result.state_history), default=0),
            1,
        )

        canvas_width = max(1240, min(2600, 330 + total_time * 18))
        margin = 48
        chart_x = 190
        chart_width = canvas_width - chart_x - margin
        unit_width = chart_width / total_time
        row_height = 42
        timeline_y = 390
        timeline_rows = len(processes) + 1
        timeline_height = timeline_rows * row_height
        table_y = timeline_y + timeline_height + 112
        table_row_height = 34
        table_height = 48 + max(len(processes), 1) * table_row_height
        canvas_height = table_y + table_height + 82

        svg: List[str] = [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{canvas_width}" height="{canvas_height}" '
                f'viewBox="0 0 {canvas_width} {canvas_height}" role="img" '
                f'aria-labelledby="title description">'
            ),
            "<title id=\"title\">Resumen de simulación del planificador de procesos</title>",
            (
                "<desc id=\"description\">Panel con parámetros, métricas, línea de "
                "tiempo y resultados por proceso.</desc>"
            ),
            """
            <defs>
              <filter id="shadow" x="-10%" y="-10%" width="120%" height="140%">
                <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#0F172A" flood-opacity="0.10"/>
              </filter>
              <style>
                text { font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
                .muted { fill: #64748B; }
                .label { fill: #334155; font-size: 13px; font-weight: 600; }
                .small { fill: #64748B; font-size: 11px; }
                .cell { fill: #334155; font-size: 12px; }
              </style>
            </defs>
            """,
            f'<rect width="{canvas_width}" height="{canvas_height}" fill="#F8FAFC"/>',
            f'<rect x="0" y="0" width="{canvas_width}" height="154" fill="#0F172A"/>',
            self._text(margin, 55, "SIMULACIÓN DE PLANIFICACIÓN", 13, "#93C5FD", 700),
            self._text(margin, 92, scheduler.policy.value, 30, "#FFFFFF", 750),
            self._text(
                margin,
                124,
                self._configuration_text(scheduler),
                14,
                "#CBD5E1",
                500,
            ),
        ]

        cpu_user_time = sum(
            1 for state in result.state_history if state.task == Task.EXECUTING_CPU
        )
        active_cpu_time = cpu_user_time + result.os_cpu_time
        utilization = (active_cpu_time / total_time) * 100
        metric_values = [
            ("Tiempo total", str(result.batch_return_time), "unidades"),
            ("Retorno promedio", f"{result.average_batch_return_time:.2f}", "unidades"),
            ("CPU de procesos", str(cpu_user_time), "unidades"),
            ("CPU del SO", str(result.os_cpu_time), "unidades"),
            ("Uso de CPU", f"{utilization:.1f}%", f"{result.idle_cpu_time} inactivas"),
        ]
        cards_y = 178
        cards_gap = 14
        cards_width = canvas_width - margin * 2
        card_width = (cards_width - cards_gap * (len(metric_values) - 1)) / len(metric_values)
        for index, (label, value, detail) in enumerate(metric_values):
            x = margin + index * (card_width + cards_gap)
            svg.extend(
                [
                    self._rect(x, cards_y, card_width, 102, "#FFFFFF", 12, "#E2E8F0"),
                    self._text(x + 18, cards_y + 27, label, 12, "#64748B", 650),
                    self._text(x + 18, cards_y + 62, value, 25, "#0F172A", 750),
                    self._text(x + 18, cards_y + 84, detail, 11, "#94A3B8", 500),
                ]
            )

        svg.append(self._text(margin, 320, "Línea de tiempo", 21, "#0F172A", 750))
        svg.append(
            self._text(
                margin,
                343,
                "Cada bloque representa una unidad de tiempo; los bloques contiguos iguales se agrupan.",
                12,
                "#64748B",
                500,
            )
        )

        cpu_states = [state for state in result.state_history if state.task != Task.WAITING_IO]
        rows: List[Tuple[str, List[SystemState], int]] = [("CPU / SO", cpu_states, -1)]
        for process in processes:
            process_states = [
                state for state in result.state_history if state.process_id == process.id
            ]
            rows.append((f"P{process.id} · {process.name}", process_states, process.arrival_time))

        tick_step = self._tick_step(unit_width)
        for tick in range(0, total_time + 1, tick_step):
            x = chart_x + tick * unit_width
            svg.append(
                f'<line x1="{x:.2f}" y1="{timeline_y - 22}" x2="{x:.2f}" '
                f'y2="{timeline_y + timeline_height}" stroke="#E2E8F0" stroke-width="1"/>'
            )
            svg.append(self._text(x, timeline_y - 29, str(tick), 10, "#64748B", 500, "middle"))

        if total_time % tick_step != 0:
            x = chart_x + chart_width
            svg.append(
                f'<line x1="{x:.2f}" y1="{timeline_y - 22}" x2="{x:.2f}" '
                f'y2="{timeline_y + timeline_height}" stroke="#E2E8F0" stroke-width="1"/>'
            )
            svg.append(self._text(x, timeline_y - 29, str(total_time), 10, "#64748B", 500, "middle"))

        for row_index, (row_label, states, arrival_time) in enumerate(rows):
            y = timeline_y + row_index * row_height
            background = "#FFFFFF" if row_index % 2 == 0 else "#F1F5F9"
            svg.append(self._rect(margin, y, canvas_width - margin * 2, row_height - 4, background, 7))
            svg.append(self._text(margin + 12, y + 24, row_label, 12, "#334155", 650))

            if arrival_time >= 0:
                arrival_x = chart_x + arrival_time * unit_width
                svg.append(
                    f'<path d="M {arrival_x:.2f} {y + 2} l -5 -7 h 10 z" fill="#0F172A">'
                    f'<title>Llegada en t={arrival_time}</title></path>'
                )

            for start, end, task, process_id, process_name in self._segments(states):
                x = chart_x + start * unit_width
                width = max((end - start) * unit_width, 0.75)
                color = self.TASK_COLORS[task]
                label = self._segment_label(task, process_name, row_index == 0)
                tooltip_process = f" · {process_name} (P{process_id})" if process_id else ""
                svg.append(
                    f'<g><rect x="{x:.2f}" y="{y + 5}" width="{width:.2f}" height="28" '
                    f'rx="4" fill="{color}" stroke="#FFFFFF" stroke-width="1">'
                    f'<title>{escape(self.TASK_LABELS[task])}{escape(tooltip_process)} · '
                    f'[{start}, {end})</title></rect>'
                )
                if width >= len(label) * 6.4 + 10:
                    svg.append(
                        self._text(x + width / 2, y + 24, label, 10, "#FFFFFF", 700, "middle")
                    )
                svg.append("</g>")

        legend_y = timeline_y + timeline_height + 26
        legend_items = [
            (Task.EXECUTING_CPU, "CPU de proceso"),
            (Task.WAITING_IO, "E/S"),
            (Task.EXECUTING_TIP, "TIP"),
            (Task.EXECUTING_TCP, "TCP"),
            (Task.EXECUTING_TFP, "TFP"),
            (Task.WAITING_IDLE, "CPU inactiva"),
        ]
        legend_x = margin
        for task, label in legend_items:
            svg.append(self._rect(legend_x, legend_y, 14, 14, self.TASK_COLORS[task], 3))
            svg.append(self._text(legend_x + 21, legend_y + 12, label, 11, "#475569", 600))
            legend_x += 35 + len(label) * 7
        svg.append(
            self._text(
                canvas_width - margin,
                legend_y + 12,
                "▲ llegada del proceso",
                11,
                "#475569",
                600,
                "end",
            )
        )

        svg.append(self._text(margin, table_y - 26, "Resultados por proceso", 21, "#0F172A", 750))
        headers = [
            "PID",
            "Proceso",
            "Llegada",
            "Ráfagas",
            "CPU/u",
            "E/S/u",
            "Prior.",
            "Fin",
            "Retorno",
            "Ret. norm.",
            "Servicio",
            "Espera",
        ]
        base_widths = [52, 170, 76, 82, 74, 74, 66, 66, 78, 94, 78, 76]
        table_width = canvas_width - margin * 2
        scale = table_width / sum(base_widths)
        column_widths = [width * scale for width in base_widths]

        svg.append(self._rect(margin, table_y, table_width, 38, "#E2E8F0", 8))
        column_x = margin
        for header, column_width in zip(headers, column_widths):
            anchor = "start" if header == "Proceso" else "middle"
            text_x = column_x + 10 if anchor == "start" else column_x + column_width / 2
            svg.append(self._text(text_x, table_y + 24, header, 11, "#334155", 700, anchor))
            column_x += column_width

        if not processes:
            svg.append(self._text(margin + 12, table_y + 68, "No hay procesos.", 12, "#64748B", 500))
        for row_index, process in enumerate(processes):
            finished = finished_by_id.get(process.id)
            row_y = table_y + 40 + row_index * table_row_height
            row_fill = "#FFFFFF" if row_index % 2 == 0 else "#F8FAFC"
            svg.append(self._rect(margin, row_y, table_width, table_row_height, row_fill, 0, "#E2E8F0"))
            values = [
                str(process.id),
                process.name,
                str(process.arrival_time),
                str(process.cpu_burst_count),
                str(process.cpu_burst_duration),
                str(process.io_burst_duration),
                str(process.priority),
                str(finished.return_instant) if finished else "—",
                str(finished.return_time) if finished else "—",
                f"{finished.normalized_return_time:.2f}" if finished else "—",
                str(finished.service_time) if finished else "—",
                str(finished.ready_wait_time) if finished else "—",
            ]
            column_x = margin
            for header, value, column_width in zip(headers, values, column_widths):
                anchor = "start" if header == "Proceso" else "middle"
                text_x = column_x + 10 if anchor == "start" else column_x + column_width / 2
                svg.append(self._text(text_x, row_y + 22, value, 11, "#334155", 500, anchor))
                column_x += column_width

        footer_y = canvas_height - 35
        svg.append(
            self._text(
                margin,
                footer_y,
                "CPU/u y E/S/u indican la duración de cada ráfaga. Los intervalos usan la convención [inicio, fin).",
                11,
                "#64748B",
                500,
            )
        )
        svg.append(
            self._text(
                canvas_width - margin,
                footer_y,
                "Generado automáticamente por el simulador",
                11,
                "#94A3B8",
                500,
                "end",
            )
        )
        svg.append("</svg>")
        return "".join(svg)

    @staticmethod
    def _configuration_text(scheduler: ProcessScheduler) -> str:
        parts = [
            f"{len(scheduler.processes)} procesos",
            f"TIP {scheduler.tip}",
            f"TCP {scheduler.tcp}",
            f"TFP {scheduler.tfp}",
        ]
        if scheduler.quantum is not None:
            parts.append(f"Quantum {scheduler.quantum}")
        return "  ·  ".join(parts)

    @staticmethod
    def _segments(
        states: Iterable[SystemState],
    ) -> List[Tuple[int, int, Task, int, str]]:
        sorted_states = sorted(states, key=lambda state: (state.order, state.task.value))
        segments: List[Tuple[int, int, Task, int, str]] = []
        for state in sorted_states:
            if segments:
                start, end, task, process_id, process_name = segments[-1]
                if (
                    state.order == end
                    and state.task == task
                    and state.process_id == process_id
                ):
                    segments[-1] = (start, end + 1, task, process_id, process_name)
                    continue
            segments.append(
                (state.order, state.order + 1, state.task, state.process_id, state.process_name)
            )
        return segments

    def _segment_label(self, task: Task, process_name: str, cpu_row: bool) -> str:
        if task == Task.EXECUTING_CPU and cpu_row and process_name:
            return process_name
        return self.TASK_LABELS[task]

    @staticmethod
    def _tick_step(unit_width: float) -> int:
        for step in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000):
            if step * unit_width >= 55:
                return step
        return 10000

    @staticmethod
    def _rect(
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str,
        radius: float = 0,
        stroke: str = "none",
    ) -> str:
        return (
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" '
            f'rx="{radius:.2f}" fill="{fill}" stroke="{stroke}"/>'
        )

    @staticmethod
    def _text(
        x: float,
        y: float,
        content: str,
        size: int,
        fill: str,
        weight: int,
        anchor: str = "start",
    ) -> str:
        return (
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(content))}</text>'
        )
