#!/usr/bin/env python3

import sys
import unittest

sys.path.append('../..')
import maildog as md


class TestExtractContents(unittest.TestCase):
    """
    Make sure the email language is detected correctly
    """

    msg = md.Mail()

    def test_detect_english_name(self):
        self.msg.body = """I have just taken a course and am interested to come.
        Do I have to register? \r\nThanks, \r\nMike"""
        self.msg.subject = 'Hi everybody!'
        self.msg.detect_language()
        self.msg.analyze_text()
        self.msg.extract_info_from_tags()
        print(self.msg.info)
        # print(self.msg._doc)
        self.assertEqual(self.msg.info['first_name'], 'Mike')

    # def test_detect_german(self):
    #     self.msg.body = 'Ein normaler Text mit einigen Informationen.'
    #     self.msg.subject = 'Hallo'
    #     self.msg.detect_language()
    #     self.assertEqual(self.msg.language, 'german')

    # # def test_detect_italian(self):
    # #     # # TODO: the following text fails
    # #     # self.msg.body = 'Cosa posso fare. Vuoi partecipare. Prego! Ciao!'
    # #     # # This one is less difficult, sometimes english, sometimes italian.
    # #     self.msg.body = "Posso essere d'aiuto? Non può andare a finire bene!"
    # #     self.msg.subject = 'Ciao'
    # #     self.msg.detect_language()
    # #     self.assertEqual(self.msg.language, 'italian')

    # def test_detect_french(self):
    #     self.msg.body = 'Je peux vous aider ?'
    #     self.msg.subject = 'Bonjour'
    #     self.msg.detect_language()
    #     self.assertEqual(self.msg.language, 'french')

# language = 'german'
# body = 'Hallo zusammen\r\nIch habe gerade einen Kurs gemacht und bin interessiert zu kommen. Muss ich mich da anmelden?\r\nLiebe Grüsse\r\nHeike'
# doc = nlp(body)
# print([(w.text, w.pos_) for w in doc])

# language = 'english'
# body = 'Hi everybody! I have just taken a course and am interested to come. Do I have to register? \r\nThanks, \r\nMike'

# import en_core_web_sm
# nlp = en_core_web_sm.load()
# doc = nlp(body)
# doc = nlp(u"This is a sentence.")
# print([(w.text, w.pos_) for w in doc])

# language = 'french'
# body = 'Salut tout le monde! Je viens de suivre un cours et je suis intéressé à venir. Dois-je m\'inscrire? \r\nMerci,\nFranci'

# import fr_core_news_sm
# nlp = fr_core_news_sm.load()
# doc = nlp(body)
# # doc = nlp(u"C'est une phrase.")
# # print([(w.text, w.pos_) for w in doc])

# def analyze_text(body, nlp):
#     pred = nlp(body)
#     return pred

# def get_first_name(predicted):
#     candidates = [w.text for w in doc if w.pos_ == 'PROPN']
#     return candidates


# text = analyze_text(body, nlp)
# names = get_first_name(text)
# print(names)
