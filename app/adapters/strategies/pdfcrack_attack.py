from pathlib import Path
import subprocess
import tempfile
import time
from typing import Optional, Callable

from app.core.domain.entities import AttackOptions, CrackResult
from app.core.interfaces.attack_strategy import IAttackStrategy


class PdfCrackAttack(IAttackStrategy):
    """Password cracking using pdfcrack CLI tool."""

    def __init__(self, options: AttackOptions):
        self.options = options

    def _prepare_wordlist(self) -> tuple[Optional[Path], Optional[Path]]:
        if self.options.wordlist_file:
            return self.options.wordlist_file, None

        if not self.options.wordlist:
            return None, None

        temp_file = Path(tempfile.mkstemp(prefix="pdfcrack_wordlist_", suffix=".txt")[1])
        with temp_file.open("w", encoding="utf-8", errors="ignore") as fh:
            for password in self.options.wordlist:
                fh.write(f"{password}\n")
        return temp_file, temp_file

    def _run_command(self, *args: str, timeout: Optional[int] = None, capture: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            list(args),
            check=True,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )

    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> CrackResult:
        start_time = time.time()
        temp_wordlist: Optional[Path] = None

        try:
            wordlist_path, temp_wordlist = self._prepare_wordlist()

            if progress_callback:
                progress_callback(10.0, "Starting pdfcrack")

            args = [self.options.pdfcrack_binary, str(pdf_path)]

            if wordlist_path:
                args.extend(["-w", str(wordlist_path)])
            else:
                args.extend(["-c", "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"])
                args.extend(["-n", str(self.options.min_length), "-m", str(self.options.max_length)])

            proc = self._run_command(*args, capture=True, timeout=self.options.timeout)

            if progress_callback:
                progress_callback(80.0, "Parsing pdfcrack output")

            password: Optional[str] = None
            for line in proc.stdout.splitlines():
                if "found user-password:" in line:
                    password = line.split(":", 1)[-1].strip().strip("'")
                    break

            duration = time.time() - start_time
            if password:
                if progress_callback:
                    progress_callback(100.0, "Password found by pdfcrack")
                return CrackResult(
                    success=True,
                    password=password,
                    method="pdfcrack",
                    attempts=0,
                    duration=duration,
                )

            if progress_callback:
                progress_callback(100.0, "pdfcrack finished without success")
            return CrackResult(
                success=False,
                method="pdfcrack",
                attempts=0,
                duration=duration,
                error="Password not found",
            )

        except subprocess.CalledProcessError as exc:
            return CrackResult(
                success=False,
                method="pdfcrack",
                error=f"Command failed: {' '.join(exc.cmd)}\n{exc.stderr or exc.stdout}",
            )
        except subprocess.TimeoutExpired:
            return CrackResult(
                success=False,
                method="pdfcrack",
                error="pdfcrack operation timed out",
            )
        finally:
            if temp_wordlist and temp_wordlist.exists():
                temp_wordlist.unlink(missing_ok=True)
