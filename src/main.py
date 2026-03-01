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
    def __init__(self, x, y, carpeta_relativa, vel_x, vel_y, assets_dir: Path):
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
        self.vel_x = vel_x
        self.vel_y = vel_y
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
            self.frames_actuales = self.frames_caida
            self.index_frame = 0 
            self.vel_x = 0
            self.vel_y = 8 

    def update(self):
        ahora = pygame.time.get_ticks()
        if self.frames_actuales and ahora - self.ultimo_cambio > 80:
            self.ultimo_cambio = ahora
            self.index_frame = (self.index_frame + 1) % len(self.frames_actuales)
            nueva_img = self.frames_actuales[self.index_frame]
            self.image = pygame.transform.flip(nueva_img, True, False) if self.vel_x < 0 else nueva_img

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.vivo:
            if self.rect.left <= 0 or self.rect.right >= BASE_WIDTH: self.vel_x *= -1
            if self.rect.top <= 0 or self.rect.bottom >= BASE_HEIGHT * 0.75: self.vel_y *= -1

class Pato_1(PatoBase):
    def __init__(self, x, y, ad): super().__init__(x, y, "pato1", 3, 3, ad)
class Pato_2(PatoBase):
    def __init__(self, x, y, ad): super().__init__(x, y, "pato2", 4, 4, ad)
class Pato_3(PatoBase):
    def __init__(self, x, y, ad): super().__init__(x, y, "pato3", 5, 5, ad)

# ==========================================================
# 3. CLASE PRINCIPAL DEL JUEGO
# ==========================================================
class DuckHuntGame(GameBase):
    def __init__(self, metadata: GameMeta):
        # 1. Configuración inicial de datos
        super().__init__(metadata)
        self.BASE_DIR = Path(__file__).resolve().parent
        self.ASSETS_DIR = self.BASE_DIR / "sprites"
        
        self.balas_maximas = 3
        self.balas_actuales = 3
        self.aciertos = 0
        self.ronda_actual = 1
        self.mostrar_anuncio_ronda = True 
        self.tiempo_anuncio = pygame.time.get_ticks()
        self.ultimo_pato_tiempo = 0
        self.espera_entre_patos = 2000
        
        # Inicializamos los objetos en None
        self.fuente_pixel = None
        self.fuente_grande = None
        self.imagen_bala = None
        self.fondo = None
        self.mis_patos = []
        self.tipos_de_patos = [Pato_1, Pato_2, Pato_3]
        self.mi_mira = None 

    def start(self, surface: pygame.Surface) -> None:
        # 2. Carga de recursos (Se ejecuta una sola vez al inicio)
        super().start(surface) 
        pygame.font.init() # <-- IMPORTANTE: Inicializa fuentes aquí
        
        self.mi_mira = Mira(self.ASSETS_DIR)
        
        # Carga de fuentes después de inicializar
        self.fuente_pixel = pygame.font.SysFont("Arial", 24, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 50, bold=True)

        try:
            # Carga de imágenes
            self.imagen_bala = pygame.transform.scale(pygame.image.load(str(self.ASSETS_DIR / "Municion.png")), (25, 40))
            self.fondo = pygame.transform.scale(pygame.image.load(str(self.ASSETS_DIR / "nuevo.png")), (BASE_WIDTH, BASE_HEIGHT))
            print("✅ Recursos cargados.")
        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}")
            
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        # 3. Entrada del usuario
        for event in events:
            if not self.mostrar_anuncio_ronda and event.type == pygame.MOUSEBUTTONDOWN:
                if self.balas_actuales > 0:
                    self.balas_actuales -= 1
                    # Lógica de disparo...
                    for pato in self.mis_patos:
                        if pato.vivo and pato.rect.collidepoint(event.pos):
                            pato.recibir_disparo()
                            self.aciertos += 1
                            if self.aciertos % 10 == 0:
                                self.ronda_actual += 1
                                self.mostrar_anuncio_ronda = True
                                self.tiempo_anuncio = pygame.time.get_ticks()
                                self.mis_patos = []
                            break

    def update(self, dt: float) -> None:
        # 4. Lógica de juego constante
        t = pygame.time.get_ticks()
        
        if self.mostrar_anuncio_ronda:
            if t - self.tiempo_anuncio > 2000: 
                self.mostrar_anuncio_ronda = False
                self.balas_actuales = self.balas_maximas
            return

        # Aparición de patos
        if t - self.ultimo_pato_tiempo > self.espera_entre_patos:
            clase = random.choice(self.tipos_de_patos)
            self.mis_patos.append(clase(random.randint(100, BASE_WIDTH-100), int(BASE_HEIGHT*0.6), self.ASSETS_DIR))
            self.ultimo_pato_tiempo = t

        # Update de entidades
        for pato in self.mis_patos[:]:
            pato.update()
            if not pato.vivo and pato.rect.top > BASE_HEIGHT: 
                self.mis_patos.remove(pato)
        
        if self.mi_mira: self.mi_mira.update()

    def render(self) -> None:
        # 5. Dibujo (Se ejecuta muchas veces por segundo)
        # Usamos self.surface (propiedad del SDK)
        if self.fondo: self.surface.blit(self.fondo, (0, 0))
        else: self.surface.fill((100, 149, 237))

        if self.mostrar_anuncio_ronda:
            txt = self.fuente_grande.render(f"ROUND {self.ronda_actual}", True, (255, 255, 255))
            self.surface.blit(txt, txt.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2)))
            return 

        for pato in self.mis_patos: 
            self.surface.blit(pato.image, pato.rect)
            
        self._dibujar_ui(self.surface) # Llamada a función auxiliar
        if self.mi_mira: 
            self.mi_mira.dibujar(self.surface)

    def _dibujar_ui(self, surface: pygame.Surface):
        # 6. Función auxiliar de dibujo
        t_ac = self.fuente_pixel.render(f"PUNTOS: {self.aciertos}", True, (255, 255, 255))
        surface.blit(t_ac, (BASE_WIDTH - 250, BASE_HEIGHT - 60))
        
        # Balas
        if self.imagen_bala:
            for i in range(self.balas_actuales):
                surface.blit(self.imagen_bala, (40 + (i * 35), BASE_HEIGHT - 60))
        else:
            t_balas = self.fuente_pixel.render(f"BALAS: {self.balas_actuales}", True, (255, 255, 255))
            surface.blit(t_balas, (40, BASE_HEIGHT - 60))

if __name__ == "__main__":
    meta = (GameMeta()
            .with_title("Duck Hunt Remake")
            .with_description("Derriba a los patos")
            .with_release_date("01/03/2026")
            .with_authors(["Gabriel", "Milagros"])
            .add_tag("Arcade")
            .with_group_number(2))
    
    game = DuckHuntGame(meta)
    game.run_independently()