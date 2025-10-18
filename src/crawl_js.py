from playwright.sync_api import sync_playwright
import random 
import time # Añadido para el Failover (Capa 5)
import os   # Añadido para el manejo de archivos
from fake_useragent import UserAgent 
from playwright_stealth import stealth_sync 

# --- FUNCIÓN DE UTILIDAD: Cargar y Rotar Proxies (Capa 1) ---
def load_proxies(filepath="config/proxies.txt"):
    """Carga proxies desde un archivo y devuelve una lista de diccionarios."""
    if not os.path.exists(filepath):
        print("ADVERTENCIA: Archivo de proxies no encontrado. Usando conexión directa.")
        return []
    
    with open(filepath, 'r') as f:
        # Formato esperado: user:pass@ip:port
        proxies = [line.strip() for line in f if line.strip()]
    return proxies
# -----------------------------------------------------------------

def extract_with_js(url, selectores: dict, max_scrolls=8, wait_ms=900, max_retries=3):
    """
    Ejecuta el scraper con Playwright implementando Stealth, Rotación de Proxies y Failover.
    
    Args:
        url (str): URL a scrapear.
        selectores (dict): Selectores de datos.
        max_scrolls (int): Número máximo de scrolls.
        wait_ms (int): Tiempo de espera base.
        max_retries (int): Número máximo de intentos con rotación de identidad/proxy.
    """
    proxies_list = load_proxies() # Cargar la lista de proxies
    
    for attempt in range(max_retries):
        try:
            data = []
            ua = UserAgent().random
            
            # 1. Seleccionar Proxy (Capa 1)
            proxy_config = {}
            if proxies_list:
                # Elige un proxy diferente en cada intento
                proxy_str = random.choice(proxies_list) 
                
                # Simple parsing de 'user:pass@ip:port'
                parts = proxy_str.split('@')
                auth_parts = parts[0].split(':')
                server_parts = parts[1].split(':')

                proxy_config = {
                    'server': f"http://{server_parts[0]}:{server_parts[1]}",
                    'username': auth_parts[0],
                    'password': auth_parts[1]
                }
            
            with sync_playwright() as p:
                # 2. Lanzamiento con Proxy y Contexto Aislado
                browser = p.chromium.launch(
                    headless=True, 
                    proxy=proxy_config if proxy_config else None # Inyectar proxy si existe
                )
                
                ctx = browser.new_context(
                    user_agent=ua,
                    # Dimensiones de pantalla aleatorias (simulación de dispositivo real)
                    viewport={'width': random.randint(1280, 1920), 'height': random.randint(800, 1080)}
                )
                page = ctx.new_page()
                
                # 3. Aplicar Stealth y Headers (Capa 2)
                stealth_sync(page) # Parche crítico anti-detección
                page.set_extra_http_headers({
                    "User-Agent": ua,
                    "Accept-Language": "es-CL,es;q=0.9,en;q=0.8" # Coherencia geográfica
                })
                
                # page.goto() puede levantar la excepción que capturamos
                page.goto(url, wait_until="networkidle", timeout=45000)

                # --- Parche de Scroll Robótico (Capa 4: Movimiento Humano) ---
                last_height = 0
                for _ in range(max_scrolls):
                    # Retraso aleatorio (Throttling)
                    delay = random.uniform(0.5, 1.5) 
                    page.wait_for_timeout(int(delay * 1000)) 

                    # Scroll gradual con rueda del ratón
                    page.mouse.wheel(0, random.randint(500, 1000)) 
                    page.wait_for_timeout(int(random.uniform(0.1, 0.3) * 1000)) # Pausa corta
                    
                    new_h = page.evaluate("document.body.scrollHeight")
                    if new_h == last_height:
                        break
                    last_height = new_h

                # ==========================================================
                ### TU CÓDIGO DE EXTRACCIÓN ORIGINAL VA AQUÍ ###
                # Por ejemplo:
                # data = page.locator('.item-selector').all_inner_texts()
                # O la lógica que tenías para llamar a parser_ficha.py
                # ==========================================================

                browser.close()
                return data # Si la extracción es exitosa, se retorna y sale del bucle
            
        except Exception as e:
            print(f"ERROR en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                # 5. Failover: Espera exponencial y reintento (Capa 5)
                wait_time = 2 ** (attempt + 1)  # 2s, 4s, 8s, ...
                print(f"Cambiando de Proxy/Identidad. Esperando {wait_time} segundos antes de reintentar.")
                time.sleep(wait_time) 
                continue
            else:
                print(f"Fallo después de {max_retries} intentos. Abortando.")
                return [] # Retorna vacío después de fallos