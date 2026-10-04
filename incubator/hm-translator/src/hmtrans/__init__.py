"""hmtrans: translate `.hm` sources, and say exactly what was and was not translated.

The translator is fail-closed. A construct it cannot translate faithfully is
kept in the IR as *untranslated*, with a reason and a source position, and is
never silently dropped, guessed at, or promoted to a proved statement.
"""

__version__ = "0.1.0.dev0"
