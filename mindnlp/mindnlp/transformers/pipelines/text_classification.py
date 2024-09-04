# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""text classification pipeline."""
import inspect
import warnings
from typing import Dict

import numpy as np

from mindnlp.utils import ExplicitEnum
from .base import GenericTensor, Pipeline

def sigmoid(_outputs):
    """
    Args:
        _outputs (numeric): The input value to calculate the sigmoid function.
        
    Returns:
        float: The output value after applying the sigmoid function.
        
    Raises:
        None
    """
    return 1.0 / (1.0 + np.exp(-_outputs))


def softmax(_outputs):
    """
    This function calculates the softmax values of the input array _outputs.

    Args:
        _outputs (numpy.ndarray): The input array containing the logits.

    Returns:
        numpy.ndarray: The softmax values of the input array.

    Raises:
        None
    """
    maxes = np.max(_outputs, axis=-1, keepdims=True)
    shifted_exp = np.exp(_outputs - maxes)
    return shifted_exp / shifted_exp.sum(axis=-1, keepdims=True)


class ClassificationFunction(ExplicitEnum):

    """
    Represents a classification function that can be used to classify data into different categories.
    
    This class inherits from the ExplicitEnum class.
    
    Attributes:
        None
    
    Methods:
        None
    
    """
    SIGMOID = "sigmoid"
    SOFTMAX = "softmax"
    NONE = "none"


class TextClassificationPipeline(Pipeline):
    """
    Text classification pipeline using any `ModelForSequenceClassification`. See the [sequence classification
    examples](../task_summary#sequence-classification) for more information.

    Example:
        ```python
        >>> from transformers import pipeline
        ...
        >>> classifier = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")
        >>> classifier("This movie is disgustingly good !")
        [{'label': 'POSITIVE', 'score': 1.0}]
        ...
        >>> classifier("Director tried too much.")
        [{'label': 'NEGATIVE', 'score': 0.996}]
        ```

    Learn more about the basics of using a pipeline in the [pipeline tutorial](../pipeline_tutorial)

    This text classification pipeline can currently be loaded from [`pipeline`] using the following task identifier:
    `"sentiment-analysis"` (for classifying sequences according to positive or negative sentiments).

    If multiple classification labels are available (`model.config.num_labels >= 2`), the pipeline will run a softmax
    over the results. If there is a single label, the pipeline will run a sigmoid over the result.

    The models that this pipeline can use are models that have been fine-tuned on a sequence classification task. See
    the up-to-date list of available models on
    [hf-mirror.com/models](https://hf-mirror.com/models?filter=text-classification).
    """
    return_all_scores = False
    function_to_apply = ClassificationFunction.NONE

    def __init__(self, **kwargs):
        """
        Initializes an instance of the TextClassificationPipeline class.

        Args:
            self: The instance of the class.

        Returns:
            None.

        Raises:
            None.
        """
        super().__init__(**kwargs)

    def _sanitize_parameters(self, return_all_scores=None, function_to_apply=None, top_k="", **tokenizer_kwargs):
        """
        Sanitizes and processes the parameters for the TextClassificationPipeline.

        Args:
            self (TextClassificationPipeline): An instance of the TextClassificationPipeline class.
            return_all_scores (bool, optional): Whether to return all scores. Defaults to None.
            function_to_apply (str or ClassificationFunction, optional): The function to apply for classification.
                Can be a string representing one of the ClassificationFunction options or an instance of ClassificationFunction enum.
                Defaults to None.
            top_k (int or None, optional): The number of top predictions to return. Defaults to ''.

        Returns:
            tuple:
                A tuple containing three dictionaries: preprocess_params, an empty dictionary, and postprocess_params.

                - preprocess_params (dict): The parameters for tokenization and preprocessing.
                - postprocess_params (dict): The parameters for post-processing.

        Raises:
            UserWarning: If `return_all_scores` is set to True or False, as it is now deprecated.
        """
        # Using "" as default argument because we're going to use `top_k=None` in user code to declare
        # "No top_k"
        preprocess_params = tokenizer_kwargs

        postprocess_params = {}
        if hasattr(self.model.config, "return_all_scores") and return_all_scores is None:
            return_all_scores = self.model.config.return_all_scores

        if isinstance(top_k, int) or top_k is None:
            postprocess_params["top_k"] = top_k
            postprocess_params["_legacy"] = False
        elif return_all_scores is not None:
            warnings.warn(
                "`return_all_scores` is now deprecated,  if want a similar functionality use `top_k=None` instead of"
                " `return_all_scores=True` or `top_k=1` instead of `return_all_scores=False`.",
                UserWarning,
            )
            if return_all_scores:
                postprocess_params["top_k"] = None
            else:
                postprocess_params["top_k"] = 1

        if isinstance(function_to_apply, str):
            function_to_apply = ClassificationFunction[function_to_apply.upper()]

        if function_to_apply is not None:
            postprocess_params["function_to_apply"] = function_to_apply
        return preprocess_params, {}, postprocess_params

    def __call__(self, *args, **kwargs):
        """
        Classify the text(s) given as inputs.

        Args:
            args (`str` or `List[str]` or `Dict[str]`, or `List[Dict[str]]`):
                One or several texts to classify. In order to use text pairs for your classification, you can send a
                dictionary containing `{"text", "text_pair"}` keys, or a list of those.
            top_k (`int`, *optional*, defaults to `1`):
                How many results to return.
            function_to_apply (`str`, *optional*, defaults to `"default"`):
                The function to apply to the model outputs in order to retrieve the scores. Accepts four different
                values:

                If this argument is not specified, then it will apply the following functions according to the number
                of labels:

                - If the model has a single label, will apply the sigmoid function on the output.
                - If the model has several labels, will apply the softmax function on the output.

                Possible values are:

                - `"sigmoid"`: Applies the sigmoid function on the output.
                - `"softmax"`: Applies the softmax function on the output.
                - `"none"`: Does not apply any function on the output.

        Returns:
            A list or a list of list of `dict`:
                Each result comes as list of dictionaries with the following keys:

                - **label** (`str`) -- The label predicted.
                - **score** (`float`) -- The corresponding probability.

            If `top_k` is used, one such dictionary is returned per label.
        """
        result = super().__call__(*args, **kwargs)
        # TODO try and retrieve it in a nicer way from _sanitize_parameters.
        _legacy = "top_k" not in kwargs
        if isinstance(args[0], str) and _legacy:
            # This pipeline is odd, and return a list when single item is run
            return [result]
        else:
            return result

    def preprocess(self, inputs, **tokenizer_kwargs) -> Dict[str, GenericTensor]:
        """
        Preprocesses the input data for text classification using a tokenizer.

        Args:
            self: An instance of the TextClassificationPipeline class.
            inputs: The input data to be preprocessed. It can be one of the following:

                - A dictionary containing the text and text_pair keys, representing the main text and its paired text
                for classification.
                - A list containing a single sublist with two elements, representing the main text and its paired text
                for classification.
                - A list containing only the main text for classification.

        Returns:
            A dictionary containing preprocessed inputs in the form of {"input_ids": tensor, "attention_mask": tensor}.
                The tensors represent the encoded input sequences and attention masks, respectively.
                The keys in the dictionary are as follows:

                - "input_ids": A tensor containing the encoded input sequences.
                - "attention_mask": A tensor indicating which tokens should be attended to.

        Raises:
            ValueError: If the inputs are invalid and don't match any of the supported formats.
        """
        if isinstance(inputs, dict):
            return self.tokenizer(**inputs, return_tensors='ms', **tokenizer_kwargs)
        elif isinstance(inputs, list) and len(inputs) == 1 and isinstance(inputs[0], list) and len(inputs[0]) == 2:
            # It used to be valid to use a list of list of list for text pairs, keeping this path for BC
            return self.tokenizer(
                text=inputs[0][0], text_pair=inputs[0][1], return_tensors='ms', **tokenizer_kwargs
            )
        elif isinstance(inputs, list):
            # This is likely an invalid usage of the pipeline attempting to pass text pairs.
            raise ValueError(
                "The pipeline received invalid inputs, if you are trying to send text pairs, you can try to send a"
                ' dictionary `{"text": "My text", "text_pair": "My pair"}` in order to send a text pair.'
            )
        return self.tokenizer(inputs, return_tensors='ms', **tokenizer_kwargs)

    def _forward(self, model_inputs):
        """
        Forward the model with the provided inputs.

        Args:
            self (TextClassificationPipeline): The instance of the TextClassificationPipeline class.
            model_inputs (dict): The input parameters for the model_forward method.

        Returns:
            None.

        Raises:
            TypeError: If the model_forward method does not accept the 'use_cache' parameter.
            Exception: Any other unhandled exceptions may be raised during the execution of the model_forward method.
        """
        # `XXXForSequenceClassification` models should not use `use_cache=True` even if it's supported
        model_forward = self.model.forward
        if "use_cache" in inspect.signature(model_forward).parameters.keys():
            model_inputs["use_cache"] = False
        return model_forward(**model_inputs)

    def postprocess(self, model_outputs, function_to_apply=None, top_k=1, _legacy=True):
        """
        Postprocess method in the TextClassificationPipeline class.

        Args:
            self (object): The instance of the TextClassificationPipeline class.
            model_outputs (dict):
                The dictionary containing model outputs with the following keys:

                - 'logits': A tensor representing the model logits.
            function_to_apply (ClassificationFunction): The function to apply to the model outputs.
                Can be one of the following:

                - ClassificationFunction.SIGMOID: Applies the sigmoid function.
                - ClassificationFunction.SOFTMAX: Applies the softmax function.
                - ClassificationFunction.NONE: No function applied.
            top_k (int): The number of top predictions to return. Default is 1.
            _legacy (bool): A flag indicating whether to use legacy behavior. Default is True.

        Returns:
            dict or None:
                If top_k is 1 and _legacy is True, returns a dictionary with keys:

                - 'label': The predicted label.
                - 'score': The confidence score of the prediction.

                If top_k is not 1 or _legacy is False, returns a list of dictionaries with keys:

                - 'label': The predicted label.
                - 'score': The confidence score of the prediction.

                The list is sorted by score in descending order and truncated to top_k if specified.
        
        Raises:
            ValueError: If the function_to_apply argument is not recognized.
        """
        # `_legacy` is used to determine if we're running the naked pipeline and in backward
        # compatibility mode, or if running the pipeline with `pipeline(..., top_k=1)` we're running
        # the more natural result containing the list.
        # Default value before `set_parameters`
        if function_to_apply is None:
            if self.model.config.problem_type == "multi_label_classification" or self.model.config.num_labels == 1:
                function_to_apply = ClassificationFunction.SIGMOID
            elif self.model.config.problem_type == "single_label_classification" or self.model.config.num_labels > 1:
                function_to_apply = ClassificationFunction.SOFTMAX
            elif hasattr(self.model.config, "function_to_apply") and function_to_apply is None:
                function_to_apply = self.model.config.function_to_apply
            else:
                function_to_apply = ClassificationFunction.NONE

        outputs = model_outputs["logits"][0]
        outputs = outputs.numpy()

        if function_to_apply == ClassificationFunction.SIGMOID:
            scores = sigmoid(outputs)
        elif function_to_apply == ClassificationFunction.SOFTMAX:
            scores = softmax(outputs)
        elif function_to_apply == ClassificationFunction.NONE:
            scores = outputs
        else:
            raise ValueError(f"Unrecognized `function_to_apply` argument: {function_to_apply}")

        if top_k == 1 and _legacy:
            return {"label": self.model.config.id2label[scores.argmax().item()], "score": scores.max().item()}

        dict_scores = [
            {"label": self.model.config.id2label[i], "score": score.item()} for i, score in enumerate(scores)
        ]
        if not _legacy:
            dict_scores.sort(key=lambda x: x["score"], reverse=True)
            if top_k is not None:
                dict_scores = dict_scores[:top_k]
        return dict_scores
