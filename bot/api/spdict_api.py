import requests
from typing import Optional
from enum import Enum

from pydantic import BaseModel

from config import SPDICT_TOKEN

URL = "https://dictionaryapi.com/api/v3/references/spanish/json/"
KEY = f"?key={SPDICT_TOKEN}"


class Lang(Enum):
    ENGLISH = "en"
    SPANISH = "es"


class Pronoun(Enum):
    FIRST_PERSON = "yo"
    SECOND_PERSON = "tú"
    THIRD_PERSON = "él/ella/Ud."
    FIRST_PERSON_PLURAL = "nosotros"
    SECOND_PERSON_PLURAL_SPAIN = "vosotros"
    SECOND_PERSON_PLURAL = "ellos/ellas/Uds."


class ConjType(Enum):
    PARTICIPLES = "gppt"

    PRESENT_INDICATIVE = "pind"
    IMPERFECT_INDICATIVE = "pret"
    PRETERITE_INDICATIVE = "pprf"
    FUTURE_INDICATIVE = "futr"
    CONDITIONAL_INDICATIVE = "cond"

    PRESENT_SUBJUNCTIVE = "psub"
    IMPERFECT_SUBJUNCTIVE1 = "pisb1"
    IMPERFECT_SUBJUNCTIVE2 = "pisb2"
    FUTURE_SUBJUNCTIVE = "fsub"

    PRESENT_PERFECT = "ppci"
    PAST_PERFECT = "ppsi"
    PRETERITE_PERFECT = "pant"
    FUTURE_PERFECT = "fpin"
    CONDITIONAL_PERFECT = "cpef"

    PRESENT_PERFECT_SUBJUNCTIVE = "ppfs"
    PAST_PERFECT_SUBJUNCTIVE1 = "ppss1"
    PAST_PERFECT_SUBJUNCTIVE2 = "ppss2"
    FUTURE_PERFECT_SUBJUNCTIVE = "fpsb"

    AFFIRMATIVE_IMPERATIVE = "impf"


class Meta(BaseModel):
    id: str
    uuid: str
    lang: Lang
    sort: Optional[str]
    src: str
    section: str
    stems: list[str]
    offensive: bool


class Pronunciation(BaseModel):
    mw: Optional[str]
    l: Optional[str]
    l2: Optional[str]
    pun: Optional[str]
    sound: Optional[dict[str, str]]


class HeadWord(BaseModel):
    hw: str
    prs: Optional[list[Pronunciation]]
    psl: Optional[str]


class AlternativeHeadWord(BaseModel):
    hw: str
    hwc: Optional[str]
    prs: Optional[Pronunciation]
    psl: Optional[str]


class Variants(BaseModel):
    va: str
    vac: Optional[str]
    vl: Optional[str]
    prs: Optional[Pronunciation]
    spl: Optional[str]


class Translation(BaseModel):
    t: str
    tr: str


class Sense(BaseModel):
    sn: Optional[str]
    sgram: Optional[str]
    ins: Optional[list[dict[str, str]]]
    sls: Optional[list[str]]
    dt: list[list[str|list[Translation]]]


class Definition(BaseModel):
    vd: Optional[str]
    sseq: list[list[list[str|Sense]]]


class Conjugation(BaseModel):
    cjid: ConjType
    cjfs: list[str]


class Suppl(BaseModel):
    cjts: list[Conjugation]


class WordConfig(BaseModel):
    meta: Meta
    hom: Optional[int]
    hwi: HeadWord
    ahws: Optional[AlternativeHeadWord]
    vrs: Optional[list[Variants]]
    fl: Optional[str]
    ins: Optional[list]
    lbs: Optional[list[str]]
    definition: Optional[list[Definition]]
    shortdef: list[str]
    suppl: Optional[Suppl]

    @property
    def audio_link(self) -> str | None:
        if not self.hwi.prs or not self.hwi.prs[0].sound:
            return None

        audio_url = "https://media.merriam-webster.com/audio/prons/{language_code}/{country_code}/{format}/{subdirectory}/{base_filename}.{format}"

        return audio_url.format(
            language_code=self.meta.lang.value,
            country_code= "me" if self.meta.lang == Lang.SPANISH else "us",
            format="mp3",
            subdirectory=self.hwi.hw[0],
            base_filename=self.hwi.prs[0].sound["audio"]
        )

    @property
    def has_cjts(self) -> bool:
        return bool(self.suppl)


class WordRequest(BaseModel):
    meta: int
    data: list[WordConfig|str]

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index: int):
        return self.data[index]

    def __bool__(self):
        return bool(self.data)


class FormattedData(BaseModel):
    definitions: list[str]
    conjugations: list[list[str]]


class SpanishDict:
    def request(word: str) -> WordRequest:
        r: list[dict|str] = requests.get(URL + word + KEY).json()
        
        r = [
            {key.replace("def", "definition") if key == "def" else key: val for key, val in i.items()}
            for i in r if isinstance(i, dict) 
        ] or r

        r = {"meta": 200 if r else 204, "data": r}

        return WordRequest(**r)

    def format(request: WordRequest) -> FormattedData:
        word_defs = []
        verb_cjts = []

        hyperlink = lambda l, t: f"<a href='{l}'>{t}</a>"
        add_i = lambda s: f"<i>{s}</i>"

        for word in request:
            if not word.definition:
                continue
            lang = word.meta.lang.name
            hw = word.hwi.hw
            fl = word.fl
            shortdef = word.shortdef
            link = hyperlink(word.audio_link, "audio") if word.audio_link else ""
            base = f"from {lang.capitalize()}\n\nWord: {hw}\n\n{add_i(fl)}\n{(' '.join(shortdef))}\n{link}"

            word_defs.append(base)

            cjts = []
            if word.has_cjts:
                for i, conjugation in enumerate(word.suppl.cjts):
                    cjtype = " ".join([s.capitalize() for s in conjugation.cjid.name.split("_")])

                    if conjugation.cjid == ConjType.IMPERFECT_SUBJUNCTIVE1 or conjugation.cjid == ConjType.PAST_PERFECT_SUBJUNCTIVE1:
                        cjfs = zip(list(Pronoun), zip(word.suppl.cjts[i].cjfs, word.suppl.cjts[i+1].cjfs))

                    elif conjugation.cjid == ConjType.IMPERFECT_SUBJUNCTIVE2 or conjugation.cjid == ConjType.PAST_PERFECT_SUBJUNCTIVE2:
                        continue

                    else:
                        cjfs = zip(list(Pronoun), conjugation.cjfs)

                    if cjtype[-1].isdigit():
                        cjtype = cjtype[:-1]

                    base = f"{cjtype}\n\n"

                    for pn, cjf in cjfs:
                        if conjugation.cjid == ConjType.PARTICIPLES:
                            base += cjf + "\n"

                        elif conjugation.cjid == ConjType.IMPERFECT_SUBJUNCTIVE1 or conjugation.cjid == ConjType.PAST_PERFECT_SUBJUNCTIVE1:
                            base += f"{pn.value} - {cjf[0]} / {cjf[1]}\n" 

                        else:
                            base += f"{pn.value} - {cjf}\n"

                    cjts.append(base)

            verb_cjts.append(cjts)

        assert len(word_defs) == len(verb_cjts)
        return FormattedData(definitions=word_defs, conjugations=verb_cjts)