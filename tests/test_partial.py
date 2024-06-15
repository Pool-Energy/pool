import unittest

from chia.util.hash import std_hash
from chia.util.byte_types import hexstr_to_bytes


class TestPartial(unittest.TestCase):
    def test_partial_filename(self):
        plot_size = 32
        plot_public_key = hexstr_to_bytes("0x85185f0e1fbc02a0678fafb2f7c66782efca63ca2e3f97d9ea46cf84f356504347203614d2fd11ca1bf2f849aa276368")
        pool_contract_puzzle_hash = hexstr_to_bytes("0xaec160dd64cc954229b1618edc8dec60fa476391d1b9a903b08430c86829cb23")
        plot_id = std_hash(pool_contract_puzzle_hash + plot_public_key)

        assert f"plot-k{plot_size}-*-{plot_id.hex()}.plot" == "plot-k32-*-596700f036101c4f3b514d71748cd512693ea80f7b13471eeeaaa00b4979fd0a.plot"


if __name__ == "__main__":
    unittest.main()
