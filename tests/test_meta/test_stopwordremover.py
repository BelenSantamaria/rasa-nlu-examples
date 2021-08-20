import pytest
import pathlib
from rasa_nlu_examples.meta import StopWordRemover
from rasa.shared.nlu.training_data.message import Message


remover = StopWordRemover(
    component_config={
        "path": pathlib.Path.cwd() / "tests" / "data" / "stopwords" / "stopwords.txt"
    }
)
checks = [
    ("", ""),
    ("this is a stopword", "this is a"),
    ("stop that word", "that"),
    ("words", "s"),
]


@pytest.mark.parametrize("goes_in, goes_out", checks)
def test_leaves_empty_msg_alone(goes_in, goes_out):
    message = Message(text="")
    remover.process(message)
    assert message.get("text") == ""
