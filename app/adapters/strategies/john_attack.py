from pathlib import Path
import subprocess
import tempfile
import time
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

from app.core.domain.entities import AttackOptions, CrackResult
from app.core.interfaces.attack_strategy import IAttackStrategy


class JohnTheRipperAttack(IAttackStrategy):
    """Password cracking using John the Ripper."""

    def __init__(self, options: AttackOptions):
        self.options = options

    def _prepare_wordlist(self) -> tuple[Optional[Path], Optional[Path]]:
        if self.options.wordlist_file:
            return self.options.wordlist_file, None

        if not self.options.wordlist:
            return None, None

        temp_file = Path(tempfile.mkstemp(prefix="john_wordlist_", suffix=".txt")[1])
        with temp_file.open("w", encoding="utf-8", errors="ignore") as fh:
            for password in self.options.wordlist:
                fh.write(f"{password}\n")
        return temp_file, temp_file

    def _run_command(self, *args: str, capture: bool = False, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Run external command with improved error handling"""
        import shutil

        # Check if command exists
        cmd_name = args[0] if args else ""
        if not shutil.which(cmd_name):
            raise FileNotFoundError(f"Command not found: {cmd_name}")

        try:
            return subprocess.run(
                list(args),
                check=True,
                capture_output=capture,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timed out after {timeout}s: {' '.join(args)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(args)}")
            logger.error(f"Return code: {e.returncode}")
            if e.stdout:
                logger.error(f"Stdout: {e.stdout[:1000]}...")  # Limit output size
            if e.stderr:
                logger.error(f"Stderr: {e.stderr[:1000]}...")  # Limit output size
            raise

    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> CrackResult:
        start_time = time.time()
        hash_file: Optional[Path] = None
        temp_wordlist: Optional[Path] = None

        def cleanup_temp_files():
            """Safely cleanup temporary files"""
            for temp_file in [hash_file, temp_wordlist]:
                if temp_file and temp_file.exists():
                    try:
                        temp_file.unlink()
                        logger.debug(f"Cleaned up temp file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")

        try:
            if progress_callback:
                progress_callback(5.0, "Generating hash with pdf2john")

            with tempfile.NamedTemporaryFile(prefix="pdf_hash_", suffix=".txt", delete=False) as tmp_hash:
                hash_file = Path(tmp_hash.name)
                proc = self._run_command(
                    self.options.pdf2john_binary,
                    str(pdf_path),
                    capture=True,
                    timeout=self.options.timeout,
                )
                tmp_hash.write(proc.stdout.encode("utf-8", errors="ignore"))

            if hash_file.stat().st_size == 0:
                return CrackResult(success=False, method="john", error="pdf2john produced empty hash")

            wordlist_path, temp_wordlist = self._prepare_wordlist()

            if progress_callback:
                progress_callback(25.0, "Running John the Ripper")

            john_cmd = [self.options.john_binary, "--format=pdf", str(hash_file)]
            if wordlist_path:
                john_cmd.extend(["--wordlist", str(wordlist_path)])

            self._run_command(*john_cmd, timeout=self.options.timeout)

            if progress_callback:
                progress_callback(80.0, "Retrieving results from John")

            show_proc = self._run_command(
                self.options.john_binary,
                "--show",
                "--format=pdf",
                str(hash_file),
                capture=True,
            )

            password: Optional[str] = None
            for line in show_proc.stdout.splitlines():
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[1].strip():
                    password = parts[1].strip()
                    break

            duration = time.time() - start_time
            if password:
                if progress_callback:
                    progress_callback(100.0, "Password found by John the Ripper")
                return CrackResult(
                    success=True,
                    password=password,
                    method="john",
                    attempts=0,
                    duration=duration,
                )

            if progress_callback:
                progress_callback(100.0, "John the Ripper finished without success")
            return CrackResult(
                success=False,
                method="john",
                attempts=0,
                duration=duration,
                error="Password not found",
            )

        except subprocess.CalledProcessError as exc:
            return CrackResult(
                success=False,
                method="john",
                error=f"Command failed: {' '.join(exc.cmd)}\n{exc.stderr or exc.stdout}",
            )
        except subprocess.TimeoutExpired:
            return CrackResult(
                success=False,
                method="john",
                error="John the Ripper operation timed out",
            )
        finally:
            cleanup_temp_files()
