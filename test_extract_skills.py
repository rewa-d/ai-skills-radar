import unittest

from extract_skills import match_dictionary_skills


class MatchDictionarySkillsTests(unittest.TestCase):
    def test_matches_skills_case_insensitively(self):
        description = "Build models with PYTHON, pandas, and Vertex AI."
        dictionary = ["Python", "Pandas", "Vertex AI", "Java"]

        self.assertEqual(
            match_dictionary_skills(description, dictionary),
            ["Python", "Pandas", "Vertex AI"]
        )

    def test_uses_whole_word_matching(self):
        description = "We use JavaScript and PostgreSQL."
        dictionary = ["Java", "JavaScript", "SQL", "PostgreSQL"]

        self.assertEqual(
            match_dictionary_skills(description, dictionary),
            ["JavaScript", "PostgreSQL"]
        )

    def test_matches_skills_with_punctuation(self):
        description = "Services are written in C++ and Node.js with CI/CD."
        dictionary = ["C++", "Node.js", "CI/CD", "C"]

        self.assertEqual(
            match_dictionary_skills(description, dictionary),
            ["C++", "Node.js", "CI/CD"]
        )


if __name__ == "__main__":
    unittest.main()
