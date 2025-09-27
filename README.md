# Yu-Gi-Oh! Power of Chaos YDC Parser

Opens a .ydc deck file and prints the list of cards.

```bash
python3 parser.py <deck>.ydc
```
```
// <deck>.ydc <YDCDeck main=3 fusion=0 side=0>
// Main deck
3x 0x0000
```

## Decode card names

You can optionally provide a list_card.txt file, extracted from the games files
by the Yu-Gi-Oh! Power of Chaos Mod Tools by PhilYeahz & DerPlayer.

```bash
python3 parser.py <deck>.ydc list_card.txt
```
```
// <deck>.ydc <YDCDeck main=3 fusion=0 side=0>
// Main deck
3x Blue-Eyes White Dragon
```

### list_card.txt

```
//	Blue-Eyes White Dragon
//	0816:[0000]
LOB001.bmp
```
