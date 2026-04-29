from ai_advisor import get_ai_advice
from pawpal_system import Pet, Task


TEST_CASES = [
    {
        "name": "Case 1: Mochi",
        "pet": {"name": "Mochi", "species": "cat", "age": 3},
        "tasks": [
            {"title": "Breakfast", "duration_minutes": 15, "priority": "high", "time_of_day": "morning"},
            {"title": "Playtime", "duration_minutes": 20, "priority": "medium", "time_of_day": "afternoon"},
        ],
    },
    {
        "name": "Case 2: Rex",
        "pet": {"name": "Rex", "species": "dog", "age": 5},
        "tasks": [
            {"title": "Morning walk", "duration_minutes": 30, "priority": "high", "time_of_day": "morning"},
            {"title": "Medication", "duration_minutes": 5, "priority": "high", "time_of_day": "morning"},
        ],
    },
    {
        "name": "Case 3: Buddy",
        "pet": {"name": "Buddy", "species": "dog", "age": 1},
        "tasks": [
            {"title": "Feeding", "duration_minutes": 10, "priority": "high", "time_of_day": "morning"},
            {"title": "Training", "duration_minutes": 25, "priority": "medium", "time_of_day": "afternoon"},
            {"title": "Evening walk", "duration_minutes": 20, "priority": "low", "time_of_day": "evening"},
        ],
    },
]


def build_pet(case_data: dict) -> Pet:
    pet_info = case_data["pet"]
    tasks = [Task(**task_data) for task_data in case_data["tasks"]]
    return Pet(
        name=pet_info["name"],
        species=pet_info["species"],
        age=pet_info["age"],
        tasks=tasks,
    )


def run_case(case_data: dict) -> tuple[bool, int]:
    pet = build_pet(case_data)
    response = get_ai_advice(pet)
    response_length = len(response)

    length_pass = response_length > 50
    name_pass = pet.name.lower() in response.lower()
    prefix_pass = not response.startswith("[WARNING]") and not response.startswith("[ERROR]")
    overall_pass = length_pass and name_pass and prefix_pass

    print(case_data["name"])
    print(f"Response: {response}")
    print(f"Length > 50: {'PASS' if length_pass else 'FAIL'} (length={response_length})")
    print(f"Pet name appears: {'PASS' if name_pass else 'FAIL'}")
    print(f"No warning/error prefix: {'PASS' if prefix_pass else 'FAIL'}")
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    print("-")

    return overall_pass, response_length


if __name__ == "__main__":
    passed_cases = 0
    total_length = 0

    for case_data in TEST_CASES:
        case_passed, response_length = run_case(case_data)
        if case_passed:
            passed_cases += 1
        total_length += response_length

    average_length = total_length / len(TEST_CASES)
    print(f"Results: {passed_cases}/{len(TEST_CASES)} test cases passed and an average response length of {average_length:.1f}")
