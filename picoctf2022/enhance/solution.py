#!/bin/env python3

from xml.etree import ElementTree

SVG_PREFIX = "{http://www.w3.org/2000/svg}"

def _svg_key(name: str) -> str:
    return SVG_PREFIX + name

def main() -> int:
    tree = ElementTree.parse("drawing.flag.svg")
    root = tree.getroot()

    for element in root.find(_svg_key("g")).find(_svg_key("text")).iter(_svg_key("tspan")):
        print(element.text.replace(" ", ""), end="")
    print()


if __name__ == '__main__':
    raise SystemExit(main())
