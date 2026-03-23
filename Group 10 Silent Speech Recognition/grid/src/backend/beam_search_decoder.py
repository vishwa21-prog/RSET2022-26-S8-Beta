import torch
import torch.nn.functional as F

def ctc_beam_search(log_probs, beam_width, tokenizer):
    """
    log_probs: (T, V) tensor of log probabilities for one sample
    beam_width: number of beams (higher = more accurate)
    tokenizer: TextTokenizer() object
    """

    T, V = log_probs.shape
    blank = tokenizer.blank

    # Beam entry: (prefix_string, log_probability)
    beams = [("", 0.0)]

    for t in range(T):
        next_beams = {}

        for prefix, score in beams:
            for v in range(V):
                p = log_probs[t, v].item()

                if v == blank:
                    new_prefix = prefix
                else:
                    if len(prefix) > 0 and prefix[-1] == tokenizer.itos[v]:
                        new_prefix = prefix  # repeated character merge
                    else:
                        new_prefix = prefix + tokenizer.itos[v]

                # Keep best score for each prefix
                if new_prefix not in next_beams:
                    next_beams[new_prefix] = score + p
                else:
                    next_beams[new_prefix] = max(next_beams[new_prefix], score + p)

        # Keep top-k beams
        beams = sorted(next_beams.items(), key=lambda x: x[1], reverse=True)[:beam_width]

    # Best final result
    best, score = beams[0]
    return best.strip()
