import unittest
from scripts.scene_planner import build_storyboard, plan_segment
class PlannerTests(unittest.TestCase):
    def test_scene_types(self):
        cases=[("Invest in stocks","investing"),("Credit card debt","debt"),("Rent a home","housing"),("Fees and taxes are risks","risk"),("Save money each week","budget"),("Compound returns grow","growth")]
        for text,kind in cases:
            with self.subTest(text=text): self.assertEqual(plan_segment(text)["scene_type"],kind)
    def test_extracts_emphasis(self):
        x=plan_segment("Invest $35 weekly for a 7% return")
        self.assertIn("$35",x["emphasis"]); self.assertIn("7%",x["emphasis"])
    def test_preserves_beats(self):
        x=build_storyboard(["Save $10","Invest it"])
        self.assertEqual(x["scene_count"],2); self.assertEqual(len(x["scenes"]),2)
    def test_rejects_empty(self):
        with self.assertRaises(ValueError): build_storyboard([" "])
if __name__=="__main__": unittest.main()
