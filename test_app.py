import unittest
import hashlib
from app import hash_password, build_check_prompt, build_generation_prompt

class TestStorytellerApp(unittest.TestCase):
    def test_hash_password(self):
        # Verify hashing is reproducible and matches sha256 output
        raw_pw = "mySecretPassword123"
        hashed = hash_password(raw_pw)
        expected = hashlib.sha256(raw_pw.encode()).hexdigest()
        self.assertEqual(hashed, expected)

    def test_build_check_prompt(self):
        # Test helper formats correct prompt string
        prompt = "Once upon a time in space"
        check_prompt = build_check_prompt(prompt)
        self.assertIn("Once upon a time in space", check_prompt)
        self.assertTrue(check_prompt.endswith("Answer only 'yes' or 'no'."))

    def test_build_generation_prompt(self):
        # Test generation prompt formatting
        user_prompt = "A quest for a lost key"
        genre = "Fantasy"
        tone = "Whimsical"
        length = "Short (1-2 paragraphs)"
        
        gen_prompt = build_generation_prompt(user_prompt, genre, tone, length, outline=True)
        self.assertIn(user_prompt, gen_prompt)
        self.assertIn(genre, gen_prompt)
        self.assertIn("Whimsical", gen_prompt)
        self.assertIn("short (1-2 paragraphs)", gen_prompt)
        self.assertIn("Also produce a 3-bullet outline", gen_prompt)

if __name__ == '__main__':
    unittest.main()
