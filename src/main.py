import pygame
import random
from pathlib import Path
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT

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
                    lista.append(pygame.transform.scale(img, (64, 64)))
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

# ==========================================================
# 3. CLASE PRINCIPAL DEL JUEGO
# ==========================================================
import pygame
import random
from pathlib import Path
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT

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
        
        # Inicialización de objetos
        self.fuente_pixel = None
        self.fuente_grande = None
        self.imagen_bala = None
        self.fondo = None
        self.mis_patos = []
        self.tipos_de_patos = [Pato_1, Pato_2, Pato_3]
        self.mi_mira = None 

    def start(self, surface: pygame.Surface) -> None:
        super().start(surface) 
        pygame.font.init()
        
        self.mi_mira = Mira(self.ASSETS_DIR)
        self.tiempo_anuncio = pygame.time.get_ticks() # Reset al empezar
        
        self.fuente_pixel = pygame.font.SysFont("Consolas", 24, bold=True)
        self.fuente_grande = pygame.font.SysFont("Consolas", 50, bold=True)

        try:
            # IMPORTANTE: Verifica que los nombres de archivos coincidan exactamente (Mayúsculas/Minúsculas)
            self.fondo = pygame.image.load(str(self.ASSETS_DIR / "nuevo.png")).convert()
            self.fondo = pygame.transform.scale(self.fondo, (BASE_WIDTH, BASE_HEIGHT))
            
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
            if self.mostrar_anuncio_ronda:
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
        
        if self.mostrar_anuncio_ronda:
            if t - self.tiempo_anuncio > 2000: 
                if self.ronda_actual > 5: return
                self.mostrar_anuncio_ronda = False
                self.balas_actuales = self.balas_maximas
                self.patos_generados_ronda = 0 
                self.patos_derribados_ronda = 0
            return

        # Lógica de aparición de patos
        if not self.mis_patos and self.patos_generados_ronda < self.max_patos_por_ronda:
            dificultad = 1.0 + (self.ronda_actual - 1) * 0.2
            clase = random.choice(self.tipos_de_patos)
            
            # Aparecen en BASE_HEIGHT * 0.75 (donde suelen estar los arbustos en el fondo)
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
            # Escapar si pasa el tiempo
            if pato.vivo and (t - pato.tiempo_nacimiento > 5000):
                pato.vel_x = 0
                pato.vel_y = -10 
            # ELIMINACIÓN:
            # 1. Si escapó por arriba
            if pato.rect.bottom < 0:
                self.mis_patos.remove(pato)
            # 2. Si cayó y tocó el suelo/arbustos
            elif not pato.vivo and not pato.estacionario and pato.rect.top >= pato.y_suelo:
                self.mis_patos.remove(pato)
        
        if self.mi_mira: 
            self.mi_mira.update()

    def render(self) -> None:
        # Dibujar fondo
        if self.fondo: 
            self.surface.blit(self.fondo, (0, 0))
        else: 
            self.surface.fill((100, 149, 237))

        if self.mostrar_anuncio_ronda:
            txt = self.fuente_grande.render(f"ROUND {self.ronda_actual}", True, (255, 255, 255))
            self.surface.blit(txt, txt.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2)))
            # No retornamos aquí para que la UI se dibuje debajo o encima si es necesario
        else:
            for pato in self.mis_patos: 
                self.surface.blit(pato.image, pato.rect)
            
        self._dibujar_ui(self.surface)
        if self.mi_mira: 
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
        
        # HIT Icons
        hits_logrados = self.patos_derribados_ronda
        for i in range(10):
            x_pos = (BASE_WIDTH // 2 - 160) + (i * 32)
            y_pos = BASE_HEIGHT - 90
            if i < hits_logrados:
                if hasattr(self, 'imagen_hit_llena'): surface.blit(self.imagen_hit_llena, (x_pos, y_pos))
            else:
                if hasattr(self, 'imagen_hit_vacia'): surface.blit(self.imagen_hit_vacia, (x_pos, y_pos))

if __name__ == "__main__":
    meta = (GameMeta()
            .with_title("Duck Hunt Remake")
            .with_description("Derriba a los patos")
            .with_release_date("01/03/2026")
            .with_authors(["Gabriel", "Milagros"])
            .add_tag("Arcade")
            .with_group_number(2))
    
    game = DuckHuntGame(meta)
    game.run_independently() # <-- Fíjate en el cierre del paréntesis