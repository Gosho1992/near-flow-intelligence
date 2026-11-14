import unittest

from nfi.build import flow_summary


class FlowSummaryTests(unittest.TestCase):
    def test_signed_net_total_and_daily_average(self):
        rows = [
            {"date": "2026-01-01", "creations": 100.0, "redemptions": 20.0, "data_status": "complete"},
            {"date": "2026-01-02", "creations": 10.0, "redemptions": 50.0, "data_status": "complete"},
        ]
        result = flow_summary(rows, basket_near=50.0)
        self.assertEqual(result["net_total"], 40.0)
        self.assertEqual(result["days"], 2)
        self.assertEqual(result["net_per_day"], 20.0)
        self.assertEqual(result["baskets_per_day"], 0.4)

    def test_incomplete_or_missing_rows_are_excluded(self):
        rows = [
            {"date": "2026-01-01", "creations": 100.0, "redemptions": 20.0, "data_status": "complete"},
            {"date": "2026-01-02", "creations": 900.0, "redemptions": 0.0, "data_status": "incomplete: rpc"},
            {"date": "2026-01-03", "creations": None, "redemptions": 0.0, "data_status": "complete"},
        ]
        result = flow_summary(rows, basket_near=50.0)
        self.assertEqual(result["net_total"], 80.0)
        self.assertEqual(result["days"], 1)
        self.assertEqual(result["net_per_day"], 80.0)
        self.assertEqual(result["baskets_per_day"], 1.6)

    def test_empty_complete_population_returns_missing_rate(self):
        rows = [
            {"date": "2026-01-01", "creations": None, "redemptions": None, "data_status": "incomplete: rpc"}
        ]
        result = flow_summary(rows, basket_near=50.0)
        self.assertIsNone(result["net_total"])
        self.assertEqual(result["days"], 0)
        self.assertIsNone(result["net_per_day"])
        self.assertIsNone(result["baskets_per_day"])


if __name__ == "__main__":
    unittest.main()


class TestPrediction2(unittest.TestCase):
    """Pre-registered prediction 2: net against net, both directions."""

    def test_evaluator(self):
        import datetime as dt
        from nfi.prediction2 import evaluate, START
        d0 = dt.date.fromisoformat(START)
        mk = lambda i, c="0", rd="0", b="1", st="complete": {"date": (d0 + dt.timedelta(i)).isoformat(), "creations": c,
                                                              "redemptions": rd, "buyback_fund_change": b, "data_status": st}
        self.assertEqual(evaluate([mk(i) for i in range(10)])[0], "PENDING")
        self.assertEqual(evaluate([mk(i, rd="5") for i in range(30)])[0], "HOLDS")       # net outflow larger
        self.assertEqual(evaluate([mk(i, c="5") for i in range(30)])[0], "HOLDS")        # net inflow larger
        self.assertEqual(evaluate([mk(i, c="5", rd="5") for i in range(30)])[0], "FAILS")  # big churn, zero net
        self.assertEqual(evaluate([mk(i, st="incomplete: x" if i < 6 else "complete") for i in range(30)])[0], "VOID")
        with self.assertRaises(ValueError):
            evaluate([mk(0), mk(0)])
