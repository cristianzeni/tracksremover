import os
import argparse
import subprocess
import shutil
import time
from pydub import AudioSegment
from rich.console import Console
from rich.panel import Panel

console = Console()

class TracksRemover:
    """
    A reusable Core Engine for multi-stem audio separation using Demucs.
    This class is completely independent of the CLI and can be imported into GUIs or scripts.
    """
    def __init__(self, output_base_dir="demucs_temp", model_name="htdemucs_6s"):
        self.output_base_dir = output_base_dir
        self.model_name = model_name

        # HTDemucs_6s outputs exactly these 6 stems.
        self.all_stems = ['vocals.wav', 'drums.wav', 'bass.wav', 'guitar.wav', 'piano.wav', 'other.wav']

        # Mapping terminal arguments to real Demucs filenames
        self.stem_mapping = {
            'vocals': 'vocals.wav',
            'drums': 'drums.wav',
            'bass': 'bass.wav',
            'guitars': 'guitar.wav'
        }

    def _validate_and_get_stems(self, items_to_remove):
        """Internal helper to validate input tokens and calculate stems to keep."""
        if not items_to_remove:
            items_to_remove = "guitars"

        requested = [item.strip().lower() for item in items_to_remove.split(',')]

        invalid = [r for r in requested if r not in self.stem_mapping]
        if invalid:
            raise ValueError(f"Invalid stem(s) requested for removal: {', '.join(invalid)}")

        if len(set(requested)) == 4:
            raise ValueError("Cannot remove all 4 main stems simultaneously.")

        stems_to_remove = [self.stem_mapping[r] for r in requested]
        stems_to_keep = [stem for stem in self.all_stems if stem not in stems_to_remove]
        return stems_to_keep, requested

    def separate_tracks(self, file_path, status_callback=None):
        """Step 1: Runs the external Demucs process."""
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        file_working_dir = os.path.join(self.output_base_dir, base_name)
        os.makedirs(file_working_dir, exist_ok=True)

        command = ["demucs", "-n", self.model_name, file_path, "-o", file_working_dir]
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        start_time = time.time()
        while process.poll() is None:
            time.sleep(0.5)
            if status_callback:
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                status_callback(f"{mins:02d}:{secs:02d}")

        if process.returncode != 0:
            raise RuntimeError(f"Demucs process failed with exit code {process.returncode}")

        return os.path.join(file_working_dir, self.model_name, base_name), file_working_dir

    def mix_stems(self, separated_stems_path, stems_to_keep):
        """Step 2: Core audio mixing logic using pydub."""
        mixed_audio = None
        for stem in stems_to_keep:
            stem_file = os.path.join(separated_stems_path, stem)
            if os.path.exists(stem_file):
                single_audio = AudioSegment.from_wav(stem_file)
                if mixed_audio is None:
                    mixed_audio = single_audio
                else:
                    mixed_audio = mixed_audio.overlay(single_audio)
        return mixed_audio

    def execute(self, file_path, remove_argument=None, status_callback=None):
        """High-level orchestrator method."""
        try:
            stems_to_keep, removed_names = self._validate_and_get_stems(remove_argument)
        except ValueError as e:
            return {"success": False, "error": str(e)}

        original_dir = os.path.dirname(os.path.abspath(file_path))
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        suffix = "".join([f"_no{r.capitalize()}" for r in removed_names])
        final_output_path = os.path.join(original_dir, f"{base_name}{suffix}.mp3")

        working_dir_to_clean = None
        start_time = time.time()

        try:
            # Separation
            stems_path, working_dir_to_clean = self.separate_tracks(file_path, status_callback)

            # Mixing
            mixed_audio = self.mix_stems(stems_path, stems_to_keep)

            if mixed_audio:
                mixed_audio.export(final_output_path, format="mp3")
                return {
                    "success": True,
                    "source": f"{base_name}.mp3",
                    "removed": removed_names,
                    "output": os.path.basename(final_output_path),
                    "duration": round(time.time() - start_time, 1)
                }
            else:
                return {"success": False, "error": "Audio mixing generated an empty file."}

        except Exception as e:
            return {"success": False, "error": str(e)}

        finally:
            if working_dir_to_clean and os.path.exists(working_dir_to_clean):
                shutil.rmtree(working_dir_to_clean)


# ─────────────────────────────────────────────────────────────────────────────────
#  CLI PRESENTATION LAYER (Terminal UI Runner)
# ─────────────────────────────────────────────────────────────────────────────────

def run_cli_mode(engine, target_file, remove_opts):
    console = Console()
    console.print(f"\n 🚀 [bold cyan]Starting[/bold cyan] : {target_file}")

    with console.status(" ⚡ [magenta]AI Demucs[/magenta]  : Separating audio tracks...") as status:
        def update_timer(time_str):
            status.update(f" ⚡ [magenta]AI Demucs[/magenta]  : Separating audio tracks... [bold magenta]({time_str})[/bold magenta]")

        result = engine.execute(target_file, remove_opts, status_callback=update_timer)

    if result["success"]:
        console.print(" ⚡ [magenta]AI Demucs[/magenta]  : Separating audio tracks... Done!")
        console.print(f" 🛠️  [blue]Mixing[/blue]    : Rebuilding track...")

        report_text = (
            f"Status:       [bold green]SUCCESS[/bold green]\n"
            f"Source:       {result['source']}\n"
            f"Removed:      [bold red]{', '.join(result['removed'])}[/bold red]\n"
            f"Output:       [green]{result['output']}[/green]\n"
            f"Time Elapsed: [bold white]{result['duration']} seconds[/bold white]"
        )
        console.print(Panel(report_text, title="[bold]PROCESS REPORT[/bold]", expand=False, border_style="#555555"))
    else:
        console.print(f" [bold red][Error][/bold red] {result['error']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TracksRemover Backend Engine Command Line.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Path to a single MP3 file")
    group.add_argument("-d", "--dir", help="Path to a directory")
    parser.add_argument("-rm", "--remove", type=str, default=None,
                        help="Stems to remove (vocals, guitars, bass, drums)")

    args = parser.parse_args()
    remover_engine = TracksRemover()

    # L'intestazione principale viene stampata una sola volta qui all'avvio effettivo del programma
    console.print("\n [bold r]───────────────────────────────── TRACKS REMOVER CLI ─────────────────────────────────[/bold r]")

    if args.file:
        if os.path.isfile(args.file):
            run_cli_mode(remover_engine, args.file, args.remove)
        else:
            print(f"Error: File does not exist: {args.file}")
    elif args.dir:
        if os.path.isdir(args.dir):
            for root, _, file_list in os.walk(args.dir):
                for f in file_list:
                    if f.lower().endswith('.mp3') and not "_no" in f:
                        run_cli_mode(remover_engine, os.path.join(root, f), args.remove)
        else:
            print(f"Error: Specified directory does not exist: {args.dir}")