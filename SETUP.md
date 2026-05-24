# Python setup (Windows)

## What was wrong

`python` and `pip` pointed to the **Microsoft Store stub** at:

`C:\Users\Harshit\AppData\Local\Microsoft\WindowsApps\python.exe`

That shortcut does not run a real interpreter until you install Python from the Store. Hence: *"Python was not found"* and *"pip is not recognized"*.

## Fix applied

**Python 3.12.10** was installed with:

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```

Real binaries live under:

`C:\Users\Harshit\AppData\Local\Programs\Python\Python312\`

## Use these commands

| Instead of | Use |
|------------|-----|
| `python` | `py` |
| `pip install ...` | `py -m pip install ...` |
| `python script.py` | `py script.py` |

### Verify (new terminal or refresh PATH)

```powershell
py --version
py -m pip --version
```

Expected: `Python 3.12.10` and pip from `Python312\Lib\site-packages`.

### Refresh PATH in current PowerShell (if `py` not found)

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Or **close and reopen** the terminal / Cursor.

## Install project dependencies

From the project root:

```powershell
.\scripts\setup-python.ps1
```

Or manually:

```powershell
cd g:\nextleap\projects
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

## Optional: stop the Store stub from hijacking `python`

1. Open **Settings** → **Apps** → **Advanced app settings** → **App execution aliases**
2. Turn **Off** the aliases for `python.exe` and `python3.exe`

After that, `python` may resolve to the real install (if its folder is on PATH).

## Reinstall Python (if needed)

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```
