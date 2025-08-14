import os
import sys
import subprocess
import shutil
from pathlib import Path

def open_editor(path=None):
    """
    يفتح محرر النصوص للملف المحدد أو يفتح محرر فارغ.
    يحاول استخدام $EDITOR أولاً، ثم يحاول محررات شائعة أو يفتح الملف بالبرنامج الافتراضي.
    """
    if path is None:
        path = Path.cwd() / "untitled.txt"
    else:
        path = Path(path)

    # تأكد من وجود الملف
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")  # ينشئ ملف فارغ

    # جرب $EDITOR أولاً
    editor = os.environ.get("EDITOR")
    if editor:
        try:
            subprocess.run([editor, str(path)])
            return
        except Exception:
            pass

    # تحقق من محررات شائعة في PATH
    candidates = ["nano", "vim", "code", "gedit", "notepad", "kate"]
    for cmd in candidates:
        if shutil.which(cmd):
            # على ويندوز notepad لا يحتاج args إضافية
            try:
                if cmd == "code":
                    subprocess.run([cmd, str(path)])  # VSCode يفتح نافذة
                else:
                    subprocess.run([cmd, str(path)])
                return
            except Exception:
                continue

    # كحل أخير: افتح الملف بالتطبيق الافتراضي حسب النظام
    try:
        if sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", str(path)])
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)])
        elif sys.platform.startswith("win"):
            os.startfile(str(path))  # نوعاً ما لا يستخدم subprocess
        else:
            print("لا يوجد محرر معروف. الملف موجود في:", path)
    except Exception as e:
        print("فشل في فتح المحرر:", e)
        print("يمكنك فتح الملف يدوياً:", path)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("file", nargs="?", help="اسم الملف لفتحه", default=None)
    args = p.parse_args()
    open_editor(args.file)
