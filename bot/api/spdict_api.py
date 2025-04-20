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
    PRETERITE_INDICATIVE = "pprf"
    IMPERFECT_INDICATIVE = "pret"
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
    sort: str
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
    fl: str
    ins: Optional[list]
    lbs: Optional[list[str]]
    definition: list[Definition]
    shortdef: list[str]
    suppl: Optional[Suppl]

    @property
    def audio_link(self):
        audio_url = "https://media.merriam-webster.com/audio/prons/{language_code}/{country_code}/{format}/{subdirectory}/{base_filename}.{format}"

        return audio_url.format(
            language_code=self.meta.lang.value,
            country_code= "me" if self.meta.lang == Lang.SPANISH else "us",
            format="mp3",
            subdirectory=self.hwi.hw[0],
            base_filename=self.hwi.prs[0].sound["audio"]
        )
    
    @property
    def is_verb(self):
        return bool(self.suppl)


class WordRequest(BaseModel):
    meta: int
    data: list[WordConfig]

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index: int):
        return self.data[index]


class SpanishWord:
    def request(word: str):
        r: list[dict] = [
            {key.replace("def", "definition") if key == "def" else key: val for key, val in i.items()}
            for i in requests.get(URL + word + KEY).json() if isinstance(i, dict)
        ]

        r = {"meta": 200 if r else 204, "data": r}

        return WordRequest(**r)

    def get(word: str) -> list:
        r: WordRequest = SpanishWord.request(word)

        if r.meta == 204:
            return [f"No results found for {word}"]

        data: list[str] = []

        hyperlink = lambda l, t: f"<a href='{l}'>{t}</a>"
        add_i = lambda s: f"<i>{s}</i>"

        for spword in r:
            lang = spword.meta.lang
            fl = spword.fl
            shortdef = spword.shortdef
            link = hyperlink(spword.audio_link, "audio") if spword.hwi.prs else ""
            base = f"from {lang.name.capitalize()}\n{spword.hwi.hw}\n{add_i(fl)}\n{(' '.join(shortdef))}\n{link}"

            data.append(base)

        return data

    def conjugate_verb(word: str):
        r: WordRequest = SpanishWord.request(word)

        data = []

        if (spword:=r.data[0]).is_verb:
            for verb in spword.suppl.cjts:
                cjtype = verb.cjid.name.replace('_', ' ').capitalize()
                cjfs = zip(list(Pronoun), verb.cjfs)

                base = f"{cjtype}\n\n"

                for pn, cjf in cjfs:
                    if verb.cjid == ConjType.PARTICIPLES:
                        base += cjf + "\n"
                    else:
                        base += f"{pn.value} - {cjf}\n"
                    
                data.append(base)

            return data