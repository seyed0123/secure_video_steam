import json
import unittest
from io import StringIO
from unittest.mock import patch

from tools.evaluate import benchmark_cipher, main, nist_report


class EvaluationTests(unittest.TestCase):
    def test_benchmark_reports_latency_throughput_and_headroom(self):
        report = benchmark_cipher(size=16_384, chunk_size=4_096, media_bitrate_mbps=2.0)
        self.assertEqual(report["bytes"], 16_384)
        self.assertEqual(report["chunks"], 4)
        self.assertGreater(report["throughput_mbps"], 0)
        self.assertGreater(report["mean_chunk_latency_ms"], 0)
        self.assertAlmostEqual(
            report["headroom_ratio"], report["throughput_mbps"] / 2.0
        )

    def test_nistrng_adapter_returns_named_results(self):
        report = nist_report(byte_count=8_192, test_names=("monobit", "runs"))
        self.assertEqual([item["name"] for item in report], ["monobit", "runs"])
        for item in report:
            self.assertIn(item["status"], {"passed", "failed", "inapplicable"})
            self.assertIn("elapsed_ms", item)

    def test_matrix_rank_does_not_change_later_test_input(self):
        alone = nist_report(8_192, ("monobit",))[0]
        after_rank = nist_report(8_192, ("binary_matrix_rank", "monobit"))[1]
        self.assertEqual(after_rank["status"], alone["status"])
        self.assertEqual(after_rank["score"], alone["score"])

    @patch("tools.compare_variants.compare")
    def test_command_includes_nonlinear_generator_comparison(self, compare):
        compare.return_value = [
            {"generator": "lfsr"},
            {"generator": "nlfsr"},
            {"generator": "geffe"},
        ]
        with (
            patch("sys.argv", ["tools.evaluate", "--bytes", "8", "--tests", "monobit"]),
            patch("tools.evaluate.benchmark_cipher", return_value={}),
            patch("tools.evaluate.nist_report", return_value=[]),
            patch("sys.stdout", new_callable=StringIO) as stdout,
        ):
            main()

        output = json.loads(stdout.getvalue())
        self.assertEqual(
            [item["generator"] for item in output["generator_comparison"]],
            ["lfsr", "nlfsr", "geffe"],
        )
        compare.assert_called_once_with(8, ("monobit",))


if __name__ == "__main__":
    unittest.main()
