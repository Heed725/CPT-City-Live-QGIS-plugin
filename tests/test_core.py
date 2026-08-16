import tempfile
import unittest
from pathlib import Path

from cpt_city_live.core import parse_color, parse_offset, parse_svg


class CoreTests(unittest.TestCase):
    def test_offsets_and_colors(self):
        self.assertEqual(parse_offset("25%"), 0.25)
        self.assertEqual(parse_color("rgb(1, 22, 203)"), (1, 22, 203))
        self.assertEqual(parse_color("#abc"), (170, 187, 204))

    def test_parse_svg_stops(self):
        svg = '''<svg xmlns="http://www.w3.org/2000/svg"><linearGradient>
        <stop offset="0%" stop-color="rgb(1, 2, 3)"/>
        <stop offset="50%" style="stop-color:#abcdef"/>
        <stop offset="100%" stop-color="#040506"/>
        </linearGradient></svg>'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ramp.svg"
            path.write_text(svg, encoding="utf-8")
            self.assertEqual(parse_svg(path), [(0.0, (1, 2, 3)), (0.5, (171, 205, 239)), (1.0, (4, 5, 6))])


if __name__ == "__main__":
    unittest.main()
