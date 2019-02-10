#!/usr/bin/env python3

# import pdb; pdb.set_trace()

import spacy
# from nltk import wordpunct_tokenize
# from nltk.corpus import stopwords
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage
from email.utils import COMMASPACE, formatdate
from jinja2 import Environment, FileSystemLoader, select_autoescape
from itertools import chain
import pycld2 as cld2

from maildog.rulesets import _find_files


class Mail(object):
    body = None
    subject = None
    to = None
    fro = None
    reply_to = None
    html = None
    date = None
    attachments = None
    tokens = None
    language = None
    ruleset = None
    uid = None
    reply = None
    raw_message = None
    reply_message = None
    send_result = None
    _doc = None
    info = None

    def extract_info_from_tags(self):
        """Tag email contents with part-of-speech classifications.

        @return: dictionary with keywords and their values as deduced from the
        email's body

        @rtype: dict

        """

        def _dissect_email(fro):
            name = fro.split('@')[0].lower()
            res = name.split('.') if '.' in name else name.split('_')
            return res

        def _get_names_from_email(doc):
            # candidates = [w.text.lower() for w in doc if w.pos_ == 'PROPN']
            # # Less stringent that the above line
            candidates = [w.text.lower() for w in doc if w.pos_ in ['NOUN', 'PROPN']]
            print(candidates)
            username = _dissect_email(self.fro)
            res = [n for n in candidates if n in username]
            return res

        self.info = {}
        self.info["first_name"] = _get_names_from_email(self._doc)
        # self.info["last_name"] = self._get_last_name(self._doc)
        return self.info

    def analyze_text(self):
        nlp = spacy.load(self.language)
        self._doc = nlp(self.subject + '\n' + self.body)
        self.tokens = [token.text for token in self._doc]
        return self._doc

    def detect_language(self):
        """
        Uses the refactored version of Google's compact language detector.

        Works for up to 80 languages.
        @return: highest scored language code
        @rtype: str

        """

        _, _, details = cld2.detect(self.subject + self.body)
        self.language = details[0][1]
        # print(details)
        # import pdb; pdb.set_trace()
        return self.language

    # def detect_language_simple_nltk(self):
    #     """
    #     Author: Alejandro Nolla - z0mbiehunt3r
    #     Purpose: detect language using a stopwords-based approach
    #     Created: 15/05/13
    #     Calculate probability of given tokens to be written in several
    #     languages and return the highest scored.

    #     It uses a stopwords based approach, counting how many unique
    #     stopwords are seen in analyzed text.

    #     @return: highest scored language according to number of stopwordsk
    #     @rtype: str
    #     """

    #     def _tokenize_email(body, subject):
    #         tokens = wordpunct_tokenize(subject + " " + body)
    #         tokens = [word.lower() for word in tokens]
    #         return tokens

    #     def _calculate_languages_ratios(words):
    #         """Calculate probability of given text to be written in several languages
    #         and return a dictionary that looks like {'french': 2, 'spanish': 4,
    #         'english': 0}

    #         @param words: Text whose language want to be detected
    #         @type words: str

    #         @return: Dictionary with languages and unique stopwords seen in
    #         analyzed words

    #         @rtype: dict

    #         """

    #         languages_ratios = {}
    #         # Compute per language included in nltk number of unique stopwords
    #         # appearing in analyzed text
    #         for language in stopwords.fileids():
    #             stopwords_set = set(stopwords.words(language))
    #             words_set = set(words)
    #             # common_elements = words_set.intersection(stopwords_set)
    #             common_elements = words_set.difference(stopwords_set)
    #             # language "score"
    #             languages_ratios[language] = len(common_elements)

    #         return languages_ratios

    #     self.tokens = _tokenize_email(self.body, self.subject)
    #     # print(self.tokens)
    #     ratios = _calculate_languages_ratios(self.tokens)
    #     self.language = min(ratios, key=ratios.get)
    #     return self.language

    def choose_ruleset(self, rulesets):
        """Applies logical questions to determine what the proper answer is.  Returns a
        template to be rendered with the addresses data.  It excludes any
        disqualified ruleset or any unqualified ruleset (no matches).

        Also prepares any possible attachments for a ruleset
        @param rulesets: rules for choosing and excluding a template for answer
        @type rulesets: [namedtuple]


        @param ruleset: rules that apply to self.tokens
        @rtype ruleset: namedtuple

        """

        rulesets = [r for r in rulesets if r.language == self.language]
        ruleset_scores = [0 for i in range(len(rulesets))]
        for i, x in enumerate(rulesets):
            qualifiers = x.qualifiers.split(' ')
            for token in self.tokens:
                if token in x.disqualifiers:
                    continue
                if len(token) > 3:
                    if token in x.qualifiers:
                        ruleset_scores[i] += 1
                elif token in qualifiers:
                    ruleset_scores[i] += 1

        if ruleset_scores:
            top_score = max(ruleset_scores)
            if top_score > 0:
                self.ruleset = rulesets[ruleset_scores.index(top_score)]
                if self.ruleset.attachments:
                    self.attachments = self.ruleset.attachments.split(' ')
                    return self.ruleset
                if self.ruleset.html:
                    self.html = True

    def compose_reply(self, reply_data_dir, reply_prefix='RE: '):
        """
        Put everything together into a nice reply email
        """
        assert isinstance(self.reply_to, list)

        rply = MIMEMultipart()
        rply['From'] = self.to
        rply['To'] = COMMASPACE.join(self.reply_to)
        rply['Date'] = formatdate(localtime=True)
        # rply['Date'] = datetime.datetime.today().isoformat()
        rply['Subject'] = reply_prefix + self.subject
        rply["In-Reply-To"] = self.message_id
        rply["References"] = self.message_id
        if self.html:
            rply.attach(MIMEText(self.reply_message, 'html', 'utf-8'))
        else:
            rply.attach(MIMEText(self.reply_message, 'plain', 'utf-8'))

        # import pdb; pdb.set_trace()
        # orig_msg = MIMEMessage(self.raw_message)
        rply.attach(MIMEMessage(self.raw_message))

        if self.attachments:
            files = chain(*[_find_files(f, reply_data_dir)
                            for f in self.attachments])

            for f in files:
                print('Attaching: ' + f)
                with open(f, "rb") as fcon:
                    p = MIMEApplication(fcon.read(), Name=basename(f))
                    # After the file is closed
                    p['Content-Disposition'] = 'attachment; filename="%s"' \
                                                              % basename(f)
                    rply.attach(p)

        return rply

    def compose_notify_owner(self, rulesets, owner):

        rply = MIMEText(self.body + '\n\n'
                        + 'Language: %s\n' % self.language
                        + 'Tokens: %s\n' % ';'.join(self.tokens)
                        + '\n'.join(str(r._asdict()) for r in rulesets))
        rply['From'] = self.to
        rply['To'] = owner
        rply['Date'] = formatdate(localtime=True)
        # rply['Date'] = datetime.datetime.today().isoformat()
        rply['Subject'] = '[MAILDOG Unknown] RE: %s' % self.subject

        return rply

    def render_template(self, reply_template_dir):
        """
        Returns a rendered template to be sent used as email body text.
        """
        # template_path = _find_file(template, '.')
        # if not os.path.isfile(template_path):
        #     raise FileNotFoundError('Template, "%s", not found' % template)

        env = Environment(
            loader=FileSystemLoader(reply_template_dir, encoding='utf-8',
                                    followlinks=True),
            autoescape=select_autoescape(enabled_extensions=['txt', 'html']),
            auto_reload=True)

        # template = env.get_template(self.template_file)
        template = env.get_template(self.ruleset[0])
        self.reply_message = template.render(**self.get_reply_info())
        return self.reply_message

    def get_reply_info(self):
        return dict(
            body=self.body,
            subject=self.subject,
            to=self.to,
            fro=self.fro,
            reply_to=self.reply_to,
            html=self.html,
            date=self.date,
            tokens=self.tokens,
            language=self.language,
            reply=self.reply,
        )

    def to_dict(self):
        return {self.uid: dict(
            body=self.body,
            subject=self.subject,
            to=self.to,
            fro=self.fro,
            reply_to=self.reply_to,
            html=self.html,
            date=self.date,
            attachments=self.attachments,
            tokens=self.tokens,
            language=self.language,
            ruleset=self.ruleset,
            reply=self.reply,
        )}
