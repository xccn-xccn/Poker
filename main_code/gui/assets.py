import pygame
import os


class Scale(float):
    """Returns a rounded integer when multiplied with a float"""

    def __mul__(self, value):
        return round(super().__mul__(value))

    __rmul__ = __mul__


class Assets:
    def __init__(self, screen, base_resolution=(1700, 900)):
        self.screen = screen
        self.base_resolution = base_resolution
        self.current_resolution = screen.get_size()
        self.root = os.path.join(os.path.dirname(__file__), "assets")

        self.colours = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "background": pygame.Color("#009900"),
            "button": (34, 140, 34),
            "button_hover": (60, 160, 100),
            "outline": (0, 0, 0),
        }

        self.fonts = {}
        self.images = {}
        self.sizes = {}

        #Cards are loaded this amount * larger so they can be scaled down for greater detail
        self.card_overscale = 6

        self.rescale(self.current_resolution)

    
    def rescale(self, new_size: tuple[int, int]):
        self.current_resolution = new_size

        self.width, self.height = new_size
        self.centre = tuple(x // 2 for x in new_size)
        self.centrex, self.centrey = self.centre

        bw, bh = self.base_resolution
        self.width_scale = Scale(self.width / bw)
        self.height_scale = Scale(self.height / bh)
        self.min_size_scale = Scale(min(self.width_scale, self.height_scale))
        self._set_sizes()
        self._load_fonts()
        self._load_images()

    def rescale_single(self, x, y):
        """Rescales the input relative to base resolution against current resolution"""
        return x * self.width_scale, y * self.height_scale

    def _set_sizes(self):
        self.sizes["button_w"] = 150 * self.width_scale
        self.sizes["button_h"] = 50 * self.height_scale
        self.sizes["chip_w"] = 40 * self.width_scale
        self.sizes["chip_h"] = 20 * self.height_scale

        self.sizes["util_button_size"] = (
            100 * self.min_size_scale,
            100 * self.min_size_scale,
        )

        table_w = 868 * self.width_scale
        table_h = 423 * self.height_scale
        self.sizes["table_size"] = (table_w, table_h)

        self.sizes["card_w"] = 51 * self.width_scale
        self.sizes["card_h"] = 73 * self.height_scale
        self.sizes["card_buffer"] = 2 * self.height_scale
        
        self.sizes["profile"] = (125 * self.min_size_scale, 125 * self.min_size_scale)

        tx = (self.current_resolution[0] - table_w) // 2
        ty = (self.current_resolution[1] - table_h) // 2
        self.sizes["table_pos"] = (tx, ty)

        tw, th = table_w, table_h
        X1 = tx + 700 / 1000 * tw
        Y1 = ty + th
        X2 = self.current_resolution[0] - X1
        Y2 = self.current_resolution[1] - Y1
        X3 = tx
        Y3 = self.current_resolution[1] / 2
        X4 = self.current_resolution[0] - X3
        self.player_coords = [
            (X1, Y1),
            (X2, Y1),
            (X3, Y3),
            (X2, Y2),
            (X1, Y2),
            (X4, Y3),
        ]

    def _load_fonts(self):
        font_path = os.path.join(self.root, "misc", "JqkasWild-w1YD6.ttf")
        base_size = max(12, int(40 * self.width_scale))
        if os.path.exists(font_path):
            self.fonts["small"] = pygame.font.Font(
                font_path, max(10, int(30 * self.width_scale))
            )
            self.fonts["main"] = pygame.font.Font(font_path, base_size)
            self.fonts["large"] = pygame.font.Font(
                font_path, max(20, int(80 * self.width_scale))
            )
            self.fonts["title"] = pygame.font.Font(
                font_path, max(24, int(120 * self.width_scale))
            )
        else:
            self.fonts["small"] = pygame.font.SysFont(
                "arial", max(10, int(30 * self.width_scale))
            )
            self.fonts["main"] = pygame.font.SysFont("arial", base_size)
            self.fonts["large"] = pygame.font.SysFont(
                "arial", max(20, int(80 * self.width_scale))
            )
            self.fonts["title"] = pygame.font.SysFont(
                "arial", max(24, int(120 * self.width_scale))
            )

    def _load_images(self):
        misc_dir = os.path.join(self.root, "misc")
        cards_dir = os.path.join(self.root, "cards")
        chips_dir = os.path.join(self.root, "chips")
        buttons_dir = os.path.join(self.root, "buttons")

        self._preload_misc_images(misc_dir)
        self._preload_card_images(cards_dir)
        self._preload_chip_images(chips_dir)

        # Button images don't get resized
        if "buttons" not in self.images:
            self._preload_button_images(buttons_dir)

    def _preload_button_images(self, buttons_dir):
        self.images["buttons"] = {}

        for fname in os.listdir(buttons_dir):
            if fname.endswith(".png") or fname.endswith(".jpg"):
                name = os.path.splitext(fname)[0]
                path = os.path.join(buttons_dir, fname)
                self.images["buttons"][name] = pygame.image.load(path).convert_alpha()

    def _preload_misc_images(self, misc_dir):
        table = pygame.image.load(
            os.path.join(misc_dir, "poker_table.png")
        ).convert_alpha()
        self.images["table"] = pygame.transform.smoothscale(
            table, self.sizes["table_size"]
        )

        black_background1 = pygame.image.load(
            os.path.join(misc_dir, "black_background1.jpg")
        ).convert_alpha()
        self.images["black_background1"] = pygame.transform.smoothscale(
            black_background1, self.current_resolution
        )

        # TODO add the rest

    def _preload_card_images(self, cards_dir):
        val_map = {
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "T": "10",
            "J": "jack",
            "Q": "queen",
            "K": "king",
            "A": "ace",
        }
        suit_map = {"C": "clubs", "D": "diamonds", "H": "hearts", "S": "spades"}
        self.images["cards"] = {}
        cw, ch = self.sizes["card_w"] * self.card_overscale, self.sizes["card_h"] * self.card_overscale
        for val, vname in val_map.items():
            for sk, sname in suit_map.items():
                name = f"{vname}_of_{sname}.png"
                path = os.path.join(cards_dir, name)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.images["cards"][val + sk] = pygame.transform.smoothscale(
                        img, (cw, ch)
                    )

        cb = pygame.image.load(os.path.join(cards_dir, "card_back.png")).convert_alpha()
        self.images["cards"]["card_back"] = pygame.transform.smoothscale(
            cb, (cw, ch)
        )


    def get_card(self, card_name, card_zoom=1):
        return pygame.transform.smoothscale_by(self.images["cards"][card_name], card_zoom/self.card_overscale)
    

    def _preload_chip_images(self, chips_dir):
        self.images["chips"] = {}
        cw, ch = self.sizes["chip_w"], self.sizes["chip_h"]
        for fname in os.listdir(chips_dir):
            name = os.path.splitext(fname)[0]
            img = pygame.image.load(os.path.join(chips_dir, fname)).convert_alpha()
            self.images["chips"][name] = pygame.transform.smoothscale(
                img, (cw, ch)
            )

    def get_card_image(self, card_code):
        return self.images.get("cards", {}).get(card_code, self.images["card_back"])

    def get_card_back(self):
        return self.images["card_back"]

    def get_table_image(self):
        return self.images["table"]

    def get_profile_image(self, name):
        path = os.path.join(self.root, "profile_pictures", f"{name}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
        except:
            print('invalid profile pic path')
            return
        return pygame.transform.smoothscale(img, self.sizes["profile"])

    def get_chip_image(self, key):
        return self.images["chips"].get(key)

    def scale_value(self, v):
        return int(v * ((self.width_scale + self.height_scale) / 2))
