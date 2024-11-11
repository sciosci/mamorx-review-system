import json
import unittest
from unittest.mock import mock_open, patch

from ai_reviewer_arena.papers import PaperRegistry

# Assuming the above code has been imported with:
# from your_module import Paper, PaperRegistry


class TestPaperRegistry(unittest.TestCase):
    def setUp(self):
        # Sample data to be used in the tests
        self.sample_papers = [
            {
                "paper_id": "1",
                "title": "Advances in Neural Network Architectures: A Comparative Study",
                "pdf_path": "s10734-010-9390-y.pdf",
                "human_reviewer": [
                    "This paper presents a thorough comparison of neural network architectures. The methodology is sound, and the results are significant. However, the discussion on potential applications could be expanded."
                ],
                "barebones": [
                    "The authors have done an excellent job in comparing various neural network models. The experimental setup is well-designed, and the results are convincing. Some minor issues with clarity in the figures."
                ],
                "liang_etal": [
                    "The paper provides a good analysis of existing architectures, but the novelty of the proposed improvements is questionable. Consider emphasizing unique contributions."
                ],
                "multi_agent_without_knowledge": [
                    "A solid contribution to the field. The comparison criteria are well chosen, but the paper would benefit from a deeper exploration of real-world applications."
                ],
                "system_d": [
                    "The technical details are well-covered, but the abstract should better highlight the key contributions. The references are up-to-date and relevant."
                ],
            },
            {
                "paper_id": "2",
                "title": "Optimization Techniques for Large-Scale Machine Learning",
                "pdf_path": "s10734-010-9390-y.pdf",
                "human_reviewer": [
                    "This paper provides a comprehensive overview of optimization techniques in large-scale machine learning. The theoretical analysis is robust, but the empirical results could be more detailed."
                ],
                "barebones": [
                    "The discussion on the scalability of different optimization algorithms is well-articulated. The paper could benefit from a more in-depth exploration of real-world applications."
                ],
                "liang_etal": [
                    "An informative paper that thoroughly covers various optimization techniques. However, the presentation of the results could be clearer."
                ],
                "multi_agent_without_knowledge": [
                    "The focus on scalability is timely and relevant. The paper could be improved by including a comparison with more recent approaches."
                ],
                "system_d": [
                    "Well-structured and informative. The paper could, however, include more practical examples to demonstrate the applicability of the techniques."
                ],
            },
            {
                "paper_id": "3",
                "title": "The Role of Quantum Computing in Cryptography",
                "pdf_path": "s10734-010-9390-y.pdf",
                "human_reviewer": [
                    "An insightful paper that explores the intersection of quantum computing and cryptography. The arguments are well-supported, though the technical sections might be difficult for a general audience."
                ],
                "barebones": [
                    "The paper addresses a timely topic with potential implications for the future of cryptography. The theoretical foundations are strong, but the practical implementation is not fully explored."
                ],
                "liang_etal": [
                    "This is an interesting and well-researched paper. However, the authors could provide more examples of potential real-world applications."
                ],
                "multi_agent_without_knowledge": [
                    "The integration of quantum computing concepts into cryptography is well-explained. The paper would benefit from a clearer summary of the main points."
                ],
                "system_d": [
                    "A strong theoretical paper. The addition of a section on the limitations and challenges of quantum computing would enhance the discussion."
                ],
            },
        ]
        self.jsonl_data = "\n".join([json.dumps(p) for p in self.sample_papers])

    def test_from_jsonl_empty(self):
        # Use mock_open directly inside the test
        with patch("builtins.open", mock_open(read_data="")):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(len(registry.get_paper_list()), 0)
            self.assertEqual(registry.get_paper_count(), 0)

    def test_get_paper_list_empty(self):
        with patch("builtins.open", mock_open(read_data="")):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(registry.get_paper_list(), [])

    def test_from_jsonl(self):
        with patch("builtins.open", mock_open(read_data=self.jsonl_data)):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(len(registry.get_paper_list()), 3)
            self.assertEqual(registry.get_paper_count(), 3)

    def test_get_next_position(self):
        with patch("builtins.open", mock_open(read_data=self.jsonl_data)):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(registry.get_next_position(0), 1)
            self.assertEqual(registry.get_next_position(1), 2)
            self.assertEqual(registry.get_next_position(2), 0)  # Loop back to start

    def test_get_previous_position(self):
        with patch("builtins.open", mock_open(read_data=self.jsonl_data)):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(registry.get_previous_position(0), 2)  # Loop back to end
            self.assertEqual(registry.get_previous_position(1), 0)
            self.assertEqual(registry.get_previous_position(2), 1)

    def test_get_paper_at_position(self):
        with patch("builtins.open", mock_open(read_data=self.jsonl_data)):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(
                registry.get_paper_at_position(0).title,
                "Advances in Neural Network Architectures: A Comparative Study",
            )
            self.assertEqual(
                registry.get_paper_at_position(1).title,
                "Optimization Techniques for Large-Scale Machine Learning",
            )
            self.assertEqual(
                registry.get_paper_at_position(2).title,
                "The Role of Quantum Computing in Cryptography",
            )
            with self.assertRaises(IndexError):
                registry.get_paper_at_position(3)

    def test_sample_paper_position(self):
        with patch("builtins.open", mock_open(read_data=self.jsonl_data)):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            sample_position = registry.sample_paper_position()
            self.assertIn(sample_position, [0, 1, 2])

    def test_get_paper_count(self):
        with patch("builtins.open", mock_open(read_data=self.jsonl_data)):
            registry = PaperRegistry.from_jsonl("fake_path.jsonl")
            self.assertEqual(registry.get_paper_count(), 3)

    def test_empty_paper_list(self):
        registry = PaperRegistry()
        with self.assertRaises(ValueError):
            registry.get_next_position(0)
        with self.assertRaises(ValueError):
            registry.get_previous_position(0)
        with self.assertRaises(ValueError):
            registry.get_paper_at_position(0)
        with self.assertRaises(ValueError):
            registry.sample_paper_position()


if __name__ == "__main__":
    unittest.main()
