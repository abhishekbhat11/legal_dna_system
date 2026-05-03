import re

def categorize_zones(blocks):
    zoned_blocks = []
    for block in blocks:
        text = block['text'].lower()
        zone = "Background Zone" # Default
        
        # Simple rule-based classifier based on common Indian legal phrasing
        if re.search(r'(in the high court of|writ petition|between:|\. \. \. petitioner)', text):
            zone = "Preamble Zone"
        elif re.search(r'(the facts of the case|the petitioner submits|case of the petitioner)', text):
            zone = "Background Zone"
        elif re.search(r'(it is observed|we are of the considered opinion|cannot be accepted|it is clear that)', text):
            zone = "Observation Zone"
        elif re.search(r'(directed to|ordered that|shall comply|is quashed|writ of mandamus)', text):
            zone = "Direction Zone"
            
        block['zone'] = zone
        zoned_blocks.append(block)
        
    return zoned_blocks