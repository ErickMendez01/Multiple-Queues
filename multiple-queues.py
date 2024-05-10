import tkinter as tk
import random
import threading
import time
from tkinter import ttk
from queue import Queue


class Proceso:
    def __init__(self, nombre, tiempo_llegada, tiempo_total, prioridad=None):
        self.nombre = nombre
        self.tiempo_total = tiempo_total
        self.tiempo_restante = tiempo_total
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_comienzo = None
        self.tiempo_finalizacion = None
        self.tiempo_espera = 0
        self.prioridad = prioridad


class PlanificacionSimulador:
    def __init__(self, root, algoritmo, queue):
        self.root = root
        self.root.title(f"Simulador de Planificación - {algoritmo}")
        self.procesos = []
        self.tiempo_transcurrido = 0
        self.cola = []
        self.algoritmo = algoritmo
        self.queue = queue
        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(expand=1, fill="both")
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="Simulación")
        self.canvas = tk.Canvas(self.tab1)
        self.scrollbar = ttk.Scrollbar(self.tab1, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.agregar_proceso_button = tk.Button(self.tab1, text="Agregar Proceso", command=self.agregar_proceso)
        self.agregar_proceso_button.pack()
        self.iniciar_simulacion()

    def agregar_proceso(self):
        tiempo_llegada = self.tiempo_transcurrido
        nombre = f'Proceso {len(self.procesos) + 1}'
        tiempo_total = random.randint(1, 10)
        prioridad = random.randint(1, 5)
        proceso = Proceso(nombre, tiempo_llegada, tiempo_total, prioridad)
        self.procesos.append(proceso)
        self.cola.append(proceso)
        self.actualizar_tamaño_ventana()

    def ejecutar_proceso(self):
        if not self.cola:
            time.sleep(1)
            return
        if self.algoritmo == "SRT":
            proceso = min(self.cola, key=lambda p: p.tiempo_restante)
            self.cola.remove(proceso)
        elif self.algoritmo == "Round Robin":
            proceso = self.cola.pop(0)
        elif self.algoritmo == "Prioridad":
            proceso = max(self.cola, key=lambda p: p.prioridad)
            self.cola.remove(proceso)
        else:
            return
        tiempo_ejecucion = min(proceso.tiempo_restante, 1)
        self.tiempo_transcurrido += tiempo_ejecucion
        proceso.tiempo_restante -= tiempo_ejecucion
        if proceso.tiempo_restante == 0:
            proceso.tiempo_finalizacion = self.tiempo_transcurrido
        else:
            self.cola.append(proceso)

    def graficar(self):
        self.canvas.delete("all")
        for i, proceso in enumerate(self.procesos):
            color = "red" if proceso.tiempo_restante > 0 else "blue"
            self.canvas.create_rectangle(20, 40 * i, 20 + proceso.tiempo_restante * 20, 40 * (i + 1), fill=color)
        self.root.update_idletasks()
        self.root.after(1000, self.graficar)

    def actualizar_tamaño_ventana(self):
        width = 400
        height = 40 * len(self.procesos)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def iniciar_simulacion(self):
        for _ in range(5):
            self.agregar_proceso()
        self.graficar()


def simulacion(simulador):
    while any(proceso.tiempo_restante > 0 for proceso in simulador.procesos):
        for proceso in simulador.procesos:
            if proceso.tiempo_llegada <= simulador.tiempo_transcurrido and proceso.tiempo_restante > 0:
                if proceso not in simulador.cola:
                    simulador.cola.append(proceso)
                    if simulador.algoritmo == "Prioridad":
                        simulador.cola.sort(key=lambda p: p.prioridad)
                simulador.ejecutar_proceso()
        time.sleep(1)  # Hacer una pausa de 1 segundo entre ejecuciones


if __name__ == "__main__":
    root = tk.Tk()
    queue = Queue()
    srt_app = PlanificacionSimulador(root, algoritmo="SRT", queue=queue)
    rr_app = PlanificacionSimulador(root, algoritmo="Round Robin", queue=queue)
    prioridad_app = PlanificacionSimulador(root, algoritmo="Prioridad", queue=queue)
    thread_srt = threading.Thread(target=simulacion, args=(srt_app,))
    thread_rr = threading.Thread(target=simulacion, args=(rr_app,))
    thread_prioridad = threading.Thread(target=simulacion, args=(prioridad_app,))
    thread_srt.start()
    thread_rr.start()
    thread_prioridad.start()
    root.mainloop()
