#!/usr/bin/env python3
"""A small, menu-driven ROT13 / ROT18 / ROT47 / ROT5 utility.

Run with ``python3 ciphers.py`` (or double-click ``Ciphers.command`` on macOS).
No arguments, installers, shell aliases, or external Python packages required.
"""

import subprocess
import sys
from pathlib import Path


# The tables transform ASCII bytes only. All other bytes pass through unchanged,
# including Unicode UTF-8 sequences and arbitrary binary file data.
def _table(*rotations):
    mapping = bytearray(range(256))
    for first, count, amount in rotations:
        for value in range(first, first + count):
            mapping[value] = first + (value - first + amount) % count
    return bytes(mapping)


CIPHERS = {
    "1": ("ROT13", _table((65, 26, 13), (97, 26, 13))),
    "2": ("ROT18", _table((65, 26, 13), (97, 26, 13), (48, 10, 5))),
    "3": ("ROT47", _table((33, 94, 47),)),
    "4": ("ROT5", _table((48, 10, 5),)),
}


def rotate(data, mode):
    """Transform bytes with a menu mode (1–4). Applying twice restores bytes."""
    return data.translate(CIPHERS[mode][1])


def ask(prompt):
    """Return a line of user input; EOF / Ctrl-C go back without a traceback."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def text_entry():
    print("\nType or paste your text below.")
    print("When finished, type /done on a line by itself and press Return.")
    print("(Blank lines are allowed. Ctrl-C cancels.)\n")
    lines = []
    while True:
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            print("\nCanceled.\n")
            return None
        if line == "":
            # EOF is also a valid way to finish a pasted block.
            break
        if line.rstrip("\r\n") == "/done":
            break
        lines.append(line)
    if not lines:
        print("No text entered.\n")
        return None
    return "".join(lines).encode("utf-8")


def clipboard_read():
    try:
        completed = subprocess.run(["pbpaste"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        print("Clipboard access requires macOS (pbpaste and pbcopy).\n")
        return None
    except OSError as exc:
        print("Could not read clipboard: {}\n".format(exc))
        return None
    except subprocess.CalledProcessError as exc:
        print("Could not read clipboard: {}\n".format(
            exc.stderr.decode("utf-8", "replace").strip() or exc))
        return None
    if not completed.stdout:
        print("The clipboard has no text to transform.\n")
        return None
    return completed.stdout


def clipboard_write(data):
    try:
        subprocess.run(["pbcopy"], input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print("Could not copy result to clipboard: {}".format(exc))
        return False
    print("Copied to clipboard. Apply the same mode again to restore the text.")
    return True


def show_result(data):
    # Do not flood the terminal with a very large clipboard or pasted message.
    limit = 4000
    preview = data[:limit].decode("utf-8", "replace")
    print("\n--- RESULT ---")
    print(preview, end="" if preview.endswith("\n") else "\n")
    if len(data) > limit:
        print("[Preview truncated to 4,000 bytes; save or copy for the full result.]")
    print("--- END ---\n")


def _path(raw):
    # Pasted Finder paths can be quoted or contain shell-escaped spaces.
    path = raw.strip()
    if len(path) >= 2 and path[0] == path[-1] and path[0] in ('"', "'"):
        path = path[1:-1]
    return Path(path.replace("\\ ", " ")).expanduser()


def save_file(data, suggested=None):
    """Ask where to save data; return the saved Path or None if not saved."""
    if suggested is not None:
        print("\nSAVE TRANSFORMED FILE")
        print("Suggested filename: {}".format(suggested.name))
        print("Folder: {}".format(suggested.parent))
        print("Press Return to save using the suggested filename.")
        print("Or type a different filename or full path.")
    else:
        print("\nSAVE RESULT TO FILE")
        print("Enter a filename or full path to save the result.")
    print("Type B to cancel. (/done is only for typed or pasted text.)")

    while True:
        raw = ask("Output filename or path: ")
        if raw is None or raw.strip().lower() == "b":
            print("Save canceled.\n")
            return None
        if raw.strip().lower() == "/done":
            print("/done is for finishing typed text, not saving files.")
            print("Press Return for the suggested filename, or B to cancel.\n")
            continue
        if not raw.strip():
            if suggested is None:
                print("Enter a filename, or B to cancel.\n")
                continue
            path = suggested
        else:
            path = _path(raw)
        try:
            if path.exists():
                if not path.is_file():
                    print("That path is not a regular file. Nothing was saved.\n")
                    return None
                overwrite = ask("File exists. Replace it? (y/N): ")
                if overwrite is None or overwrite.strip().lower() not in ("y", "yes"):
                    print("Not overwritten.\n")
                    return None
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        except OSError as exc:
            print("Could not save file: {}\n".format(exc))
            return None
        # Only report success after the write has completed successfully.
        print("Saved to {} ({} bytes).\n".format(path, len(data)))
        return path


def followup(data, clipboard_already=False):
    while True:
        if clipboard_already:
            choice = ask("[S]ave a copy to file, or Return for menu: ")
        else:
            choice = ask("[S]ave to file, [C]opy to clipboard, or Return for menu: ")
        if choice is None or not choice.strip():
            print()
            return
        choice = choice.strip().lower()
        if choice == "s":
            save_file(data)
            return
        if choice == "c" and not clipboard_already:
            clipboard_write(data)
            print()
            return
        print("Choose one of the shown letters, or press Return.\n")


def file_mode(mode):
    raw = ask("\nInput file path (or Return to cancel): ")
    if raw is None or not raw.strip():
        print("Canceled.\n")
        return
    source = _path(raw)
    try:
        if not source.is_file():
            print("That file does not exist or is not a regular file.\n")
            return
        data = source.read_bytes()
    except OSError as exc:
        print("Could not read file: {}\n".format(exc))
        return
    # By default, put the mode in the name, leaving the source untouched.
    suggested = source.with_name(source.stem + "." + CIPHERS[mode][0].lower() + source.suffix)
    saved_path = save_file(rotate(data, mode), suggested)
    if saved_path is not None:
        print("{} complete. The original file was not changed.\n".format(
            CIPHERS[mode][0]))


def source_menu(mode):
    label = CIPHERS[mode][0]
    while True:
        print("\n{} — choose input".format(label))
        print("  1. Type or paste text")
        print("  2. macOS clipboard (replace clipboard with result)")
        print("  3. File (save result as a new file)")
        print("  B. Back to ciphers")
        choice = ask("Choose: ")
        if choice is None or choice.strip().lower() == "b":
            return
        choice = choice.strip()
        if choice == "1":
            data = text_entry()
            if data is not None:
                result = rotate(data, mode)
                show_result(result)
                followup(result)
        elif choice == "2":
            data = clipboard_read()
            if data is not None:
                result = rotate(data, mode)
                if clipboard_write(result):
                    show_result(result)
                    followup(result, clipboard_already=True)
        elif choice == "3":
            file_mode(mode)
        else:
            print("Please choose 1, 2, 3, or B.")


def main():
    print("ROTATION CIPHERS")
    print("The same mode scrambles and unscrambles. No password needed.")
    while True:
        print("\n  1. ROT13 — letters")
        print("  2. ROT18 — letters and digits")
        print("  3. ROT47 — letters, digits and symbols")
        print("  4. ROT5  — digits only")
        print("  Q. Quit")
        choice = ask("Choose a cipher: ")
        if choice is None or choice.strip().lower() == "q":
            print("Goodbye.")
            return 0
        choice = choice.strip()
        if choice in CIPHERS:
            source_menu(choice)
        else:
            print("Please choose 1, 2, 3, 4, or Q.")


if __name__ == "__main__":
    sys.exit(main())
