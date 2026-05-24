# Unicode Selector

- [Unicode Selector](#unicode-selector)
    - [Braille Mode](#braille-mode)
        - [Use Cases](#use-cases)
        - [Usage](#usage)
        - [Logic](#logic)

## Braille Mode

A mode that converts braille symbols to and from binary numbers.

### Use Cases

- **Accessibility**: create Braille symbols that can be printed out and used to label
  objects or identify locations in a space.

- **Art and Design**: create custom Braille patterns that can be incorporated into
  artwork or design projects.

- **⢹⠁⣟ ⡱⢎ ⢹⠁ converters**: make physical embossed printout using Braille symbols

### Usage

To encode braille symbols, simply pass in the binary string patterns that represent
the symbol:

```sh
python main.py braille 10001111 1 01101001 1001011
# ⢹⠁⢎⡱
python main.py braille -t bin_row 10001111 1 01101001 1001011
# ⣥⠁⢎⡱
python main.py braille -t ascii Hello, World!
# ⡓ ⠑ ⠇ ⠇ ⠕ ⠂ ⠀ ⡺ ⠕ ⠗ ⠇ ⠙ ⠼
python main.py braille -pattern-type ascii flexy --pretty-print
⠋ - 'f'
⠇ - 'l'
⠑ - 'e'
⠭ - 'x'
⠽ - 'y'
```

> Trailing zeros in bin patterns can be omitted.

To decode Braille symbols to their corresponding binary pattern, pass in the symbols:

```sh
python main.py braille -t encode ⣒ ⡱
# 01010101 10010110
```

### Logic

There are 8 bits that represent the possible positions where a dot may be present in a
Braille symbol: 4 bits for the first column, and 4 for the last. A value of 1 indicates
the presence of a dot, while 0 indicates the absence.

In total, there are 256 braille symbols (2^8), so their binary values range from
`00000000` to `11111111`. This allows for fast conversion between the symbols and their
binary value.
