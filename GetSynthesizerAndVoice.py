"""
I still wonder why we choose to use ObjC speech instead of the Pythonista speech module.
"""

from objc_util import ObjCClass, ObjCInstance
from typing import Tuple

AVSpeechUtterance = ObjCClass("AVSpeechUtterance")


def get_synthesizer_and_voice(
        language: str="ja-JP") -> Tuple[ObjCInstance, ObjCInstance]:
    assert isinstance(language, str), (type(language), language)
    AVSpeechSynthesizer = ObjCClass("AVSpeechSynthesizer")
    AVSpeechSynthesisVoice = ObjCClass("AVSpeechSynthesisVoice")
    synthesizer = AVSpeechSynthesizer.new()
    for voice in AVSpeechSynthesisVoice.speechVoices():
        # print(voice, voice.description())
        if language in str(voice.description()):
            return synthesizer, voice
    raise ValueError(f"No voice found for {language}")


def my_say(text: str="Hello", language: str="en-US", rate: float=0.5) -> None:
    try:
        synthesizer, voice = get_synthesizer_and_voice(language)
    except ValueError as e:
        print(e)
        synthesizer, voice = get_synthesizer_and_voice("en-US")
    utterance = AVSpeechUtterance.speechUtteranceWithString_(text)
    #the value that sounds good apparantly depends on ios version
    utterance.rate = rate
    utterance.useCompactVoice = False
    utterance.voice = voice
    synthesizer.speakUtterance_(utterance)
    del utterance


if __name__ == "__main__":
    my_say("Are you talkin' to me?")
    import time
    time.sleep(2)

    my_say("Sprichst du mit mir?", "de-DE")
    time.sleep(2)

    my_say("Sprichst du mit mir?", "junk")
    time.sleep(2)

    my_say("Are you talkin' to me?", rate=0.2)
    time.sleep(4)

    import speech
    speech.say("Are you talkin' to me?")
    while speech.is_speaking():
        time.sleep(0.1)

    speech.say("Sprichst du mit mir?", "de-DE")
    while speech.is_speaking():
        time.sleep(0.1)

    speech.say("Are you talkin' to me?", "", 0.2)
