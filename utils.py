"""
Utility functions for the Sales Ledger Generator.

This module provides helper functions for:
- Seasonal weight presets
- Percentage normalization
- Amount splitting algorithms
"""

from typing import List, Dict
import random


def get_preset_weights(preset_name: str) -> List[float]:
    """
    Return a list of 12 monthly weights based on a preset name.

    Args:
        preset_name: One of "Fruit Wholesale", "Textiles", "Electronics", 
                     "FMCG", or "Custom".

    Returns:
        A list of 12 floats representing relative weights for each month 
        (January to December).

    Raises:
        ValueError: If preset_name is not recognized.
    """
    presets: Dict[str, List[float]] = {
        "Fruit Wholesale": [
            6.0,   # Jan
            6.5,   # Feb
            7.0,   # Mar
            8.0,   # Apr
            9.0,   # May
            10.0,  # Jun
            11.0,  # Jul
            10.0,  # Aug
            9.0,   # Sep
            8.0,   # Oct
            7.0,   # Nov
            6.5    # Dec
        ],
        "Textiles": [
            7.0,   # Jan
            6.0,   # Feb
            6.0,   # Mar
            6.0,   # Apr
            6.0,   # May
            5.0,   # Jun
            5.0,   # Jul
            6.0,   # Aug
            7.0,   # Sep
            12.0,  # Oct (Festival/Wedding)
            12.0,  # Nov (Festival/Wedding)
            8.0    # Dec
        ],
        "Electronics": [
            7.0,   # Jan
            6.0,   # Feb
            6.0,   # Mar
            6.0,   # Apr
            6.0,   # May
            6.0,   # Jun
            6.0,   # Jul
            6.0,   # Aug
            7.0,   # Sep
            12.0,  # Oct (Diwali)
            8.0,   # Nov
            11.0   # Dec (Christmas/Year-end)
        ],
        "FMCG": [
            8.0,   # Jan
            8.0,   # Feb
            8.0,   # Mar
            8.0,   # Apr
            8.0,   # May
            8.0,   # Jun
            8.0,   # Jul
            8.0,   # Aug
            8.5,   # Sep
            9.0,   # Oct (Festival)
            9.0,   # Nov (Festival)
            8.5    # Dec
        ],
        "Custom": [
            8.33, 8.33, 8.33, 8.33, 8.33, 8.33,
            8.33, 8.33, 8.33, 8.33, 8.33, 8.34
        ]
    }

    if preset_name not in presets:
        raise ValueError(f"Unknown preset: {preset_name}. Choose from {list(presets.keys())}")

    return presets[preset_name].copy()


def normalize_percentages(weights: List[float]) -> List[float]:
    """
    Normalize a list of weights so they sum to exactly 100.0.

    Uses the largest remainder method to ensure exact summation without 
    floating point drift.

    Args:
        weights: A list of positive numeric weights.

    Returns:
        A list of floats summing to exactly 100.0.
    """
    total_weight = sum(weights)
    if total_weight == 0:
        return [100.0 / len(weights)] * len(weights)

    # Calculate raw percentages
    raw_percentages = [(w / total_weight) * 100.0 for w in weights]
    
    # Floor values
    floored = [int(p) for p in raw_percentages]
    remainders = [p - f for p, f in zip(raw_percentages, floored)]
    
    current_sum = sum(floored)
    deficit = 100.0 - current_sum
    
    # Distribute deficit to largest remainders
    indices = sorted(range(len(remainders)), key=lambda i: remainders[i], reverse=True)
    
    result = floored[:]
    for i in range(int(round(deficit))):
        idx = indices[i % len(indices)]
        result[idx] += 1.0
        
    return [float(x) for x in result]


def split_amount_into_entries(
    total: float, 
    min_entries: int, 
    max_entries: int, 
    min_entry_value: float = 1.0
) -> List[float]:
    """
    Split a total amount into a random number of entries between min and max.

    Ensures:
    - Each entry is >= min_entry_value
    - Sum of entries equals total exactly (within floating point precision)
    - No infinite loops even for small totals

    Args:
        total: The total amount to split.
        min_entries: Minimum number of entries to generate.
        max_entries: Maximum number of entries to generate.
        min_entry_value: Minimum value for any single entry.

    Returns:
        A list of floats summing to total.

    Raises:
        ValueError: If total is too small to satisfy constraints.
    """
    if total <= 0:
        return []
    
    # Determine feasible number of entries
    max_possible_entries = int(total // min_entry_value)
    
    if max_possible_entries < min_entries:
        raise ValueError(
            f"Total {total} is too small to create {min_entries} entries "
            f"of at least {min_entry_value} each."
        )
    
    actual_count = random.randint(min_entries, min(max_entries, max_possible_entries))
    
    if actual_count == 1:
        return [round(total, 2)]
    
    # Generate random splits using cumulative method
    remaining = total
    entries = []
    
    for i in range(actual_count - 1):
        # Ensure remaining entries can still meet minimum requirement
        entries_left = actual_count - i - 1
        max_allowed = remaining - (entries_left * min_entry_value)
        
        if max_allowed <= min_entry_value:
            val = min_entry_value
        else:
            val = random.uniform(min_entry_value, max_allowed)
        
        val = round(val, 2)
        entries.append(val)
        remaining -= val
    
    # Last entry takes the remainder to ensure exact sum
    last_entry = round(remaining, 2)
    
    if last_entry < min_entry_value:
        # Adjust previous entries if last one is too small
        diff = min_entry_value - last_entry
        if len(entries) > 0:
            entries[-1] = round(entries[-1] - diff, 2)
            last_entry = min_entry_value
        else:
            raise ValueError("Could not satisfy minimum entry constraints.")
            
    entries.append(last_entry)
    
    # Final sanity check and correction for floating point drift
    current_sum = sum(entries)
    if abs(current_sum - total) > 0.01:
        diff = round(total - current_sum, 2)
        entries[-1] = round(entries[-1] + diff, 2)
        
    return entries
