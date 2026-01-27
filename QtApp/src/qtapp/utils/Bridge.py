"""
Bridge between Qt GUI and citation linker CLI tools.
Manages subprocess execution and path configuration.
"""
import  re
import  os
import  sys
import  subprocess
import  pymupdf
import  shutil
import  time
from    pathlib                         import  Path
from    PySide6.QtCore                  import  QObject, Signal, Slot

from    citation_linker.configPaths     import  (ensure_defaults, 
                                                  resolve_config_path,
                                                  resolve_dir_paths,
                                                  active_config_file,
                                                  active_dir)
from    citation_linker.multiArticle    import  main as multi_article_main
from    citation_linker.multiFile       import  main as multi_file_main
from    citation_linker.citationLinker  import  main as citation_linker_main

class Bridge(QObject):
    """
    Interface between Qt UI and citation-linker CLI.
    
    Parent: QObject
    Children: None
    
    Handles:
    - Configuration path management via citation-config
    - Subprocess execution of citation linking tools
    - Input/output directory management
    - Document saving and file operations
    """
    config_path_changed = Signal(str)
    linking_finished = Signal(bool, str)

    def __init__(self, parent=None):
        """Initialize bridge with parent app reference."""
        super().__init__(parent)
        
        # Ensure config directories and default files exist on first startup
        # ensure_defaults()

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
        """Detect and return user's shell."""
        user_shell = os.environ.get("SHELL")
        if not user_shell and sys.platform == "win32":
            user_shell = os.environ.get("COMSPEC", "cmd.exe")
        self.user_shell = user_shell
        return user_shell

    def get_config_path(self):
        """
        Retrieve configuration paths directly from configPaths module.
        
        No longer uses subprocess calls - directly imports and calls Python functions
        for bundled executable compatibility.
        
        Returns:
            str: Path to the configuration file
        """
        self.get_input_file_path()
        
        try:
            # Get config path directly
            config_path = resolve_config_path()
            self.config_path = str(config_path)
            
            # Get config location file
            self.config_location = str(active_config_file())
            
            # Get input/output directories
            dir_paths = resolve_dir_paths()
            self.input_dir = str(dir_paths.get("input", ""))
            self.output_dir = str(dir_paths.get("output", ""))
            
            # Get location files for input/output
            self.input_location = str(active_dir(True))
            self.output_location = str(active_dir(False))
            
            # Print for debugging (matching old format)
            print("=========================")
            print(f"config path location file:       {self.config_location}")
            print(f"config location:                 {self.config_path}")
            print("----")
            print(f"input location:                 {self.input_location}")
            print(f"input dir:                      {self.input_dir}")
            print("----")
            print(f"output location:                 {self.output_location}")
            print(f"output dir:                      {self.output_dir}")
            print("----")
            
            return self.config_path
        except Exception as e:
            print(f"Error getting config path: {e}")
            # Set defaults to prevent AttributeError
            self.config_path = ""
            self.config_location = ""
            self.input_dir = ""
            self.output_dir = ""
            self.input_location = ""
            self.output_location = ""

    def get_input_file_path(self):
        """Get the current input file path from parent application."""
        self.input_file_path = self.parent.upload_path
        print("input file bridge component: ", self.input_file_path)



    def set_paths(self, input_dir=None, output_dir=None, config_path=None):
        """
        Update input/output/config paths directly using configPaths functions.
        
        Calls resolve_config_path and resolve_dir_paths to persist path changes.
        Emits config_path_changed signal if config path is set.
        
        Args:
            input_dir: Path to input directory (optional)
            output_dir: Path to output directory (optional)
            config_path: Path to configuration file (optional)
        """
        try:
            # Update config path if provided
            if config_path:
                new_config = resolve_config_path(config_path)
                self.config_path = str(new_config)
                self.config_path_changed.emit(config_path)
                print(f"Config path changed to: {self.config_path}")
            
            # Update input/output directories if provided
            if input_dir or output_dir:
                dirs = {
                    "input": input_dir,
                    "output": output_dir
                }
                dir_paths = resolve_dir_paths(dirs)
                if input_dir and "input" in dir_paths:
                    self.input_dir = str(dir_paths["input"])
                    print(f"Input dir changed to: {self.input_dir}")
                if output_dir and "output" in dir_paths:
                    self.output_dir = str(dir_paths["output"])
                    print(f"Output dir changed to: {self.output_dir}")
        except Exception as e:
            print(f"Error setting paths: {e}")


    def start_linking_process(self, cmd_in=None):
        """
        Execute the citation linking process by calling main functions directly.
        
        The main functions now return exit codes instead of calling sys.exit(),
        so they can be safely called from the Qt application without terminating it.
        
        Workflow:
        1. Save current configuration
        2. Copy input PDF to input directory
        3. Execute citation linking function (multi_article by default)
        4. Verify output file was created
        5. Emit linking_finished signal with success status
        
        Args:
            cmd_in: Function to use: "citation-linker", "citation-multi-file", 
                   or "citation-multi-article". Defaults to citation-multi-article.
                    
        Returns:
            tuple: (success: bool, output_file_path: str)
        """
        self.parent.document_config.save_config()
        self.get_input_file_path()
        base, ext = os.path.splitext(os.path.basename(self.input_file_path))
        self.delete_files_in_dir(self.input_dir)
        shutil.copy(self.input_file_path, os.path.join(self.input_dir, base+ext))
        output_file_base = base + "_linked" + ext
        output_file_path = os.path.join(self.output_dir, output_file_base)

        try:
            # Call the appropriate main function directly
            # They now return exit codes instead of calling sys.exit()
            if cmd_in == "citation-linker":
                return_code = citation_linker_main()
            elif cmd_in == "citation-multi-file":
                return_code = multi_file_main()
            else:
                return_code = multi_article_main()
        except Exception as e:
            print(f"Error during linking process: {e}")
            import traceback
            traceback.print_exc()
            return_code = 1  # Failure
            
        self.output_file_path = output_file_path
        print("output file path: ", output_file_path)
        
        success = return_code == 0 and os.path.exists(output_file_path)
        self.linking_finished.emit(success, output_file_path)
        return (success, output_file_path)


    def delete_files_in_dir(self, dir):
        """
        Delete all files in the specified directory.
        
        Used to clean the input directory before copying new PDF.
        Subdirectories are not removed.
        
        Args:
            dir: Directory path (currently unused, uses self.input_dir)
        """
        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def save_final_doc(self, pymu_doc):
        """
        Save the final processed document to output location.
        
        Document should be closed before calling this to avoid file locks.
        
        Args:
            pymu_doc: PyMuPDF document object to save
        """
        if pymu_doc:
            temp_path = self.output_file_path + ".tmp"
            pymu_doc.save(temp_path)
            
            # Replace existing file
            if os.path.exists(self.output_file_path):
                os.remove(self.output_file_path)
            os.rename(temp_path, self.output_file_path)
            print("file saved")

    def set_kwargs(self, shell=True):
        """
        Configure subprocess keyword arguments for shell command execution.
        
        Args:
            shell: Whether to use shell execution (default: True)
            
        Returns:
            dict: Keyword arguments for subprocess.run()
        """
        kwargs = {
                "shell": shell,
                "capture_output": True,
                "text": True
                }
        if self.user_shell and sys.platform != "win32":
            kwargs["executable"] = self.user_shell
        return kwargs

    def run_process(self, cmd, kwargs):
        """
        Execute a shell command and return its exit code.
        
        Args:
            cmd: Command string to execute
            kwargs: Keyword arguments for subprocess.run()
            
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        try:
            print("cmd:", cmd)
            result = subprocess.run(cmd, **kwargs)
            output = result.stdout
            print ("output: ", output)
            print("stderr:", result.stderr)
            return result.returncode
        except Exception as e:
            print(f"Error running process: {e}")
            return 1



if __name__ == "__main__":
    bridge = Bridge()
    config_path = bridge.get_config_path()
    bridge.set_paths(input_dir="/home/thiew/code_tuts_other/citation_linker_app/QtApp/input",
                     output_dir="/home/thiew/code_tuts_other/citation_linker_app/QtApp/output")
    print(bridge.input_dir)
    print(bridge.output_dir)
