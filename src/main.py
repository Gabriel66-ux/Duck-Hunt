import pygame
import random
from pathlib import Path
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT

#==========================================================
#MI MENU QUE ME TIENE CRAZY
#==========================================================
class MenuPrincipal:
    def __init__(self):
        # Definición de colores
        self.NEGRO = (0, 0, 0)
        self.CIAN = (0, 255, 255)
        self.BLANCO = (255, 255, 255)
        self.VERDE_RETRO = (163, 232, 112)
        
        # Inicialización de fuentes
        self.fuente_logo = None
        self.fuente_boton = None
        self.fuente_rec = None
        
        # Configuración del botón de inicio
        self.rect_boton = pygame.Rect(0, 0, 320, 70)
        self.rect_boton.center = (BASE_WIDTH // 2, BASE_HEIGHT // 2 + 30) # Subí este un poco
        self.mouse_encima = False

        # --- NUEVO: Configuración botón REGLAS ---
        self.rect_reglas = pygame.Rect(0, 0, 320, 70)
        self.rect_reglas.center = (BASE_WIDTH // 2, BASE_HEIGHT // 2 + 120)
        self.mouse_en_reglas = False

    def manejar_eventos(self, eventos: list[pygame.event.Event]):
        """Ahora retorna un string indicando la acción"""
        pos_mouse = pygame.mouse.get_pos()
        self.mouse_encima = self.rect_boton.collidepoint(pos_mouse)
        self.mouse_en_reglas = self.rect_reglas.collidepoint(pos_mouse)
        
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "JUGAR"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.mouse_encima:
                    return "JUGAR"
                if self.mouse_en_reglas:
                    return "REGLAS"
        return None

    def dibujar(self, surface: pygame.Surface, records_list: list):
        if self.fuente_logo is None:
            self.fuente_logo = pygame.font.SysFont("Courier New", 80, bold=True)
            self.fuente_boton = pygame.font.SysFont("Courier New", 35, bold=True)
            self.fuente_rec = pygame.font.SysFont("Courier New", 28, bold=True)
        
        surface.fill(self.NEGRO)
        
        # Título
        txt_duck = self.fuente_logo.render("DUCK", True, self.CIAN)
        txt_hunt = self.fuente_logo.render("HUNT", True, self.CIAN)
        surface.blit(txt_duck, txt_duck.get_rect(center=(BASE_WIDTH // 2, 140)))
        surface.blit(txt_hunt, txt_hunt.get_rect(center=(BASE_WIDTH // 2, 220)))
        
        # Botón Jugar
        color_btn = self.BLANCO if self.mouse_encima else self.CIAN
        pygame.draw.rect(surface, color_btn, self.rect_boton, 3)
        txt_btn = self.fuente_boton.render(">>> JUGAR <<<", True, color_btn)
        surface.blit(txt_btn, txt_btn.get_rect(center=self.rect_boton.center))

        # --- NUEVO: Dibujar botón REGLAS ---
        color_reg = self.BLANCO if self.mouse_en_reglas else self.CIAN
        pygame.draw.rect(surface, color_reg, self.rect_reglas, 3)
        txt_reg = self.fuente_boton.render("REGLAS", True, color_reg)
        surface.blit(txt_reg, txt_reg.get_rect(center=self.rect_reglas.center))
        
        # --- SECCIÓN DE RÉCORD MÁXIMO ---
        if records_list and len(records_list) > 0:
            top_nombre = records_list[0]['nombre'].upper()
            top_puntos = records_list[0]['puntos']
            texto_highscore = f"TOP SCORE: {top_nombre} - {top_puntos:06d}"
        else:
            texto_highscore = "TOP SCORE: --- 000000"

        txt_rec = self.fuente_rec.render(texto_highscore, True, self.VERDE_RETRO)
        surface.blit(txt_rec, txt_rec.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT - 60))) # Bajé este a 60

#==========================================================
#MI JUEGO MIS REGLAS
#==========================================================
class PantallaReglas:
    def __init__(self):
        # Usamos fuentes que ya tienes inicializadas en el sistema
        self.fuente_titulo = pygame.font.SysFont("Consolas", 50, bold=True)
        self.fuente_texto = pygame.font.SysFont("Consolas", 22, bold=True)
        self.fuente_volver = pygame.font.SysFont("Consolas", 20, bold=True)
        
        # Lista de reglas claras y concisas
        self.reglas = [
            "1. OBJETIVO: Derriba 10 patos por ronda.",
            "2. MUNICIÓN: Tienes 3 balas por pato.",
            "3. RECARGA: Si aciertas el tiro, recuperas la bala.",
            "4. DERROTA: Si fallas todas las balas, pierdes.",
            "5. ESCAPE: Los patos huyen tras 5 segundos.",
            "6. VICTORIA: Supera la RONDA 5 para ganar."
        ]

    def manejar_eventos(self, eventos):
        """Si el jugador hace click o presiona una tecla, vuelve al menú."""
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN or evento.type == pygame.KEYDOWN:
                return True # Retornar True indica que queremos salir de esta pantalla
        return False

    def dibujar(self, surface):
        # Fondo negro sólido
        surface.fill((0, 0, 0))
        
        # Título en color Cian
        txt_titulo = self.fuente_titulo.render("COMO JUGAR", True, (0, 255, 255))
        rect_titulo = txt_titulo.get_rect(center=(BASE_WIDTH // 2, 80))
        surface.blit(txt_titulo, rect_titulo)
        
        # Línea decorativa
        pygame.draw.line(surface, (0, 255, 255), (100, 120), (BASE_WIDTH - 100, 120), 2)
        
        # Dibujar las reglas con un espaciado vertical
        for i, regla in enumerate(self.reglas):
            # El texto de la regla en blanco
            txt_r = self.fuente_texto.render(regla, True, (255, 255, 255))
            surface.blit(txt_r, (80, 180 + (i * 50)))
        
        # Instrucción para volver al menú en verde neón
        txt_v = self.fuente_volver.render("PRESIONA CUALQUIER TECLA PARA VOLVER", True, (163, 232, 112))
        rect_v = txt_v.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT - 80))
        surface.blit(txt_v, rect_v)



#==========================================================
# GAME OVER QUE ME TIENE CRAZY
#==========================================================
class PantallaGameOver:
    def __init__(self):
        # Configuración de colores
        self.NEGRO = (0, 0, 0)
        self.ROJO = (255, 0, 0)
        self.BLANCO = (255, 255, 255)
        
        # Inicializamos fuentes como None para carga diferida
        self.fuente_grande = None
        self.fuente_puntos = None
        self.fuente_retry = None
        
        # Variables para el efecto de parpadeo (Blink)
        self.mostrar_texto_retry = True
        self.ultimo_parpadeo = pygame.time.get_ticks()

    def manejar_eventos(self, eventos: list[pygame.event.Event]) -> bool:
        """
        Detecta si el jugador quiere salir de la pantalla de Game Over.
        Retorna True si se presiona cualquier tecla o botón del mouse.
        """
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
        return False

    def dibujar(self, surface: pygame.Surface, puntaje_final: int, es_nuevo_record: bool = False):
        """Dibuja la pantalla de fin de juego con el puntaje y efectos visuales."""
        # Carga de fuentes segura dentro del ciclo de dibujo
        if self.fuente_grande is None:
            self.fuente_grande = pygame.font.SysFont("Courier New", 85, bold=True)
            self.fuente_puntos = pygame.font.SysFont("Courier New", 35, bold=True)
            self.fuente_retry = pygame.font.SysFont("Courier New", 25)
            
        surface.fill(self.NEGRO)
        
        # 1. Título principal
        txt_gameover = self.fuente_grande.render("GAME OVER", True, self.ROJO)
        rect_go = txt_gameover.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2 - 60))
        surface.blit(txt_gameover, rect_go)
        
        # 2. Puntaje obtenido
        color_puntos = (0, 255, 0) if es_nuevo_record else self.BLANCO
        txt_puntos = self.fuente_puntos.render(f"FINAL SCORE: {puntaje_final:05d}", True, color_puntos)
        rect_puntos = txt_puntos.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2 + 30))
        surface.blit(txt_puntos, rect_puntos)
        
        # 3. Lógica y dibujo del texto parpadeante (Press any key)
        t_actual = pygame.time.get_ticks()
        if t_actual - self.ultimo_parpadeo > 600:  # Cambia cada 600 milisegundos
            self.mostrar_texto_retry = not self.mostrar_texto_retry
            self.ultimo_parpadeo = t_actual
            
        if self.mostrar_texto_retry:
            txt_retry = self.fuente_retry.render("CONTINUE: PRESS ANY KEY OR CLICK", True, self.BLANCO)
            rect_retry = txt_retry.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT - 120))
            surface.blit(txt_retry, rect_retry)
            
#==========================================================
#PANTALLA DE VICTORIA
#=====≠====================================================
class PantallaVictoria:
    def __init__(self):
        # Inicializamos las fuentes (se cargan en start() del juego)
        self.fuente_titulo = pygame.font.SysFont("Consolas", 60, bold=True)
        self.fuente_puntos = pygame.font.SysFont("Consolas", 40, bold=True)
        self.fuente_input = pygame.font.SysFont("Consolas", 30, bold=True)
        self.fuente_instruccion = pygame.font.SysFont("Consolas", 24, bold=True)
        
        self.nombre = "" # Aquí se guarda el nombre que escribe el usuario
        self.guardado = False # Para saber si ya pulsó Enter

    def manejar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if not self.guardado:
                    if evento.key == pygame.K_RETURN:
                        if len(self.nombre) > 0:
                            self.guardado = True
                            return "GUARDAR" # Avisamos al juego que guarde el record
                    elif evento.key == pygame.K_BACKSPACE:
                        self.nombre = self.nombre[:-1]
                    else:
                        # Limitar el nombre a 10 caracteres y solo letras/números
                        if len(self.nombre) < 10 and evento.unicode.isalnum():
                            self.nombre += evento.unicode.upper()
                else:
                    # Si ya guardó, cualquier tecla vuelve al menú
                    return "MENU"
        return None

    def dibujar(self, surface, puntos_finales):
        surface.fill((0, 0, 0)) 

        # Título
        txt_vic = self.fuente_titulo.render("YOU WIN!", True, (255, 255, 0))
        surface.blit(txt_vic, txt_vic.get_rect(center=(BASE_WIDTH // 2, 100)))

        # Score
        txt_score = self.fuente_puntos.render(f"SCORE: {puntos_finales}", True, (255, 255, 255))
        surface.blit(txt_score, txt_score.get_rect(center=(BASE_WIDTH // 2, 180)))

        # --- SECCIÓN DE ENTRADA DE NOMBRE ---
        if not self.guardado:
            txt_promo = self.fuente_input.render("NUEVO RECORD! ESCRIBE TU NOMBRE:", True, (0, 255, 255))
            surface.blit(txt_promo, txt_promo.get_rect(center=(BASE_WIDTH // 2, 280)))
            
            # El nombre parpadea un poco con un guion bajo (opcional)
            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            txt_nom = self.fuente_titulo.render(self.nombre + cursor, True, (255, 255, 255))
            surface.blit(txt_nom, txt_nom.get_rect(center=(BASE_WIDTH // 2, 350)))
            
            txt_hint = self.fuente_instruccion.render("PRESIONA ENTER PARA GUARDAR", True, (100, 100, 100))
            surface.blit(txt_hint, txt_hint.get_rect(center=(BASE_WIDTH // 2, 420)))
        else:
            txt_done = self.fuente_input.render(f"¡RECORD GUARDADO: {self.nombre}!", True, (0, 255, 0))
            surface.blit(txt_done, txt_done.get_rect(center=(BASE_WIDTH // 2, 320)))
            
            txt_exit = self.fuente_instruccion.render("PRESIONA CUALQUIER TECLA PARA SALIR", True, (255, 255, 255))
            surface.blit(txt_exit, txt_exit.get_rect(center=(BASE_WIDTH // 2, 450)))


# ==========================================================
# 1GESTOR DE RECORDS
# ==========================================================          
import json
from pathlib import Path

class GestorRecords:
    def __init__(self, archivo="records.json"):
        # Localizamos el archivo en la misma carpeta que el script
        self.ruta = Path(__file__).resolve().parent / archivo
        self.max_registros = 5
        self.records = self.cargar_records()

    def cargar_records(self):
        """Carga los records desde el archivo JSON de forma segura."""
        try:
            if self.ruta.exists():
                with open(self.ruta, "r") as f:
                    datos = json.load(f)
                    # Aseguramos que los datos sean una lista
                    return datos if isinstance(datos, list) else []
            return []
        except Exception as e:
            print(f"⚠️ Error al cargar records: {e}")
            return []

    def es_high_score(self, puntaje):
        """Devuelve True si el puntaje entra en el top 5."""
        if len(self.records) < self.max_registros:
            return True
        return puntaje > self.records[-1]["puntos"]

    def guardar_nuevo_record(self, nombre, puntaje):
        """Inserta el record, ordena la lista y actualiza el archivo en disco."""
        nombre_final = nombre.strip().upper() if nombre.strip() else "ANÓNIMO"
        
        self.records.append({"nombre": nombre_final, "puntos": puntaje})
        
        # Ordenamos de mayor a menor según los puntos
        self.records = sorted(self.records, key=lambda x: x["puntos"], reverse=True)
        
        # Mantenemos solo los mejores 5
        self.records = self.records[:self.max_registros]
        
        try:
            with open(self.ruta, "w") as f:
                json.dump(self.records, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error al guardar el archivo de records: {e}")

# ==========================================================
# 1. CLASE MIRA
# ==========================================================
class Mira(pygame.sprite.Sprite):
    def __init__(self, assets_dir: Path):
        super().__init__()
        ruta_imagen = assets_dir / "mira.png"
        try:
            self.image = pygame.image.load(str(ruta_imagen)).convert_alpha()
            self.image = pygame.transform.scale(self.image, (45, 45)) 
        except Exception:
            # Mira de emergencia si no hay imagen
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (15, 15), 15, 2)
            pygame.draw.line(self.image, (255, 0, 0), (15, 0), (15, 30), 2)
            pygame.draw.line(self.image, (255, 0, 0), (0, 15), (30, 15), 2)

        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

    def dibujar(self, superficie):
        superficie.blit(self.image, self.rect)

# ==========================================================
# 2. CLASES DE PATOS
# ==========================================================
class PatoBase:
    def __init__(self, x, y, carpeta_relativa, vel_x, vel_y, assets_dir: Path,dif=1.0):
        self.ruta_sprite = assets_dir / carpeta_relativa
        self.frames_volando = self.cargar_imagenes(self.ruta_sprite / "vuelo")
        self.frames_caida = self.cargar_imagenes(self.ruta_sprite / "caida")
        self.frames_actuales = self.frames_volando
        self.index_frame = 0
        
        if self.frames_actuales:
            self.image = self.frames_actuales[self.index_frame]
        else:
            self.image = pygame.Surface((64, 64))
            self.image.fill((255, 0, 255))
        
        self.rect = self.image.get_rect(center=(x, y))
        self.y_suelo = y
        self.vel_x = vel_x
        self.vel_y = -abs(vel_y)
        self.vivo = True
        self.ultimo_cambio = pygame.time.get_ticks()

    def cargar_imagenes(self, ruta: Path):
        lista = []
        if ruta.exists():
            archivos = sorted([f for f in ruta.iterdir() if f.suffix.lower() in ['.png', '.jpg']])
            for arch in archivos:
                try:
                    img = pygame.image.load(str(arch)).convert_alpha()
                    lista.append(pygame.transform.scale(img, (70, 70)))
                except: continue
        return lista

    def recibir_disparo(self):
        if self.vivo:
            self.vivo = False
            self.estacionario = True
            self.tiempo_muerte = pygame.time.get_ticks()
            self.frames_actuales = self.frames_caida
            self.index_frame = 0
            if self.frames_actuales:
                self.image = self.frames_actuales[0] 
            self.vel_x = 0
            self.vel_y = 0

    def update(self):
        ahora = pygame.time.get_ticks()
        
        if not self.vivo and hasattr(self, 'estacionario') and self.estacionario:
            # Si han pasado 400ms, empezamos la caída real
            if ahora - self.tiempo_muerte > 400:
                self.estacionario = False
                self.vel_y = 8  # Empieza a caer
                # Si tienes varios frames de caída, saltamos el primero (el de impacto)
                if len(self.frames_actuales) > 1:
                    self.index_frame = 1 
            else:
                # Mientras está estacionario, no hacemos nada más
                return
        
        if self.frames_actuales and ahora - self.ultimo_cambio > 80:
            self.ultimo_cambio = ahora
            if not self.vivo:
                if len(self.frames_actuales) > 1:
                    self.index_frame = 1 + (self.index_frame % (len(self.frames_actuales) - 1))
            
            else:        
                self.index_frame = (self.index_frame + 1) % len(self.frames_actuales)
                
            nueva_img = self.frames_actuales[self.index_frame]
            self.image = pygame.transform.flip(nueva_img, True, False) if self.vel_x < 0 else nueva_img

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.vivo:
            if self.rect.left <= 0 or self.rect.right >= BASE_WIDTH: self.vel_x *= -1
            if self.rect.top <= 0 or self.rect.bottom >= BASE_HEIGHT * 0.75: self.vel_y *= -1
            #limite superior y el "suelo" mientras vuela
            if self.rect.left <= 0 or self.rect.right >= BASE_WIDTH:
                self.vel_y = abs(self.vel_y)
            if self.rect.bottom >= self.y_suelo:
                self.vel_y = -abs(self.vel_y)    

class Pato_1(PatoBase):
    def __init__(self, x, y, ad, dif=1.0): 
        super().__init__(x, y, "pato1", 3 * dif, 3 * dif, ad)
        self.puntos = 500
class Pato_2(PatoBase):
    def __init__(self, x, y, ad, dif=1.0): 
        super().__init__(x, y, "pato2", 4 * dif, 4 * dif, ad)
        self.puntos = 1000
class Pato_3(PatoBase):
    def __init__(self, x, y, ad, dif=1.0): 
        super().__init__(x, y, "pato3", 5 *dif, 5 * dif, ad)
        self.puntos = 1500

class Pato_4(PatoBase):
    def __init__(self, x, y, ad, dif=1.0): 
        #Velocidad base de 3, escalada con dificultad
        super().__init__(x, y, "pato4", 3 * dif, 3 * dif, ad)
        self.puntos = 500
        
class Pato_5(PatoBase):
    def __init__(self, x, y, ad, dif=1.0): 
        # Velocidad base de 4, escalada con dificultad
        super().__init__(x, y, "pato5", 4 * dif, 4 * dif, ad)
        self.puntos = 1000
        
class Pato_6(PatoBase):
    def __init__(self, x, y, ad, dif=1.0): 
        # Velocidad base de 5, escalada con dificultad
        super().__init__(x, y, "pato6", 5 * dif, 5 * dif, ad)
        self.puntos = 1500                        

class Perro(pygame.sprite.Sprite):
    def __init__(self, assets_dir: Path):
        super().__init__()
        self.assets_dir = assets_dir / "perro"
        
        # Carga de imágenes
        self.frames_risa = self.cargar_imagenes("risa")
        self.frames_captura = self.cargar_imagenes("captura")
        self.frames_camina = self.cargar_imagenes("camina")
        self.frames_salto = self.cargar_imagenes("salto")
        
        self.frames_actuales = []
        self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.activo = False
        self.estado = "oculto"
        self.frame_idx = 0
        self.timer_anim = 0
        self.x_vel = 2

        self.y_suelo = BASE_HEIGHT * 0.75 
        self.y_caminata = self.y_suelo + 34 
        self.y_emergente = self.y_suelo + 28 
        
        self.esperando_salto = False
        self.duracion_sorpresa = 600 

    def cargar_imagenes(self, subcarpeta):
        lista = []
        ruta = self.assets_dir / subcarpeta
        if ruta.exists():
            archivos = sorted([f for f in ruta.iterdir() if f.suffix.lower() in ['.png', '.jpg']])
            for arch in archivos:
                try:
                    img = pygame.image.load(str(arch)).convert_alpha()
                    lista.append(pygame.transform.scale(img, (120, 120)))
                except: continue    
        return lista
    
    def iniciar_intro(self):
        if not self.frames_camina: return
        self.activo = True
        self.estado = "inicio"
        self.frames_actuales = self.frames_camina
        self.rect.midbottom = (0, self.y_caminata)
        self.tiempo_inicio = pygame.time.get_ticks()
        self.paso_salto = False
        self.esperando_salto = False

    def aparecer(self, tipo, x_pos):
        self.frames_actuales = self.frames_risa if tipo == "risa" else self.frames_captura
        if not self.frames_actuales: return
        
        self.activo = True
        self.estado = "animado"
        self.frame_idx = 0
        self.rect.midbottom = (x_pos, self.y_emergente)
        self.tiempo_inicio = pygame.time.get_ticks()

    def update(self):
        if not self.activo: return
        ahora = pygame.time.get_ticks()

        if self.estado == "inicio":
            self._update_intro(ahora)
        else:
            progreso = ahora - self.tiempo_inicio
            distancia_subida = 90 
            
            # Subida (0.8 segundos)
            if progreso < 800: 
                self.rect.bottom = self.y_emergente - (progreso / 800) * distancia_subida
            # Pausa arriba (1 segundo para que se vea bien)
            elif 800 <= progreso <= 1800:
                self.rect.bottom = self.y_emergente - distancia_subida
            # Bajada (0.7 segundos)
            elif progreso > 1800 and progreso <= 2500: 
                self.rect.bottom = (self.y_emergente - distancia_subida) + ((progreso - 1800) / 700) * distancia_subida
            # Fin de animación
            elif progreso > 2500: 
                self.activo = False
                self.estado = "oculto"

            # Animación de frames
            if ahora - self.timer_anim > 120:
                self.timer_anim = ahora
                if self.frames_actuales:
                    self.frame_idx = (self.frame_idx + 1) % len(self.frames_actuales)

        # Asignación de imagen segura
        if self.frames_actuales:
            idx_seguro = min(self.frame_idx, len(self.frames_actuales) - 1)
            self.image = self.frames_actuales[idx_seguro]

    def _update_intro(self, ahora):
        distancia_centro = BASE_WIDTH // 2 - 60
        
        # 1. Caminar
        if self.rect.x < distancia_centro:
            self.rect.x += self.x_vel
            self.frames_actuales = self.frames_camina
            if ahora - self.timer_anim > 120:
                self.timer_anim = ahora
                self.frame_idx = (self.frame_idx + 1) % len(self.frames_actuales)
            
        # 2. Sorpresa (El momento crítico)
        elif not self.paso_salto:
            if not self.esperando_salto:
                self.esperando_salto = True
                self.tiempo_sorpresa = ahora
                self.frames_actuales = self.frames_salto
                self.frame_idx = 0 # FORZAMOS el frame 0 (el de sorpresa)
            
            # Bloqueamos el índice aquí para que no se mueva durante la pausa
            self.frame_idx = 0 
            
            if ahora - self.tiempo_sorpresa > self.duracion_sorpresa:
                self.paso_salto = True
                self.tiempo_salto = ahora

        # 3. Salto Parabólico
        else:
            t_salto = (ahora - self.tiempo_salto) / 1000 
            if t_salto < 1.2:
                self.rect.x += 3 
                desplazamiento_y = (-900 * t_salto) + (700 * (t_salto**2))
                self.rect.y = self.y_caminata + desplazamiento_y - self.rect.height
                
                if len(self.frames_salto) > 1:
                    # Cicla frames a partir del 1 (omite el de sorpresa)
                    self.frame_idx = 1 + (int(ahora / 100) % (len(self.frames_salto) - 1))
            else:
                self.activo = False
                self.estado = "oculto"

# ==========================================================
# 3. CLASE PRINCIPAL DEL JUEGO
# ==========================================================

# ... (Clases Mira y Patos se mantienen igual, asegúrate de que las rutas existan) ...

class DuckHuntGame(GameBase):
    def __init__(self, metadata: GameMeta):
        super().__init__(metadata)
        self.BASE_DIR = Path(__file__).resolve().parent
        self.ASSETS_DIR = self.BASE_DIR / "sprites"
        
        self.balas_maximas = 3
        self.balas_actuales = 3
        self.aciertos = 0
        self.ronda_actual = 1
        self.mostrar_anuncio_ronda = True 
        self.tiempo_anuncio = 0
        self.patos_derribados_ronda = 0
        self.patos_generados_ronda = 0
        self.max_patos_por_ronda = 10
        self.estados_patos_ronda = [] # Lista de booleanos: True=derribado, False=escapado
        self.mensaje_pato_escapado = False
        self.tiempo_mensaje_escape = 0
        
        # Inicialización de objetos
        self.fuente_pixel = None
        self.fuente_grande = None
        self.imagen_bala = None
        self.fondo = None
        self.mis_patos = []
        self.tipos_de_patos = [Pato_1, Pato_2, Pato_3, Pato_4, Pato_5, Pato_6]
        self.mi_mira = None 
        self.imagen_arbusto = None

    def start(self, surface: pygame.Surface) -> None:
        super().start(surface) 
        
        # REINICIO TOTAL DE VARIABLES
        self.balas_actuales = self.balas_maximas
        self.aciertos = 0
        self.ronda_actual = 1
        self.patos_generados_ronda = 0
        self.estados_patos_ronda = []
        self.mis_patos = [] # Vaciar la lista de patos viejos
        self.mi_mira = Mira(self.ASSETS_DIR)
        self.tiempo_anuncio = pygame.time.get_ticks() # Reset al empezar
        self.perro = Perro(self.ASSETS_DIR)
        self.perro.iniciar_intro() # Lanzamos la animación
        
        self.fuente_pixel = pygame.font.SysFont("Consolas", 24, bold=True)
        self.fuente_grande = pygame.font.SysFont("Consolas", 50, bold=True)

        try:
            # IMPORTANTE: Verifica que los nombres de archivos coincidan exactamente (Mayúsculas/Minúsculas)
            self.fondo = pygame.image.load(str(self.ASSETS_DIR / "nuevo.png")).convert()
            self.fondo = pygame.transform.scale(self.fondo, (BASE_WIDTH, BASE_HEIGHT))
            
            ruta_arbusto = self.ASSETS_DIR / "arbusto.png"
            if ruta_arbusto.exists():
                self.imagen_arbusto = pygame.image.load(str(ruta_arbusto)).convert_alpha()
                self.imagen_arbusto = pygame.transform.scale(self.imagen_arbusto, (BASE_WIDTH, 120))
            else:
                print("⚠️ El archivo arbustos.png no existe en la carpeta sprites")
            
            self.imagen_bala = pygame.image.load(str(self.ASSETS_DIR / "Municion.png")).convert_alpha()
            self.imagen_bala = pygame.transform.scale(self.imagen_bala, (25, 40))
            
            self.imagen_hit_vacia = pygame.image.load(str(self.ASSETS_DIR / "hit_vacio.png")).convert_alpha()
            self.imagen_hit_vacia = pygame.transform.scale(self.imagen_hit_vacia, (25, 25))
            
            self.imagen_hit_llena = pygame.image.load(str(self.ASSETS_DIR / "hit_lleno.png")).convert_alpha()
            self.imagen_hit_llena = pygame.transform.scale(self.imagen_hit_llena, (25, 25))
            print("✅ Recursos cargados correctamente.")
        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}. Se usará fondo de color.")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if self.mostrar_anuncio_ronda or (self.perro.activo and self.perro.estado == "inicio"):
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.balas_actuales > 0:
                    self.balas_actuales -= 1
                    disparo_acertado = False
                    # Posición del mouse ajustada
                    pos_mouse = event.pos

                    for pato in self.mis_patos:
                        if pato.vivo and pato.rect.collidepoint(pos_mouse):
                            pato.recibir_disparo()
                            self.aciertos += pato.puntos
                            self.patos_derribados_ronda += 1
                            disparo_acertado = True
                            if self.balas_actuales < self.balas_maximas:
                                self.balas_actuales += 1
                            break 

    def update(self, dt: float) -> None:
        t = pygame.time.get_ticks()
        
        # 1. ACTUALIZAR SIEMPRE AL PERRO
        self.perro.update()
        
        # 2. BLOQUEAR SPAWN DE PATOS SI EL PERRO ESTÁ EN INTRO
        if self.perro.activo and self.perro.estado == "inicio":
            return # Aquí sí cortamos, porque no queremos patos mientras camina
        
        
        if self.mostrar_anuncio_ronda:
            if t - self.tiempo_anuncio > 2000: 
                if self.ronda_actual > 5: return
                self.mostrar_anuncio_ronda = False
                self.balas_actuales = self.balas_maximas
                self.patos_generados_ronda = 0 
                self.patos_derribados_ronda = 0
                self.estados_patos_ronda = []
            return
        
        # Quitar el mensaje de escape después de 1 segundo
        if self.mensaje_pato_escapado and t - self.tiempo_mensaje_escape > 1000:
            self.mensaje_pato_escapado = False
        
        # SI EL PERRO ESTÁ HACIENDO LA INTRO, NO HACEMOS NADA MÁS
        if self.perro.activo and self.perro.estado == "inicio":
            return

        # 3. CONDICIÓN PARA NUEVO PATO (Sincronizada con el perro)
        # Solo generamos si: no hay patos, no terminó la ronda Y EL PERRO NO ESTÁ EN PANTALLA
        if not self.mis_patos and self.patos_generados_ronda < self.max_patos_por_ronda:
            if not self.perro.activo: # <-- ESTA ES LA CLAVE
                dificultad = 1.0 + (self.ronda_actual - 1) * 0.2
                clase = random.choice(self.tipos_de_patos)
                y_aparicion = int(BASE_HEIGHT * 0.75) 
                nuevo_pato = clase(random.randint(100, BASE_WIDTH-100), y_aparicion, self.ASSETS_DIR, dificultad)
                nuevo_pato.tiempo_nacimiento = t 
                self.mis_patos.append(nuevo_pato)
                self.patos_generados_ronda += 1
                

        # Cambio de ronda
        if self.patos_generados_ronda >= self.max_patos_por_ronda and not self.mis_patos:
            self.ronda_actual += 1
            self.mostrar_anuncio_ronda = True
            self.tiempo_anuncio = t

        for pato in self.mis_patos[:]:
            pato.update()
            # Escapar si pasa el tiempo (empieza a subir)
            if pato.vivo and (t - pato.tiempo_nacimiento > 5000):
                pato.vel_x = 0
                pato.vel_y = -10 

            # ELIMINACIÓN 1: Si escapó por el techo
            if pato.rect.bottom < 0:
                if not self.perro.activo:
                    self.perro.aparecer("risa", pato.rect.centerx)
                
                self.estados_patos_ronda.append(False)
                self.mensaje_pato_escapado = True
                self.tiempo_mensaje_escape = t
                self.mis_patos.remove(pato)
            
        
            # ELIMINACIÓN 2: Si cayó muerto al suelo
            elif not pato.vivo and not pato.estacionario:
                if pato.rect.centery >= int(BASE_HEIGHT * 0.75):
                    if not self.perro.activo:
                        self.perro.aparecer("captura", pato.rect.centerx)
                    
                    self.estados_patos_ronda.append(True) 
                    self.mis_patos.remove(pato) # Solo una vez
        
        # Actualizar al perro
        self.perro.update()
        
        if self.mi_mira: 
            self.mi_mira.update()
            
        if self.balas_actuales == 0 and not self.perro.activo and self.mis_patos:
            # Solo si el pato sigue volando y no tienes munición
            pato_actual = self.mis_patos[0]
            if pato_actual.vivo:
                pato_actual.vel_y = -15 # El pato huye rápido
                if not self.perro.activo:
                    self.perro.aparecer("risa", BASE_WIDTH // 2)    

    def render(self) -> None:
        # 1. Dibujar fondo
        if self.fondo: 
            self.surface.blit(self.fondo, (0, 0))
        else: 
            self.surface.fill((100, 149, 237))

        # 2. Dibujar Patos
        if not self.mostrar_anuncio_ronda:
            for pato in self.mis_patos: 
                self.surface.blit(pato.image, pato.rect)

        # 3. Dibujar Perro (SOLO si NO es la INTRO)
        # Aquí se dibuja cuando sale a reírse o por capturas, quedando detrás del arbusto
        if self.perro.activo and self.perro.estado != "inicio":
            self.surface.blit(self.perro.image, self.perro.rect)

        # 4. Dibujar el Arbusto (Capa de Primer Plano)
        if self.imagen_arbusto:
            y_pos_arbusto = int(BASE_HEIGHT * 0.75) - 90 
            self.surface.blit(self.imagen_arbusto, (0, y_pos_arbusto))

        # 5. Dibujar Perro (SOLO si es la INTRO/CAMINATA)
        # Al dibujarlo DESPUÉS del arbusto, aparecerá mágicamente por encima de él
        if self.perro.activo and self.perro.estado == "inicio":
            self.surface.blit(self.perro.image, self.perro.rect)

        # 6. UI y Anuncios (Siempre al frente de todo)
        if self.mostrar_anuncio_ronda:
            txt = self.fuente_grande.render(f"ROUND {self.ronda_actual}", True, (255, 255, 255))
            self.surface.blit(txt, txt.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2)))
            
            # Dibujar mensaje de "PATO ESCAPADO"
        if self.mensaje_pato_escapado:
            txt_esc = self.fuente_grande.render("FLY AWAY!", True, (255, 255, 255))
            self.surface.blit(txt_esc, txt_esc.get_rect(center=(BASE_WIDTH//2, 150)))
            
        self._dibujar_ui(self.surface)
        
        if self.mi_mira: 
            if not self.mostrar_anuncio_ronda and not (self.perro.activo and self.perro.estado == "inicio"):
                self.mi_mira.dibujar(self.surface)

    def _dibujar_ui(self, surface: pygame.Surface):
        
        # Renderizamos el texto de la ronda actual
        t_ronda_num = self.fuente_pixel.render(f"R = {self.ronda_actual}", True, (0, 255, 0))
        surface.blit(t_ronda_num, (100, BASE_HEIGHT - 152))
        
        # Puntos
        t_ac = self.fuente_pixel.render(f"SCORE: {self.aciertos}", True, (255, 255, 255))
        surface.blit(t_ac, (BASE_WIDTH - 250, BASE_HEIGHT - 90))
        
        # Balas
        for i in range(self.balas_actuales):
            if self.imagen_bala:
                surface.blit(self.imagen_bala, (90 + (i * 35), BASE_HEIGHT - 105))
        
        # Texto "SHOT" justo debajo de las balas
        t_shot = self.fuente_pixel.render("SHOT", True, (0, 255, 255)) # Color cian para que resalte
        surface.blit(t_shot, (114, BASE_HEIGHT - 70))        
                
        #Texto hit
        t_hit = self.fuente_pixel.render("HITS:", True, (0, 255, 0))
        surface.blit(t_hit, (BASE_WIDTH // 2 - 240, BASE_HEIGHT - 90))        
        
        # HIT Icons dinámicos
        for i in range(10):
            x_pos = (BASE_WIDTH // 2 - 160) + (i * 32)
            y_pos = BASE_HEIGHT - 90
            
            # Si el pato ya pasó (está en la lista)
            if i < len(self.estados_patos_ronda):
                if self.estados_patos_ronda[i]: # Fue derribado
                    surface.blit(self.imagen_hit_llena, (x_pos, y_pos))
                else: # Se escapó (Icono vacío o podrías usar uno rojo de 'fail')
                    # Aquí simplemente no dibujamos el lleno, queda el vacío de abajo
                    surface.blit(self.imagen_hit_vacia, (x_pos, y_pos))
                    # Opcional: dibujar una X roja pequeña encima
            else:
                # Patos que aún no salen
                surface.blit(self.imagen_hit_vacia, (x_pos, y_pos))
                
# Asumiendo que tus otras clases (MenuPrincipal, etc.) están importadas o definidas arriba
# ...

class Juego(GameBase):
    def __init__(self, metadata: GameMeta):
        # Pasamos la metadata al constructor padre (GameBase)
        pygame.init()
        pygame.font.init()
        super().__init__(metadata)
        
        # 1. Instanciamos el motor del juego de patos
        # Le pasamos la misma metadata o una personalizada
        self.duck_hunt = DuckHuntGame(metadata)
        
        # 2. Instanciamos las pantallas de interfaz
        self.menu = MenuPrincipal()
        self.pantalla_reglas = PantallaReglas()
        self.pantalla_gameover = PantallaGameOver()
        self.pantalla_victoria = PantallaVictoria()
        self.gestor_records = GestorRecords()
        
        # Estado inicial
        self.estado = "MENU"

    def start(self, surface: pygame.Surface) -> None:
        """Se ejecuta una sola vez al iniciar el juego en el SDK."""
        super().start(surface)
        # Aquí puedes inicializar cosas globales si fuera necesario

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """El SDK llama a este método para procesar eventos."""
        
        if self.estado == "MENU":
            accion = self.menu.manejar_eventos(events)
            if accion == "JUGAR":
                self.duck_hunt.start(self.surface) # Inicializa recursos del juego
                self.estado = "JUGANDO"
            elif accion == "REGLAS":
                self.estado = "REGLAS"

        elif self.estado == "REGLAS":
            if self.pantalla_reglas.manejar_eventos(events):
                self.estado = "MENU"

        elif self.estado == "JUGANDO":
            self.duck_hunt.handle_events(events)

        elif self.estado == "VICTORIA":
            accion = self.pantalla_victoria.manejar_eventos(events)
            if accion == "GUARDAR":
                self.gestor_records.guardar_nuevo_record(
                    self.pantalla_victoria.nombre, 
                    self.duck_hunt.aciertos
                )
            elif accion == "MENU":
                self.estado = "MENU"
                self.pantalla_victoria.guardado = False
                self.pantalla_victoria.nombre = ""

        elif self.estado == "GAMEOVER":
            if self.pantalla_gameover.manejar_eventos(events):
                self.estado = "MENU"

    def update(self, dt: float) -> None:
        """El SDK llama a este método cada frame."""
        t_actual = pygame.time.get_ticks()

        if self.estado == "JUGANDO":
            self.duck_hunt.update(t_actual)
            
            # Chequeo de condiciones de salida
            if self.duck_hunt.ronda_actual > 5:
                pygame.key.start_text_input() # <--- ¡ACTIVA ESTO AQUÍ!
                pygame.mouse.set_visible(True)
                self.estado = "VICTORIA"
            
            # Condición de Game Over
            if self.duck_hunt.balas_actuales <= 0 and not self.duck_hunt.mis_patos:
                pygame.mouse.set_visible(True)
                self.estado = "GAMEOVER"

    def render(self) -> None:
        """El SDK llama a este método para dibujar en pantalla."""
        # Limpiamos la superficie
        self.surface.fill((0, 0, 0))

        if self.estado == "MENU":
            self.menu.dibujar(self.surface, self.gestor_records.records)

        elif self.estado == "REGLAS":
            self.pantalla_reglas.dibujar(self.surface)

        elif self.estado == "JUGANDO":
            self.duck_hunt.render()

        elif self.estado == "VICTORIA":
            self.pantalla_victoria.dibujar(self.surface, self.duck_hunt.aciertos)

        elif self.estado == "GAMEOVER":
            self.pantalla_gameover.dibujar(self.surface, self.duck_hunt.aciertos)

   
# Iniciamos el juego usando el método del SDK               
if __name__ == "__main__":
    meta = (GameMeta()
            .with_title("Duck Hunt Remake")
            .with_description("Derriba a los patos antes de que escapen de la pantalla.")
            .with_release_date("03/03/2026")
            .with_authors(["Gabriel", "Milagros"])
            .add_tag("Arcade")
            .add_tag("Shooter")
            .add_tag("Retro")
            .with_group_number(2)) 
    game = Juego(meta)
    game.run_independently() # <-- Fíjate en el cierre del paréntesis