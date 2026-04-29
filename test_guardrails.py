from ai_advisor import validate_response


FALLBACK_MESSAGE = (
    "[WARNING] The AI advisor is unavailable right now. "
    "Your schedule was still generated using the rule-based scheduler."
)


def run_case(test_name: str, payload: str) -> None:
    result = validate_response(payload)
    print(f"Test: {test_name}")
    print(f"Passed in: {repr(payload)}")
    print(f"Came out: {repr(result)}")
    print("-")


if __name__ == "__main__":
    run_case("Valid normal response", "The pet schedule looks balanced and appropriate.")
    run_case("Empty string response", "")
    run_case("Response shorter than 20 characters", "Too short")
    run_case("Response longer than 2000 characters", "A" * 2001)
    run_case("Response containing a banned phrase like 'I cannot'", "I cannot help with that request safely.")
