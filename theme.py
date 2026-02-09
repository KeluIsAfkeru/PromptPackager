import customtkinter as ctk

class Material3:
    COLORS = {
        "light": {
            "bg": "#FDF8FD",
            "surface": "#F3EDF7",
            "surface_variant": "#E7E0EC",
            "primary": "#6750A4",
            "on_primary": "#FFFFFF",
            "secondary": "#625B71",
            "outline": "#79747E",
            "text": "#1D1B20",
            "text_dim": "#49454F",
            "error": "#B3261E",
            "on_error": "#FFFFFF"
        },
        "dark": {
            "bg": "#141218",
            "surface": "#211F26",
            "surface_variant": "#49454F",
            "primary": "#D0BCFF",
            "on_primary": "#381E72",
            "secondary": "#CCC2DC",
            "outline": "#938F99",
            "text": "#E6E1E5",
            "text_dim": "#CAC4D0",
            "error": "#F2B8B5",
            "on_error": "#601410"
        }
    }

    @staticmethod
    def get(key):
        mode = ctk.get_appearance_mode().lower()
        if mode == "system": mode = "dark" 
        return Material3.COLORS[mode].get(key)

    @staticmethod
    def pair(key):
        return (Material3.COLORS["light"][key], Material3.COLORS["dark"][key])