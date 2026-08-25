import json

from app.config import TRACE_PATH


def main():

    if not TRACE_PATH.exists():

        print(
            "No trace file found."
        )

        return

    with TRACE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        lines = [
            line.strip()
            for line in file
            if line.strip()
        ]

    if not lines:

        print(
            "Trace file is empty."
        )

        return

    trace = json.loads(
        lines[-1]
    )

    print(
        json.dumps(
            trace,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()