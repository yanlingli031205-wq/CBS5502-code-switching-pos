#!/usr/bin/env python3
"""
Fill gold_pos for english_tokens_copy.csv and output highlighted xlsx.
Rules:
  1. Already-filled gold_pos (rows 0-12) are preserved as-is.
  2. Pattern rules cover common token types.
  3. Row-specific overrides handle edge cases.
  4. Yellow highlight = gold_pos differs from auto_pos.
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment
from openpyxl.utils import get_column_letter

CSV_IN  = "../corpus/english_tokens_copy.csv"
XLSX_OUT = "../annotation/gold_standard/gold_standard.xlsx"

# ── Pattern-based rules ───────────────────────────────────────────────────────

INTJ = {
    'btw','BTW','Btw','omg','OMG','Omggggg','omggggg',
    'wow','wah','haha','lol','loll','xd','XD','xdd','XDD','XDXD','wwwwww',
    'Fighting','Cheers','congrats','pls','Salute','welcome','Hello','hello',
    'thx','Thx','bbg','TT','wa',
}

PROPN = {
    # people
    'Trump','Elon','Musk','Donald','Ariel','Torres','Kiki','kiki',
    'Jenn','jenn','jen','Jen','Grace','Megan','Hilary','hilary',
    'Hebe','hebe','Wing','wing','JENNN','Guang','Hana','HANA',
    'Pu',
    # brands / products
    'Tesla','iPhone','iphone','Apple','apple','ikea','IKEA','Hermes',
    'maybelline','Maybelline','picotin','Picotin','GANTOGELATO',
    'LALAPORT','Gundam','NAMCO','youtube','YouTube',
    'Bakehouse','bakehouse','vission','Bake','House',
    'Radius','IVE','YT','IG','ig','Threads','threads',
    # places / languages
    'Singapore','Cantonese','French','romansh','Romansh',
    'Lima','Chifa','Peruana','Avenue','Aviation',
    'Miraflores','Larcomar','Mango','Restaurante','Tanta',
    # movie / game characters
    'TIFA','Now',  # "Now You See Me"
    # misc proper
    'DingDing',
}

X_TOKENS = {
    # Cantonese particles written in English letters
    'ge','ar','wor','lor','la','ding',
    # internet abbreviations / emoticons
    'fdz','der','xdd','XDD','XDXD','wwwwww','xd','XD',
    'P','y','x','CLS','LOR','Yr','etc',
    'FD',                # 男友 abbreviation
    'D',                 # emoticon :D  or 啲
    'jeng','Jeng',       # Cantonese slang
    'lee',               # Cantonese particle
    'ootd',              # keep as NOUN below; override here if needed
}

# Tokens that should be NOUN (override wrong auto_pos)
FORCE_NOUN = {
    'daddy','dad','mom','Mom','mami','Uncle','uncle',
    'video','Video','vlog','Vlog','channel','Channel',
    'app','App','banner','Banner','setup','Setup',
    'party','map','rank','team','contractor','workshop',
    'hotel','Hotel','HOTEL',
    'wig','quality','intro','style','type','boss',
    'fans','Fans','fan',
    'feel','FEEL',
    'friend','fd',
    'make',         # make up
    'one',          # one man band → NUM below
    'chicken',
    'casino',
    'facial',       # 賺facial錢 → NOUN
    'respect',      # 佢講廣東話冇口音，respect → NOUN
    'comment','comments',
    'booking','Booking',
    'reel','reels',
    'support',      # 支持 context → NOUN when used as noun; see overrides
    'follow',       # 一直都有follow → NOUN when object; override below
    'look','Look',
    'point','Point',
    'part','Part',
    'room','Room',
    'kitchen',
    'tour','Tour',
    'post',         # 係ig post → NOUN; but 成日post佢 → VERB; handle by override
    'update',       # 冇Update → NOUN; but 快d update → VERB; override
    'dislike',
    'UFO',
    'BGM',
    'MC','MV',
    'ABC',          # American-Born Chinese → NOUN
    'accent',
    'speaker','Speaker',
    'speech',
    'expression',
    'way',
    'foundation',
    'con',          # contact lens
    'ootd',
    'outfit',
    'vibe',
    'chemistry',
    'relationship',
    'din',          # graduation dinner
    'detail','details',
    'collection',
    'deck',
    'day',
    'view',
    'share',        # 幫手share → VERB; 希望你share → VERB; override below
    'frame',
    'parts',
    'level',
    'Nursing',
    'five',         # high five
    'missed',       # 完全missed → VERB below
    'major',
    'lamb','mutton',
    'programmer',
    'con',
    'playhouse','Playhouse',
    'cam',
    'Keeping',      # House Keeping → VERB
    'Drag','Queen',
    'EPISODE',
    'band',
    'man',
    'outlet',
    'center',
    'sport',
    'hea',
    'ball',
    'jam',
    'travel',       # travel vlog → NOUN
    'Auntie','auntie','Aunty','aunty',
    'everyone',
    'immigration',
    'editor',
    'bookhouse',
    'Sourdough',    # common noun
    'Eggs',
    'Bling',        # 叮叮 Bling Bling → NOUN
    'food','Food',
    'ghost',        # ghost jobs → ADJ below
    'native',       # native speaker → ADJ below
    'language',
    'logo',
    'thread',
    'series',
    'link',
    'event',
    'shot',
    'intro',
    'colour',
    'staff',
    'logo',
}

FORCE_VERB = {
    'claim',    # 搵律師claim爆你 → VERB
    'upgrade',  # upgrade左 → VERB
    'bookmark', # bookmark左 → VERB
    'delete',   # 可以delete → VERB
    'keep',     # keep到, keep fit → VERB
    'admire',   # 值得我admire → VERB
    'KO',       # KO啲毛毛 → VERB
    'sub',      # 即刻sub → VERB
    'repost',   # 會repost → VERB
    'plan',     # 要plan → VERB
    'call',     # 唔call我 → VERB
    'deal',     # deal with → VERB
    'copy',     # copy行程 → VERB
    'fly',      # 你今次會否fly → VERB
    'loop',     # loop左 → VERB
    'approve',  # 唔approve → VERB
    'expect',   # 唔可以expect → VERB
    'translate',# 唔係用英文去translate → VERB
    'playback', # 睇洛playback → VERB
    'share',    # 幫手share, 可唔可以share → VERB
    'follow',   # follow佐你好多年 → VERB; but 一直都有follow → NOUN context (override)
    'gel',      # 唔gel甲 → VERB
    'like',     # 好like你, 就like → VERB
    'subscribe','Subscribed','subscribed',
    'miss',     # 怕你miss了 → VERB
    'Quit','quit',
    'Compare','compare',
    'cheer',
    'interview',
    'upload',
    'book',     # 點book → VERB
    'mark',     # mark個標籤 → VERB
    'po',       # po咗片 → VERB
    'mute',     # 想mute聲 → VERB
    'enjoyed',  # enjoyed it → VERB
    'inspired', # already ADJ; keep as ADJ
    'glowing',  # already ADJ
    'propose',  # propose planning → VERB
    'planning', # planning deck → VERB
    'learn',    # 要learn → VERB
    'subscribe',
    'loop',
    'chill',    # 係個小chill的 → ADJ; but override
    'proud',    # 好proud of → ADJ
}

FORCE_ADJ = {
    'final',    # final fantasy → ADJ
    'different',# different offers → ADJ
    'chill','Chill',    # 好chill → ADJ
    'warm','Warm',      # 好warm → ADJ
    'aesthetic','Aesthetic',
    'positive','Positive',
    'friendly','Friendly',
    'nice','Nice',
    'cute','Cute',
    'dirty','Dirty',
    'online',
    'Dramatic','dramatic',
    'Huge','huge',
    'non',      # non native → ADJ
    'native',   # native speaker → ADJ
    'grand',
    'clear',
    'few',      # a few → DET; but tagged as NOUN; use DET
    'detailed',
    'social',   # 去social飲酒 → ADJ
    'jealous',
    'inspired','Inspired',   # 你已經inspired緊好多人 → ADJ
    'glowing',
    'sweet','Sweet',
    'good','Good',          # 好靚好good → ADJ; but "呢個 outfit so good" → ADJ
    'pro',                  # 好pro → ADJ? actually NOUN "professional" → NOUN; keep ADJ
    'Jeng',                 # 黑髮好Jeng → X (Cantonese)
    'underrated',
    'inspiring',
    'better',
    'TRUE','true',
    'local',
    'perfect','Perfect',
    'high',         # 超high → ADJ
    'ok','OK',
    'pretty',
    'charm',        # 好charm → NOUN? context "格仔衫好charm" → ADJ... actually NOUN "charm" in English but here adj-like; use ADJ
    'abstract',
    'Hardsell',
    'facial',       # 全部係賺你地facial → NOUN; use NOUN override above
    'proud',        # 好proud of → ADJ
}

FORCE_ADV = {
    'btw','BTW','Btw',   # → INTJ (handled above)
    'so',       # so good → ADV
    'really',   # really made → ADV
    'never',    # never give up → ADV
    'yet',      # yet to come → ADV
    'much',     # so much → ADV
    'anyway','Anyway',
    'just',
    'actually',
}

FORCE_NUM = {
    'one',      # one man band
}

# ── Row-specific overrides: {row_idx (0-based): {token_col_name: gold_pos}} ──
# Use these for tokens where pattern rules give wrong result in context.

OVERRIDES = {
    # Row 10 (upgrade, free)
    10: {'gold_pos_1': 'VERB', 'gold_pos_2': 'ADJ'},
    # Row 11 (excuse me)
    11: {'gold_pos_1': 'VERB', 'gold_pos_2': 'PRON'},
    # Row 12 (cut, pass)
    12: {'gold_pos_1': 'VERB', 'gold_pos_2': 'NOUN'},
    # Row 13 (btw)
    13: {'gold_pos_1': 'INTJ'},
    # Row 14 (deal, BA, staff)
    14: {'gold_pos_1': 'VERB', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN'},
    # Row 15 (different, offers)
    15: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 16 (repost, story)
    16: {'gold_pos_1': 'VERB', 'gold_pos_2': 'NOUN'},
    # Row 17 (party, high)
    17: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'ADJ'},
    # Row 18 (call)
    18: {'gold_pos_1': 'VERB'},
    # Row 19 (app, chur, register)
    19: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'ADJ', 'gold_pos_3': 'VERB'},
    # Row 20 (plan)
    20: {'gold_pos_1': 'VERB'},
    # Row 21 (map)
    21: {'gold_pos_1': 'NOUN'},
    # Row 22 (delete)
    22: {'gold_pos_1': 'VERB'},
    # Row 24 (parts)
    24: {'gold_pos_1': 'NOUN'},
    # Row 25 (keep → VERB)
    25: {'gold_pos_1': 'VERB'},
    # Row 26 (apple → PROPN)
    26: {'gold_pos_1': 'PROPN'},
    # Row 27 (Professor → NOUN)
    27: {'gold_pos_1': 'NOUN'},
    # Row 28 (recommendation, letter, scholarship)
    28: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 29 (admire)
    29: {'gold_pos_1': 'VERB'},
    # Row 31 (Performance, pick)
    31: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 32 (contractor)
    32: {'gold_pos_1': 'NOUN'},
    # Row 33 (team)
    33: {'gold_pos_1': 'NOUN'},
    # Row 34 (rank)
    34: {'gold_pos_1': 'NOUN'},
    # Row 35 (haha→INTJ, honey→NOUN, d→X)
    35: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'X'},
    # Row 36 (warm)
    36: {'gold_pos_1': 'ADJ'},
    # Row 37 (vlog, pattern, Please→INTJ)
    37: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'INTJ'},
    # Row 39 (warm, duplicate)
    39: {'gold_pos_1': 'ADJ'},
    # Row 40 (xd→INTJ, carry→VERB, s→X, bag, make→VERB, up→ADP, bag)
    40: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'VERB', 'gold_pos_3': 'X',
         'gold_pos_4': 'NOUN', 'gold_pos_5': 'VERB', 'gold_pos_6': 'ADP', 'gold_pos_7': 'NOUN'},
    # Row 41 (lee→X, video, ar→X, d→X)
    41: {'gold_pos_1': 'X', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'X', 'gold_pos_4': 'X'},
    # Row 42 (TT→INTJ, d→X, tick→VERB, d→X)
    42: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'X', 'gold_pos_3': 'VERB', 'gold_pos_4': 'X'},
    # Row 43 (restaurant→NOUN, try→VERB)
    43: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB'},
    # Row 44 (room)
    44: {'gold_pos_1': 'NOUN'},
    # Row 45 (Hardsell→NOUN)
    45: {'gold_pos_1': 'NOUN'},
    # Row 46 (bbg→INTJ)
    46: {'gold_pos_1': 'INTJ'},
    # Row 47 (channel→NOUN, iphone→PROPN, Bling→NOUN, Bling→NOUN)
    47: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN', 'gold_pos_4': 'NOUN'},
    # Row 48 (outfit, good→ADJ)
    48: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'ADJ'},
    # Row 49 (d→X, d→X, so→ADV, nice)
    49: {'gold_pos_1': 'X', 'gold_pos_2': 'X', 'gold_pos_3': 'ADV', 'gold_pos_4': 'ADJ'},
    # Row 50 (mascara, maybelline→PROPN, mascara→NOUN)
    50: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN'},
    # Row 51 (up→ADV, d→X)
    51: {'gold_pos_1': 'ADV', 'gold_pos_2': 'X'},
    # Row 52 (wig)
    52: {'gold_pos_1': 'NOUN'},
    # Row 53 (d→X, d→X, video)
    53: {'gold_pos_1': 'X', 'gold_pos_2': 'X', 'gold_pos_3': 'NOUN'},
    # Row 54 (fdz→X, xdd→INTJ)
    54: {'gold_pos_1': 'X', 'gold_pos_2': 'INTJ'},
    # Row 55 (FD→X, COS→NOUN)
    55: {'gold_pos_1': 'X', 'gold_pos_2': 'NOUN'},
    # Row 56 (perfect)
    56: {'gold_pos_1': 'ADJ'},
    # Row 57 (video)
    57: {'gold_pos_1': 'NOUN'},
    # Row 58 (DingDing→NOUN)
    58: {'gold_pos_1': 'NOUN'},
    # Row 59 (con)
    59: {'gold_pos_1': 'NOUN'},
    # Row 60 (Food→NOUN, Like→NOUN)
    60: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 61 (food, looks→VERB, so→ADV, good→ADJ)
    61: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'ADV', 'gold_pos_4': 'ADJ'},
    # Row 62 (like→VERB)
    62: {'gold_pos_1': 'VERB'},
    # Row 63 (point)
    63: {'gold_pos_1': 'NOUN'},
    # Row 64 (contact, lenses)
    64: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 65 (carry)
    65: {'gold_pos_1': 'VERB'},
    # Row 66 (HANA→PROPN, bangs→NOUN)
    66: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN'},
    # Row 67 (KO)
    67: {'gold_pos_1': 'VERB'},
    # Row 68 (video, thanks→INTJ, sharing→VERB)
    68: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'INTJ', 'gold_pos_3': 'VERB'},
    # Row 69 (gay, gay)
    69: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 70 (quality)
    70: {'gold_pos_1': 'NOUN'},
    # Row 72 (sis)
    72: {'gold_pos_1': 'NOUN'},
    # Row 73 (d→X, d→X)
    73: {'gold_pos_1': 'X', 'gold_pos_2': 'X'},
    # Row 74 (thx→INTJ, w→X, thx→INTJ, w→X)
    74: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'X', 'gold_pos_3': 'INTJ', 'gold_pos_4': 'X'},
    # Row 75 (facial→NOUN)
    75: {'gold_pos_1': 'NOUN'},
    # Row 77 (respect→NOUN)
    77: {'gold_pos_1': 'NOUN'},
    # Row 78 (aesthetic)
    78: {'gold_pos_1': 'ADJ'},
    # Row 79 (Ariel→PROPN, XDXD→INTJ)
    79: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'INTJ'},
    # Row 80 (video)
    80: {'gold_pos_1': 'NOUN'},
    # Row 81 (omg→INTJ, setup→NOUN)
    81: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'NOUN'},
    # Row 82 (wwwwww→INTJ)
    82: {'gold_pos_1': 'INTJ'},
    # Row 83 (pro→NOUN)
    83: {'gold_pos_1': 'NOUN'},
    # Row 84 (wah→INTJ)
    84: {'gold_pos_1': 'INTJ'},
    # Row 85 (ikea)
    85: {'gold_pos_1': 'PROPN'},
    # Row 86 (gay, gay)
    86: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 87 (Youtuber)
    87: {'gold_pos_1': 'NOUN'},
    # Row 88 (H→PROPN, CP→NOUN, picotin→PROPN)
    88: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'PROPN'},
    # Row 89 (chill)
    89: {'gold_pos_1': 'ADJ'},
    # Row 90 (chill→ADJ)
    90: {'gold_pos_1': 'ADJ'},
    # Row 91 (copy→VERB, GANTOGELATO→PROPN)
    91: {'gold_pos_1': 'VERB', 'gold_pos_2': 'PROPN'},
    # Row 92 (picotin→PROPN, brand→NOUN, cheap→ADJ)
    92: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADJ'},
    # Row 93 (lunch→NOUN, bakehouse→PROPN)
    93: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN'},
    # Row 94 (Btw→INTJ, Anyway→ADV)
    94: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'ADV'},
    # Row 95 (ghost→ADJ, jobs→NOUN)
    95: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 96 (level)
    96: {'gold_pos_1': 'NOUN'},
    # Row 97 (btw→INTJ)
    97: {'gold_pos_1': 'INTJ'},
    # Row 98 (passione→PROPN, panini→NOUN)
    98: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN'},
    # Row 99 (soft, thunder)
    99: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 100 (travis→PROPN, scott→PROPN)
    100: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN'},
    # Row 101 (welcome→INTJ)
    101: {'gold_pos_1': 'INTJ'},
    # Row 102 (backhouse→PROPN)
    102: {'gold_pos_1': 'PROPN'},
    # Row 103 (Chill)
    103: {'gold_pos_1': 'ADJ'},
    # Row 104 (sub→VERB)
    104: {'gold_pos_1': 'VERB'},
    # Row 105 (fans)
    105: {'gold_pos_1': 'NOUN'},
    # Row 106 (travel→NOUN, vlog)
    106: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 107 (besides→ADV, cute)
    107: {'gold_pos_1': 'ADV', 'gold_pos_2': 'ADJ'},
    # Row 108 (follow→VERB)
    108: {'gold_pos_1': 'VERB'},
    # Row 109 (chemistry)
    109: {'gold_pos_1': 'NOUN'},
    # Row 111 (Bakehouse, Sourdough→NOUN, Eggs)
    111: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 112 (miss→VERB)
    112: {'gold_pos_1': 'VERB'},
    # Row 113 (make→VERB, sure→ADJ)
    113: {'gold_pos_1': 'VERB', 'gold_pos_2': 'ADJ'},
    # Row 114 (enjoyed→VERB)
    114: {'gold_pos_1': 'VERB'},
    # Row 115 (google→PROPN, map, comment, la→X, etc→X, fans)
    115: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'X', 'gold_pos_5': 'X', 'gold_pos_6': 'NOUN'},
    # Row 116 (fans)
    116: {'gold_pos_1': 'NOUN'},
    # Row 117 (Singapore→PROPN)
    117: {'gold_pos_1': 'PROPN'},
    # Row 118 (Guang→PROPN)
    118: {'gold_pos_1': 'PROPN'},
    # Row 119 (butter)
    119: {'gold_pos_1': 'NOUN'},
    # Row 120 (Butter, Butter, Chinese→ADJ)
    120: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADJ'},
    # Row 121 (daddy→NOUN)
    121: {'gold_pos_1': 'NOUN'},
    # Row 122 (daddy→NOUN)
    122: {'gold_pos_1': 'NOUN'},
    # Row 123 (Mom)
    123: {'gold_pos_1': 'NOUN'},
    # Row 124 (mami, mami)
    124: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 125 (chicken→NOUN)
    125: {'gold_pos_1': 'NOUN'},
    # Row 126 (warm→ADJ)
    126: {'gold_pos_1': 'ADJ'},
    # Row 127 (dad→NOUN, cute)
    127: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'ADJ'},
    # Row 128 (Uncle)
    128: {'gold_pos_1': 'NOUN'},
    # Row 129 (style)
    129: {'gold_pos_1': 'NOUN'},
    # Row 130 (nice)
    130: {'gold_pos_1': 'ADJ'},
    # Row 131 (Yr→X, Cantonese→PROPN, well→ADV, long→ADJ, French→PROPN)
    131: {'gold_pos_1': 'X', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'ADV',
          'gold_pos_4': 'ADJ', 'gold_pos_5': 'PROPN'},
    # Row 132 (Hello→INTJ, Megan→PROPN)
    132: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'PROPN'},
    # Row 133 (feel→NOUN)
    133: {'gold_pos_1': 'NOUN'},
    # Row 134 (points, Dad, knowing→VERB, use→VERB)
    134: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'VERB', 'gold_pos_4': 'VERB'},
    # Row 135 (detailed→ADJ)
    135: {'gold_pos_1': 'ADJ'},
    # Row 136 (feel)
    136: {'gold_pos_1': 'NOUN'},
    # Row 137 (TART)
    137: {'gold_pos_1': 'NOUN'},
    # Row 138 (positive)
    138: {'gold_pos_1': 'ADJ'},
    # Row 139 (follow→VERB, Kiki→PROPN)
    139: {'gold_pos_1': 'VERB', 'gold_pos_2': 'PROPN'},
    # Row 140 (TRUE→ADJ, enjoy→VERB)
    140: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'VERB'},
    # Row 141 (friendly, Follow→VERB, Kiki→PROPN)
    141: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'VERB', 'gold_pos_3': 'PROPN'},
    # Row 142 (Kiki→PROPN, local)
    142: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'ADJ'},
    # Row 143 (btw→INTJ)
    143: {'gold_pos_1': 'INTJ'},
    # Row 144 (vlog, pattern, Please→INTJ)  duplicate of row 37
    144: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'INTJ'},
    # Row 145 (Love→NOUN)
    145: {'gold_pos_1': 'NOUN'},
    # Row 146 (ice→NOUN)
    146: {'gold_pos_1': 'NOUN'},
    # Row 147 (mic→NOUN, voice, over→ADP)
    147: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADP'},
    # Row 148 (editor)
    148: {'gold_pos_1': 'NOUN'},
    # Row 149 (hotel→NOUN)
    149: {'gold_pos_1': 'NOUN'},
    # Row 150 (dirty)
    150: {'gold_pos_1': 'ADJ'},
    # Row 151 (youtuber, Kiki→PROPN)
    151: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN'},
    # Row 152 (feel, Cheers→INTJ)
    152: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'INTJ'},
    # Row 153 (type)
    153: {'gold_pos_1': 'NOUN'},
    # Row 154 (side→NOUN)
    154: {'gold_pos_1': 'NOUN'},
    # Row 155 (chill→ADJ)
    155: {'gold_pos_1': 'ADJ'},
    # Row 156 (vission→PROPN, bakery, Tart→NOUN, Bake→PROPN, House→PROPN)
    156: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'PROPN', 'gold_pos_5': 'PROPN'},
    # Row 158 (booking)
    158: {'gold_pos_1': 'NOUN'},
    # Row 159 (social, gym)
    159: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 160 (gym, proud→ADJ)
    160: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'ADJ'},
    # Row 161 (torres→PROPN)
    161: {'gold_pos_1': 'PROPN'},
    # Row 162 (never→ADV, give→VERB)
    162: {'gold_pos_1': 'ADV', 'gold_pos_2': 'VERB'},
    # Row 164 (God)
    164: {'gold_pos_1': 'PROPN'},
    # Row 165 (casino→NOUN, Torres→PROPN)
    165: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN'},
    # Row 166 (ge→X, ge→X)
    166: {'gold_pos_1': 'X', 'gold_pos_2': 'X'},
    # Row 167 (romansh→PROPN, romansh→PROPN)
    167: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN'},
    # Row 168 (d→X, love→VERB)
    168: {'gold_pos_1': 'X', 'gold_pos_2': 'VERB'},
    # Row 169 (part)
    169: {'gold_pos_1': 'NOUN'},
    # Row 170 (best→ADJ, school)
    170: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 171 (BTW→INTJ, Torres→PROPN, lovely, Torres→PROPN)
    171: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'ADJ', 'gold_pos_4': 'PROPN'},
    # Row 172 (d→X, Now→PROPN)
    172: {'gold_pos_1': 'X', 'gold_pos_2': 'PROPN'},
    # Row 173 (der→X)
    173: {'gold_pos_1': 'X'},
    # Row 174 (video)
    174: {'gold_pos_1': 'NOUN'},
    # Row 175 (Torres→PROPN, full, shit)
    175: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'ADJ', 'gold_pos_3': 'NOUN'},
    # Row 176 (online, shopping)
    176: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 177 (playback)
    177: {'gold_pos_1': 'VERB'},
    # Row 178 (charm→NOUN)
    178: {'gold_pos_1': 'NOUN'},
    # Row 179 (d→X)
    179: {'gold_pos_1': 'X'},
    # Row 180 (ok→INTJ)
    180: {'gold_pos_1': 'INTJ'},
    # Row 181 (omg→INTJ, d→X)
    181: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'X'},
    # Row 182 (Nursing)
    182: {'gold_pos_1': 'NOUN'},
    # Row 183 (high, five, missed→VERB)
    183: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'VERB'},
    # Row 184 (Quit→VERB, XDD→INTJ)
    184: {'gold_pos_1': 'VERB', 'gold_pos_2': 'INTJ'},
    # Row 185 (CLS→X)
    185: {'gold_pos_1': 'X'},
    # Row 186 (Umass→PROPN)
    186: {'gold_pos_1': 'PROPN'},
    # Row 187 (crazy→ADJ)
    187: {'gold_pos_1': 'ADJ'},
    # Row 188 (major)
    188: {'gold_pos_1': 'NOUN'},
    # Row 189 (lamb, mutton)
    189: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 190 (level)
    190: {'gold_pos_1': 'NOUN'},
    # Row 191 (D→X, LOR→X, programmer, D→X, D→X)
    191: {'gold_pos_1': 'X', 'gold_pos_2': 'X', 'gold_pos_3': 'NOUN', 'gold_pos_4': 'X', 'gold_pos_5': 'X'},
    # Row 192 (House→NOUN, Keeping→VERB, Drag, Queen, Torres→PROPN, EPISODE)
    192: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'NOUN', 'gold_pos_5': 'PROPN', 'gold_pos_6': 'NOUN'},
    # Row 193 (sad)
    193: {'gold_pos_1': 'ADJ'},
    # Row 194 (dislike)
    194: {'gold_pos_1': 'NOUN'},
    # Row 195 (UFO)
    195: {'gold_pos_1': 'NOUN'},
    # Row 196 (Hebe→PROPN, Radius→PROPN)
    196: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN'},
    # Row 197 (one→NUM, man→NOUN, band)
    197: {'gold_pos_1': 'NUM', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 198 (con→NOUN, con)
    198: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 199 (support→NOUN)
    199: {'gold_pos_1': 'NOUN'},
    # Row 200 (part-time)
    200: {'gold_pos_1': 'NOUN'},
    # Row 201 (workshop)
    201: {'gold_pos_1': 'NOUN'},
    # Row 202 (YT→PROPN, Hebe→PROPN, comment, Hebe→PROPN)
    202: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN', 'gold_pos_4': 'PROPN'},
    # Row 203 (feel)
    203: {'gold_pos_1': 'NOUN'},
    # Row 204 (Delay→VERB)
    204: {'gold_pos_1': 'VERB'},
    # Row 205 (LALAPORT→PROPN, Gundam→PROPN, base→NOUN, Round→PROPN, NAMCO→PROPN)
    205: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'PROPN', 'gold_pos_5': 'PROPN'},
    # Row 206 (ball→NOUN, ball, d→X, outlet, center, hea→X, sport)
    206: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'X',
          'gold_pos_4': 'NOUN', 'gold_pos_5': 'NOUN', 'gold_pos_6': 'X', 'gold_pos_7': 'NOUN'},
    # Row 207 (playhouse)
    207: {'gold_pos_1': 'NOUN'},
    # Row 208 (d→X, proud→ADJ)
    208: {'gold_pos_1': 'X', 'gold_pos_2': 'ADJ'},
    # Row 209 (youtube→PROPN, cam)
    209: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN'},
    # Row 210 (approve→VERB, D→X)
    210: {'gold_pos_1': 'VERB', 'gold_pos_2': 'X'},
    # Row 211 (house, gorgeous→ADJ)
    211: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'ADJ'},
    # Row 212 (fans)
    212: {'gold_pos_1': 'NOUN'},
    # Row 213 (fly→VERB)
    213: {'gold_pos_1': 'VERB'},
    # Row 214 (Singapore→PROPN, Aunty)
    214: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN'},
    # Row 215 (Compare→VERB)
    215: {'gold_pos_1': 'VERB'},
    # Row 216 (Auntie, video)
    216: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 217 (everyone→PRON)
    217: {'gold_pos_1': 'PRON'},
    # Row 218 (reel)
    218: {'gold_pos_1': 'NOUN'},
    # Row 219 (like→VERB)
    219: {'gold_pos_1': 'VERB'},
    # Row 220 (IG→PROPN, reels)
    220: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN'},
    # Row 221 (follow→VERB)
    221: {'gold_pos_1': 'VERB'},
    # Row 222 (threads→PROPN, post→NOUN)
    222: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'NOUN'},
    # Row 223 (Subscribed→VERB)
    223: {'gold_pos_1': 'VERB'},
    # Row 224 (language)
    224: {'gold_pos_1': 'NOUN'},
    # Row 225 (American→ADJ, accent, ABC, haha→INTJ)
    225: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN', 'gold_pos_4': 'INTJ'},
    # Row 226 (Huge, respect, non→ADJ, native→ADJ, speaker)
    226: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADJ',
          'gold_pos_4': 'ADJ', 'gold_pos_5': 'NOUN'},
    # Row 227 (Dramatic)
    227: {'gold_pos_1': 'ADJ'},
    # Row 230 (loop→VERB, d→X)
    230: {'gold_pos_1': 'VERB', 'gold_pos_2': 'X'},
    # Row 231 (comments, d→X, D→X)
    231: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'X', 'gold_pos_3': 'X'},
    # Row 232 (native, speaker, follow→VERB, channel→NOUN)
    232: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'VERB', 'gold_pos_4': 'NOUN'},
    # Row 233 (expect)
    233: {'gold_pos_1': 'VERB'},
    # Row 234 (Omggggg→INTJ)
    234: {'gold_pos_1': 'INTJ'},
    # Row 235 (Salute→INTJ)
    235: {'gold_pos_1': 'INTJ'},
    # Row 236 (speech, way, facial, expression)
    236: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADJ', 'gold_pos_4': 'NOUN'},
    # Row 237 (BGM)
    237: {'gold_pos_1': 'NOUN'},
    # Row 238 (Hilary→PROPN, Like→VERB)
    238: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB'},
    # Row 239 (Hilary, gel, like)  already filled in original
    239: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'VERB'},
    # Row 240 (ANY→DET)
    240: {'gold_pos_1': 'DET'},
    # Row 241 (Hello→INTJ, BGM)
    241: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'NOUN'},
    # Row 242 (BGM, mute→VERB)
    242: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB'},
    # Row 243 (FEEL)
    243: {'gold_pos_1': 'NOUN'},
    # Row 244 (Hilary, IVE→PROPN, vibe)
    244: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN'},
    # Row 245 (MC, MV)
    245: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 246 (btw→INTJ)
    246: {'gold_pos_1': 'INTJ'},
    # Row 247 (Jeng→X, TIFA→PROPN, feel→NOUN)
    247: {'gold_pos_1': 'X', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN'},
    # Row 249 (interview→VERB)
    249: {'gold_pos_1': 'VERB'},
    # Row 250 (part-time, D→X, D→X, AI)
    250: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'X', 'gold_pos_3': 'X', 'gold_pos_4': 'NOUN'},
    # Row 251 (Best→ADJ)
    251: {'gold_pos_1': 'ADJ'},
    # Row 252 (share→VERB, view)
    252: {'gold_pos_1': 'VERB', 'gold_pos_2': 'NOUN'},
    # Row 253: Lima,calle→PROPN,Chifa,Peruana,Avenue,Aviation,Miraflores,Larcomar,Mango→PROPN,Restaurante→PROPN,Lunch,Buffet,Tanta→PROPN
    253: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'PROPN',
          'gold_pos_4': 'PROPN', 'gold_pos_5': 'PROPN', 'gold_pos_6': 'PROPN',
          'gold_pos_7': 'PROPN', 'gold_pos_8': 'PROPN', 'gold_pos_9': 'PROPN',
          'gold_pos_10': 'PROPN', 'gold_pos_11': 'NOUN', 'gold_pos_12': 'NOUN',
          'gold_pos_13': 'PROPN'},
    # Row 254 (underrated→ADJ, channel→NOUN, shot)
    254: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 255 (day, tour)
    255: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 256 (youtuber)
    256: {'gold_pos_1': 'NOUN'},
    # Row 257 (Fighting→INTJ)
    257: {'gold_pos_1': 'INTJ'},
    # Row 258 (really→ADV, made→VERB, day)
    258: {'gold_pos_1': 'ADV', 'gold_pos_2': 'VERB', 'gold_pos_3': 'NOUN'},
    # Row 259 (share)
    259: {'gold_pos_1': 'VERB'},
    # Row 260 (share)
    260: {'gold_pos_1': 'VERB'},
    # Row 261 (wow→INTJ)
    261: {'gold_pos_1': 'INTJ'},
    # Row 262 (fd, point, fun→ADJ)
    262: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADJ'},
    # Row 263 (friend)
    263: {'gold_pos_1': 'NOUN'},
    # Row 264 (boss)
    264: {'gold_pos_1': 'NOUN'},
    # Row 265 (pls→INTJ)
    265: {'gold_pos_1': 'INTJ'},
    # Row 266 (book→VERB)
    266: {'gold_pos_1': 'VERB'},
    # Row 267 (key→NOUN, BTW→INTJ, young→ADJ, grad→NOUN, din)
    267: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'INTJ', 'gold_pos_3': 'ADJ',
          'gold_pos_4': 'NOUN', 'gold_pos_5': 'NOUN'},
    # Row 268 (youtuber)
    268: {'gold_pos_1': 'NOUN'},
    # Row 269 (wa→INTJ, jenn→PROPN, video, update→VERB, vlog)
    269: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'VERB', 'gold_pos_5': 'NOUN'},
    # Row 270 (look, jen→PROPN, d→X)
    270: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'X'},
    # Row 271 (GRADDIN→PROPN, LIKE→VERB, P→X, JENNN→PROPN, KEEPGOING→VERB)
    271: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'X',
          'gold_pos_4': 'PROPN', 'gold_pos_5': 'VERB'},
    # Row 272 (update→VERB, miss→VERB, much→ADV)
    272: {'gold_pos_1': 'VERB', 'gold_pos_2': 'VERB', 'gold_pos_3': 'ADV'},
    # Row 273 (ig→PROPN, good→INTJ)
    273: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'INTJ'},
    # Row 274 (support→VERB)
    274: {'gold_pos_1': 'VERB'},
    # Row 276 (support→VERB, all→DET, times, jenn→PROPN, x→X, video)
    276: {'gold_pos_1': 'VERB', 'gold_pos_2': 'DET', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'PROPN', 'gold_pos_5': 'X', 'gold_pos_6': 'NOUN'},
    # Row 277 (Jenn, make→VERB, up→ADP, collection)
    277: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'ADP', 'gold_pos_4': 'NOUN'},
    # Row 278 (update→VERB, haha→INTJ)
    278: {'gold_pos_1': 'VERB', 'gold_pos_2': 'INTJ'},
    # Row 279 (feel)
    279: {'gold_pos_1': 'NOUN'},
    # Row 280 (share→VERB, keep, fit→ADJ)
    280: {'gold_pos_1': 'VERB', 'gold_pos_2': 'VERB', 'gold_pos_3': 'ADJ'},
    # Row 281 (topic→NOUN)
    281: {'gold_pos_1': 'NOUN'},
    # Row 282 (Jenn, keep, fit)  already correct
    282: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'ADJ'},
    # Row 283 (jealous, push→VERB, up→ADP)
    283: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'VERB', 'gold_pos_3': 'ADP'},
    # Row 284 (accessory→NOUN)
    284: {'gold_pos_1': 'NOUN'},
    # Row 285 (D→X)
    285: {'gold_pos_1': 'X'},
    # Row 286 (btw→INTJ, video, top)
    286: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 287 (video, thanks→INTJ)
    287: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'INTJ'},
    # Row 288 (Vedio)
    288: {'gold_pos_1': 'NOUN'},
    # Row 289 (cheer)
    289: {'gold_pos_1': 'VERB'},
    # Row 290 (support→VERB, D→X, cheer→VERB, yet→ADV, come→VERB)
    290: {'gold_pos_1': 'VERB', 'gold_pos_2': 'X', 'gold_pos_3': 'VERB',
          'gold_pos_4': 'ADV', 'gold_pos_5': 'VERB'},
    # Row 291 (inspiring→ADJ, better→ADJ)
    291: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'ADJ'},
    # Row 292 (nice)
    292: {'gold_pos_1': 'ADJ'},
    # Row 293 (inspired→ADJ)
    293: {'gold_pos_1': 'ADJ'},
    # Row 294 (congrats→INTJ, jenn→PROPN, outfit, so→ADV, happy)
    294: {'gold_pos_1': 'INTJ', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'ADV', 'gold_pos_5': 'ADJ'},
    # Row 295 (details→NOUN, d→X)
    295: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'X'},
    # Row 297 (Jenn, propose→VERB, planning→VERB, deck)
    297: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'VERB', 'gold_pos_4': 'NOUN'},
    # Row 298 (glowing→ADJ, relationship)
    298: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'NOUN'},
    # Row 299 (grad→NOUN, din, keep→VERB)
    299: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'VERB'},
    # Row 300 (sweet)
    300: {'gold_pos_1': 'ADJ'},
    # Row 301 (video)
    301: {'gold_pos_1': 'NOUN'},
    # Row 302 (first→ADJ, ig→PROPN, jeng→X)
    302: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'X'},
    # Row 303 (outlook, Vlog, video)
    303: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 304 (youtuber, follow→VERB)
    304: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB'},
    # Row 305 (foundation)
    305: {'gold_pos_1': 'NOUN'},
    # Row 306 (d→X, ootd)
    306: {'gold_pos_1': 'X', 'gold_pos_2': 'NOUN'},
    # Row 307 (link→NOUN)
    307: {'gold_pos_1': 'NOUN'},
    # Row 308 (event)
    308: {'gold_pos_1': 'NOUN'},
    # Row 309 (IG→PROPN, Update→VERB)
    309: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB'},
    # Row 310 (upload→VERB)
    310: {'gold_pos_1': 'VERB'},
    # Row 312 (colour)
    312: {'gold_pos_1': 'NOUN'},
    # Row 313 (ding→X, ding→X, con)
    313: {'gold_pos_1': 'X', 'gold_pos_2': 'X', 'gold_pos_3': 'NOUN'},
    # Row 314 (post→VERB, video, lip→NOUN, stick)
    314: {'gold_pos_1': 'VERB', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN', 'gold_pos_4': 'NOUN'},
    # Row 315 (mark→VERB, XD→INTJ)
    315: {'gold_pos_1': 'VERB', 'gold_pos_2': 'INTJ'},
    # Row 316 (HOTEL)
    316: {'gold_pos_1': 'NOUN'},
    # Row 317 (po→VERB, Wing→PROPN)
    317: {'gold_pos_1': 'VERB', 'gold_pos_2': 'PROPN'},
    # Row 318 (Mum, Fans, Mum, Wing→PROPN, D→X)
    318: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN',
          'gold_pos_4': 'PROPN', 'gold_pos_5': 'X'},
    # Row 319 (Nice→ADJ, cute→ADJ)
    319: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'ADJ'},
    # Row 320 (comment)
    320: {'gold_pos_1': 'NOUN'},
    # Row 321 (feel→NOUN)
    321: {'gold_pos_1': 'NOUN'},
    # Row 322 (channel→NOUN, subscribed→VERB)
    322: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB'},
    # Row 323 (intro)
    323: {'gold_pos_1': 'NOUN'},
    # Row 324 (logic→NOUN, translate→VERB)
    324: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'VERB'},
    # Row 325 (wor→X, lor→X, Respect→INTJ)
    325: {'gold_pos_1': 'X', 'gold_pos_2': 'X', 'gold_pos_3': 'INTJ'},
    # Row 326 (ABC→NOUN, BBC→PROPN, CBC→PROPN)
    326: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'PROPN', 'gold_pos_3': 'PROPN'},
    # Row 327 (few→DET, videos, grand→ADJ, clear→ADJ)
    327: {'gold_pos_1': 'DET', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'ADJ', 'gold_pos_4': 'ADJ'},
    # Row 328 (anyway→ADV, learn→VERB, support→VERB, apple→PROPN)
    328: {'gold_pos_1': 'ADV', 'gold_pos_2': 'VERB', 'gold_pos_3': 'VERB', 'gold_pos_4': 'PROPN'},
    # Row 329 (Grace→PROPN, follow→VERB, channel→NOUN)
    329: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'VERB', 'gold_pos_3': 'NOUN'},
    # Row 330 (sweet, ar→X)
    330: {'gold_pos_1': 'ADJ', 'gold_pos_2': 'X'},
    # Row 331 (kitchen, tour)
    331: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'NOUN'},
    # Row 332 (d→X, house, tour)
    332: {'gold_pos_1': 'X', 'gold_pos_2': 'NOUN', 'gold_pos_3': 'NOUN'},
    # Row 333 (part, d→X)
    333: {'gold_pos_1': 'NOUN', 'gold_pos_2': 'X'},
    # Row 334 (So→ADV, SWEET→ADJ, btw→INTJ, y→X, P→X)
    334: {'gold_pos_1': 'ADV', 'gold_pos_2': 'ADJ', 'gold_pos_3': 'INTJ',
          'gold_pos_4': 'X', 'gold_pos_5': 'X'},
    # Row 335 (Hermes→PROPN, btw→INTJ, appreciate→VERB)
    335: {'gold_pos_1': 'PROPN', 'gold_pos_2': 'INTJ', 'gold_pos_3': 'VERB'},
}

# ── Main logic ────────────────────────────────────────────────────────────────

def infer_gold_pos(token, auto_pos):
    """Return gold_pos based on pattern rules. Returns None if no rule matches."""
    if not token or str(token).strip() == '':
        return None
    t = str(token).strip()
    if t in INTJ:
        return 'INTJ'
    if t in PROPN:
        return 'PROPN'
    if t in X_TOKENS:
        return 'X'
    if t in FORCE_VERB:
        return 'VERB'
    if t in FORCE_ADJ:
        return 'ADJ'
    if t in FORCE_ADV:
        return 'ADV'
    if t in FORCE_NUM:
        return 'NUM'
    if t in FORCE_NOUN:
        return 'NOUN'
    # fallback: keep auto_pos
    return str(auto_pos).strip() if pd.notna(auto_pos) else ''


def process():
    df = pd.read_csv(CSV_IN, dtype=str)
    df = df.fillna('')

    # Identify gold_pos columns
    gold_cols = [c for c in df.columns if c.startswith('gold_pos_')]
    auto_cols  = [c for c in df.columns if c.startswith('auto_pos_')]
    token_cols = [c for c in df.columns if c.startswith('en_token_')]

    # Map index suffix → column names
    def col_idx(name):  # 'gold_pos_3' → 3
        return int(name.split('_')[-1])

    for row_idx, row in df.iterrows():
        row_overrides = OVERRIDES.get(row_idx, {})

        for gcol, acol, tcol in zip(gold_cols, auto_cols, token_cols):
            idx = col_idx(gcol)
            token    = row[tcol]
            auto_pos = row[acol]
            existing = row[gcol]

            # Skip if already filled by user (non-empty)
            if existing.strip():
                continue

            # Apply override first
            if gcol in row_overrides:
                df.at[row_idx, gcol] = row_overrides[gcol]
                continue

            # Apply pattern rules
            if token.strip():
                df.at[row_idx, gcol] = infer_gold_pos(token, auto_pos)

    # ── Write xlsx with yellow highlight ────────────────────────────────────
    wb = Workbook()
    ws = wb.active
    ws.title = "gold_standard"

    YELLOW = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    # Header
    for col_idx_xl, header in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx_xl, value=header)
        cell.font = cell.font.copy(bold=True)

    # Data rows
    for row_idx, row in df.iterrows():
        xl_row = row_idx + 2  # 1-based + header
        for col_idx_xl, col in enumerate(df.columns, start=1):
            val = row[col]
            cell = ws.cell(row=xl_row, column=col_idx_xl, value=val)

            # Highlight gold_pos cells that differ from auto_pos
            if col.startswith('gold_pos_'):
                n = col.split('_')[-1]
                acol = f'auto_pos_{n}'
                auto_val = row.get(acol, '').strip()
                gold_val = str(val).strip()
                if gold_val and auto_val and gold_val != auto_val:
                    cell.fill = YELLOW

    # Auto-fit first column width
    ws.column_dimensions['A'].width = 40
    for col_letter in [get_column_letter(i) for i in range(2, len(df.columns)+1)]:
        ws.column_dimensions[col_letter].width = 12

    wb.save(XLSX_OUT)
    print(f"Saved → {XLSX_OUT}")
    corrected = sum(
        1 for _, row in df.iterrows()
        for gcol in gold_cols
        for acol in [f"auto_pos_{gcol.split('_')[-1]}"]
        if row[gcol].strip() and row[acol].strip() and row[gcol].strip() != row[acol].strip()
    )
    print(f"Yellow-highlighted cells (corrections): {corrected}")


if __name__ == '__main__':
    process()
