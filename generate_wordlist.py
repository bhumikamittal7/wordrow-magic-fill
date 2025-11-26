#!/usr/bin/env python3
"""
Generate a comprehensive list of all valid 5-letter English words for Wordle-like games.
This script creates an alphabetized list of all valid 5-letter words from comprehensive dictionaries.
"""

import re
import urllib.request
from collections import OrderedDict

def get_comprehensive_word_list():
    """Fetch comprehensive word lists from multiple sources."""
    words = set()
    
    # Source 1: Common English words dictionary
    try:
        print("Fetching word list from MIT dictionary...")
        url = "https://www.mit.edu/~ecprice/wordlist.10000"
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            for word in content.splitlines():
                word = word.strip().lower()
                if len(word) == 5 and word.isalpha():
                    words.add(word)
    except Exception as e:
        print(f"Could not fetch MIT word list: {e}")
    
    # Source 2: Additional comprehensive word list
    try:
        print("Fetching additional words from web...")
        # Using a comprehensive word list source
        url2 = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        with urllib.request.urlopen(url2) as response:
            content = response.read().decode('utf-8')
            for word in content.splitlines():
                word = word.strip().lower()
                if len(word) == 5 and word.isalpha():
                    words.add(word)
    except Exception as e:
        print(f"Could not fetch additional word list: {e}")
    
    return words

def generate_wordle_word_list():
    """Generate a comprehensive list of all valid 5-letter English words."""
    # We'll combine multiple sources to get comprehensive coverage
    
    words = set()
    
    # Add common 5-letter words manually to ensure we have a good base
    common_words = [
        # Common words that should definitely be included
        'about', 'above', 'abuse', 'actor', 'acute', 'admit', 'adopt', 'adult',
        'after', 'again', 'agent', 'agree', 'ahead', 'alarm', 'album', 'alert',
        'alien', 'align', 'alike', 'alive', 'allow', 'alone', 'along', 'alter',
        'among', 'angel', 'anger', 'angle', 'angry', 'apart', 'apple', 'apply',
        'arena', 'argue', 'arise', 'array', 'arrow', 'arson', 'aside', 'asset',
        'attic', 'audio', 'audit', 'avoid', 'awake', 'award', 'aware', 'badge',
        'basic', 'beach', 'began', 'begin', 'being', 'below', 'bench', 'billy',
        'birth', 'black', 'blade', 'blame', 'blank', 'blast', 'blaze', 'bleak',
        'bless', 'blind', 'blink', 'block', 'blood', 'bloom', 'blown', 'blues',
        'bluff', 'blunt', 'board', 'boast', 'bobby', 'bonus', 'boost', 'booth',
        'bound', 'brain', 'brake', 'brand', 'brass', 'brave', 'bread', 'break',
        'breed', 'brick', 'bride', 'brief', 'bring', 'brink', 'brisk', 'broad',
        'broke', 'brook', 'brown', 'brush', 'buddy', 'build', 'built', 'bulge',
        'bulky', 'bunch', 'bunny', 'burnt', 'burst', 'bushy', 'buyer', 'cable',
        'cache', 'camel', 'canal', 'candy', 'canoe', 'canon', 'cargo', 'carol',
        'carry', 'carve', 'caste', 'catch', 'cause', 'cease', 'cedar', 'chain',
        'chair', 'chalk', 'champ', 'chant', 'chaos', 'charm', 'chart', 'chase',
        'cheap', 'cheat', 'check', 'cheek', 'cheer', 'chess', 'chest', 'chick',
        'chief', 'child', 'chili', 'chill', 'chime', 'china', 'chirp', 'chock',
        'choir', 'choke', 'chord', 'chore', 'chose', 'chuck', 'chunk', 'churn',
        'cider', 'cigar', 'cinch', 'circa', 'civic', 'civil', 'claim', 'clamp',
        'clash', 'class', 'clean', 'clear', 'cleat', 'clerk', 'click', 'cliff',
        'climb', 'cling', 'clink', 'cloak', 'clock', 'clone', 'close', 'cloth',
        'cloud', 'clout', 'clove', 'clown', 'coach', 'coast', 'cobra', 'cocoa',
        'colon', 'color', 'comet', 'comic', 'comma', 'condo', 'coral', 'corer',
        'corny', 'couch', 'cough', 'could', 'count', 'court', 'cover', 'covet',
        'crack', 'craft', 'cramp', 'crane', 'crank', 'crash', 'crass', 'crate',
        'crave', 'crawl', 'craze', 'crazy', 'creak', 'cream', 'creed', 'creek',
        'creep', 'crept', 'crest', 'cried', 'crier', 'crime', 'crimp', 'crisp',
        'croak', 'crock', 'crone', 'crony', 'crook', 'cross', 'croup', 'crowd',
        'crown', 'crude', 'cruel', 'crumb', 'crush', 'crust', 'crypt', 'cubic',
        'cumin', 'curio', 'curly', 'curry', 'curse', 'curve', 'curvy', 'cycle',
        'cynic', 'daily', 'dairy', 'daisy', 'dance', 'dandy', 'datum', 'daunt',
        'death', 'debit', 'debug', 'debut', 'decal', 'decay', 'decor', 'decoy',
        'defer', 'deity', 'delay', 'delta', 'delve', 'demon', 'denim', 'dense',
        'depot', 'depth', 'derby', 'deter', 'deuce', 'devil', 'diary', 'dicey',
        'digit', 'dilly', 'dimly', 'diner', 'dingo', 'dingy', 'diode', 'dirge',
        'dirty', 'disco', 'ditch', 'ditto', 'ditty', 'diver', 'dizzy', 'dodge',
        'dodgy', 'dogma', 'doing', 'dolly', 'donor', 'donut', 'dopey', 'doubt',
        'dough', 'dowdy', 'dowel', 'downy', 'dowry', 'dozen', 'draft', 'drain',
        'drake', 'drama', 'drank', 'drape', 'drawl', 'drawn', 'dread', 'dream',
        'dress', 'dried', 'drier', 'drift', 'drill', 'drink', 'drive', 'droit',
        'droll', 'drone', 'drool', 'droop', 'dross', 'drove', 'drown', 'druid',
        'drunk', 'dryer', 'dryly', 'duchy', 'dully', 'dummy', 'dumpy', 'dunce',
        'dusky', 'dusty', 'dutch', 'duvet', 'dwarf', 'dwell', 'dwelt', 'dying',
        'eager', 'eagle', 'early', 'earth', 'easel', 'eaten', 'eater', 'ebony',
        'edict', 'edify', 'eerie', 'egret', 'eight', 'eject', 'eking', 'elate',
        'elbow', 'elder', 'elect', 'elegy', 'elfin', 'elide', 'elite', 'elope',
        'elude', 'email', 'embed', 'ember', 'emcee', 'empty', 'enact', 'endow',
        'enemy', 'enjoy', 'ennui', 'ensue', 'enter', 'entry', 'envoy', 'epoch',
        'epoxy', 'equal', 'equip', 'erase', 'erect', 'erode', 'error', 'erupt',
        'essay', 'ester', 'ether', 'ethic', 'ethos', 'etude', 'evade', 'event',
        'every', 'evict', 'evoke', 'exact', 'exalt', 'excel', 'exert', 'exile',
        'exist', 'expel', 'extol', 'extra', 'exult', 'eying', 'fable', 'facet',
        'faint', 'fairy', 'faith', 'false', 'fancy', 'fanny', 'farce', 'fatal',
        'fatty', 'fault', 'fauna', 'favor', 'feast', 'fecal', 'feign', 'fella',
        'felon', 'femme', 'femur', 'fence', 'feral', 'ferry', 'fetal', 'fetch',
        'fetid', 'fetus', 'fever', 'fewer', 'fiber', 'fibre', 'ficus', 'field',
        'fiend', 'fiery', 'fifth', 'fifty', 'fight', 'filer', 'filet', 'filly',
        'filmy', 'filth', 'final', 'finch', 'finer', 'first', 'fishy', 'fixer',
        'fizzy', 'fjord', 'flack', 'flail', 'flair', 'flake', 'flaky', 'flame',
        'flank', 'flare', 'flash', 'flask', 'fleck', 'fleet', 'flesh', 'flick',
        'flier', 'fling', 'flint', 'flirt', 'float', 'flock', 'flood', 'floor',
        'flora', 'floss', 'flour', 'flout', 'flown', 'fluff', 'fluid', 'fluke',
        'flume', 'flung', 'flunk', 'flush', 'flute', 'flyer', 'foamy', 'focal',
        'focus', 'foggy', 'foist', 'folio', 'folly', 'foray', 'force', 'forge',
        'forgo', 'forte', 'forth', 'forty', 'forum', 'found', 'foyer', 'frail',
        'frame', 'frank', 'fraud', 'freak', 'freed', 'freer', 'fresh', 'friar',
        'fried', 'frill', 'frisk', 'fritz', 'frock', 'frond', 'front', 'frost',
        'froth', 'frown', 'froze', 'fruit', 'fudge', 'fugue', 'fully', 'fungi',
        'funky', 'funny', 'furor', 'furry', 'fussy', 'fuzzy', 'gaffe', 'gaily',
        'gamer', 'gamma', 'gamut', 'gassy', 'gaudy', 'gauge', 'gaunt', 'gauze',
        'gavel', 'gawky', 'gayer', 'gayly', 'gazer', 'gecko', 'geeky', 'geese',
        'genie', 'genre', 'ghost', 'ghoul', 'giant', 'giddy', 'gipsy', 'girly',
        'girth', 'given', 'giver', 'glade', 'gland', 'glare', 'glass', 'glaze',
        'gleam', 'glean', 'glide', 'glint', 'gloat', 'globe', 'gloom', 'glory',
        'gloss', 'glove', 'glyph', 'gnash', 'gnome', 'godly', 'going', 'golem',
        'golly', 'gonad', 'goner', 'goody', 'gooey', 'goofy', 'goose', 'gorge',
        'gouge', 'gourd', 'grace', 'grade', 'graft', 'grail', 'grain', 'grand',
        'grant', 'grape', 'graph', 'grasp', 'grass', 'grate', 'grave', 'gravy',
        'graze', 'great', 'greed', 'green', 'greet', 'grief', 'grill', 'grime',
        'grimy', 'grind', 'gripe', 'groan', 'groin', 'groom', 'grope', 'gross',
        'group', 'grout', 'grove', 'growl', 'grown', 'gruel', 'gruff', 'grunt',
        'guard', 'guava', 'guess', 'guest', 'guide', 'guild', 'guile', 'guilt',
        'guise', 'gulch', 'gully', 'gumbo', 'gummy', 'guppy', 'gusto', 'gusty',
        'gypsy', 'habit', 'hairy', 'halve', 'handy', 'happy', 'hardy', 'harem',
        'harpy', 'harry', 'harsh', 'haste', 'hasty', 'hatch', 'hater', 'haunt',
        'haute', 'haven', 'havoc', 'hazel', 'heady', 'heard', 'heart', 'heath',
        'heave', 'heavy', 'hedge', 'hefty', 'heist', 'helix', 'hello', 'hence',
        'heron', 'hilly', 'hinge', 'hippo', 'hippy', 'hitch', 'hoard', 'hobby',
        'hoist', 'holly', 'homer', 'honey', 'honor', 'horde', 'horny', 'horse',
        'hotel', 'hotly', 'hound', 'house', 'hovel', 'hover', 'howdy', 'human',
        'humid', 'humor', 'humph', 'humus', 'hunch', 'hunky', 'hurry', 'husky',
        'hussy', 'hutch', 'hydro', 'hyena', 'hymen', 'hyper', 'icily', 'icing',
        'ideal', 'idiom', 'idiot', 'idler', 'idyll', 'igloo', 'iliac', 'image',
        'imbue', 'impel', 'imply', 'inane', 'inbox', 'incur', 'index', 'inept',
        'inert', 'infer', 'ingot', 'inlay', 'inlet', 'inner', 'input', 'inter',
        'intro', 'ionic', 'irate', 'irony', 'islet', 'issue', 'itchy', 'ivory',
        'jaunt', 'jazzy', 'jelly', 'jerky', 'jetty', 'jewel', 'jiffy', 'joint',
        'joist', 'joker', 'jolly', 'joust', 'judge', 'juice', 'juicy', 'jumbo',
        'jumpy', 'junta', 'junto', 'juror', 'kappa', 'karma', 'kayak', 'kebab',
        'khaki', 'kinky', 'kiosk', 'kitty', 'knack', 'knave', 'knead', 'kneed',
        'kneel', 'knelt', 'knife', 'knock', 'knoll', 'known', 'koala', 'krill',
        'label', 'labor', 'laden', 'ladle', 'lager', 'lance', 'lanky', 'lapel',
        'lapse', 'large', 'larva', 'lasso', 'latch', 'later', 'lathe', 'latte',
        'laugh', 'layer', 'leach', 'leafy', 'leaky', 'leant', 'leapt', 'learn',
        'lease', 'leash', 'least', 'leave', 'ledge', 'leech', 'leery', 'lefty',
        'legal', 'leggy', 'lemon', 'lemur', 'leper', 'level', 'lever', 'libel',
        'liege', 'light', 'liken', 'lilac', 'limbo', 'limit', 'linen', 'liner',
        'lingo', 'lipid', 'lithe', 'liver', 'livid', 'llama', 'loamy', 'loath',
        'lobby', 'local', 'locus', 'lodge', 'lofty', 'logic', 'login', 'loopy',
        'loose', 'lorry', 'loser', 'louse', 'lousy', 'lover', 'lower', 'lowly',
        'loyal', 'lucid', 'lucky', 'lumen', 'lumpy', 'lunar', 'lunch', 'lunge',
        'lupus', 'lurch', 'lurid', 'lusty', 'lying', 'lymph', 'lynch', 'lyric',
        'macaw', 'macho', 'macro', 'madam', 'madly', 'mafia', 'magic', 'magma',
        'maize', 'major', 'maker', 'mambo', 'mamma', 'mammy', 'manga', 'mange',
        'mango', 'mangy', 'mania', 'manic', 'manly', 'manor', 'maple', 'march',
        'marry', 'marsh', 'mason', 'masse', 'match', 'matey', 'mauve', 'maxim',
        'maybe', 'mayor', 'mealy', 'meant', 'meaty', 'mecca', 'medal', 'media',
        'medic', 'melee', 'melon', 'mercy', 'merge', 'merit', 'merry', 'metal',
        'meter', 'metro', 'micro', 'midge', 'midst', 'might', 'milky', 'mimic',
        'mince', 'miner', 'minim', 'minor', 'minty', 'minus', 'mirth', 'miser',
        'missy', 'mocha', 'modal', 'model', 'modem', 'mogul', 'moist', 'molar',
        'moldy', 'money', 'month', 'moody', 'moose', 'moral', 'moron', 'morph',
        'mossy', 'motel', 'motif', 'motor', 'motto', 'moult', 'mound', 'mount',
        'mourn', 'mouse', 'mouth', 'mover', 'movie', 'mower', 'mucky', 'mucus',
        'muddy', 'mulch', 'mummy', 'munch', 'mural', 'murky', 'mushy', 'music',
        'musky', 'musty', 'myrrh', 'nadir', 'naive', 'nanny', 'nasal', 'nasty',
        'natal', 'naval', 'navel', 'needy', 'neigh', 'nerdy', 'nerve', 'never',
        'newer', 'newly', 'nicer', 'niche', 'niece', 'night', 'ninja', 'ninny',
        'ninth', 'noble', 'nobly', 'noise', 'noisy', 'nomad', 'noose', 'north',
        'nosey', 'notch', 'novel', 'nudge', 'nurse', 'nutty', 'nylon', 'nymph',
        'oaken', 'obese', 'occur', 'ocean', 'octal', 'octet', 'odder', 'oddly',
        'offal', 'offer', 'often', 'olden', 'older', 'olive', 'ombre', 'omega',
        'onion', 'onset', 'opera', 'opine', 'opium', 'optic', 'orbit', 'order',
        'organ', 'other', 'otter', 'ought', 'ounce', 'outdo', 'outer', 'outgo',
        'ovary', 'ovate', 'overt', 'ovine', 'ovoid', 'owing', 'owner', 'oxide',
        'ozone', 'paddy', 'pagan', 'paint', 'paler', 'palsy', 'panel', 'panic',
        'pansy', 'papal', 'paper', 'parer', 'parka', 'parry', 'parse', 'party',
        'pasta', 'paste', 'pasty', 'patch', 'patio', 'patsy', 'patty', 'pause',
        'payee', 'payer', 'peace', 'peach', 'pearl', 'pecan', 'pedal', 'penal',
        'pence', 'penne', 'penny', 'perch', 'peril', 'perky', 'pesky', 'pesto',
        'petal', 'petty', 'phase', 'phone', 'phony', 'photo', 'piano', 'picky',
        'piece', 'piety', 'piggy', 'pilot', 'pinch', 'piney', 'pinky', 'pinto',
        'piper', 'pique', 'pitch', 'pithy', 'pivot', 'pixel', 'pixie', 'pizza',
        'place', 'plaid', 'plain', 'plait', 'plane', 'plank', 'plant', 'plate',
        'plaza', 'plead', 'pleat', 'plied', 'plier', 'pluck', 'plumb', 'plume',
        'plump', 'plunk', 'plush', 'poesy', 'point', 'poise', 'poker', 'polar',
        'polka', 'polyp', 'pooch', 'poppy', 'porch', 'poser', 'posit', 'posse',
        'pouch', 'pound', 'pouty', 'power', 'prank', 'prawn', 'preen', 'press',
        'price', 'prick', 'pride', 'pried', 'prime', 'primo', 'print', 'prior',
        'prism', 'privy', 'prize', 'probe', 'prone', 'prong', 'proof', 'prose',
        'proud', 'prove', 'prowl', 'proxy', 'prude', 'prune', 'psalm', 'pubic',
        'pudgy', 'puffy', 'pulpy', 'pulse', 'punch', 'pupal', 'pupil', 'puppy',
        'puree', 'purer', 'purge', 'purse', 'pushy', 'putty', 'pygmy', 'quack',
        'quail', 'quake', 'qualm', 'quark', 'quart', 'quash', 'quasi', 'queen',
        'queer', 'quell', 'query', 'quest', 'queue', 'quick', 'quiet', 'quill',
        'quilt', 'quirk', 'quite', 'quota', 'quote', 'quoth', 'rabbi', 'rabid',
        'racer', 'radar', 'radii', 'radio', 'rainy', 'raise', 'rajah', 'rally',
        'ralph', 'ramen', 'ranch', 'randy', 'range', 'rapid', 'rarer', 'raspy',
        'ratio', 'ratty', 'raven', 'rayon', 'razor', 'reach', 'react', 'ready',
        'realm', 'rearm', 'rebar', 'rebel', 'rebus', 'rebut', 'recap', 'recur',
        'recut', 'reedy', 'refer', 'refit', 'regal', 'rehab', 'reign', 'relax',
        'relay', 'relic', 'remit', 'renal', 'renew', 'repay', 'repel', 'reply',
        'rerun', 'reset', 'resin', 'retch', 'retro', 'retry', 'reuse', 'revel',
        'revue', 'rhino', 'rhyme', 'rider', 'ridge', 'rifle', 'right', 'rigid',
        'rigor', 'rinse', 'ripen', 'riper', 'risen', 'riser', 'risky', 'rival',
        'river', 'rivet', 'roach', 'roast', 'robin', 'robot', 'rocky', 'rodeo',
        'roger', 'rogue', 'roomy', 'roost', 'rotor', 'rouge', 'rough', 'round',
        'rouse', 'route', 'rover', 'rowdy', 'rower', 'royal', 'ruddy', 'ruder',
        'rugby', 'ruler', 'rumba', 'rumor', 'rupee', 'rural', 'rusty', 'sadly',
        'safer', 'saint', 'salad', 'sally', 'salon', 'salsa', 'salty', 'salve',
        'salvo', 'sandy', 'saner', 'sappy', 'sassy', 'satin', 'satyr', 'sauce',
        'saucy', 'sauna', 'saute', 'savor', 'savoy', 'savvy', 'scald', 'scale',
        'scalp', 'scaly', 'scamp', 'scant', 'scare', 'scarf', 'scary', 'scene',
        'scent', 'scion', 'scoff', 'scold', 'scone', 'scoop', 'scope', 'score',
        'scorn', 'scour', 'scout', 'scowl', 'scram', 'scrap', 'scree', 'screw',
        'scrub', 'scrum', 'scuba', 'sedan', 'seedy', 'segue', 'seize', 'semen',
        'sense', 'sepia', 'serif', 'serum', 'serve', 'setup', 'seven', 'sever',
        'sewer', 'shack', 'shade', 'shady', 'shaft', 'shake', 'shaky', 'shale',
        'shall', 'shalt', 'shame', 'shank', 'shape', 'shard', 'share', 'shark',
        'sharp', 'shave', 'shawl', 'shear', 'sheen', 'sheep', 'sheer', 'sheet',
        'sheik', 'shelf', 'shell', 'shied', 'shift', 'shine', 'shiny', 'shire',
        'shirk', 'shirt', 'shoal', 'shock', 'shone', 'shook', 'shoot', 'shore',
        'shorn', 'short', 'shout', 'shove', 'shown', 'showy', 'shrew', 'shrub',
        'shrug', 'shuck', 'shunt', 'shush', 'shyly', 'siege', 'sieve', 'sight',
        'sigma', 'silky', 'silly', 'since', 'sinew', 'singe', 'siren', 'sissy',
        'sixth', 'sixty', 'skate', 'skier', 'skiff', 'skill', 'skimp', 'skirt',
        'skulk', 'skull', 'skunk', 'slack', 'slain', 'slang', 'slant', 'slash',
        'slate', 'slave', 'sleek', 'sleep', 'sleet', 'slept', 'slice', 'slick',
        'slide', 'slime', 'slimy', 'sling', 'slink', 'sloop', 'slope', 'slosh',
        'sloth', 'slump', 'slung', 'slunk', 'slurp', 'slush', 'slyly', 'smack',
        'small', 'smart', 'smash', 'smear', 'smell', 'smelt', 'smile', 'smirk',
        'smite', 'smith', 'smock', 'smoke', 'smoky', 'smote', 'snack', 'snail',
        'snake', 'snaky', 'snare', 'snarl', 'sneak', 'sneer', 'snide', 'sniff',
        'snipe', 'snoop', 'snore', 'snort', 'snout', 'snowy', 'snuck', 'snuff',
        'soapy', 'sober', 'soggy', 'solar', 'solid', 'solve', 'sonar', 'sonic',
        'sooth', 'sooty', 'sorry', 'sound', 'south', 'sower', 'space', 'spade',
        'spank', 'spare', 'spark', 'spasm', 'spawn', 'speak', 'spear', 'speck',
        'speed', 'spell', 'spelt', 'spend', 'spent', 'sperm', 'spice', 'spicy',
        'spied', 'spiel', 'spike', 'spiky', 'spill', 'spilt', 'spine', 'spiny',
        'spire', 'spite', 'splat', 'split', 'spoil', 'spoke', 'spoof', 'spook',
        'spool', 'spoon', 'spore', 'sport', 'spout', 'spray', 'spree', 'sprig',
        'spunk', 'spurn', 'spurt', 'squad', 'squat', 'squib', 'stack', 'staff',
        'stage', 'staid', 'stain', 'stair', 'stake', 'stale', 'stalk', 'stall',
        'stamp', 'stand', 'stank', 'stare', 'stark', 'start', 'stash', 'state',
        'stave', 'stead', 'steak', 'steal', 'steam', 'steed', 'steel', 'steep',
        'steer', 'stein', 'stern', 'stick', 'stiff', 'still', 'stilt', 'sting',
        'stink', 'stint', 'stock', 'stoic', 'stoke', 'stole', 'stomp', 'stone',
        'stony', 'stood', 'stool', 'stoop', 'store', 'stork', 'storm', 'story',
        'stout', 'stove', 'strap', 'straw', 'stray', 'strip', 'strut', 'stuck',
        'study', 'stuff', 'stump', 'stung', 'stunk', 'stunt', 'style', 'suave',
        'sugar', 'suing', 'suite', 'sulky', 'sully', 'sumac', 'sunny', 'super',
        'surer', 'surge', 'surly', 'sushi', 'swami', 'swamp', 'swarm', 'swash',
        'swath', 'swear', 'sweat', 'sweep', 'sweet', 'swell', 'swept', 'swift',
        'swill', 'swine', 'swing', 'swirl', 'swish', 'swoon', 'swoop', 'sword',
        'swore', 'sworn', 'swung', 'synod', 'syrup', 'tabby', 'table', 'taboo',
        'tacit', 'tacky', 'taffy', 'taint', 'taken', 'taker', 'tally', 'talon',
        'tamer', 'tango', 'tangy', 'taper', 'tapir', 'tardy', 'tarot', 'taste',
        'tasty', 'tatty', 'taunt', 'tawny', 'teach', 'teary', 'tease', 'teddy',
        'teeth', 'tempo', 'tenet', 'tenor', 'tense', 'tenth', 'tepee', 'tepid',
        'terra', 'terse', 'testy', 'thank', 'theft', 'their', 'theme', 'there',
        'these', 'theta', 'thick', 'thief', 'thigh', 'thing', 'think', 'third',
        'thong', 'thorn', 'those', 'three', 'threw', 'throb', 'throw', 'thrum',
        'thumb', 'thump', 'thyme', 'tiara', 'tibia', 'tidal', 'tiger', 'tight',
        'tilde', 'timer', 'timid', 'tipsy', 'titan', 'tithe', 'title', 'toast',
        'today', 'toddy', 'token', 'tonal', 'tonga', 'tonic', 'tooth', 'topaz',
        'topic', 'torch', 'torso', 'torus', 'total', 'totem', 'touch', 'tough',
        'towel', 'tower', 'toxic', 'toxin', 'trace', 'track', 'tract', 'trade',
        'trail', 'train', 'trait', 'tramp', 'trash', 'trawl', 'tread', 'treat',
        'trend', 'triad', 'trial', 'tribe', 'trice', 'trick', 'tried', 'tripe',
        'trite', 'troll', 'troop', 'trope', 'trout', 'trove', 'truce', 'truck',
        'truer', 'truly', 'trump', 'trunk', 'truss', 'trust', 'truth', 'tryst',
        'tubal', 'tuber', 'tulip', 'tulle', 'tumor', 'tunic', 'turbo', 'tutor',
        'twang', 'tweak', 'tweed', 'tweet', 'twice', 'twine', 'twirl', 'twist',
        'twixt', 'tying', 'udder', 'ulcer', 'ultra', 'umbra', 'uncle', 'uncut',
        'under', 'undid', 'undue', 'unfed', 'unfit', 'unify', 'union', 'unite',
        'unity', 'unlit', 'unmet', 'unset', 'untie', 'until', 'unwed', 'unzip',
        'upper', 'upset', 'urban', 'urine', 'usage', 'usher', 'using', 'usual',
        'usurp', 'utile', 'utter', 'vague', 'valet', 'valid', 'valor', 'value',
        'valve', 'vapid', 'vapor', 'vault', 'vaunt', 'vegan', 'venom', 'venue',
        'verge', 'verse', 'verso', 'verve', 'vicar', 'video', 'vigil', 'vigor',
        'villa', 'vinyl', 'viola', 'viper', 'viral', 'virus', 'visit', 'visor',
        'vista', 'vital', 'vivid', 'vixen', 'vocal', 'vodka', 'vogue', 'voice',
        'voila', 'vomit', 'voter', 'vouch', 'vowel', 'vying', 'wacky', 'wafer',
        'wager', 'wagon', 'waist', 'waive', 'waltz', 'warty', 'waste', 'watch',
        'water', 'waver', 'waxen', 'weary', 'weave', 'wedge', 'weedy', 'weigh',
        'weird', 'welch', 'welsh', 'wench', 'whack', 'whale', 'wharf', 'wheat',
        'wheel', 'whelp', 'where', 'which', 'whiff', 'while', 'whine', 'whiny',
        'whirl', 'whisk', 'white', 'whole', 'whoop', 'whose', 'widen', 'wider',
        'widow', 'width', 'wield', 'wight', 'willy', 'wimpy', 'wince', 'winch',
        'windy', 'wiser', 'wispy', 'witch', 'witty', 'woken', 'woman', 'women',
        'woody', 'wooer', 'wooly', 'woozy', 'wordy', 'world', 'worry', 'worse',
        'worst', 'worth', 'would', 'wound', 'woven', 'wrack', 'wrath', 'wreak',
        'wreck', 'wrest', 'wring', 'wrist', 'write', 'wrong', 'wrote', 'wrung',
        'wryly', 'yacht', 'yearn', 'yeast', 'yield', 'young', 'youth', 'zebra',
        'zesty', 'zonal'
    ]
    
    for word in common_words:
        if len(word) == 5 and word.isalpha():
            words.add(word.lower())
    
    # Try to fetch additional words from online sources
    try:
        fetched_words = get_comprehensive_word_list()
        words.update(fetched_words)
    except Exception as e:
        print(f"Note: Could not fetch additional words: {e}")
        print("Using base word list...")
    
    # Fetch ALL 5-letter words from comprehensive sources
    print("Fetching all 5-letter words from comprehensive dictionary...")
    try:
        url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            count = 0
            for word in content.splitlines():
                word = word.strip().lower()
                if len(word) == 5 and word.isalpha():
                    words.add(word)
                    count += 1
                    if count % 1000 == 0:
                        print(f"  Processed {count} words so far...")
        print(f"  Fetched {len(words)} unique 5-letter words from dictionary")
    except Exception as e:
        print(f"Could not fetch additional words: {e}")
    
    # Final filtering and sorting
    five_letter_words = sorted([w for w in words if len(w) == 5 and w.isalpha()])
    
    # Remove duplicates and ensure alphabetical order
    unique_words = list(OrderedDict.fromkeys(five_letter_words))
    
    # Return all valid 5-letter words
    return unique_words

def main():
    print("Generating comprehensive 5-letter word list...")
    words = generate_wordle_word_list()
    
    print(f"Generated {len(words)} words")
    
    # Write to file
    output_file = "wordlist.txt"
    with open(output_file, 'w') as f:
        for word in words:
            f.write(word + '\n')
    
    print(f"Word list written to {output_file}")
    print(f"Total words: {len(words)}")
    
    # Show first and last few words
    if words:
        print(f"\nFirst 10 words: {words[:10]}")
        print(f"Last 10 words: {words[-10:]}")

if __name__ == "__main__":
    main()

