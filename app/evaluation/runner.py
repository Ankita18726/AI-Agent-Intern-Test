import argparse
import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.agent.service import (
    SupportAgent,
)
from app.config import (
    EVALUATION_DIR,
)
from app.evaluation.assertions import (
    evaluate_expectations,
)


RESULTS_DIR = (
    EVALUATION_DIR
    / "results"
)


def load_json(
    path: Path,
) -> dict[str, Any]:

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


def load_all_cases() -> list[dict[str, Any]]:
    """
    Load both supplied and original evaluation cases.
    """

    visible_path = (
        EVALUATION_DIR
        / "visible-cases.json"
    )

    original_path = (
        EVALUATION_DIR
        / "original-cases.json"
    )

    visible = load_json(
        visible_path
    )

    original = load_json(
        original_path
    )

    cases = []

    for case in visible.get(
        "cases",
        [],
    ):

        copied = dict(
            case
        )

        copied["suite"] = (
            "visible"
        )

        cases.append(
            copied
        )

    for case in original.get(
        "cases",
        [],
    ):

        copied = dict(
            case
        )

        copied["suite"] = (
            "original"
        )

        cases.append(
            copied
        )

    return cases


def run_case(
    case: dict[str, Any],
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Run every user message in the same case within
    one LangGraph conversation/thread.
    """

    case_id = case[
        "id"
    ]

    session_id = (
        "eval-"
        + case_id
        + "-"
        + uuid4().hex[:8]
    )

    agent = SupportAgent(
        session_id=session_id
    )

    turn_results = []

    started = time.perf_counter()

    error = None

    try:

        for message in case.get(
            "messages",
            [],
        ):

            if (
                message.get("role")
                != "user"
            ):
                continue

            content = message.get(
                "content",
                ""
            )

            if verbose:

                print(
                    f"\n    USER: {content}"
                )

            result = agent.ask(
                content
            )

            turn_results.append(
                result
            )

            if verbose:

                print(
                    "    AGENT:",
                    result.get(
                        "answer",
                        "",
                    ),
                )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    elapsed = (
        time.perf_counter()
        - started
    )

    failures = []

    if error:

        failures.append(
            f"Runtime error: {error}"
        )

    else:

        failures.extend(
            evaluate_expectations(
                case.get(
                    "expect",
                    {},
                ),
                turn_results,
            )
        )

    passed = (
        len(failures) == 0
    )

    final_result = (
        turn_results[-1]
        if turn_results
        else {}
    )

    return {
        "id":
            case_id,

        "suite":
            case.get(
                "suite"
            ),

        "category":
            case.get(
                "category",
                "uncategorized",
            ),

        "passed":
            passed,

        "failures":
            failures,

        "duration_seconds":
            round(
                elapsed,
                3,
            ),

        "final_answer":
            final_result.get(
                "answer",
                "",
            ),

        "sources":
            final_result.get(
                "sources",
                [],
            ),

        "handoff":
            final_result.get(
                "handoff",
                False,
            ),

        "handoff_reason":
            final_result.get(
                "handoff_reason"
            ),

        "tool_called":
            any(
                result.get(
                    "tool_called",
                    False,
                )
                for result
                in turn_results
            ),

        "requested_order_ids": [
            result.get(
                "requested_order_id"
            )
            for result
            in turn_results
            if result.get(
                "requested_order_id"
            )
        ],

        "turn_count":
            len(
                turn_results
            ),

        "error":
            error,
    }


def summarize(
    results: list[dict[str, Any]],
) -> dict[str, Any]:

    category_data = defaultdict(
        lambda: {
            "passed": 0,
            "total": 0,
        }
    )

    suite_data = defaultdict(
        lambda: {
            "passed": 0,
            "total": 0,
        }
    )

    for result in results:

        category = result[
            "category"
        ]

        suite = result[
            "suite"
        ]

        category_data[
            category
        ]["total"] += 1

        suite_data[
            suite
        ]["total"] += 1

        if result[
            "passed"
        ]:

            category_data[
                category
            ]["passed"] += 1

            suite_data[
                suite
            ]["passed"] += 1

    total = len(
        results
    )

    passed = sum(
        1
        for result in results
        if result[
            "passed"
        ]
    )

    def with_percentages(
        data,
    ):

        output = {}

        for key, values in data.items():

            count = values[
                "total"
            ]

            success = values[
                "passed"
            ]

            percentage = (
                (success / count) * 100
                if count
                else 0
            )

            output[key] = {
                "passed":
                    success,

                "total":
                    count,

                "percentage":
                    round(
                        percentage,
                        1,
                    ),
            }

        return dict(
            sorted(
                output.items()
            )
        )

    return {
        "passed":
            passed,

        "total":
            total,

        "percentage":
            round(
                (
                    passed
                    / total
                    * 100
                )
                if total
                else 0,
                1,
            ),

        "by_category":
            with_percentages(
                category_data
            ),

        "by_suite":
            with_percentages(
                suite_data
            ),
    }


def print_results(
    results: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:

    print()
    print(
        "=" * 78
    )

    print(
        "Aster & Row Evaluation Results"
    )

    print(
        "=" * 78
    )

    print()

    for result in results:

        marker = (
            "PASS"
            if result[
                "passed"
            ]
            else "FAIL"
        )

        print(
            f"[{marker:<4}] "
            f"{result['id']:<38} "
            f"{result['category']}"
        )

        if not result[
            "passed"
        ]:

            for failure in result[
                "failures"
            ]:

                print(
                    f"       - {failure}"
                )

    print()
    print(
        "-" * 78
    )

    print(
        f"Overall: "
        f"{summary['passed']}/"
        f"{summary['total']} "
        f"({summary['percentage']}%)"
    )

    print()
    print(
        "By category:"
    )

    for category, values in (
        summary[
            "by_category"
        ].items()
    ):

        print(
            f"  {category:<26} "
            f"{values['passed']}/"
            f"{values['total']} "
            f"({values['percentage']}%)"
        )

    print()
    print(
        "By suite:"
    )

    for suite, values in (
        summary[
            "by_suite"
        ].items()
    ):

        print(
            f"  {suite:<26} "
            f"{values['passed']}/"
            f"{values['total']} "
            f"({values['percentage']}%)"
        )

    print(
        "=" * 78
    )


def save_results(
    label: str,
    results: list[dict[str, Any]],
    summary: dict[str, Any],
) -> Path:

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        RESULTS_DIR
        / f"{label}.json"
    )

    payload = {
        "label":
            label,

        "generated_at":
            datetime.now()
            .astimezone()
            .isoformat(),

        "summary":
            summary,

        "cases":
            results,
    }

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return path


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Run Aster & Row support-agent evaluations."
        )
    )

    parser.add_argument(
        "--label",
        default="latest",
        help=(
            "Name used for the saved results file. "
            "Examples: baseline, final"
        ),
    )

    parser.add_argument(
        "--case",
        default=None,
        help=(
            "Run only one case ID."
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Print user messages and agent answers."
        ),
    )

    args = parser.parse_args()

    cases = load_all_cases()

    if args.case:

        cases = [
            case
            for case in cases
            if case[
                "id"
            ]
            == args.case
        ]

        if not cases:

            raise SystemExit(
                f"Unknown evaluation case: {args.case}"
            )

    print(
        f"Loaded {len(cases)} evaluation cases."
    )

    results = []

    for index, case in enumerate(
        cases,
        start=1,
    ):

        print(
            f"[{index}/{len(cases)}] "
            f"{case['id']}..."
        )

        result = run_case(
            case,
            verbose=args.verbose,
        )

        results.append(
            result
        )

    summary = summarize(
        results
    )

    print_results(
        results,
        summary,
    )

    output_path = save_results(
        args.label,
        results,
        summary,
    )

    print(
        f"\nResults saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()