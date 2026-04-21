import ctypes
import platform
import traceback
from pathlib import Path
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Union, List
import time
import tkinter as tk
from tkinter import filedialog
import os
import sys
import inspect
import re
from typing import Optional, Dict, Any
import datetime
import logging



def cronometro(func):
    """
    Decorador para medir el tiempo de ejecución de una función.
    
    Args:
        func: Función a medir
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        print(f"{func.__name__} tomó {fin - inicio:.6f} segundos")
        return resultado
    return wrapper

def try_except(func):
    """
    Decorador para manejar excepciones en funciones.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*arg, **args):
        try:
            return func(*arg, **args)
        except Exception as e:
            describe_el_error(e)
            return None
    return wrapper


def describe_el_error(
    e: Exception, 
    max_depth: int = None, 
    mostrar_libs: bool = False, 
    colorizar: bool = True,
    capturar_variables: bool = True,
    archivo_log: str = None
):
    """
    Muestra un árbol visual de la cadena de llamadas que llevó al error,
    priorizando el código del usuario sobre el código de librerías.
    
    Args:
        e: Excepción a describir
        max_depth: Profundidad máxima del árbol (None para mostrar todo)
        mostrar_libs: Si es True, muestra también las llamadas a librerías
        colorizar: Si es True, coloriza la salida para mejor visualización
        capturar_variables: Si es True, muestra las variables locales en cada frame
        archivo_log: Si se proporciona, guarda el error en este archivo
    """
    # Colores ANSI
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    
    # Deshabilitar colores si no se quieren
    if not colorizar:
        RESET = BOLD = RED = YELLOW = BLUE = GREEN = MAGENTA = CYAN = GRAY = ""
    
    # Símbolos para el árbol
    TREE_BRANCH = "├── "
    TREE_CORNER = "└── "
    TREE_VERTICAL = "│   "
    TREE_SPACE = "    "
    ERROR_SYMBOL = "🔴 "
    USER_CODE_SYMBOL = "👉 "
    LIB_CODE_SYMBOL = "📚 "
    
    # Determinar directorios de usuario vs. librerías
    script_dir = os.path.abspath(os.getcwd())
    site_packages_dirs = [p for p in sys.path if 'site-packages' in p or 'dist-packages' in p]
    
    # Obtener información del traceback
    frames_summary = traceback.extract_tb(e.__traceback__)
    frames_list = []
    
    # Capturar frames para acceder a variables locales
    if capturar_variables:
        frame = sys._getframe()
        while frame:
            frames_list.append(frame)
            frame = frame.f_back
        frames_list.reverse()
    
    # Extraer información del error
    error_type = type(e).__name__
    error_msg = str(e)
    
    # Función para determinar si un archivo es del usuario
    def es_codigo_usuario(filename: str) -> bool:
        if not filename:
            return False
        abs_path = os.path.abspath(filename)
        return (abs_path.startswith(script_dir) and 
                not any(abs_path.startswith(lib_dir) for lib_dir in site_packages_dirs))
    
    # Formatear la línea del frame para mostrar
    def formatear_linea(frame: traceback.FrameSummary, es_ultimo: bool, es_usuario: bool) -> str:
        filename = os.path.basename(frame.filename)
        function = frame.name
        lineno = frame.lineno
        line = frame.line
        
        # Decidir el estilo según el tipo de frame
        prefix = ""
        if es_ultimo:
            prefix = BOLD + RED + ERROR_SYMBOL
        elif es_usuario:
            prefix = BOLD + BLUE + USER_CODE_SYMBOL
        else:
            prefix = GRAY + LIB_CODE_SYMBOL
        
        # Formatear la ubicación y el código
        color = BOLD + (BLUE if es_usuario else GRAY)
        ubicacion = f"{color}{filename}:{lineno}{RESET} en {BOLD}{function}{RESET}"
        codigo = f"{GREEN}'{line.strip() if line else ''}'{RESET}" if line else ""
        
        # Etiquetar según origen
        culpa = ""
        if es_usuario:
            culpa = f"{RED}[TU CÓDIGO] {RESET}"
        elif not es_ultimo:
            culpa = f"{GRAY}[LIBRERÍA] {RESET}"
        
        return f"{prefix}{culpa}{ubicacion} → {codigo}"
    
    # Analizar y explicar errores comunes
    def explicar_error(tipo: str, mensaje: str) -> str:
        explicacion = ""
        
        # Patrones de errores comunes
        if tipo == "TypeError":
            # Error de número de argumentos
            match = re.search(r"(\w+)\(\) takes (\d+) positional arguments? but (\d+) (?:was|were) given", mensaje)
            if match:
                func, esperados, dados = match.groups()
                explicacion = f"La función {func} esperaba {esperados} argumentos pero recibió {dados}"
            
            # Error de tipo de argumento
            match = re.search(r"([\w\.]+)\(\) argument '(\w+)' must be ([\w\.]+), not ([\w\.]+)", mensaje)
            if match:
                func, param, tipo_esperado, tipo_dado = match.groups()
                explicacion = f"Para el parámetro '{param}', se esperaba {tipo_esperado} pero se recibió {tipo_dado}"
        
        elif tipo == "AttributeError":
            match = re.search(r"'([\w\.]+)' object has no attribute '(\w+)'", mensaje)
            if match:
                obj_tipo, atributo = match.groups()
                explicacion = f"Intentaste acceder al atributo '{atributo}' en un objeto de tipo '{obj_tipo}', pero este tipo no tiene ese atributo"
        
        elif tipo == "IndexError":
            match = re.search(r"(list|tuple) index out of range", mensaje)
            if match:
                explicacion = "Intentaste acceder a un índice que está fuera del rango de la lista o tupla"
        
        elif tipo == "KeyError":
            explicacion = f"Intentaste acceder a una clave que no existe en el diccionario: {mensaje}"
        
        elif tipo == "NameError":
            match = re.search(r"name '(\w+)' is not defined", mensaje)
            if match:
                var = match.group(1)
                explicacion = f"La variable o función '{var}' no está definida en este ámbito"
        
        # Si hay explicación, formatearla
        if explicacion:
            explicacion = f"{BOLD}Explicación:{RESET} {explicacion}"
        
        return explicacion
    
    # Obtener variables locales en un frame
    def obtener_variables_locales(frame_idx: int) -> Dict[str, Any]:
        if not capturar_variables or frame_idx >= len(frames_list):
            return {}
        
        frame = frames_list[frame_idx]
        variables = {}
        
        for key, value in frame.f_locals.items():
            if not key.startswith('__') and not inspect.ismodule(value):
                try:
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:47] + "..."
                    
                    tipo = type(value).__name__
                    variables[key] = (str_value, tipo)
                except Exception:
                    variables[key] = ("ERROR_AL_CONVERTIR", "desconocido")
        
        return variables
    
    # Preparar buffer para output
    output_lines = []
    
    def print_buf(text: str = ""):
        output_lines.append(text)
        print(text)
    
    # Imprimir cabecera
    print_buf(f"\n{BOLD}{RED}{'='*50}{RESET}")
    print_buf(f"{BOLD}{RED}ERROR: {error_type}: {error_msg}{RESET}")
    print_buf(f"{BOLD}{RED}{'='*50}{RESET}\n")
    
    # Filtrar frames según configuración
    all_frames = frames_summary.copy()
    frames_con_problemas = []
    
    # Identificar frames de código del usuario
    for i, frame in enumerate(all_frames):
        if es_codigo_usuario(frame.filename) or i == len(all_frames) - 1:
            frames_con_problemas.append(frame)
    
    # Usar todos los frames o solo los problemáticos
    frames_a_mostrar = all_frames if mostrar_libs else frames_con_problemas
    
    # Limitar profundidad si es necesario
    if max_depth is not None and max_depth > 0:
        frames_a_mostrar = frames_a_mostrar[-max_depth:]
    
    # Mostrar resumen de puntos probables del error
    print_buf(f"{BOLD}{RED}Puntos probables del error:{RESET}")
    
    for i, frame in enumerate(frames_a_mostrar):
        es_ultimo = (i == len(frames_a_mostrar) - 1)
        es_usuario = es_codigo_usuario(frame.filename)
        
        if es_usuario or es_ultimo:
            indent = "  "
            simbolo = TREE_CORNER if i == len(frames_a_mostrar) - 1 else TREE_BRANCH
            linea = formatear_linea(frame, es_ultimo, es_usuario)
            print_buf(f"{indent}{simbolo}{linea}")
    
    # Mostrar árbol completo de llamadas
    print_buf(f"\n{BOLD}Árbol completo de llamadas:{RESET}")
    
    for i, frame in enumerate(frames_a_mostrar):
        es_ultimo = (i == len(frames_a_mostrar) - 1)
        es_usuario = es_codigo_usuario(frame.filename)
        
        # Calcular indentación para el árbol
        indent = ""
        for j in range(i):
            indent += TREE_VERTICAL if j < i - 1 else TREE_BRANCH
        
        linea = formatear_linea(frame, es_ultimo, es_usuario)
        print_buf(f"{indent}{linea}")
        
        # Mostrar variables locales si se solicitó
        if capturar_variables:
            variables = obtener_variables_locales(i)
            if variables:
                var_indent = indent.replace(TREE_BRANCH, TREE_VERTICAL)
                print_buf(f"{var_indent}{CYAN}Variables locales:{RESET}")
                
                for idx, (var_name, (var_value, var_type)) in enumerate(sorted(variables.items())):
                    es_ultima_var = idx == len(variables) - 1
                    var_simbolo = TREE_CORNER if es_ultima_var else TREE_BRANCH
                    print_buf(f"{var_indent}{var_simbolo}{CYAN}{var_name}{RESET} ({var_type}) = {MAGENTA}{var_value}{RESET}")
        
        # Mostrar explicación para el último frame
        if es_ultimo:
            print_buf()
            explicacion = explicar_error(error_type, error_msg)
            if explicacion:
                print_buf(f"  {explicacion}")
    
    # Mostrar sugerencias específicas según el tipo de error
    print_buf(f"\n{BOLD}Sugerencias:{RESET}")
    
    if error_type == "TypeError":
        print_buf("  • Verifica que estás pasando el número correcto de argumentos a las funciones")
        print_buf("  • Comprueba los tipos de datos que estás pasando")
        print_buf("  • Revisa la definición de la función para ver qué espera")
    elif error_type == "AttributeError":
        print_buf("  • Verifica que el nombre del atributo o método es correcto (incluyendo mayúsculas/minúsculas)")
        print_buf("  • Comprueba que el objeto sea del tipo que esperas con print(type(objeto))")
        print_buf("  • Usa dir(objeto) para ver qué atributos y métodos tiene disponibles")
    elif error_type == "IndexError":
        print_buf("  • Revisa los índices que usas para acceder a listas o tuplas")
        print_buf("  • Usa len(lista) para verificar la longitud antes de acceder a un índice")
        print_buf("  • Recuerda que los índices empiezan en 0, no en 1")
    
    # Opciones del depurador
    print_buf(f"\n{BOLD}Opciones del depurador:{RESET}")
    print_buf("  • Usa 'describe_el_error(e, mostrar_libs=True)' para ver también las llamadas a librerías")
    print_buf("  • Usa 'describe_el_error(e, max_depth=3)' para limitar la profundidad del árbol")
    print_buf("  • Usa 'describe_el_error(e, capturar_variables=False)' para ocultar las variables locales")
    print_buf("  • Usa 'describe_el_error(e, archivo_log=\"error.log\")' para guardar en un archivo")
    
    # Guardar en archivo si se solicitó
    if archivo_log:
        try:
            # Eliminar códigos ANSI para el archivo
            lineas_limpias = []
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            for linea in output_lines:
                lineas_limpias.append(ansi_escape.sub('', linea))
            
            # Añadir timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encabezado = f"=== ERROR LOG: {timestamp} ===\n"
            
            with open(archivo_log, 'a', encoding='utf-8') as f:
                f.write(encabezado)
                f.write('\n'.join(lineas_limpias))
                f.write('\n\n')
            
            print_buf(f"\n{BOLD}{GREEN}Error guardado en: {archivo_log}{RESET}")
        except Exception as log_error:
            print_buf(f"\n{BOLD}{RED}Error al guardar el log: {str(log_error)}{RESET}")

def input_validado(texto: str, tipo: str, limites: tuple = None) -> Union[Tuple[bool, Union[int, float]], str, int, float]:
    """
    Valida la entrada del usuario según diferentes criterios.
    
    Args:
        texto (str): Mensaje que se mostrará al usuario
        tipo (str): Tipo de validación a realizar
            'entero': Número entero
            'decimal': Número decimal
            'rango_entero': Número entero dentro de un rango
            'texto': Texto no vacío
            'nombre': Nombre (alfanumérico comenzando con letra)
            'rango_decimal': Número decimal dentro de un rango
        limites (tuple, optional): Tupla con (valor_minimo, valor_maximo) para rangos
    
    Returns:
        Union[tuple, str, int, float]: Valor validado según el tipo de entrada requerida
        Para rangos retorna una tupla (bool, number) donde bool indica si está en rango
    """
    TIPOS_VALIDOS = {
        'entero',
        'decimal', 
        'rango_entero',
        'texto',
        'nombre',
        'rango_decimal'
    }
    
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo de validación no válido. Tipos válidos: {TIPOS_VALIDOS}")
    
    if 'rango' in tipo and limites is None:
        raise ValueError("Se requieren límites para validar rangos")

    MENSAJES_ERROR = {
        'numero': "Error: Debe ingresar un número válido",
        'rango': f"Error: El valor debe estar entre {limites[0]} y {limites[1]}" if limites else "",
        'vacio': "Error: El campo no puede estar vacío",
        'primer_caracter': "Error: El primer caracter debe ser una letra",
        'alfanumerico': "Error: Solo se permiten caracteres alfanuméricos y espacios"
    }

    while True:
        try:
            match tipo:
                case 'entero':
                    valor = int(input(texto + ": "))
                    return valor
                    
                case 'decimal':
                    valor = float(input(texto + ": "))
                    return valor
                    
                case 'rango_entero' | 'rango_decimal':
                    tipo_num = 'entero' if tipo == 'rango_entero' else 'decimal'
                    valor = input_validado(f"{texto} ({limites[0]}, {limites[1]}): ", 
                                        tipo_num)
                    
                    if limites[0] <= valor <= limites[1]:
                        return True, valor
                    print(MENSAJES_ERROR['rango'])
                    return False, valor
                    
                case 'texto':
                    valor = input(texto + ': ').strip()
                    if valor:
                        return valor
                    print(MENSAJES_ERROR['vacio'])
                    
                case 'nombre':
                    valor = input_validado(texto + ': ').strip()
                    
                    if not valor[0].isalpha():
                        print(MENSAJES_ERROR['primer_caracter'])
                        continue
                        
                    if not all(c.isalnum() or c.isspace() for c in valor):
                        print(MENSAJES_ERROR['alfanumerico'])
                        continue
                        
                    return valor
                    
        except ValueError:
            print(MENSAJES_ERROR['numero'])



def eleccion(pregunta: str, por_defecto: bool = True, intentos_maximos: int = None) -> bool:
    """ 
    Función para preguntar al usuario si desea continuar con una acción.
    
    Args:
        pregunta: Texto de la pregunta
        por_defecto: Valor a retornar para entrada vacía
        intentos_maximos: Número máximo de intentos antes de usar el valor por defecto.
                         None para intentos ilimitados.
        
    Returns:
        True si la respuesta es afirmativa, False en caso contrario, 
        o el valor por defecto tras entrada vacía o máximo de intentos alcanzado.
    """
    # Respuestas válidas (más completas y flexibles)
    respuestas_afirmativas = {'s', 'si', 'sí', 'y', 'yes', '1', 'true', 'ok'}
    respuestas_negativas = {'n', 'no', '0', 'false', 'nope'}
    
    leyenda = "(S/n)" if por_defecto else "(s/N)"
    intentos = 0
    
    while True:
        try:
            # Mostrar número de intento si hay límite
            prompt = f"\n{pregunta} {leyenda}"
            if intentos_maximos and intentos > 0:
                prompt += f" (intento {intentos + 1}/{intentos_maximos})"
            
            respuesta = input(f"{prompt}: ").strip()
            
            # Si está vacía, usar valor por defecto
            if not respuesta:
                return por_defecto
            
            # Normalizar respuesta (minúsculas, sin acentos)
            respuesta_normalizada = respuesta.lower().replace('í', 'i')
            
            if respuesta_normalizada in respuestas_afirmativas:
                return True
            elif respuesta_normalizada in respuestas_negativas:
                return False
            else:
                intentos += 1
                
                # Si se alcanzó el máximo de intentos, usar valor por defecto
                if intentos_maximos and intentos >= intentos_maximos:
                    print(f"Máximo de intentos alcanzado. Usando valor por defecto: {'Sí' if por_defecto else 'No'}")
                    return por_defecto
                
                # Mensaje de error más informativo
                print("Respuesta no válida. Use 's/si/sí/y/yes/1' para Sí o 'n/no/0' para No.")
                if intentos_maximos:
                    restantes = intentos_maximos - intentos
                    print(f"Intentos restantes: {restantes}")
                
        except (KeyboardInterrupt, EOFError):
            # Manejar Ctrl+C o EOF graciosamente
            print(f"\nOperación cancelada. Usando valor por defecto: {'Sí' if por_defecto else 'No'}")
            return por_defecto



# Variable global para controlar si ya se configuró DPI
_dpi_configurado = False


def _configurar_sistema_automatico():
    """
    Configura el sistema automáticamente para optimal funcionamiento.
    Se ejecuta una sola vez, la primera vez que se usa cualquier función.
    """
    global _dpi_configurado
    
    if _dpi_configurado:
        return
    
    try:
        sistema = platform.system()
        
        # Configuración específica para Windows
        if sistema == 'Windows':
            _configurar_windows_dpi()
            
        # Configuración específica para macOS
        elif sistema == 'Darwin':
            _configurar_macos()
            
        # Linux y otros sistemas Unix generalmente manejan bien el escalado
        elif sistema == 'Linux':
            _configurar_linux()
            
        _dpi_configurado = True
        
    except Exception as e:
        # Si algo falla, continúa sin configuración especial
        logging.debug(f"No se pudo configurar sistema automáticamente: {e}")
        _dpi_configurado = True  # Marcar como configurado para evitar reintentos


def _configurar_windows_dpi():
    """Configuración específica para Windows."""
    try:
        import ctypes
        import os
        # Obtener versión de Windows
        version = platform.version()
        major_version = int(version.split('.')[0]) if '.' in version else 0
        
        if major_version >= 6:  # Windows Vista o superior
            try:
                # Método más moderno (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                try:
                    # Método legacy (Windows Vista+)
                    ctypes.windll.user32.SetProcessDPIAware()
                except (AttributeError, OSError):
                    pass
        
        # Variables de entorno para mejorar renderizado
        os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '1')
        os.environ.setdefault('QT_SCALE_FACTOR', '1')
        
    except Exception:
        pass


def _configurar_macos():
    """Configuración específica para macOS."""
    try:
        import os
        # macOS maneja bien el escalado Retina automáticamente
        # Pero podemos optimizar algunas configuraciones
        os.environ.setdefault('TK_SILENCE_DEPRECATION', '1')
    except Exception:
        pass


def _configurar_linux():
    """Configuración específica para Linux."""
    try:
        import os
        # Linux con entornos de escritorio modernos maneja bien el escalado
        # Configuraciones para mejor compatibilidad con diferentes DEs
        os.environ.setdefault('GDK_SCALE', '1')
        os.environ.setdefault('GDK_DPI_SCALE', '1')
    except Exception:
        pass


def _obtener_ventana_tk() -> tk.Tk:
    """
    Obtiene o crea una ventana Tk de manera segura y optimizada.
    
    Returns:
        Instancia de Tk configurada apropiadamente
    """
    # Configurar sistema automáticamente si es la primera vez
    _configurar_sistema_automatico()
    
    try:
        # Intentar obtener la ventana raíz existente
        root = tk._default_root
        if root is None:
            root = tk.Tk()
            _configurar_tkinter_window(root)
        
        # Configurar la ventana para que no sea visible
        root.withdraw()
        
        # Traer al frente (multiplataforma)
        try:
            root.attributes('-topmost', True)
            # En algunos sistemas, necesitamos bajar el topmost después de un momento
            root.after(100, lambda: root.attributes('-topmost', False))
        except tk.TclError:
            # Fallback para sistemas que no soportan -topmost
            try:
                root.lift()
                root.focus_force()
            except tk.TclError:
                pass
        
        return root
        
    except Exception:
        # Fallback: crear nueva ventana
        root = tk.Tk()
        root.withdraw()
        _configurar_tkinter_window(root)
        return root


def _configurar_tkinter_window(root: tk.Tk):
    """Configuraciones específicas para la ventana Tkinter."""
    try:
        # Configurar escalado si está disponible
        if hasattr(tk, 'call'):
            try:
                tk.call('tk', 'scaling', '-displayof', '.', 1.0)
            except tk.TclError:
                pass
        
        # Configuraciones específicas por sistema
        sistema = platform.system()
        
        if sistema == 'Windows':
            try:
                # Mejorar renderizado de fuentes en Windows
                root.tk.call('tk', 'fontchooser', 'configure', '-visible', False)
            except tk.TclError:
                pass
                
        elif sistema == 'Darwin':  # macOS
            try:
                # Configuraciones específicas para macOS
                root.createcommand('::tk::mac::Quit', root.quit)
            except tk.TclError:
                pass
                
    except Exception:
        pass

def seleccionar_carpeta(
    titulo: str = 'Seleccionar carpeta',
    directorio_inicial: Optional[str] = None
) -> Optional[Path]:
    """ 
    Función para seleccionar una carpeta desde el explorador de archivos.
    Compatible con Windows, macOS y Linux.

    Args:
        titulo: Texto para el título de la ventana de diálogo
        directorio_inicial: Directorio donde abrir el diálogo inicialmente

    Returns:
        Path opcional con la ruta de la carpeta seleccionada,
        o None si no se seleccionó nada.
        
    Raises:
        ImportError: Si tkinter no está disponible
        OSError: Si hay problemas de acceso al sistema de archivos
    """
    try:
        root = _obtener_ventana_tk()
        
        # Parámetros del diálogo
        dialog_params = {
            'title': titulo,
            'mustexist': True,
            'parent': root
        }
        
        if directorio_inicial:
            dialog_params['initialdir'] = str(directorio_inicial)
        
        ruta = filedialog.askdirectory(**dialog_params)
        
        return Path(ruta) if ruta else None
        
    except ImportError:
        error_msg = "tkinter no está disponible en este sistema"
        logging.error(error_msg)
        raise ImportError(error_msg)
        
    except Exception as e:
        logging.error(f"Error al seleccionar carpeta: {e}")
        return None
        
    finally:
        if root and root.winfo_exists():
            root.quit()
            root.destroy()

def seleccionar_archivo(
    titulo: str = 'Seleccionar archivo', 
    filetypes: Optional[List[Tuple[str, str]]] = None,
    directorio_inicial: Optional[str] = None,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """ 
    Función para seleccionar archivo(s) desde el explorador de archivos.
    Compatible con Windows, macOS y Linux.

    Args:
        titulo: Texto para el título de la ventana de diálogo
        filetypes: Lista de tuplas con tipos de archivos permitidos.
                  Si es None, usa todos los archivos por defecto.
        directorio_inicial: Directorio donde abrir el diálogo inicialmente
        multiples: Si True, permite seleccionar múltiples archivos

    Returns:
        Path opcional con la ruta del archivo, lista de Path si multiples=True,
        o None/lista vacía si no se seleccionó nada.
        
    Raises:
        ImportError: Si tkinter no está disponible
        OSError: Si hay problemas de acceso al sistema de archivos

    Examples:
        >>> # Archivo único
        >>> archivo = seleccionar_archivo('Seleccionar imagen', [('PNG', '*.png')])
        >>> 
        >>> # Múltiples archivos
        >>> archivos = seleccionar_archivo('Múltiples', multiples=True)
        >>> 
        >>> # Con directorio inicial
        >>> doc = seleccionar_archivo('PDF', [('PDF', '*.pdf')], Path.cwd())
    """
    # Valor por defecto para filetypes
    if filetypes is None:
        filetypes = [('Todos los archivos', '*.*')]
    
    root = None
    try:
        # Obtener ventana Tk configurada
        root = _obtener_ventana_tk()
        
        # Parámetros comunes del diálogo
        dialog_params = {
            'title': titulo,
            'filetypes': filetypes,
            'parent': root
        }
        
        # Agregar directorio inicial si se especifica
        if directorio_inicial:
            dialog_params['initialdir'] = str(directorio_inicial)
        
        # Seleccionar función según si se permiten múltiples archivos
        if multiples:
            rutas = filedialog.askopenfilenames(**dialog_params)
            resultado = [Path(ruta) for ruta in rutas] if rutas else []
        else:
            ruta = filedialog.askopenfilename(**dialog_params)
            resultado = Path(ruta) if ruta else None
        
        return resultado
        
    except ImportError:
        error_msg = "tkinter no está disponible en este sistema"
        logging.error(error_msg)
        raise ImportError(error_msg)
        
    except Exception as e:
        logging.error(f"Error al seleccionar archivo: {e}")
        return [] if multiples else None
        
    finally:
        # Limpieza cuidadosa de la ventana
        if root:
            try:
                if root.winfo_exists():
                    root.quit()
                    root.destroy()
            except (tk.TclError, AttributeError):
                pass


def seleccionar_imagen(
    titulo: str = "Seleccionar imagen",
    directorio_inicial: Optional[str] = None,
    incluir_webp: bool = True,
    incluir_svg: bool = True,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """ 
    Función especializada para seleccionar archivos de imagen.
    
    Args:
        titulo: Título de la ventana de diálogo
        directorio_inicial: Directorio donde iniciar la búsqueda
        incluir_webp: Si incluir formato WebP en los tipos permitidos
        incluir_svg: Si incluir formato SVG en los tipos permitidos
        multiples: Si permitir seleccionar múltiples imágenes
        
    Returns:
        Path con la imagen seleccionada, lista de Path si multiples=True,
        o None si no se seleccionó nada.
    """
    # Tipos de imagen más completos
    formatos_imagen = "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.gif *.ico"
    
    if incluir_webp:
        formatos_imagen += " *.webp"
    if incluir_svg:
        formatos_imagen += " *.svg"
    
    filetypes = [
        ("Archivos de imagen", formatos_imagen),
        ("PNG", "*.png"),
        ("JPEG", "*.jpg *.jpeg"),
        ("GIF", "*.gif"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
    ]
    
    if incluir_webp:
        filetypes.append(("WebP", "*.webp"))
    if incluir_svg:
        filetypes.append(("SVG", "*.svg"))
        
    filetypes.append(("Todos los archivos", "*.*"))
    
    return seleccionar_archivo(
        titulo=titulo,
        filetypes=filetypes,
        directorio_inicial=directorio_inicial,
        multiples=multiples
    )


def seleccionar_documento(
    titulo: str = "Seleccionar documento",
    directorio_inicial: Optional[str] = None,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """ 
    Función especializada para seleccionar documentos.
    
    Args:
        titulo: Título de la ventana de diálogo
        directorio_inicial: Directorio donde iniciar la búsqueda
        multiples: Si permitir seleccionar múltiples documentos
        
    Returns:
        Path con el documento seleccionado, lista de Path si multiples=True,
        o None si no se seleccionó nada.
    """
    filetypes = [
        ("Documentos", "*.pdf *.doc *.docx *.txt *.rtf *.odt"),
        ("PDF", "*.pdf"),
        ("Word", "*.doc *.docx"),
        ("Texto", "*.txt *.rtf"),
        ("OpenDocument", "*.odt"),
        ("Todos los archivos", "*.*")
    ]
    
    return seleccionar_archivo(
        titulo=titulo,
        filetypes=filetypes,
        directorio_inicial=directorio_inicial,
        multiples=multiples
    )


def seleccionar_csv(
    titulo: str = "Seleccionar archivo CSV",
    directorio_inicial: Optional[str] = None,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """
    Función especializada para seleccionar archivos CSV.
    
    Args:
        titulo: Título de la ventana de diálogo
        directorio_inicial: Directorio donde iniciar la búsqueda
        multiples: Si permitir seleccionar múltiples archivos CSV
        
    Returns:
        Path con el CSV seleccionado, lista de Path si multiples=True,
        o None si no se seleccionó nada.
    """
    filetypes = [
        ("Archivos CSV", "*.csv"),
        ("Archivos de texto separado por comas", "*.csv *.txt"),
        ("Todos los archivos", "*.*")
    ]
    
    return seleccionar_archivo(
        titulo=titulo,
        filetypes=filetypes,
        directorio_inicial=directorio_inicial,
        multiples=multiples
    )


# Función de conveniencia para mantener compatibilidad
def cargar_enlace_imagen() -> Optional[Path]:
    """ 
    Función legacy para cargar una imagen.
    Se recomienda usar seleccionar_imagen() directamente.
    """
    return seleccionar_imagen()


def obtener_info_sistema() -> dict:
    """
    Obtiene información del sistema para debugging.
    
    Returns:
        Diccionario con información del sistema
    """
    return {
        'sistema': platform.system(),
        'version': platform.version(),
        'arquitectura': platform.architecture(),
        'python_version': sys.version,
        'dpi_configurado': _dpi_configurado,
        'tkinter_disponible': 'tkinter' in sys.modules
    }


# Ejemplo de uso de la selección de archivos
if __name__ == "__main__":
    print("=== Selector de Archivos Universal ===")
    print(f"Sistema: {platform.system()}")
    print("=" * 40)
    
    try:
        # Ejemplo básico
        print("1. Seleccionar cualquier archivo:")
        archivo = seleccionar_archivo("Seleccionar cualquier archivo")
        print(f"   Resultado: {archivo}")
        
        # CSV específico
        print("\n2. Seleccionar archivo CSV:")
        csv_path = seleccionar_csv(
            'Selecciona un CSV',
            directorio_inicial=str(Path.cwd())
        )
        print(f"   CSV elegido: {csv_path}")
        
        # Imagen con opciones avanzadas
        print("\n3. Seleccionar imagen (con WebP y SVG):")
        imagen = seleccionar_imagen(
            "Seleccionar imagen",
            incluir_webp=True,
            incluir_svg=True
        )
        print(f"   Imagen seleccionada: {imagen}")


        # Con directorio inicial
        print('\n4. Selección de un documento en el directorio especializado')
        doc = seleccionar_documento(
            "Seleccionar documento",
            directorio_inicial=str(Path.home() / "Documents")
        )
        print(f"   Documento seleccionado: {doc}")
        
        # Información del sistema
        print("\n5. Información del sistema:")
        info = obtener_info_sistema()
        for clave, valor in info.items():
            print(f"   {clave}: {valor}")
            
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        print("Verifique que tkinter esté instalado correctamente.")