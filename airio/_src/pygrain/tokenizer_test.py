# Copyright 2024 The AirIO Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for airio.tokenizer."""

import os
from unittest import mock

from absl.testing import absltest
from airio._src.core import tokenizer as core_tokenizer
from airio._src.pygrain import tokenizer
import numpy as np
from seqio import vocabularies


_TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../test_data"
)


class TokenizerTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    sentencepiece_vocab = vocabularies.SentencePieceVocabulary(
        os.path.join(_TEST_DATA_DIR, "sentencepiece", "sentencepiece.model")
    )
    self.tokenizer_configs = {
        "inputs": core_tokenizer.TokenizerConfig(vocab=sentencepiece_vocab),
        "targets": core_tokenizer.TokenizerConfig(vocab=sentencepiece_vocab),
    }

  def test_tokenizer_properties(self):
    tokenizer_obj = tokenizer.Tokenizer(
        tokenizer_configs=self.tokenizer_configs
    )
    self.assertDictEqual(
        tokenizer_obj.tokenizer_configs, self.tokenizer_configs
    )
    self.assertEqual(tokenizer_obj.copy_pretokenized, True)
    self.assertEqual(tokenizer_obj.with_eos, False)

  def test_tokenize(self):
    orig_example = {
        "inputs": "imdb ebc   ahgjefjhfe",
        "targets": "positive",
    }
    tokenizer_obj = tokenizer.Tokenizer(
        tokenizer_configs=self.tokenizer_configs
    )
    tokenized_example = tokenizer_obj(orig_example)
    expected_example = {
        "inputs_pretokenized": "imdb ebc   ahgjefjhfe",
        "inputs": np.array(
            [3, 8, 14, 21, 2, 3, 4, 2, 13, 3, 5, 20, 2, 4, 2, 20, 2, 4]
        ),
        "targets_pretokenized": "positive",
        "targets": np.array([3, 15, 7, 6, 8, 24, 8, 25, 4]),
    }
    for feature, value in tokenized_example.items():
      if isinstance(value, np.ndarray):
        np.testing.assert_allclose(value, expected_example[feature])
      else:
        self.assertEqual(value, expected_example[feature])

  def test_tokenize_feature_not_in_config(self):
    orig_example = {
        "metadata": "sequence metadata",
    }
    tokenizer_obj = tokenizer.Tokenizer(
        tokenizer_configs=self.tokenizer_configs
    )
    tokenized_example = tokenizer_obj(orig_example)
    for feature, value in tokenized_example.items():
      if isinstance(value, np.ndarray):
        np.testing.assert_allclose(value, orig_example[feature])
      else:
        self.assertEqual(value, orig_example[feature])

  def test_tokenize_do_not_copy_pretokenized(self):
    orig_example = {
        "inputs": "imdb ebc   ahgjefjhfe",
        "targets": "positive",
    }
    tokenizer_obj = tokenizer.Tokenizer(
        tokenizer_configs=self.tokenizer_configs,
        copy_pretokenized=False,
    )
    tokenized_example = tokenizer_obj(orig_example)
    expected_example = {
        "inputs": np.array(
            [3, 8, 14, 21, 2, 3, 4, 2, 13, 3, 5, 20, 2, 4, 2, 20, 2, 4]
        ),
        "targets": np.array([3, 15, 7, 6, 8, 24, 8, 25, 4]),
    }
    for feature, value in tokenized_example.items():
      if isinstance(value, np.ndarray):
        np.testing.assert_allclose(value, expected_example[feature])
      else:
        self.assertEqual(value, expected_example[feature])

  def test_tokenize_empty(self):
    tokenizer_obj = tokenizer.Tokenizer(
        tokenizer_configs=self.tokenizer_configs
    )
    tokenized_example = tokenizer_obj({})
    self.assertEmpty(tokenized_example)



if __name__ == "__main__":
  absltest.main()
