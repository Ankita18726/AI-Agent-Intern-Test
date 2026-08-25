from app.config import TRACE_PATH


def main():

    if TRACE_PATH.exists():

        TRACE_PATH.unlink()

        print(
            f"Deleted trace file: "
            f"{TRACE_PATH}"
        )

    else:

        print(
            "No trace file exists."
        )


if __name__ == "__main__":
    main()