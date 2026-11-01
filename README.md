# ZMK config

This is a ZMK config for a Ferris Sweep keyboard (34-keys) built using Nice!Nano v2 micro-controllers.

The base layer is based on the DVORAK layout with home row mods (GACS) and a bunch of combos setup to easy access to important keys. Three other layers can be accessed from the base, providing quick access to the numerical, navigation and symbols layers.

More details can be seen in the map below or in the `cradio.keymap` file.

![](keymap.svg)

## Building locally

Requires Docker.

**First-time setup** — clones ZMK and initializes the west workspace (takes a few minutes):

```bash
python build.py setup
```

**Build firmware:**

```bash
python build.py build
python build.py build --pristine  # clean build
```

**Flash** — for keymap changes, only the left (central) half needs to be reflashed.

Enter bootloader mode via the keymap: hold the right thumb key (FUN layer) and press the top-left key (`&bootloader`). The LED pattern changes to confirm bootloader mode.

The keyboard shows up as `/dev/sdb` but doesn't auto-mount. Mount it manually:

```bash
sudo mount -o uid=1000,gid=985 /dev/sdb /media/kb
python build.py flash left
```

The drive unmounts itself automatically once flashing is done.

## Special characters

The keyboard runs `us(altgr-intl)` on Linux and the standard US layout on macOS. All special character access is handled through ZMK combos — no AltGr key-hold required.

### OS mode toggle

The dead key combos send different keycodes depending on the active OS mode. Default is Linux.

| Action | Keys |
|--------|------|
| Toggle macOS mode on/off | FUN layer (hold right thumb) → right pinky top key (`L` position) |
| Check current mode | Press `F + G + C` simultaneously — types `lnx` or `mac` |

### Dead keys (left-hand column pairs)

Press both keys simultaneously, release, then type the vowel.

Ordered by finger strength — most-used dead key on the strongest finger.

| Combo | Finger | Dead key | Composes |
|-------|--------|----------|---------|
| `'` + `A` | pinky | grave ` | à è ì ò ù |
| `,` + `O` | ring | tilde ~ | ã õ ñ |
| `.` + `E` | middle | acute ´ | á é í ó ú ý |
| `P` + `U` | index | diaeresis ¨ | ä ë ï ö ü |
| `Y` + `I` | inner | circumflex ^ | â ê î ô û |

### Direct characters

| Combo | Character |
|-------|-----------|
| `R` + `N` | ß |
| `C` + `T` | ç |

### Notes

- All combos require a brief pause (~150ms) after the last typed key before they fire — this prevents accidental triggers during normal typing.
- For any other AltGr/Option character not covered above, use the sticky RALT combo: press both inner thumbs (`TAB + BSPC`) simultaneously, release, then press the target key.
