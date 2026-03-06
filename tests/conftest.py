import pytest


def make_api_response(tree_value=3, grass_value=1, weed_value=0, include_health=True):
    """Build a realistic Google Pollen API response for testing."""
    health_recs = {
        "recommendedOutdoorActivities": "Limit outdoor activity during peak pollen hours.",
        "allergicSymptoms": "Wear a mask if you are sensitive to pollen.",
    } if include_health else None

    pollen_types = []
    if tree_value is not None:
        tree_entry = {
            "code": "TREE",
            "indexInfo": {
                "value": tree_value,
                "category": "Moderate",
                "indexDescription": "Tree pollen is moderate.",
            },
        }
        if health_recs:
            tree_entry["healthRecommendations"] = health_recs
        pollen_types.append(tree_entry)

    if grass_value is not None:
        pollen_types.append({
            "code": "GRASS",
            "indexInfo": {
                "value": grass_value,
                "category": "Low",
                "indexDescription": "Grass pollen is low.",
            },
        })

    if weed_value is not None:
        pollen_types.append({
            "code": "WEED",
            "indexInfo": {
                "value": weed_value,
                "category": "None",
                "indexDescription": "Weed pollen is none.",
            },
        })

    return {
        "dailyInfo": [
            {
                "date": {"year": 2026, "month": 3, "day": 6},
                "pollenTypeInfo": pollen_types,
            }
        ]
    }


@pytest.fixture
def sample_api_response():
    return make_api_response()


@pytest.fixture
def high_pollen_api_response():
    return make_api_response(tree_value=5)
