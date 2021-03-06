
from pathlib import Path
import argparse
import urllib.request
from src.utils import create_folder


def download_models(model_folder = "laser/models"):
    create_folder(model_folder)
    url = "https://dl.fbaipublicfiles.com/laser/models"
    models = ["bilstm.93langs.2018-12-26.pt", "93langs.fcodes", "93langs.fvocab"]
    for model in models:
        file = f"{model_folder}/{model}"
        if Path(file).exists():
            print(f"{file} is already downloaded")
        else:
            print(f"Downloading {url}/{model}")
            urllib.request.urlretrieve(f"{url}/{model}", file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("laser_folder", nargs='?', default="laser/models")
    args = parser.parse_args()

    download_models(args.laser_folder)