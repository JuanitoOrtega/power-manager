# Power Manager

Aplicación gráfica (Tkinter) para ajustar configuraciones de energía en Windows y programar un reinicio automático diario.

## Descripción

Esta herramienta ofrece control granular sobre el estado de energía del equipo mediante cuatro acciones independientes:

- **Mantener PC despierta** — desactiva suspensión, hibernación y apagado de pantalla (timeouts a `0`, tanto en corriente como en batería) usando `powercfg`.
- **Permitir suspensión** — restaura tiempos de suspensión estándar (ver tabla más abajo).
- **Programar reinicio diario** — crea, opcionalmente, una tarea de reinicio forzado diario a las 00:00 mediante `schtasks` (nombre de la tarea: `Reinicio_Diario_Medianoche`).
- **Cancelar reinicio diario** — elimina esa tarea programada.

La aplicación **detecta automáticamente el sistema operativo** y lo muestra en pantalla; no es necesario seleccionarlo. Si el SO no es Windows, los botones se deshabilitan.

### Distribución de la interfaz

Los botones se organizan en una cuadrícula 2×2 — la columna izquierda **aplica** el comportamiento "mantener activo" y la derecha lo **revierte**:

| | Aplicar (izquierda) | Revertir (derecha) |
|---|---|---|
| **Energía** | Mantener PC despierta | Permitir suspensión |
| **Reinicio** | Programar reinicio diario | Cancelar reinicio diario |

En el pie de la ventana se muestra la compatibilidad (izquierda) y la versión de la aplicación (derecha).

### Valores restaurados por "Permitir suspensión"

| Configuración | Con corriente (AC) | Con batería (DC) |
|---|---|---|
| Apagar pantalla | 10 min | 5 min |
| Suspender | 30 min | 15 min |
| Hibernar | 180 min | 60 min |

## Requisitos

- Windows 7 / 8 / 10 (la aplicación solo ejecuta comandos compatibles con Windows).
- Python 3.x con Tkinter disponible.
- Ejecutar la aplicación con permisos de Administrador para que `powercfg` y `schtasks` puedan modificar la configuración del sistema y crear/eliminar tareas.
- Los binarios `powercfg` y `schtasks` deben estar disponibles en `PATH` (normalmente vienen con Windows).

## Riesgos y advertencias

- El reinicio programado usa `shutdown /r /f /t 0`: fuerza el cierre de aplicaciones sin guardar. Asegúrate de no tener trabajo no guardado antes de habilitarlo.
- "Mantener PC despierta" establece los timeouts de energía a `0` (nunca). Esto puede afectar consumo y duración de batería en portátiles; usa "Permitir suspensión" para volver a valores razonables.

## Uso

1. Ejecutar la aplicación (ejecutar como Administrador):

```bash
python main.py
```

2. La ventana muestra el sistema operativo detectado y las cuatro acciones.
3. Pulsa la acción deseada. Las acciones sensibles (programar y cancelar el reinicio) piden confirmación.

### Comandos manuales (si prefieres hacerlo por consola)

- Crear tarea de reinicio (equivalente a "Programar reinicio diario"):

```powershell
schtasks /create /tn "Reinicio_Diario_Medianoche" /tr "shutdown /r /f /t 0" /sc daily /st 00:00 /ru "SYSTEM" /f
```

- Eliminar tarea (equivalente a "Cancelar reinicio diario"):

```powershell
schtasks /delete /tn "Reinicio_Diario_Medianoche" /f
```

- Mantener la PC despierta (equivalente a "Mantener PC despierta"):

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0
```

- Restaurar suspensión estándar (equivalente a "Permitir suspensión"):

```powershell
powercfg /change monitor-timeout-ac 10
powercfg /change monitor-timeout-dc 5
powercfg /change standby-timeout-ac 30
powercfg /change standby-timeout-dc 15
powercfg /change hibernate-timeout-ac 180
powercfg /change hibernate-timeout-dc 60
```

## Notas de desarrollo

- El código evita `shell=True` y pasa argumentos como lista a `subprocess.run` para mayor seguridad y robustez.
- La detección del sistema operativo usa `platform.system()` + `platform.release()`.
- La aplicación no realiza registro (logging) por decisión del autor.

## Mejoras sugeridas

- Añadir confirmación con horario o ventana de mantenimiento antes del reinicio.
- Opción para programar reinicios en horarios distintos o con notificación previa a usuarios.
- Guardar un histórico de acciones (si se desea trazabilidad).

## Licencia y contacto

Proyecto sin licencia especificada (útil para uso personal). Para dudas o cambios, modifica directamente `main.py` en este repositorio.

## Empaquetado y distribución (Windows)

Se recomienda empaquetar la aplicación en Windows con PyInstaller para generar un ejecutable independiente.

### Opción rápida: `build.bat`

El repositorio incluye un script `build.bat` que automatiza todo el proceso en Windows. Basta con hacer doble clic sobre él (o ejecutar `build.bat` en la terminal) y realiza:

1. Crea el entorno virtual `.venv` (o reutiliza el existente).
2. Instala/actualiza las dependencias desde `requirements.txt` (PyInstaller).
3. Limpia compilaciones anteriores (`build\`, `dist\`, `*.spec`).
4. Genera el ejecutable en `dist\PowerManager.exe` (usa `icon.ico` si está presente).

> Nota: `build.bat` solo funciona en Windows. PyInstaller no genera ejecutables de Windows de forma fiable desde macOS/Linux.

### Opción manual

1. Crear un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
.venv\Scripts\activate      # En Windows
pip install --upgrade pip
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Generar un ejecutable "one-file" (desde Windows):

Con icono personalizado (PyInstaller en Windows espera un archivo `.ico`):

```bash
pyinstaller --onefile --windowed --name PowerManager --icon icon.ico main.py
```

Sin icono:

```bash
pyinstaller --onefile --windowed --name PowerManager main.py
```

- `--onefile` empaqueta todo en un solo `.exe`.
- `--windowed` evita abrir una consola cuando se ejecute la app GUI.

4. Resultado: el ejecutable estará en `dist\PowerManager.exe`.

Notas importantes:
- Construye el ejecutable en Windows; PyInstaller no construye ejecutables de Windows desde macOS/Linux de forma fiable.
- Si la aplicación utiliza recursos externos, puede que necesites opciones adicionales de PyInstaller (`--add-data`, archivos `.spec`).

## Releases automáticas (GitHub Actions)

El repositorio incluye un workflow (`.github/workflows/release.yml`) que compila el `.exe` en un runner de Windows y lo publica como **Release de GitHub** automáticamente. No necesitas compilar ni subir nada a mano.

Para publicar una nueva versión:

1. Actualiza la constante `VERSION` en `main.py` (ej. `1.3.0`).
2. Crea y sube un tag de versión con el mismo número, prefijado con `v`:

```bash
git tag v1.3.0
git push origin v1.3.0
```

3. GitHub Actions se encarga del resto: compila `PowerManager.exe` y lo adjunta a una Release con notas generadas automáticamente. El ejecutable queda disponible en la pestaña **Releases** del repositorio.

> El workflow también puede lanzarse manualmente desde la pestaña **Actions → Release → Run workflow**.

### Crear un instalador (opcional)

Puedes usar Inno Setup para crear un instalador `.exe` profesional:

- Instala Inno Setup: https://jrsoftware.org/isinfo.php
- Crea un script que copie `dist\PowerManager.exe` y cree accesos directos.

Alternativas: `cx_Freeze` o `py2exe`. Para despliegues empresariales, considera crear un MSI.

### Pruebas finales

- Ejecuta `PowerManager.exe` como Administrador para verificar que `powercfg` y `schtasks` funcionan correctamente.
- Verifica que la interfaz GUI arranca sin consola y que las cuatro acciones aplican los cambios esperados.
