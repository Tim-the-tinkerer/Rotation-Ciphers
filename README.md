# Rotation Ciphers

A small, menu-driven cipher toy for ROT13, ROT18, ROT47, and ROT5. **No installer, no Zsh shortcuts, no command options, and no extra Python packages.** Requires Python 3 (3.8 or newer). ROT is reversible obfuscation, **not secure encryption**.

## Open it

**On a Mac:** Keep `Ciphers.command` next to `ciphers.py`. Double-click **Ciphers.command**, then choose a number from the menu. If macOS blocks a downloaded launcher, Control-click it, choose **Open**, and confirm. If the launcher isn't executable, open Terminal in the folder and run `bash Ciphers.command`.

**In Terminal (Mac, Windows, or Linux):** Open the folder and run:

```sh
python3 ciphers.py
```

On Windows, you may need to use `py ciphers.py` instead.

## Use it

1. Choose **1 ROT13** (letters), **2 ROT18** (letters and digits), **3 ROT47** (printable ASCII symbols too), or **4 ROT5** (digits only).
2. Choose **1 Type/paste**, **2 Clipboard**, or **3 File**.
3. For typed/pasted text, finish by typing **`/done` on its own line** and pressing Return. You'll see the result and can save or copy it. Blank lines within the message are okay.
4. Clipboard mode on macOS **replaces your clipboard** with the transformed message; run the same mode again to restore the original text. You can also save a copy.
5. File mode asks for a source file, then suggests an output filename with the rotation added (such as `notes.rot47.txt`). At **SAVE TRANSFORMED FILE**, **press Return** to save alongside the original, **type another filename or path**, or **type `B` to cancel**. You do **not** type `/done` in file mode—that command is only for finishing typed/pasted text. The program confirms success **only after the result has been saved**, and it asks before overwriting an existing file.

Use **B** to go back, and **Q** to quit. There's no separate decode button: applying the same rotation twice restores the original.

Example: ROT13 turns `Hello 123!` into `Uryyb 123!`. ROT18 turns it into `Uryyb 678!`.

**Files:** Transformation is byte-for-byte, preserving line endings, Unicode bytes outside ASCII, and non-text bytes. Files can contain binary data; the app doesn't attempt to display file contents in the terminal.

## About earlier versions

You do **not** need `rot13.py`, `rot47.py`, `ciphers.zsh`, or `Install shortcuts.command` to use this edition. It doesn't edit `.zshrc` or install shell functions. Older shortcuts you previously installed can simply be ignored; this package doesn't change your existing shell settings.
