import unittest

from pydantic import ValidationError

from ai_reviewer_arena.elo_system import \
    ReviewEvalWeights  # Replace with the actual import path of your class


class TestReviewEvalWeights(unittest.TestCase):
    def test_valid_weights(self):
        # Test case with valid weights that sum to 1
        weights = ReviewEvalWeights(
            technical_quality=0.2,
            constructiveness=0.2,
            clarity=0.3,
            overall_quality=0.3,
        )
        self.assertAlmostEqual(
            sum(
                [
                    weights.technical_quality,
                    weights.constructiveness,
                    weights.clarity,
                    weights.overall_quality,
                ]
            ),
            1.0,
            places=6,
            msg="The sum of weights should be 1.",
        )

    def test_invalid_weights_sum(self):
        # Test case where weights do not sum to 1
        with self.assertRaises(ValidationError) as context:
            ReviewEvalWeights(
                technical_quality=0.3,
                constructiveness=0.3,
                clarity=0.3,
                overall_quality=0.3,
            )
        self.assertIn("The sum of all weights must be 1", str(context.exception))

    def test_invalid_weight_range(self):
        # Test case where a weight is out of the valid range (not between 0 and 1)
        with self.assertRaises(ValidationError) as context:
            ReviewEvalWeights(
                technical_quality=-0.1,  # Invalid weight
                constructiveness=0.3,
                clarity=0.4,
                overall_quality=0.4,
            )
        self.assertIn("Input should be greater than 0", str(context.exception))

    def test_float_precision(self):
        # Test case to ensure floating-point precision handling
        weights = ReviewEvalWeights(
            technical_quality=0.333333,
            constructiveness=0.333333,
            clarity=0.333334,
            overall_quality=0.0000001,
        )
        self.assertAlmostEqual(
            sum(
                [
                    weights.technical_quality,
                    weights.constructiveness,
                    weights.clarity,
                    weights.overall_quality,
                ]
            ),
            1.0,
            places=6,
            msg="The sum of weights should be approximately 1.",
        )


if __name__ == "__main__":
    unittest.main()
