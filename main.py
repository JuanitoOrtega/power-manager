import shutil
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


def es_windows():
    return platform.system().lower() == 'windows'


def run_command(cmd_args):
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError:
        raise


def aplicar_configuracion():
    sistema = combo_sistemas.get()

    if not sistema:
        messagebox.showwarning(
            "Selección vacía",
            "Por favor selecciona un sistema operativo antes de continuar."
        )
        return

    if not es_windows():
        messagebox.showerror("SO no soportado", "Esta aplicación solo puede ejecutar cambios en Windows.")
        return

    # Verificar que los binarios necesarios existan
    if not shutil.which('powercfg'):
        messagebox.showerror('Falta powercfg', 'No se encontró el comando `powercfg` en el sistema.')
        return
    if not shutil.which('schtasks'):
        messagebox.showerror('Falta schtasks', 'No se encontró el comando `schtasks` en el sistema.')
        return

    try:
        # 1. Configurar energía: Nunca suspender ni hibernar (con corriente y batería)
        run_command(['powercfg', '/change', 'standby-timeout-ac', '0'])
        run_command(['powercfg', '/change', 'standby-timeout-dc', '0'])
        run_command(['powercfg', '/change', 'hibernate-timeout-ac', '0'])
        run_command(['powercfg', '/change', 'hibernate-timeout-dc', '0'])

        # 2. Configurar pantalla: Nunca apagarse
        run_command(['powercfg', '/change', 'monitor-timeout-ac', '0'])
        run_command(['powercfg', '/change', 'monitor-timeout-dc', '0'])

        # 3. Confirmación antes de crear la tarea programada
        crear = messagebox.askyesno(
            'Confirmar Reinicio Programado',
            '¿Deseas programar un reinicio automático diario a las 00:00?'
        )
        

        if crear:
            # Crear la tarea programada para reiniciar a la medianoche (00:00)
            tarea_nombre = 'Reinicio_Diario_Medianoche'
            # /tr acepta el comando como una sola cadena
            run_command([
                'schtasks', '/create', '/tn', tarea_nombre,
                '/tr', 'shutdown /r /f /t 0', '/sc', 'daily', '/st', '00:00', '/ru', 'SYSTEM', '/f'
            ])
            messagebox.showinfo(
                'Configuración Exitosa',
                f'¡Operación completada para {sistema}!\n\n'
                '- El sistema nunca entrará en suspensión.\n'
                '- Se programó un reinicio automático diario a las 00:00.'
            )
            
        else:
            messagebox.showinfo('Configuración Parcial', 'Se aplicaron cambios de energía sin programar reinicio.')

    except subprocess.CalledProcessError:
        messagebox.showerror(
            'Error al aplicar cambios',
            'No se pudieron aplicar completamente los cambios. Asegúrate de ejecutar como Administrador.'
        )
        


def desactivar_reinicio():
    if not es_windows():
        messagebox.showerror("SO no soportado", "Esta función solo está disponible en Windows.")
        return

    confirmar = messagebox.askyesno('Confirmar eliminación', '¿Deseas eliminar la tarea programada de reinicio?')
    if not confirmar:
        return

    try:
        tarea_nombre = 'Reinicio_Diario_Medianoche'
        run_command(['schtasks', '/delete', '/tn', tarea_nombre, '/f'])
        messagebox.showinfo('Tarea Eliminada', 'La tarea programada ha sido eliminada correctamente.')
    except subprocess.CalledProcessError:
        messagebox.showerror('Error', 'No se pudo eliminar la tarea programada. Comprueba permisos.')
        


# --- Configuración de la Interfaz Gráfica (Tkinter) ---
ventana = tk.Tk()
ventana.title('Configurador de Sistema Activo')
ventana.geometry('460x260')
ventana.resizable(False, False)

# Etiqueta de instrucción
lbl_instruccion = tk.Label(ventana, text='Seleccione su Sistema Operativo:', font=('Arial', 11, 'bold'))
lbl_instruccion.pack(pady=16)

# Selector (Combobox)
sistemas_disponibles = ['Windows 7', 'Windows 8', 'Windows 10']
combo_sistemas = ttk.Combobox(ventana, values=sistemas_disponibles, state='readonly', font=('Arial', 10))
combo_sistemas.pack(pady=5, ipady=3)
combo_sistemas.current(0)  # Selecciona Windows 7 por defecto

# Botones de acción
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=20)

btn_aplicar = tk.Button(frame_botones, text='Aplicar Configuración', command=aplicar_configuracion, bg='#1b7ced', fg='white', font=('Arial', 10, 'bold'), relief='flat')
btn_aplicar.grid(row=0, column=0, padx=8, ipadx=10, ipady=5)

btn_desactivar = tk.Button(frame_botones, text='Desactivar Reinicio', command=desactivar_reinicio, bg='#d9534f', fg='white', font=('Arial', 10, 'bold'), relief='flat')
btn_desactivar.grid(row=0, column=1, padx=8, ipadx=10, ipady=5)

# Si no es Windows, deshabilitar botones y avisar
if not es_windows():
    btn_aplicar.config(state='disabled')
    btn_desactivar.config(state='disabled')
    lbl_no_so = tk.Label(ventana, text=f"SO detectado: {platform.system()} — solo Windows soportado.", fg='red')
    lbl_no_so.pack(pady=6)

ventana.mainloop()