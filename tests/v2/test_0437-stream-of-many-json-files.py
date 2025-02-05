# BSD 3-Clause License; see https://github.com/scikit-hep/awkward-1.0/blob/main/LICENSE

import pytest  # noqa: F401
import numpy as np  # noqa: F401
import awkward as ak  # noqa: F401
import json

import os
from pathlib import Path

DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(DIR).parents[0]

to_list = ak._v2.operations.to_list


def test_unfinished_fragment_exception():
    # read unfinished json fragments
    strs0 = """{"one": 1, "two": 2.2,"""
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs0)

    strs1 = """{"one": 1,
        "two": 2.2,"""
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs1)

    strs2 = """{"one": 1,
        "two": 2.2,
        """
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs2)

    strs3 = """{"one": 1, "two": 2.2, "three": "THREE"}
        {"one": 10, "two": 22,"""
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs3)

    strs4 = """{"one": 1, "two": 2.2, "three": "THREE"}
        {"one": 10, "two": 22,
        """
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs4)

    strs5 = """["one", "two","""
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs5)

    strs6 = """["one",
        "two","""
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs6)

    strs7 = """["one",
        "two",
        """
    with pytest.raises(ValueError):
        ak._v2.operations.from_json(strs7)


def test_two_arrays():

    str = """{"one": 1, "two": 2.2}{"one": 10, "two": 22}"""
    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json(str)
        assert str(err.value).startswith("Extra data")

    str = """{"one": 1, "two": 2.2}     {"one": 10, "two": 22}"""
    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json(str)
        assert str(err.value).startswith("Extra data")

    str = """{"one": 1, \t "two": 2.2}{"one": 10, "two": 22}"""
    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json(str)
        assert str(err.value).startswith("Extra data")

    str = """{"one": 1, "two": 2.2}  \t   {"one": 10, "two": 22}"""
    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json(str)
        assert str(err.value).startswith("Extra data")

    str = """{"one": 1, "two": 2.2}\n{"one": 10, "two": 22}"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """{"one": 1, "two": 2.2}\n\r{"one": 10, "two": 22}"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """{"one": 1, "two": 2.2}     \n     {"one": 10, "two": 22}"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """{"one": 1, "two": 2.2}     \n\r     {"one": 10, "two": 22}"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """{"one": 1, "two": 2.2}\n{"one": 10, "two": 22}\n"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """{"one": 1, "two": 2.2}\n\r{"one": 10, "two": 22}\n\r"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """["one", "two"]\n["uno", "dos"]"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [["one", "two"], ["uno", "dos"]]

    str = """["one", "two"]\n\r["uno", "dos"]"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [["one", "two"], ["uno", "dos"]]

    str = """["one", "two"]  \n   ["uno", "dos"]"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [["one", "two"], ["uno", "dos"]]

    str = """["one", "two"]  \n\r   ["uno", "dos"]"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [["one", "two"], ["uno", "dos"]]

    str = '"one"\n"two"'
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == ["one", "two"]

    str = '"one"\n\r"two"'
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == ["one", "two"]

    str = '"one"  \n   "two"'
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == ["one", "two"]

    array = ak._v2.operations.from_json_file(
        os.path.join(path, "samples/test-two-arrays.json")
    )
    assert array.tolist() == [
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        {"one": 1, "two": 2.2},
        {"one": 10, "two": 22.0},
        ["one", "two"],
        ["uno", "dos"],
        ["one", "two"],
        ["uno", "dos"],
        ["one", "two"],
        ["uno", "dos"],
        ["one", "two"],
        ["uno", "dos"],
        ["one", "two"],
        ["uno", "dos"],
        ["one", "two"],
        ["uno", "dos"],
        "one",
        "two",
        "one",
        "two",
        "one",
        "two",
        "one",
        "two",
        "one",
        "two",
        "one",
        "two",
    ]


def test_blanc_lines():
    str = """{"one": 1, "two": 2.2}

    {"one": 10, "two": 22}"""
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """{"one": 1, "two": 2.2}

    {"one": 10, "two": 22}
    """
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [{"one": 1, "two": 2.2}, {"one": 10, "two": 22.0}]

    str = """ 1
    2

    3   """
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [1, 2, 3]

    str = """
        1
        2

        3
        """
    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [1, 2, 3]


def test_tostring():
    # write a json string from an array built from
    # multiple json fragments from a string
    str = """{"x": 1.1, "y": []}
             {"x": 2.2, "y": [1]}
             {"x": 3.3, "y": [1, 2]}
             {"x": 4.4, "y": [1, 2, 3]}
             {"x": 5.5, "y": [1, 2, 3, 4]}
             {"x": 6.6, "y": [1, 2, 3, 4, 5]}"""

    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [
        {"x": 1.1, "y": []},
        {"x": 2.2, "y": [1]},
        {"x": 3.3, "y": [1, 2]},
        {"x": 4.4, "y": [1, 2, 3]},
        {"x": 5.5, "y": [1, 2, 3, 4]},
        {"x": 6.6, "y": [1, 2, 3, 4, 5]},
    ]

    assert (
        ak._v2.operations.to_json(array)
        == '[{"x":1.1,"y":[]},{"x":2.2,"y":[1]},{"x":3.3,"y":[1,2]},{"x":4.4,"y":[1,2,3]},{"x":5.5,"y":[1,2,3,4]},{"x":6.6,"y":[1,2,3,4,5]}]'
    )


def test_fromstring():
    # read multiple json fragments from a string
    str = """{"x": 1.1, "y": []}
             {"x": 2.2, "y": [1]}
             {"x": 3.3, "y": [1, 2]}
             {"x": 4.4, "y": [1, 2, 3]}
             {"x": 5.5, "y": [1, 2, 3, 4]}
             {"x": 6.6, "y": [1, 2, 3, 4, 5]}"""

    array = ak._v2.operations.from_json(str)
    assert array.tolist() == [
        {"x": 1.1, "y": []},
        {"x": 2.2, "y": [1]},
        {"x": 3.3, "y": [1, 2]},
        {"x": 4.4, "y": [1, 2, 3]},
        {"x": 5.5, "y": [1, 2, 3, 4]},
        {"x": 6.6, "y": [1, 2, 3, 4, 5]},
    ]


def test_array_tojson():
    # convert float 'nan' and 'inf' to user-defined strings
    array = ak._v2.contents.NumpyArray(
        np.array(
            [[float("nan"), float("nan"), 1.1], [float("inf"), 3.3, float("-inf")]]
        )
    )

    assert (
        ak._v2.operations.to_json(
            array, nan_string="NaN", infinity_string="inf", minus_infinity_string="-inf"
        )
        == '[["NaN","NaN",1.1],["inf",3.3,"-inf"]]'
    )

    array2 = ak._v2.highlevel.Array([[0, 2], None, None, None, "NaN", "NaN"])
    assert (
        ak._v2.operations.to_json(array2, nan_string="NaN")
        == '[[0,2],null,null,null,"NaN","NaN"]'
    )


def test_fromfile():
    # read multiple json fragments from a json file
    array = ak._v2.operations.from_json_file(
        os.path.join(path, "samples/test-record-array.json")
    )
    assert array.tolist() == [
        {"x": 1.1, "y": []},
        {"x": 2.2, "y": [1]},
        {"x": 3.3, "y": [1, 2]},
        {"x": 4.4, "y": [1, 2, 3]},
        {"x": 5.5, "y": [1, 2, 3, 4]},
        {"x": 6.6, "y": [1, 2, 3, 4, 5]},
    ]

    # read json file containing 'nan' and 'inf' user-defined strings
    # and replace 'nan' and 'inf' strings with floats
    array = ak._v2.operations.from_json_file(
        os.path.join(path, "samples/test.json"),
        infinity_string="inf",
        minus_infinity_string="-inf",
    )

    assert array.tolist() == [
        1.1,
        2.2,
        3.3,
        float("inf"),
        float("-inf"),
        [4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.1, 11.11],
        [12.12, 13.13, 14.14, 15.15, 16.16, 17.17],
        [
            [
                [18.18, 19.19, 20.2, 21.21, 22.22],
                [
                    23.23,
                    24.24,
                    25.25,
                    26.26,
                    27.27,
                    28.28,
                    29.29,
                    30.3,
                    31.31,
                    32.32,
                    33.33,
                    34.34,
                    35.35,
                    36.36,
                    37.37,
                ],
                [38.38],
                [39.39, 40.4, "NaN", "NaN", 41.41, 42.42, 43.43],
            ],
            [
                [44.44, 45.45, 46.46, 47.47, 48.48],
                [
                    49.49,
                    50.5,
                    51.51,
                    52.52,
                    53.53,
                    54.54,
                    55.55,
                    56.56,
                    57.57,
                    58.58,
                    59.59,
                    60.6,
                    61.61,
                    62.62,
                    63.63,
                ],
                [64.64],
                [65.65, 66.66, "NaN", "NaN", 67.67, 68.68, 69.69],
            ],
        ],
    ]

    # read json file containing 'nan' and 'inf' user-defined strings
    array = ak._v2.operations.from_json_file(os.path.join(path, "samples/test.json"))

    assert array.tolist() == [
        1.1,
        2.2,
        3.3,
        "inf",
        "-inf",
        [4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.1, 11.11],
        [12.12, 13.13, 14.14, 15.15, 16.16, 17.17],
        [
            [
                [18.18, 19.19, 20.2, 21.21, 22.22],
                [
                    23.23,
                    24.24,
                    25.25,
                    26.26,
                    27.27,
                    28.28,
                    29.29,
                    30.3,
                    31.31,
                    32.32,
                    33.33,
                    34.34,
                    35.35,
                    36.36,
                    37.37,
                ],
                [38.38],
                [39.39, 40.4, "NaN", "NaN", 41.41, 42.42, 43.43],
            ],
            [
                [44.44, 45.45, 46.46, 47.47, 48.48],
                [
                    49.49,
                    50.5,
                    51.51,
                    52.52,
                    53.53,
                    54.54,
                    55.55,
                    56.56,
                    57.57,
                    58.58,
                    59.59,
                    60.6,
                    61.61,
                    62.62,
                    63.63,
                ],
                [64.64],
                [65.65, 66.66, "NaN", "NaN", 67.67, 68.68, 69.69],
            ],
        ],
    ]

    # read json file containing 'nan' and 'inf' user-defined strings
    # and replace 'nan' and 'inf' strings with a predefined 'None' string
    array = ak._v2.operations.from_json_file(
        os.path.join(path, "samples/test.json"),
        infinity_string="inf",
        minus_infinity_string="-inf",
        nan_string="NaN",
    )

    def fix(obj):
        if isinstance(obj, list):
            return [fix(x) for x in obj]
        elif np.isnan(obj):
            return "COMPARE-NAN"
        else:
            return obj

    assert fix(array.tolist()) == fix(
        [
            1.1,
            2.2,
            3.3,
            float("inf"),
            float("-inf"),
            [4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.1, 11.11],
            [12.12, 13.13, 14.14, 15.15, 16.16, 17.17],
            [
                [
                    [18.18, 19.19, 20.2, 21.21, 22.22],
                    [
                        23.23,
                        24.24,
                        25.25,
                        26.26,
                        27.27,
                        28.28,
                        29.29,
                        30.3,
                        31.31,
                        32.32,
                        33.33,
                        34.34,
                        35.35,
                        36.36,
                        37.37,
                    ],
                    [38.38],
                    [39.39, 40.4, float("nan"), float("nan"), 41.41, 42.42, 43.43],
                ],
                [
                    [44.44, 45.45, 46.46, 47.47, 48.48],
                    [
                        49.49,
                        50.5,
                        51.51,
                        52.52,
                        53.53,
                        54.54,
                        55.55,
                        56.56,
                        57.57,
                        58.58,
                        59.59,
                        60.6,
                        61.61,
                        62.62,
                        63.63,
                    ],
                    [64.64],
                    [65.65, 66.66, float("nan"), float("nan"), 67.67, 68.68, 69.69],
                ],
            ],
        ]
    )

    # read json file containing multiple definitions of 'nan' and 'inf'
    # user-defined strings
    # replace can only work for one string definition
    array = ak._v2.operations.from_json_file(
        os.path.join(path, "samples/test-nan-inf.json"),
        infinity_string="Infinity",
        nan_string="None at all",
    )

    assert array.tolist() == [
        1.1,
        2.2,
        3.3,
        "inf",
        "-inf",
        [4.4, float("inf"), 6.6, 7.7, 8.8, "NaN", 10.1, 11.11],
        [12.12, 13.13, 14.14, 15.15, 16.16, 17.17],
        [
            [
                [18.18, 19.19, 20.2, 21.21, 22.22],
                [
                    23.23,
                    24.24,
                    25.25,
                    26.26,
                    27.27,
                    28.28,
                    29.29,
                    30.3,
                    31.31,
                    32.32,
                    33.33,
                    34.34,
                    35.35,
                    36.36,
                    37.37,
                ],
                [38.38],
                [39.39, 40.4, "NaN", "NaN", 41.41, 42.42, 43.43],
            ],
            [
                [44.44, 45.45, 46.46, 47.47, 48.48],
                [
                    49.49,
                    50.5,
                    51.51,
                    52.52,
                    53.53,
                    54.54,
                    55.55,
                    56.56,
                    57.57,
                    58.58,
                    59.59,
                    60.6,
                    61.61,
                    62.62,
                    63.63,
                ],
                [64.64],
                [65.65, 66.66, "NaN", "NaN", 67.67, 68.68, 69.69],
            ],
        ],
    ]


def test_three():
    array = ak._v2.operations.from_json('["one", "two"] \n ["three"]')
    assert array.tolist() == [["one", "two"], ["three"]]


def test_jpivarski():
    assert to_list(ak._v2.operations.from_json('{"x": 1, "y": [1, 2, 3]}')) == {
        "x": 1,
        "y": [1, 2, 3],
    }

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json('{"x": 1, "y": [1, 2, 3]} {"x": 2, "y": []}')
        assert str(err.value).startswith("Extra data")

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json('{"x": 1, "y": [1, 2, 3]} 123')
        assert str(err.value).startswith("Extra data")

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json('{"x": 1, "y": [1, 2, 3]} [1, 2, 3, 4, 5]')
        assert str(err.value).startswith("Extra data")

    assert ak._v2.operations.from_json("123") == 123

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json("123 456")
        assert str(err.value).startswith("Extra data")

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json('123 {"x": 1, "y": [1, 2, 3]}')
        assert str(err.value).startswith("Extra data")

    assert ak._v2.operations.from_json("null") is None

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json("null 123")
        assert str(err.value).startswith("Extra data")

    with pytest.raises(json.decoder.JSONDecodeError) as err:
        ak._v2.operations.from_json("123 null")
        assert str(err.value).startswith("Extra data")
