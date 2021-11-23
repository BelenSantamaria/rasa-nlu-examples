import pathlib
import pytest
import scipy.sparse

from rasa.model_training import train_nlu
from rasa.shared.nlu.training_data.message import Message
from rasa_nlu_examples.scikit import load_interpreter
from rasa_nlu_examples.featurizers.sparse.hashing_featurizer import HashingFeaturizer
from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer

from .sparse_featurizer_checks import sparse_standard_test_combinations

component_config = dict(n_features=1024, norm=None)


@pytest.mark.parametrize(
    "test_fn,tok,feat,msg",
    sparse_standard_test_combinations(
        tokenizer=WhitespaceTokenizer(),
        featurizer=HashingFeaturizer(component_config=component_config),
    ),
)
def test_auto_featurizer_checks(test_fn, tok, feat, msg):
    test_fn(tok, feat, msg)


@pytest.fixture
def whitespace_tokenizer() -> WhitespaceTokenizer:
    return WhitespaceTokenizer()


@pytest.fixture
def hashing_featurizer() -> HashingFeaturizer:
    return HashingFeaturizer(component_config=component_config)


def test_features_are_sparse(
    whitespace_tokenizer: WhitespaceTokenizer,
    hashing_featurizer: HashingFeaturizer,
):
    message = Message.build("am I talking to a bot")

    whitespace_tokenizer.process(message)
    hashing_featurizer.process(message)

    for feature in message.features:
        assert scipy.sparse.issparse(feature.features)


def test_feature_shapes(
    whitespace_tokenizer: WhitespaceTokenizer,
    hashing_featurizer: HashingFeaturizer,
):
    message = Message.build("am I talking to a bot")

    whitespace_tokenizer.process(message)
    hashing_featurizer.process(message)

    feat_tok, feat_sent = message.get_sparse_features("text")
    assert feat_tok.features.shape == (6, 1024)
    assert feat_sent.features.shape == (1, 1024)
    assert feat_tok.features.sum() == feat_sent.features.sum()


def test_feature_overlap(
    whitespace_tokenizer: WhitespaceTokenizer,
    hashing_featurizer: HashingFeaturizer,
):
    message_1 = Message.build("am I talking to a bot")
    whitespace_tokenizer.process(message_1)
    hashing_featurizer.process(message_1)

    message_2 = Message.build("sharing a subset of words")
    whitespace_tokenizer.process(message_2)
    hashing_featurizer.process(message_2)

    message_3 = Message.build("completely different message")
    whitespace_tokenizer.process(message_3)
    hashing_featurizer.process(message_3)

    _, feat_sent_1 = message_1.get_sparse_features("text")
    _, feat_sent_2 = message_2.get_sparse_features("text")
    _, feat_sent_3 = message_3.get_sparse_features("text")

    # the first ans second message have overlapping vocabulary, so some column
    # index should contain non-zero values in both
    assert feat_sent_1.features.dot(feat_sent_2.features.T) > 0
    assert feat_sent_1.features.dot(feat_sent_3.features.T) == 0
