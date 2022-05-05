from __future__ import annotations


__all__ = (
    "AllColors",
    "FlatUIColors",
    "MaterialColors",
)


from pathlib import Path
from typing import TYPE_CHECKING
from yaml import safe_load


if TYPE_CHECKING:
    from typing import Dict


class NestedInt(int):
    """
    Integer with a read-only dictionary.
    """

    _values: Dict[str | int, int] = {}

    def __new__(
        cls,
        x: int,
        values: Dict[str | int, int],
    ) -> NestedInt:
        obj = super().__new__(cls, x)
        obj._values = values
        return obj

    def __getitem__(self, item: str | int) -> int:
        return self._values[item]

    def __iter__(self):
        return self._values.__iter__()

    def items(self):
        return self._values.items()

    def __copy__(self) -> int:
        return int(self)

    def __deepcopy__(self, *_) -> int:
        return int(self)


_colors_path = Path(__file__).parent / "colors"

with open(_colors_path / "flat_ui.yml", encoding="utf-8") as f:
    _color_data_flat_ui: Dict[str, int] = safe_load(f)

with open(_colors_path / "material.yml", encoding="utf-8") as f:
    _color_data_material: Dict[str, dict[str | int, int]] = safe_load(f)


def _load_flat_ui(
    name: str,
) -> int:
    return _color_data_flat_ui[name]


def _load_material(
    name: str,
) -> NestedInt:
    data = _color_data_material[name]
    return NestedInt(data[500], data)


class FlatUIColors:
    """
    All Flat-UI-Colors (https://materialui.co/flatuicolors).
    """

    __slots__ = ()

    turquoise: int = _load_flat_ui("turquoise")
    greensea: int = _load_flat_ui("greensea")
    emerland: int = _load_flat_ui("emerland")
    nephritis: int = _load_flat_ui("nephritis")
    peterriver: int = _load_flat_ui("peterriver")
    belizehole: int = _load_flat_ui("belizehole")
    amethyst: int = _load_flat_ui("amethyst")
    wisteria: int = _load_flat_ui("wisteria")
    wetasphalt: int = _load_flat_ui("wetasphalt")
    midnightblue: int = _load_flat_ui("midnightblue")
    sunflower: int = _load_flat_ui("sunflower")
    orange: int = _load_flat_ui("orange")
    carrot: int = _load_flat_ui("carrot")
    pumpkin: int = _load_flat_ui("pumpkin")
    alizarin: int = _load_flat_ui("alizarin")
    pomegranate: int = _load_flat_ui("pomegranate")
    clouds: int = _load_flat_ui("clouds")
    silver: int = _load_flat_ui("silver")
    concrete: int = _load_flat_ui("concrete")
    asbestos: int = _load_flat_ui("asbestos")


class MaterialColors:
    """
    All Material-Colors (https://materialui.co/colors).
    """

    __slots__ = ()

    red: NestedInt = _load_material("red")
    pink: NestedInt = _load_material("pink")
    purple: NestedInt = _load_material("purple")
    deeppurple: NestedInt = _load_material("deeppurple")
    indigo: NestedInt = _load_material("indigo")
    blue: NestedInt = _load_material("blue")
    lightblue: NestedInt = _load_material("lightblue")
    cyan: NestedInt = _load_material("cyan")
    teal: NestedInt = _load_material("teal")
    green: NestedInt = _load_material("green")
    lightgreen: NestedInt = _load_material("lightgreen")
    lime: NestedInt = _load_material("lime")
    yellow: NestedInt = _load_material("yellow")
    amber: NestedInt = _load_material("amber")
    orange: NestedInt = _load_material("orange")
    deeporange: NestedInt = _load_material("deeporange")
    brown: NestedInt = _load_material("brown")
    grey: NestedInt = _load_material("grey")
    bluegrey: NestedInt = _load_material("bluegrey")

    default: int = teal[600]
    error: int = red["a700"]
    warning: int = yellow["a200"]
    assertion: int = orange[900]
    notimplemented: int = lightblue[900]
    max_concurrency: int = bluegrey[600]


class AllColors(FlatUIColors, MaterialColors):
    """
    Flat-UI-Colors and Material-Colors combined.

    Notes
    -----
    There is a name-conflict with ``orange``.
    The value from ``MaterialColors`` will be set
    since it's more detailed.
    """

    __slots__ = FlatUIColors.__slots__ + MaterialColors.__slots__

    orange = MaterialColors.orange
