# coding=utf-8
# Copyright 2020 The HuggingFace Team. All rights reserved.
# Copyright 2023 Huawei Technologies Co., Ltd
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
# ============================================================================
"""test xlm roberta"""

import pytest

import numpy as np
import mindspore
from mindnlp.transformers import XLMRobertaModel
from .....common import MindNLPTestCase

class XLMRobertaModelIntegrationTest(MindNLPTestCase):
    """XLMRobertaModelIntegrationTest"""
    @pytest.mark.download
    def test_xlm_roberta_base(self):
        """test_xlm_roberta_base"""
        model = XLMRobertaModel.from_pretrained("xlm-roberta-base")
        input_ids = mindspore.tensor([[0, 581, 10269, 83, 99942, 136, 60742, 23, 70, 80583, 18276, 2]])
        # The dog is cute and lives in the garden house

        expected_output_shape = (1, 12, 768)  # batch_size, sequence_length, embedding_vector_dim
        expected_output_values_last_dim = mindspore.tensor(
            [[-0.0101, 0.1218, -0.0803, 0.0801, 0.1327, 0.0776, -0.1215, 0.2383, 0.3338, 0.3106, 0.0300, 0.0252]]
        )
        output = model(input_ids)["last_hidden_state"]
        self.assertEqual(output.shape, expected_output_shape)
        # compare the actual values for a slice of last dim
        self.assertTrue(np.allclose(output[:, :, -1].asnumpy(), expected_output_values_last_dim.asnumpy(), atol=1e-3))

    @pytest.mark.download
    def test_xlm_roberta_large(self):
        """test_xlm_roberta_large"""
        model = XLMRobertaModel.from_pretrained("xlm-roberta-large")
        input_ids = mindspore.tensor([[0, 581, 10269, 83, 99942, 136, 60742, 23, 70, 80583, 18276, 2]])
        # The dog is cute and lives in the garden house

        expected_output_shape = (1, 12, 1024)  # batch_size, sequence_length, embedding_vector_dim
        expected_output_values_last_dim = mindspore.tensor(
            [[-0.0699, -0.0318, 0.0705, -0.1241, 0.0999, -0.0520, 0.1004, -0.1838, -0.4704, 0.1437, 0.0821, 0.0126]]
        )
        output = model(input_ids)["last_hidden_state"]
        self.assertEqual(output.shape, expected_output_shape)
        # compare the actual values for a slice of last dim
        self.assertTrue(np.allclose(output[:, :, -1].asnumpy(), expected_output_values_last_dim.asnumpy(), atol=1e-3))
