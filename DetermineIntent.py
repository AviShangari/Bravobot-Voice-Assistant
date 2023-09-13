import json


f = open('intents.json')
intents = json.load(f)


def lower_case(lst):

    for i in range(len(lst)):
        lst[i] = lst[i].lower()
    return lst


def determine_intent(user_input, patterns):
    
    user_words = user_input.split(" ")
    user_words = lower_case(user_words)

    best_match = ""
    best_match_probability = 0

    for phrase in patterns:
        matched = 0
        unmatched = 0

        for word in user_words:
            if word in phrase.lower():
                matched += 1
            else:
                unmatched += 1
        
        if unmatched != 0:
            match_probability = matched/unmatched
            
            if match_probability >= best_match_probability:
                best_match_probability = match_probability
                best_match = phrase
        
        else:
            match_probability = 100
            best_match = phrase
    
    return [best_match, best_match_probability]


def get_results(user_input):
    
    best_probability = 0
    tag = ""
    
    for i in intents:
        result = determine_intent(user_input, intents[i])
        if result[1] > best_probability:
            best_probability = result[1]
            tag = i
    
    return tag
