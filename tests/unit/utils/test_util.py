from story_protocol_python_sdk.utils.util import (
    convert_dict_keys_to_camel_case,
    snake_to_camel,
)


class TestSnakeToCamel:
    def test_single_word(self):
        assert snake_to_camel("hello") == "hello"

    def test_two_words(self):
        assert snake_to_camel("hello_world") == "helloWorld"

    def test_multiple_words(self):
        assert snake_to_camel("this_is_a_test") == "thisIsATest"

    def test_empty_string(self):
        assert snake_to_camel("") == ""

    def test_already_camel_case(self):
        assert snake_to_camel("alreadyCamel") == "alreadyCamel"


class TestConvertDictKeysToCamelCase:
    def test_single_key(self):
        result = convert_dict_keys_to_camel_case({"hello_world": 1})
        assert result == {"helloWorld": 1}

    def test_multiple_keys(self):
        result = convert_dict_keys_to_camel_case(
            {
                "first_key": 1,
                "second_key": 2,
                "third_key": 3,
            }
        )
        assert result == {
            "firstKey": 1,
            "secondKey": 2,
            "thirdKey": 3,
        }

    def test_empty_dict(self):
        result = convert_dict_keys_to_camel_case({})
        assert result == {}
