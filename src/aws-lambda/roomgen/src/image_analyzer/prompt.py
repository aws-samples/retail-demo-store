from typing import List
from room_generator.image_analyzer import LabelBox

room_style_prompt_mapping = {
    'minimalist': 'Transform a traditional living room into a modern, minimalist space with sleek furniture and natural light enhancement.', 
    'modern': 'Revamp a traditional living room into a Mid Century Modern oasis featuring clean lines, organic forms, and a mix of different materials such as wood, metal, and glass.', 
    'bohemian': 'Rework a traditional living room into a Bohemian Chic haven with eclectic furnishings, vibrant textiles, and an abundance of plants and cultural artifacts.', 
    'rustic': 'Update a traditional living room into a Rustic Farmhouse setting with reclaimed wood accents, comfortable and practical furniture, and a warm, neutral color palette.', 
    'industrial': 'Transform a traditional living area into an edgy Industrial loft, highlighting raw, unfinished materials like exposed brick and steel, open spaces, and vintage-inspired lighting for a touch of modernity.', 
    'scandanavian': 'Redesign a conventional living space into a serene, Scandinavian sanctuary that emphasizes functionality, natural light flooding, and a palette of soft, muted colors paired with elements of wood.'
}

def create_approximate_prompt(room_style: str, labelled_furniture: List[LabelBox]):
    # Get the base prompt for the style requested
    prompt = [room_style_prompt_mapping[room_style]]

    if captions := [labelled_box.similar_items[0].caption for labelled_box in labelled_furniture if labelled_box.similar_items]:
        for caption in captions:
            # Potentially do some caption cleanup - if not, this can be simplfied to just add captions to prompt
            prompt.append(caption)

    # For now just create a list of comman separated weights equal in size to the number of captions, and set to the same value: 0.3
    weights = ','.join(['0.3']*(len(prompt)-1))
    # This will produce a prompt like: 
    # "[Transform a traditional living room into a modern..., caption 1, caption 2,...].and(1, caption 1 weight, caption 2 weight, ...)"
    conjugate_prompt = f"{prompt}.and(1, {weights})"
    return conjugate_prompt