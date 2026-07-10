# Configurador de Sistema Activo

Aplicación gráfica (Tkinter) para ajustar configuraciones de energía en Windows y programar un reinicio automático diario.

## Descripción

Esta pequeña herramienta permite:
- Desactivar suspensión e hibernación (tanto en AC como en batería) usando `powercfg`.
- Evitar que el monitor se apague (timeout = 0).
- Programar, opcionalmente, un reinicio forzado diario a las 00:00 mediante una tarea creada con `schtasks` (nombre de la tarea: `Reinicio_Diario_Medianoche`).
- Eliminar la tarea programada (botón "Desactivar Reinicio").

La interfaz es mínima: el usuario selecciona la versión de Windows y pulsa `Aplicar Configuración`.

## Requisitos

- Windows 7 / 8 / 10 (la aplicación solo ejecuta comandos compatibles con Windows).
- Python 3.x con Tkinter disponible.
- Ejecutar la aplicación con permisos de Administrador para que `powercfg` y `schtasks` puedan modificar la configuración del sistema y crear/eliminar tareas.
- Los binarios `powercfg` y `schtasks` deben estar disponibles en `PATH` (normalmente vienen con Windows).

## Riesgos y advertencias

- El reinicio programado usa `shutdown /r /f /t 0`: fuerza el cierre de aplicaciones sin guardar. Asegúrate de no tener trabajo no guardado antes de habilitarlo.
- Las opciones de energía se establecen a `0` (nunca). Esto puede afectar consumo y duración de batería en portátiles.

## Uso

1. Ejecutar la aplicación (ejecutar como Administrador):

```bash
python main.py
```

2. En la ventana, seleccionar la versión de Windows y pulsar `Aplicar Configuración`.
3. Cuando se pregunte, confirmar si se desea programar el reinicio automático.
4. Para eliminar la tarea programada después, usar el botón `Desactivar Reinicio` en la misma interfaz.

### Comandos manuales (si prefieres hacerlo por consola)

- Crear tarea (equivalente a la opción de la app):

```powershell
schtasks /create /tn "Reinicio_Diario_Medianoche" /tr "shutdown /r /f /t 0" /sc daily /st 00:00 /ru "SYSTEM" /f
```

- Eliminar tarea:

```powershell
schtasks /delete /tn "Reinicio_Diario_Medianoche" /f
```

- Parámetros de energía (ejemplos):

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0
```

## Notas de desarrollo

- El código evita `shell=True` y pasa argumentos como lista a `subprocess.run` para mayor seguridad y robustez.
- La aplicación actualmente no realiza registro (logging) por decisión del autor.

## Mejoras sugeridas

- Añadir confirmación con horario o ventana de mantenimiento antes del reinicio.
- Opción para programar reinicios en horarios distintos o con notificación previa a usuarios.
- Guardar un histórico de acciones (si se desea trazabilidad).

## Licencia y contacto

Proyecto sin licencia especificada (útil para uso personal). Para dudas o cambios, modifica directamente `main.py` en este repositorio.

## Empaquetado y distribución (Windows)

Se recomienda empaquetar la aplicación en Windows con PyInstaller para generar un ejecutable independiente.

1. Crear un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows: .venv\Scripts\activate
pip install --upgrade pip
```

2. Instalar PyInstaller:

```bash
pip install pyinstaller
```

3. Generar un ejecutable "one-file" (desde Windows):

Si quieres incluir un icono personalizado, PyInstaller en Windows espera un archivo `.ico`, ejecuta:

```bash
pyinstaller --onefile --windowed --name PowerManager --icon icon.ico main.py
```

Si no necesitas icono, usa el comando sin `--icon`:

```bash
pyinstaller --onefile --windowed --name PowerManager main.py
```

- `--onefile` empaqueta todo en un solo `.exe`.
- `--windowed` evita abrir una consola cuando se ejecute la app GUI.

Asegúrate de colocar `icon.ico` en la misma carpeta desde la que ejecutas `pyinstaller` o especifica la ruta completa en `--icon`.

4. Resultado: el ejecutable estará en `dist\PowerManager.exe`.

Notas importantes:
- Construye el ejecutable en Windows; PyInstaller no construye ejecutables de Windows desde macOS/Linux de forma fiable.
- Si la aplicación utiliza recursos externos o librerías, puede que necesites opciones adicionales de PyInstaller (`--add-data`, archivos `.spec`).

5. Crear un instalador (opcional):

Puedes usar Inno Setup para crear un instalador `.exe` profesional:

- Instala Inno Setup: https://jrsoftware.org/isinfo.php
- Crea un script que copie `dist\PowerManager.exe` y cree accesos directos.

Alternativas:
- `cx_Freeze` o `py2exe` (otras herramientas para generar ejecutables en Windows).
- Para despliegues empresariales, considera crear un MSI con herramientas de empaquetado adicionales.

Pruebas finales:
- Ejecuta `PowerManager.exe` como Administrador para verificar que `powercfg` y `schtasks` funcionan correctamente.
- Verifica que la interfaz GUI arranca sin consola y que las acciones aplican los cambios esperados.

Si quieres, puedo añadir un `setup.bat` o un script de `pyinstaller` al repo para facilitar el empaquetado.
