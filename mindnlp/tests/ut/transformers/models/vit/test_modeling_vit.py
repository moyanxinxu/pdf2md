# coding=utf-8
# Copyright 2021 The HuggingFace Inc. team. All rights reserved.
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
""" Testing suite for the MindSpore ViT model. """

import sys
import numpy as np
import unittest

from mindnlp.transformers.models.vit import ViTConfig
from mindnlp.utils.testing_utils import (
    require_mindspore,
    require_vision,
    slow,
    is_mindspore_available
)
from mindnlp.utils.import_utils import is_vision_available
from ...test_configuration_common import ConfigTester
from ...test_modeling_common import ModelTesterMixin, floats_tensor, ids_tensor



if is_mindspore_available():
    import mindspore
    from mindnlp.core import nn, ops

    from mindnlp.transformers import ViTForImageClassification, ViTForMaskedImageModeling, ViTModel, ViTPreTrainedModel

if is_vision_available():
    from PIL import Image

    from mindnlp.transformers import ViTImageProcessor


class ViTModelTester:
    def __init__(
        self,
        parent,
        batch_size=13,
        image_size=30,
        patch_size=2,
        num_channels=3,
        is_training=True,
        use_labels=True,
        hidden_size=32,
        num_hidden_layers=2,
        num_attention_heads=4,
        intermediate_size=37,
        hidden_act="gelu",
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
        type_sequence_label_size=10,
        initializer_range=0.02,
        scope=None,
        encoder_stride=2,
    ):
        self.parent = parent
        self.batch_size = batch_size
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.is_training = is_training
        self.use_labels = use_labels
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.type_sequence_label_size = type_sequence_label_size
        self.initializer_range = initializer_range
        self.scope = scope
        self.encoder_stride = encoder_stride

        # in ViT, the seq length equals the number of patches + 1 (we add 1 for the [CLS] token)
        num_patches = (image_size // patch_size) ** 2
        self.seq_length = num_patches + 1

    def prepare_config_and_inputs(self):
        pixel_values = floats_tensor([self.batch_size, self.num_channels, self.image_size, self.image_size])

        labels = None
        if self.use_labels:
            labels = ids_tensor([self.batch_size], self.type_sequence_label_size)

        config = self.get_config()

        return config, pixel_values, labels

    def get_config(self):
        return ViTConfig(
            image_size=self.image_size,
            patch_size=self.patch_size,
            num_channels=self.num_channels,
            hidden_size=self.hidden_size,
            num_hidden_layers=self.num_hidden_layers,
            num_attention_heads=self.num_attention_heads,
            intermediate_size=self.intermediate_size,
            hidden_act=self.hidden_act,
            hidden_dropout_prob=self.hidden_dropout_prob,
            attention_probs_dropout_prob=self.attention_probs_dropout_prob,
            is_decoder=False,
            initializer_range=self.initializer_range,
            encoder_stride=self.encoder_stride,
        )

    def create_and_check_model(self, config, pixel_values, labels):
        model = ViTModel(config=config)
        model.set_train(False)
        result = model(pixel_values)
        self.parent.assertEqual(result.last_hidden_state.shape, (self.batch_size, self.seq_length, self.hidden_size))

    def create_and_check_for_masked_image_modeling(self, config, pixel_values, labels):
        model = ViTForMaskedImageModeling(config=config)
        model.set_train(False)
        result = model(pixel_values)
        self.parent.assertEqual(
            result.reconstruction.shape, (self.batch_size, self.num_channels, self.image_size, self.image_size)
        )

        # test greyscale images
        config.num_channels = 1
        model = ViTForMaskedImageModeling(config)
        model.set_train(False)

        pixel_values = floats_tensor([self.batch_size, 1, self.image_size, self.image_size])
        result = model(pixel_values)
        self.parent.assertEqual(result.reconstruction.shape, (self.batch_size, 1, self.image_size, self.image_size))

    def create_and_check_for_image_classification(self, config, pixel_values, labels):
        config.num_labels = self.type_sequence_label_size
        model = ViTForImageClassification(config)
        model.set_train(False)
        result = model(pixel_values, labels=labels)
        self.parent.assertEqual(result.logits.shape, (self.batch_size, self.type_sequence_label_size))

        # test greyscale images
        config.num_channels = 1
        model = ViTForImageClassification(config)
        model.set_train(False)

        pixel_values = floats_tensor([self.batch_size, 1, self.image_size, self.image_size])
        result = model(pixel_values)
        self.parent.assertEqual(result.logits.shape, (self.batch_size, self.type_sequence_label_size))

    def prepare_config_and_inputs_for_common(self):
        config_and_inputs = self.prepare_config_and_inputs()
        (
            config,
            pixel_values,
            labels,
        ) = config_and_inputs
        inputs_dict = {"pixel_values": pixel_values}
        return config, inputs_dict


@require_mindspore
class ViTModelTest(ModelTesterMixin, unittest.TestCase):
    """
    Here we also overwrite some of the tests of test_modeling_common.py, as ViT does not use input_ids, inputs_embeds,
    attention_mask and seq_length.
    """

    all_model_classes = (
        (
            ViTForImageClassification,
            ViTForMaskedImageModeling,
        )
        if is_mindspore_available()
        else ()
    )
    pipeline_model_mapping = (
        {"image-feature-extraction": ViTModel, "image-classification": ViTForImageClassification}
        if is_mindspore_available()
        else {}
    )
    fx_compatible = True

    test_pruning = False
    test_resize_embeddings = False
    test_head_masking = False

    def setUp(self):
        self.model_tester = ViTModelTester(self)
        self.config_tester = ConfigTester(self, config_class=ViTConfig, has_text_modality=False, hidden_size=37)

    def test_config(self):
        self.config_tester.run_common_tests()

    @unittest.skip(reason="ViT does not use inputs_embeds")
    def test_inputs_embeds(self):
        pass

    def test_model_get_set_embeddings(self):
        config, _ = self.model_tester.prepare_config_and_inputs_for_common()
        for model_class in self.all_model_classes:
            model = model_class(config)
            self.assertIsInstance(model.get_input_embeddings(), (nn.Module))
            x = model.get_output_embeddings()
            self.assertTrue(x is None or isinstance(x, nn.Dense))

    def test_model(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_model(*config_and_inputs)

    def test_for_masked_image_modeling(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_for_masked_image_modeling(*config_and_inputs)

    def test_for_image_classification(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_for_image_classification(*config_and_inputs)

    @slow
    def test_model_from_pretrained(self):
        model_name = "google/vit-base-patch16-224"
        model = ViTModel.from_pretrained(model_name, from_pt = True)
        self.assertIsNotNone(model)


# We will verify our results on an image of cute cats
def prepare_img():
    image = Image.open("./tests/fixtures/tests_samples/COCO/000000039769.png")
    return image


@require_mindspore
@require_vision
class ViTModelIntegrationTest(unittest.TestCase):
    #@cached_property
    def default_image_processor(self):
        return ViTImageProcessor.from_pretrained("google/vit-base-patch16-224", from_pt = True) if is_vision_available() else None
    @slow
    def test_inference_image_classification_head(self):
        model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224", from_pt = True)

        #image_processor = self.default_image_processor
        image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224", from_pt = True)
        image = prepare_img()
        inputs = image_processor(images=image, return_tensors="ms")

        # forward pass
        outputs = model(**inputs)

        # verify the logits
        expected_shape = (1, 1000)
        self.assertEqual(outputs.logits.shape, expected_shape)
        expected_slice = mindspore.tensor([-0.2744, 0.8215, -0.0836])
        self.assertTrue(np.allclose(outputs.logits[0, :3].asnumpy(), expected_slice.asnumpy(), atol=1e-4))

    @slow
    def test_inference_interpolate_pos_encoding(self):
        # ViT models have an `interpolate_pos_encoding` argument in their forward method,
        # allowing to interpolate the pre-trained position embeddings in order to use
        # the model on higher resolutions. The DINO model by Facebook AI leverages this
        # to visualize self-attention on higher resolution images.
        model = ViTModel.from_pretrained("facebook/dino-vits8", from_pt = True)

        image_processor = ViTImageProcessor.from_pretrained("facebook/dino-vits8", size=480, from_pt = True)
        image = prepare_img()
        inputs = image_processor(images=image, return_tensors="ms")
        pixel_values = inputs.pixel_values

        # forward pass
        outputs = model(pixel_values, interpolate_pos_encoding=True)

        # verify the logits
        expected_shape = (1, 3601, 384)
        self.assertEqual(outputs.last_hidden_state.shape, expected_shape)

        expected_slice = mindspore.tensor(
            [[4.2340, 4.3906, -6.6692], [4.5463, 1.8928, -6.7257], [4.4429, 0.8496, -5.8585]]
        )
        self.assertTrue(np.allclose(outputs.last_hidden_state[0, :3, :3].asnumpy(), expected_slice.asnumpy(), atol=1e-4))

    @slow
    def test_inference_fp16(self):
        r"""
        A small test to make sure that inference work in half precision without any problem.
        """
        model = ViTModel.from_pretrained("facebook/dino-vits8", ms_dtype=mindspore.float16, from_pt = True)
        #image_processor = self.default_image_processor
        image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224", from_pt = True)

        image = prepare_img()
        inputs = image_processor(images=image, return_tensors="ms")
        pixel_values = inputs.pixel_values

        # forward pass to make sure inference works in fp16
        _ = model(pixel_values)