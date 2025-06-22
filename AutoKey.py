import subprocess
import json

AHK_PATH = r"ahk/AutoHotkey32.exe"
TEMP_AHK_FILE = "ahk/temp_press_key.ahk"
KEYBINDINGS_FILE = "ahk/keybindingsAhk.json"

# Carregar mapeamento uma vez
with open(KEYBINDINGS_FILE, "r") as f:
    keybindings = json.load(f)

def auto_key(key_name):
    if key_name not in keybindings:
        print(f"Tecla '{key_name}' não encontrada no keybindings.json")
        return
    
    ahk_command = keybindings[key_name]
    
    # Cria arquivo .ahk temporário com o comando
    with open(TEMP_AHK_FILE, "w", encoding="utf-8") as f:
        f.write(ahk_command + "\n")
    
    try:
        subprocess.run([AHK_PATH, TEMP_AHK_FILE], check=True)
        print(f"Script AHK executado com sucesso para tecla '{key_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar tecla '{key_name}': {e}")