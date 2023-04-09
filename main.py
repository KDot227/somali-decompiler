from assets.pyinstxtractor import PyInstArchive
from zipfile import ZipFile
import subprocess
import requests
import pathlib
import shutil
import sys
import os

from tkinter import Tk
from tkinter import filedialog as kdot2

# hide the tkinter window
# I love stack overflow
root = Tk()
root.withdraw()

root.overrideredirect(True)
root.geometry("0x0+0+0")

root.deiconify()
root.lift()
root.focus_force()


class main:
    def __init__(self) -> None:
        self.ext = "extracted"

        if not os.path.exists("pycdc.exe"):
            build_pycdc()

        self.file = kdot2.askopenfilename(
            title="Select a file to decompile",
            filetypes=(("exe files", "*.exe"), ("All files", "*.*")),
        )
        while not os.path.exists(self.file):
            self.file = kdot2.askopenfilename(
                title="Select a file to decompile",
                filetypes=(("exe files", "*.exe"), ("All files", "*.*")),
            )

        self.file_path = os.path.abspath(self.file)
        self.file = os.path.basename(self.file)

        try:
            self.extracted = PyInstArchive(self.file)
        except Exception as e:
            print(e)
            sys.exit(1)

        self.pyinstxtractor_extract()

        self.get_pyc_info()

    def decompile_pyc(self, pyc_path):
        command = [self.pycdc, pyc_path, "-o", self.py_file_output]
        subprocess.Popen(command).wait()

    def pyinstxtractor_extract(self):
        # I can't get this to work with the normal extract method so we gotta call it from command line :puke:
        out = subprocess.Popen(
            "python assets\\pyinstxtractor.py " + self.file, shell=True
        ).wait()

        if out == 0:
            print("Extracted successfully.")
        else:
            print("Failed to extract.")

    def get_pyc_info(self):
        self.pycdc = "pycdc.exe"
        try:
            os.mkdir(self.ext)
        except FileExistsError:
            pass

        self.extracted_folder_path = os.path.join(os.getcwd(), f"{self.file}_extracted")

        print(self.extracted_folder_path)

        for pyc in os.listdir(self.extracted_folder_path):
            pyc_path = os.path.join(self.extracted_folder_path, pyc)
            ending = pathlib.Path(pyc).suffix
            if ending == ".pyc":
                self.py_file_output = os.path.join(os.getcwd(), self.ext, pyc[:-1])
                self.decompile_pyc(pyc_path)


class build_pycdc:
    def __init__(self) -> None:
        self.url = "https://github.com/zrax/pycdc/archive/refs/heads/master.zip"
        self.checked = False
        if not self.check_cmake():
            sys.exit(1)
        self.download_pycdc_and_install()

    @staticmethod
    def check_cmake() -> None:
        if not shutil.which("cmake"):
            print("Please install cmake and add to path.")
            return False
        else:
            print("Cmake is installed. Continuing...")
            return True

    def download_pycdc_and_install(self) -> None:
        r = requests.get(self.url, stream=True)
        # write to zip file
        with open("pycdc.zip", "wb") as f:
            shutil.copyfileobj(r.raw, f)

        if os.path.exists("pycdc-master.zip"):
            ZipFile("pycdc-master.zip").extractall()
            os.chdir("pycdc-master")
        else:
            ZipFile("pycdc.zip").extractall()
            os.chdir("pycdc-master")
        subprocess.run(["cmake", "."])
        subprocess.run(["cmake", "--build", "."])
        shutil.move("Debug/pycdc.exe", "../pycdc.exe")
        os.chdir("..")
        shutil.rmtree("pycdc-master")
        os.remove("pycdc.zip")


if __name__ == "__main__":
    main()
