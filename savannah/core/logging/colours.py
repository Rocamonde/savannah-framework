from typing import Iterable

_ANSI_FORMAT = "\033[{PARAMS}m"

def make_params(l: Iterable[int]):
    l = [str(i) for i in l]
    return ";".join(l)


"""
                                                  PARAMS INFO
╔══════════╦════════════════════════════════╦═════════════════════════════════════════════════════════════════════════╗
║  Code    ║             Effect             ║                                   Note                                  ║
╠══════════╬════════════════════════════════╬═════════════════════════════════════════════════════════════════════════╣
║ 0        ║  Reset / Normal                ║  all attributes off                                                     ║
║ 1        ║  Bold or increased intensity   ║                                                                         ║
║ 2        ║  Faint (decreased intensity)   ║  Not widely supported.                                                  ║
║ 3        ║  Italic                        ║  Not widely supported. Sometimes treated as inverse.                    ║
║ 4        ║  Underline                     ║                                                                         ║
║ 5        ║  Slow Blink                    ║  less than 150 per minute                                               ║
║ 6        ║  Rapid Blink                   ║  MS-DOS ANSI.SYS; 150+ per minute; not widely supported                 ║
║ 7        ║  [[reverse video]]             ║  swap foreground and background colors                                  ║
║ 8        ║  Conceal                       ║  Not widely supported.                                                  ║
║ 9        ║  Crossed-out                   ║  Characters legible, but marked for deletion.  Not widely supported.    ║
║ 10       ║  Primary(default) font         ║                                                                         ║
║ 11–19    ║  Alternate font                ║  Select alternate font `n-10`                                           ║
║ 20       ║  Fraktur                       ║  hardly ever supported                                                  ║
║ 21       ║  Bold off or Double Underline  ║  Bold off not widely supported; double underline hardly ever supported. ║
║ 22       ║  Normal color or intensity     ║  Neither bold nor faint                                                 ║
║ 23       ║  Not italic, not Fraktur       ║                                                                         ║
║ 24       ║  Underline off                 ║  Not singly or doubly underlined                                        ║
║ 25       ║  Blink off                     ║                                                                         ║
║ 27       ║  Inverse off                   ║                                                                         ║
║ 28       ║  Reveal                        ║  conceal off                                                            ║
║ 29       ║  Not crossed out               ║                                                                         ║
║ 30–37    ║  Set foreground color          ║  See color table below                                                  ║
║ 38       ║  Set foreground color          ║  Next arguments are `5;n` or `2;r;g;b`, see below                       ║
║ 39       ║  Default foreground color      ║  implementation defined (according to standard)                         ║
║ 40–47    ║  Set background color          ║  See color table below                                                  ║
║ 48       ║  Set background color          ║  Next arguments are `5;n` or `2;r;g;b`, see below                       ║
║ 49       ║  Default background color      ║  implementation defined (according to standard)                         ║
║ 51       ║  Framed                        ║                                                                         ║
║ 52       ║  Encircled                     ║                                                                         ║
║ 53       ║  Overlined                     ║                                                                         ║
║ 54       ║  Not framed or encircled       ║                                                                         ║
║ 55       ║  Not overlined                 ║                                                                         ║
║ 60       ║  ideogram underline            ║  hardly ever supported                                                  ║
║ 61       ║  ideogram double underline     ║  hardly ever supported                                                  ║
║ 62       ║  ideogram overline             ║  hardly ever supported                                                  ║
║ 63       ║  ideogram double overline      ║  hardly ever supported                                                  ║
║ 64       ║  ideogram stress marking       ║  hardly ever supported                                                  ║
║ 65       ║  ideogram attributes off       ║  reset the effects of all of 60-64                                      ║
║ 90–97    ║  Set bright foreground color   ║  aixterm (not in standard)                                              ║
║ 100–107  ║  Set bright background color   ║  aixterm (not in standard)                                              ║
╚══════════╩════════════════════════════════╩═════════════════════════════════════════════════════════════════════════╝

             COLOURS:
╔═══════════╦═════════╦═════════╗
║   Color   ║ FG code ║ BG code ║
╠═══════════╬═════════╬═════════╣
║ Black     ║ 30      ║ 40      ║
║ Red       ║ 31      ║ 41      ║
║ Green     ║ 32      ║ 42      ║
║ Yellow    ║ 33      ║ 43      ║
║ Blue      ║ 34      ║ 44      ║
║ Magenta   ║ 35      ║ 45      ║
║ Cyan      ║ 36      ║ 46      ║
║ White     ║ 37      ║ 47      ║
╠═══════════ ═════════ ═════════╣
║          Bright colors        ║
╠═══════════ ═════════ ═════════╣
║ Black     ║ 30;1    ║ 100     ║
║ Red       ║ 31;1    ║ 101     ║
║ Green     ║ 32;1    ║ 102     ║
║ Yellow    ║ 33;1    ║ 103     ║
║ Blue      ║ 34;1    ║ 104     ║
║ Magenta   ║ 35;1    ║ 105     ║
║ Cyan      ║ 36;1    ║ 106     ║
║ White     ║ 37;1    ║ 107     ║
╚═══════════╩═════════╩═════════╝

Made by: https://stackoverflow.com/users/752843/richard, @r-barnes (GitHub)
Taken from: https://stackoverflow.com/a/33206814/4396006

"""

RESET = "\033[0;0m"

from dataclasses import dataclass

@dataclass
class Colours:
    BLACK: int   = 30
    RED: int     = 31
    GREEN: int   = 32
    YELLOW: int  = 33
    BLUE: int    = 34
    MAGENTA: int = 35
    CYAN: int    = 36
    WHITE: int   = 37

BackgroundColours = Colours(BLACK=40, RED=41, GREEN=42, YELLOW=43, BLUE=44, MAGENTA=45, CYAN=46, WHITE=47)

def apply_effect(EFFECT, msg): return "{0}{msg}{1}".format(EFFECT, RESET, msg=msg)
def make_effect(l): return _ANSI_FORMAT.format(PARAMS=make_params(l))
def make_text(l, msg): return apply_effect(make_effect(l), msg)


def std(colour, msg):
    """
    Standard white background bold message
    """
    return make_text([getattr(Colours, colour), '107'], msg)

def std_bold(colour, msg):
    """
    Standard white background bold message
    """
    return make_text([getattr(Colours, colour), '1', '107'], msg)