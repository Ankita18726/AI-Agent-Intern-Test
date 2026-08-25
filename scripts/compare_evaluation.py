import json
from pathlib import Path


RESULTS_DIR = Path(
    "evaluation/results"
)


def load(
    name: str,
):

    path = (
        RESULTS_DIR
        / f"{name}.json"
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


def main():

    baseline = load(
        "baseline"
    )

    final = load(
        "final"
    )

    base_summary = baseline[
        "summary"
    ]

    final_summary = final[
        "summary"
    ]

    print(
        "=" * 65
    )

    print(
        "Baseline vs Final"
    )

    print(
        "=" * 65
    )

    print(
        f"Baseline: "
        f"{base_summary['passed']}/"
        f"{base_summary['total']} "
        f"({base_summary['percentage']}%)"
    )

    print(
        f"Final:    "
        f"{final_summary['passed']}/"
        f"{final_summary['total']} "
        f"({final_summary['percentage']}%)"
    )

    print()

    categories = sorted(
        set(
            base_summary[
                "by_category"
            ]
        )
        | set(
            final_summary[
                "by_category"
            ]
        )
    )

    print(
        f"{'Category':<28} "
        f"{'Baseline':<15} "
        f"{'Final':<15}"
    )

    print(
        "-" * 60
    )

    for category in categories:

        before = (
            base_summary[
                "by_category"
            ].get(
                category,
                {
                    "passed": 0,
                    "total": 0,
                },
            )
        )

        after = (
            final_summary[
                "by_category"
            ].get(
                category,
                {
                    "passed": 0,
                    "total": 0,
                },
            )
        )

        before_text = (
            f"{before['passed']}/"
            f"{before['total']}"
        )

        after_text = (
            f"{after['passed']}/"
            f"{after['total']}"
        )

        print(
            f"{category:<28} "
            f"{before_text:<15} "
            f"{after_text:<15}"
        )


if __name__ == "__main__":
    main()
    