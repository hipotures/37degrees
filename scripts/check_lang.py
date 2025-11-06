#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sprawdzanie zgodności języka w plikach audio względem kodu w nazwie pliku.
Wspierane rozszerzenia: .m4a, .mp4
Wzorzec nazwy: NNNN_xxxx_LANG.[mp4|m4a]  -> LANG to dwuliterowy kod ISO-639-1, np. pl, en, de.

Domyślnie:
- przeszukuje tylko podany folder (bez podkatalogów; domyślnie ".")
- wykrywa język z audio przez Whisper
- wypisuje TYLKO pliki z niezgodnością
- brak outputu = brak niezgodności

Opcje:
- --folder PATH
- --model {tiny,base,small,medium,large,turbo,...}
- --device {auto,cpu,cuda}
- --threads N  (gdy CPU)
- --transcription            (włącza pełną transkrypcję)
- --format {txt,vtt,srt,tsv,json,all}  (format plików transkrypcji)
- --debug
- --whisper-args ...         (dowolne dodatkowe parametry dla model.transcribe; składnia zbliżona do CLI Whisper)

Przykład:
python check_lang.py --folder books/0100_the_left_hand_of_darkness/audio --model medium --device cuda --debug
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Torch i Whisper ładowane dopiero po sparsowaniu argumentów,
# aby móc ustawić wątki przed importem torch.
torch = None
whisper = None


FNAME_LANG_RE = re.compile(r".*_([a-z]{2})\.(m4a|mp4)$", re.IGNORECASE)
AUDIO_EXTS = {".m4a", ".mp4"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detekcja języka w plikach audio i weryfikacja zgodności z kodem w nazwie pliku (Whisper)."
    )
    parser.add_argument("--folder", type=str, default=".", help="Folder z plikami audio (bez podkatalogów).")
    parser.add_argument("--model", type=str, default="turbo", help="Nazwa modelu Whisper, np. tiny/base/small/medium/large/turbo.")
    parser.add_argument("--device", type=str, choices=["auto", "cpu", "cuda"], default="auto", help="Urządzenie obliczeniowe.")
    parser.add_argument("--threads", type=int, default=0, help="Liczba wątków dla CPU (0 = domyślnie wg PyTorch).")
    parser.add_argument("--debug", action="store_true", help="Wypisuje szczegóły: plik, oczekiwany i wykryty język oraz licznik plików.")

    # Transkrypcja
    parser.add_argument("--transcription", action="store_true", help="Wykonaj pełną transkrypcję plików.")
    parser.add_argument("--format", type=str, default="txt", choices=["txt", "vtt", "srt", "tsv", "json", "all"],
                        help="Format zapisu transkrypcji (gdy --transcription).")

    # Swobodny passthrough dla parametrów Whisper (transcribe)
    parser.add_argument("--whisper-args", nargs=argparse.REMAINDER,
                        help="Dodatkowe parametry dla whisper.transcribe(), np. --whisper-args --language pl --temperature 0.0")

    return parser.parse_args()


def load_libs_and_model(model_name: str, device_pref: str, threads: int, debug: bool):
    global torch, whisper
    import torch as _torch
    import whisper as _whisper

    # Wątki CPU przed inicjacją modelu
    if threads and threads > 0:
        _torch.set_num_threads(threads)
        os.environ["OMP_NUM_THREADS"] = str(threads)
        os.environ["MKL_NUM_THREADS"] = str(threads)

    # Urządzenie
    if device_pref == "auto":
        device = "cuda" if _torch.cuda.is_available() else "cpu"
    else:
        device = device_pref
        if device == "cuda" and not _torch.cuda.is_available():
            if debug:
                print("# Ostrzeżenie: CUDA niedostępna, przełączam na CPU", file=sys.stderr)
            device = "cpu"

    if debug:
        print(f"# Device: {device}", file=sys.stderr)

    model = _whisper.load_model(model_name, device=device)

    torch = _torch
    whisper = _whisper
    return model, device


def collect_audio_files(folder: str) -> List[Path]:
    p = Path(folder)
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"Folder nie istnieje lub nie jest katalogiem: {folder}")
    files = []
    for entry in p.iterdir():
        if entry.is_file() and entry.suffix.lower() in AUDIO_EXTS:
            files.append(entry)
    return sorted(files)


def expected_lang_from_name(path: Path) -> Optional[str]:
    m = FNAME_LANG_RE.match(path.name)
    if not m:
        return None
    return m.group(1).lower()


def detect_language(model, device: str, filepath: Path) -> Tuple[Optional[str], Optional[float]]:
    """
    Zwraca: (lang_code, probability) lub (None, None) przy błędzie.
    """
    try:
        audio = whisper.load_audio(str(filepath))
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
        _, probs = model.detect_language(mel)
        if not probs:
            return None, None
        lang = max(probs, key=probs.get)
        return lang, float(probs[lang])
    except Exception:
        return None, None


def parse_whisper_kwargs(rest: Optional[List[str]], debug: bool) -> Dict[str, Any]:
    """
    Luźny parser par klucz-wartość dla --whisper-args.
    Przykład: --whisper-args --language pl --temperature 0.0 --fp16 True
    """
    if not rest:
        return {}

    kw: Dict[str, Any] = {}
    i = 0
    while i < len(rest):
        token = rest[i]
        if token.startswith("--"):
            key = token.lstrip("-").replace("-", "_")
            val: Any = True  # flaga bez wartości
            if i + 1 < len(rest) and not rest[i + 1].startswith("--"):
                raw = rest[i + 1]
                # heurystyczny rzut typów
                if raw.lower() in {"true", "false"}:
                    val = raw.lower() == "true"
                else:
                    try:
                        if "." in raw:
                            val = float(raw)
                        else:
                            val = int(raw)
                    except ValueError:
                        # listy rozdzielane przecinkiem
                        if "," in raw:
                            val = [x for x in raw.split(",")]
                        else:
                            val = raw
                i += 1  # zużyto wartość
            kw[key] = val
        else:
            # luźny element, ignorujemy
            if debug:
                print(f"# Ignoruję token: {token}", file=sys.stderr)
        i += 1
    return kw


def transcribe_to_files(model, filepath: Path, out_format: str, whisper_kwargs: Dict[str, Any], debug: bool):
    """
    Zapisuje transkrypcję do plików w tym samym katalogu co źródło.
    """
    # Ustawienia domyślne sensowne lokalnie
    kwargs = dict(whisper_kwargs) if whisper_kwargs else {}
    # Jeśli pracujemy na CPU i fp16 nie ma sensu
    if torch.device(model.device).type == "cpu":
        kwargs.setdefault("fp16", False)
    # Domyślnie wyłączamy gadatliwość
    kwargs.setdefault("verbose", False)

    result = model.transcribe(str(filepath), **kwargs)

    # Zapisy przez writer
    from whisper.utils import get_writer

    out_dir = str(filepath.parent)
    base = filepath.with_suffix("").name

    if out_format == "all":
        for fmt in ["txt", "vtt", "srt", "tsv", "json"]:
            writer = get_writer(fmt, out_dir)
            writer(result, base)
    else:
        writer = get_writer(out_format, out_dir)
        writer(result, base)

    if debug:
        # Pokaż dokąd zapisano
        if out_format == "all":
            exts = ["txt", "vtt", "srt", "tsv", "json"]
        else:
            exts = [out_format]
        for e in exts:
            print(f"# zapisano: {os.path.join(out_dir, base+'.'+e)}", file=sys.stderr)


def main():
    args = parse_args()

    # Przygotowanie
    try:
        model, device = load_libs_and_model(args.model, args.device, args.threads, args.debug)
    except Exception as e:
        print(f"# Błąd inicjalizacji Whisper: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        files = collect_audio_files(args.folder)
    except Exception as e:
        print(f"# Błąd odczytu folderu: {e}", file=sys.stderr)
        sys.exit(2)

    # Parsowanie dodatkowych argumentów do transcribe
    whisper_kwargs = parse_whisper_kwargs(args.whisper_args, args.debug)

    checked = 0
    mismatches = 0

    for f in files:
        expected = expected_lang_from_name(f)
        if expected is None:
            # ignoruj pliki, które nie pasują do wzorca nazwy
            continue

        detected, prob = detect_language(model, device, f)
        checked += 1

        mismatch = (detected is None) or (detected.lower() != expected.lower())

        if args.debug:
            print(f"# {f}\texpected={expected}\tdetected={detected or 'None'}\tp={('%.3f' % prob) if prob is not None else 'None'}",
                  file=sys.stderr)

        if mismatch:
            mismatches += 1
            # Wypisujemy plik wraz z oczekiwanym i wykrytym językiem
            output_line = f"{f}\texpected={expected}\tdetected={detected or 'None'}"
            print(output_line)

            # Tworzymy plik .err z raportem
            err_file = f.with_suffix('.err')
            try:
                with open(err_file, 'w', encoding='utf-8') as ef:
                    ef.write(output_line + '\n')
            except Exception as e:
                if args.debug:
                    print(f"# Błąd zapisu {err_file}: {e}", file=sys.stderr)

        # Opcjonalna transkrypcja
        if args.transcription:
            try:
                transcribe_to_files(model, f, args.format, whisper_kwargs, args.debug)
            except Exception as e:
                # Nie przerywaj pracy, pokaż błąd w debug
                if args.debug:
                    print(f"# Błąd transkrypcji {f}: {e}", file=sys.stderr)

    if args.debug:
        print(f"# checked={checked}\tmismatches={mismatches}", file=sys.stderr)


if __name__ == "__main__":
    main()

