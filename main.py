import os
import sys
import shutil
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox


def resource_path(rel):
    """Ruta a un recurso, tanto en desarrollo como dentro del .exe de PyInstaller.

    PyInstaller (--onefile) extrae los archivos empaquetados a una carpeta
    temporal accesible vía sys._MEIPASS; en desarrollo se usa la carpeta actual.
    """
    base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, rel)

# Nombre único de la tarea programada (compartido al crear y eliminar)
TAREA_NOMBRE = 'Reinicio_Diario_Medianoche'

# Metadatos de la aplicación
VERSION = '1.3.1'
COMPATIBLE_CON = 'Compatible con Windows 7 / 8 / 10'


def es_windows():
    return platform.system().lower() == 'windows'


def nombre_sistema():
    """Devuelve el nombre legible del sistema operativo detectado."""
    sistema = platform.system()
    version = platform.release()
    return f"{sistema} {version}".strip()


def run_command(cmd_args):
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError:
        raise


def _validar_binario(binario):
    """Comprueba que estamos en Windows y que el binario exista en el PATH."""
    if not es_windows():
        messagebox.showerror("SO no soportado", "Esta acción solo está disponible en Windows.")
        return False
    if not shutil.which(binario):
        messagebox.showerror(f'Falta {binario}', f'No se encontró el comando `{binario}` en el sistema.')
        return False
    return True


def tarea_existe(nombre):
    """Devuelve True si existe una tarea programada con ese nombre."""
    resultado = subprocess.run(
        ['schtasks', '/query', '/tn', nombre],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return resultado.returncode == 0


# --- Fila 1: control de suspensión / energía -------------------------------

def mantener_despierta():
    """Fija todos los timeouts en 0: la PC nunca se suspende ni apaga pantalla."""
    if not _validar_binario('powercfg'):
        return
    confirmar = messagebox.askyesno(
        'Confirmar modo activo',
        '¿Deseas mantener la PC siempre despierta?\n\n'
        '- No entrará en suspensión ni hibernación.\n'
        '- La pantalla no se apagará.\n\n'
        'En portátiles esto aumenta el consumo de batería.'
    )
    if not confirmar:
        return
    try:
        run_command(['powercfg', '/change', 'standby-timeout-ac', '0'])
        run_command(['powercfg', '/change', 'standby-timeout-dc', '0'])
        run_command(['powercfg', '/change', 'hibernate-timeout-ac', '0'])
        run_command(['powercfg', '/change', 'hibernate-timeout-dc', '0'])
        run_command(['powercfg', '/change', 'monitor-timeout-ac', '0'])
        run_command(['powercfg', '/change', 'monitor-timeout-dc', '0'])
        messagebox.showinfo(
            'PC en modo activo',
            'La PC se mantendrá despierta:\n\n'
            '- No entrará en suspensión ni hibernación.\n'
            '- La pantalla no se apagará.'
        )
    except subprocess.CalledProcessError:
        messagebox.showerror(
            'Error al aplicar cambios',
            'No se pudieron aplicar los cambios. Ejecuta la aplicación como Administrador.'
        )


def permitir_suspension():
    """Restaura tiempos de suspensión estándar (en minutos)."""
    if not _validar_binario('powercfg'):
        return
    try:
        run_command(['powercfg', '/change', 'monitor-timeout-ac', '10'])
        run_command(['powercfg', '/change', 'monitor-timeout-dc', '5'])
        run_command(['powercfg', '/change', 'standby-timeout-ac', '30'])
        run_command(['powercfg', '/change', 'standby-timeout-dc', '15'])
        run_command(['powercfg', '/change', 'hibernate-timeout-ac', '180'])
        run_command(['powercfg', '/change', 'hibernate-timeout-dc', '60'])
        messagebox.showinfo(
            'Suspensión restaurada',
            'Se restauraron tiempos de suspensión estándar:\n\n'
            '- Pantalla: 10 min (corriente) / 5 min (batería)\n'
            '- Suspender: 30 min (corriente) / 15 min (batería)\n'
            '- Hibernar: 180 min (corriente) / 60 min (batería)'
        )
    except subprocess.CalledProcessError:
        messagebox.showerror(
            'Error al restaurar',
            'No se pudieron restaurar los valores. Ejecuta la aplicación como Administrador.'
        )


# --- Fila 2: control del reinicio automático diario ------------------------

def programar_reinicio():
    """Crea una tarea programada que reinicia el equipo a diario a las 00:00."""
    if not _validar_binario('schtasks'):
        return
    crear = messagebox.askyesno(
        'Confirmar reinicio programado',
        '¿Deseas programar un reinicio automático diario a las 00:00?\n\n'
        'El reinicio usa "shutdown /r /f": cierra las aplicaciones sin guardar.'
    )
    if not crear:
        return
    try:
        # /tr acepta el comando como una sola cadena
        run_command([
            'schtasks', '/create', '/tn', TAREA_NOMBRE,
            '/tr', 'shutdown /r /f /t 0', '/sc', 'daily', '/st', '00:00', '/ru', 'SYSTEM', '/f'
        ])
        messagebox.showinfo(
            'Reinicio programado',
            'Se programó un reinicio automático diario a las 00:00.'
        )
    except subprocess.CalledProcessError:
        messagebox.showerror(
            'Error al programar',
            'No se pudo crear la tarea programada. Ejecuta la aplicación como Administrador.'
        )


def cancelar_reinicio():
    """Elimina la tarea programada de reinicio diario."""
    if not _validar_binario('schtasks'):
        return
    if not tarea_existe(TAREA_NOMBRE):
        messagebox.showinfo(
            'Sin tareas programadas',
            'No se han encontrado tareas programadas de reinicio para eliminar.'
        )
        return
    confirmar = messagebox.askyesno('Confirmar cancelación', '¿Deseas eliminar la tarea de reinicio automático?')
    if not confirmar:
        return
    try:
        run_command(['schtasks', '/delete', '/tn', TAREA_NOMBRE, '/f'])
        messagebox.showinfo('Reinicio cancelado', 'La tarea de reinicio automático fue eliminada correctamente.')
    except subprocess.CalledProcessError:
        messagebox.showerror('Error al cancelar', 'No se pudo eliminar la tarea programada. Comprueba permisos.')


# --- Configuración de la Interfaz Gráfica (Tkinter) ---
ventana = tk.Tk()
ventana.title('Power Manager')
ventana.geometry('480x320')
ventana.resizable(False, False)

# Icono de la ventana (barra de título y barra de tareas).
# En Windows usa el .ico; si falla (p. ej. en macOS/Linux) se ignora.
try:
    ventana.iconbitmap(resource_path('icon.ico'))
except Exception:
    pass

# Etiqueta de instrucción
lbl_instruccion = tk.Label(ventana, text='Sistema operativo detectado:', font=('Arial', 11, 'bold'))
lbl_instruccion.pack(pady=(16, 4))

# Nombre del SO detectado automáticamente
lbl_sistema = tk.Label(ventana, text=nombre_sistema(), font=('Arial', 12), fg='#1b7ced')
lbl_sistema.pack(pady=(0, 4))

# Botones de acción (grid 2x2)
# Columna izquierda = aplicar el comportamiento "mantener activo".
# Columna derecha  = revertir cada acción.
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=20)

btn_mantener = tk.Button(frame_botones, text='Mantener PC despierta', command=mantener_despierta, bg='#28a745', fg='white', font=('Arial', 10, 'bold'), relief='flat', width=22)
btn_mantener.grid(row=0, column=0, padx=8, pady=6, ipady=5)

btn_permitir = tk.Button(frame_botones, text='Permitir suspensión', command=permitir_suspension, bg='#6c757d', fg='white', font=('Arial', 10, 'bold'), relief='flat', width=22)
btn_permitir.grid(row=0, column=1, padx=8, pady=6, ipady=5)

btn_programar = tk.Button(frame_botones, text='Programar reinicio diario', command=programar_reinicio, bg='#1b7ced', fg='white', font=('Arial', 10, 'bold'), relief='flat', width=22)
btn_programar.grid(row=1, column=0, padx=8, pady=6, ipady=5)

btn_cancelar = tk.Button(frame_botones, text='Cancelar reinicio diario', command=cancelar_reinicio, bg='#d9534f', fg='white', font=('Arial', 10, 'bold'), relief='flat', width=22)
btn_cancelar.grid(row=1, column=1, padx=8, pady=6, ipady=5)

botones = [btn_mantener, btn_permitir, btn_programar, btn_cancelar]

# Si no es Windows, deshabilitar botones y avisar
if not es_windows():
    for boton in botones:
        boton.config(state='disabled')
    lbl_no_so = tk.Label(ventana, text=f"SO detectado: {platform.system()} — solo Windows soportado.", fg='red')
    lbl_no_so.pack(pady=6)

# Footer: compatibilidad (izquierda) y versión (derecha)
frame_footer = tk.Frame(ventana)
frame_footer.pack(side='bottom', fill='x', padx=10, pady=6)

lbl_compatibilidad = tk.Label(frame_footer, text=COMPATIBLE_CON, font=('Arial', 8), fg='gray')
lbl_compatibilidad.pack(side='left')

lbl_version = tk.Label(frame_footer, text=f'v{VERSION}', font=('Arial', 8), fg='gray')
lbl_version.pack(side='right')

ventana.mainloop()