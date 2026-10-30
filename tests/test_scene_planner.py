import unittest

from scripts.scene_planner import build_storyboard, plan_segment


class ScenePlannerTests(unittest.TestCase):
    def test_finance_topics_map_to_scene_types(self):
        cases = {
            "I invest in stocks for retirement.": "investing",
            "Credit card debt can grow with interest.": "debt",
            "Rent and mortgage payments are major costs.": "housing",
            "Fees and taxes are risks; returns are not guaranteed.": "risk",
            "Save money every week with a budget.": "budget",
        }
        for narration, expected in cases.items():
            with self.subTest(narration=narration):
                self.assertEqual(plan_segment(narration)["scene_type"], expected)

    def test_amounts_and_entities_are_extracted(self):
        scene = plan_segment("Invest $35 each week and target a 7% return.")
        self.assertIn("cash", scene["entities"])
        self.assertIn("$35", scene["emphasis"])
        self.assertIn("7%", scene["emphasis"])

    def test_storyboard_preserves_all_beats(self):
        result = build_storyboard(["Save $10.", "Invest it."])
        self.assertEqual(result["scene_count"], 2)
        self.assertEqual([s["segment_index"] for s in result["scenes"]], [0, 1])

    def test_empty_segments_are_rejected(self):
        with self.assertRaises(ValueError):
            build_storyboard([" ", ""])


if __name__ == "__main__":
    unittest.main()
