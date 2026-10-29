import io, os, shutil, zipfile, urllib.request, urllib.error, sys, importlib.util
import pygame, sverpykit as spk

appdata = os.path.join(
    str(os.getenv("APPDATA")) if os.name == "nt"\
        else os.path.join(os.path.expanduser("~"), ".config"), "GambaOS-Sverryboiii"
)
instances_path = os.path.join(appdata, "instances")
objects: list[spk.SearchBar | spk.Button]
display = spk.set_display(600, 500, title="GambaOS Launcher")

reset: bool = False

def open_instance(instance):
    print(instance)
    global reset
    if reset:
        return

    if instance in sys.path:
        sys.path.remove(instance)
    sys.path.insert(0, instance)
    spec = importlib.util.spec_from_file_location(
        "appdata_GambaOS",
        os.path.join(instance, "src/gambaos/system/GambaOS/main.py")
    )
    gamba_os = importlib.util.module_from_spec(spec)
    print(gamba_os)
    sys.modules["gamba_main"] = gamba_os
    spec.loader.exec_module(gamba_os)

def download_gambaos_version(version: str = "vTEST-0.1.1", dest_directory: str = ""):
    # https://github.com/sverryboiii/gambaos/archive/refs/tags/vTEST-0.1.1.zip
    # Example link

    pygame.event.pump()

    target_dir = os.path.join(instances_path, f"{dest_directory}")

    if os.path.exists(target_dir):
        return {
            "error": "There is already an instance here!"
        }
    os.makedirs(target_dir)

    url = f"https://github.com/sverryboiii/gambaos/archive/refs/tags/{version}.zip"

    try:

        with urllib.request.urlopen(url) as response:
            repo_data = response.read()

        with zipfile.ZipFile(io.BytesIO(repo_data)) as zip_ref:

            root = zip_ref.namelist()[0].split("/")[0]
            src = os.path.join(root, "src")

            for file in zip_ref.infolist():
                if not file.filename.startswith(src):
                    continue

                relative_path = file.filename.replace(f"{root}/", "", 1)
                target_path = os.path.join(target_dir, relative_path)

                if file.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)

                    with zip_ref.open(file) as source, open(target_path, "wb") as dest:
                        shutil.copyfileobj(source, dest)

    except urllib.error.HTTPError:
        return {
            "error": "Invalid url (Please report this to Sverryboiii)!"
        }
    open_instance(os.path.join(instances_path, dest_directory))
    return {}

def get_gambaos_version(instance: str = "TestInstance"):
    full_path = os.path.join(instances_path, instance)
    if os.path.exists(full_path):
        print(full_path)
        open_instance(full_path)
        return
    global objects
    objects = [
        spk.SearchBar(
            rect=pygame.Rect(0, 0, display.get_width(), 50),
            display=display,
            function=download_gambaos_version,
            preset="Version",
            dest_directory=instance
        )
    ]

def frame():
    [part.draw() for part in objects]

def tick():
    [part.events() for part in objects]

def get_gambaos_instance():
    global objects
    objects = [
        spk.SearchBar(
            rect=pygame.Rect(0, 0, display.get_width(), 50),
            display=display,
            function=get_gambaos_version,
            preset="Instance name"
        )
    ]

def main():
    get_gambaos_instance()
    spk.set_frame_method(frame)
    spk.set_tick_method(tick)
    spk.start()

if __name__ == "__main__":
    main()