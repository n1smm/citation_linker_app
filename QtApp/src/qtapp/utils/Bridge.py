import  re
import  os
import  sys
import  subprocess
import  pymupdf
from    pathlib         import  Path
from    PySide6.QtCore  import  QObject, Signal

class Bridge(QObject):
    config_path_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


        ### member declarations
        self.parent = parent
        self.input_location = ""
        self.input_dir = ""
        self.output_location = ""
        self.output_dir= ""
        self.input_file_path = ""
        self.output_file_path = ""
        self.user_shell = self.get_user_shell()
        self.config_path = self.get_config_path()



    def get_user_shell(self):
        user_shell = os.environ.get("SHELL")
        if not user_shell and sys.platform == "win32":
            user_shell = os.environ.get("COMSPEC", "cmd.exe")
        self.user_shell = user_shell
        return user_shell

    def get_config_path(self):
        user_shell = self.get_user_shell()
        cmd  = "citation-config --list"
        kwargs = self.set_kwargs()

        try:
            result = subprocess.run(cmd, **kwargs)
            output = result.stdout
            tokens = re.split(r":|\n", output)
            for idx, t in enumerate(tokens):
                if "config location" in t and tokens[idx+1]:
                    self.config_path = tokens[idx+1].strip()
                    print(f"Config path: {self.config_path}")
                elif "config path location file" in t and tokens[idx+1]:
                    self.config_location = tokens[idx+1].strip()
                    print(f"Config location: {self.config_location}")
                elif "input dir" in t and tokens[idx +1]:
                    self.input_dir = tokens[idx+1].strip()
                    print(f"input dir: {self.input_dir}")
                elif "output dir" in t and tokens[idx+1]:
                    self.output_dir = tokens[idx+1].strip()
                    print(f"output dir: {self.output_dir}")
                elif "output location" in t and tokens[idx+1]:
                    self.output_location = tokens[idx+1].strip()
                    print(f"output location: {self.output_location}")
                elif "input location" in t and tokens[idx+1]:
                    self.input_location = tokens[idx+1].strip()
                    print(f"input location: {self.input_location}")
            return self.config_path
        except Exception as e:
            print(f"Error getting config path: {e}")

    def set_kwargs(self, shell=True):
        kwargs = {
                "shell": shell,
                "capture_output": True,
                "text": True
                }
        if self.user_shell and sys.platform != "win32":
            kwargs["executable"] = self.user_shell
        return kwargs


    # TODO change path also for citation-linker
    def set_paths(self, input_dir=None, output_dir=None, config_path=None):
        # cmd = ["citation-config"]
        cmd = "citation-config"
        if input_dir:
           cmd += f" --input {input_dir}"
        if output_dir:
            cmd += f" --output {output_dir}"
        if config_path:
            self.config_path_changed.emit(config_path)
            cmd += f" --config {config_path}"

        # cmd = ["citation-config", "--input", input_dir, "--output", output_dir]
        kwargs = self.set_kwargs(shell=True)

        try:
            print("cmd:", cmd)
            result = subprocess.run(cmd, **kwargs)
            output = result.stdout
            print ("output: ", output)
            print("stderr:", result.stderr)
        except Exception as e:
            print(f"Error modifying paths: {e}")


if __name__ == "__main__":
    bridge = Bridge()
    config_path = bridge.get_config_path()
    bridge.set_paths(input_dir="/home/thiew/code_tuts_other/citation_linker_app/QtApp/input",
                     output_dir="/home/thiew/code_tuts_other/citation_linker_app/QtApp/output")
    print(bridge.input_dir)
    print(bridge.output_dir)
