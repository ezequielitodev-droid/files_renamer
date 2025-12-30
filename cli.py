import argparse
from pathlib import Path
import json
import sys
from src.renamer import (
    buil_rename_plan, 
    dry_run_cli, 
    reverse_rename_run, 
    rename_run
    )
from src.utils import (
    is_valid_order, 
    is_valid_prefix, 
    is_valid_separator, 
    is_valid_start_index, 
    is_valid_padding, 
    is_valid_case, 
    is_invalid_keep_no_number_combination, 
    is_invalid_dry_run_reverse_run_combination, 
    is_invalid_run_reverse_with_extra_option, 
    get_backup_folder, 
    save_rename_plan_json
)


def cli_run() -> None:
    
    """
    Entry point for the command-line interface that performs massive file renaming or reverts a previous renaming plan.

    This CLI builds a deterministic renaming plan from a target folder, validates all user-supplied options,
    and then executes one of the supported modes:

    - Normal rename execution (`rename_run`)
    - Simulation without file system changes (`dry_run_cli`)
    - Restoration of a previous renaming plan (`reverse_rename_run`)

    Reverse-run mode is intended to undo a prior renaming operation using a stored JSON backup and,
    when enabled, prevents the normal renaming or dry-run simulation from running afterward.

    Args:
        None. All parameters are read from CLI flags via argparse.

    Returns:
        None. Outputs results to stdout and performs file system operations when applicable.

    Raises:
        ValueError: If any provided CLI option is invalid or if an incompatible option combination is detected.

    CLI Options validated in this flow:
        --order, --prefix, --separator, --start, --padding, --case, --keep, --no-number, --dry-run, --reverse-run.

    Examples:
        $ python cli.py ./files --order name --prefix img --separator _ --start 1 --padding 3
        Renames all files in "./files" using the generated plan.

        $ python cli.py ./files --dry-run --order mtime --prefix test
        Simulates the renaming plan and prints it without modifying files.

        $ python cli.py ./backup-folder --reverse-run
        Loads the stored JSON backup and restores all file names to their previous state.
    """
    
    parser = argparse.ArgumentParser(description="Bulk file renamer with ordering, prefixes, casing and a reversible backup plan.")

    parser.add_argument("folder", type=Path)
    parser.add_argument("--order", type=str, required=True)
    parser.add_argument("--prefix", type=str, default="")
    parser.add_argument("--separator", type=str, default="_")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--padding", type=int, default=0)
    parser.add_argument("--case", type=str, default="lower")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--no-number", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reverse-run", action="store_true")

    args = parser.parse_args()

    #Ahora tendria que pensar el flujo

    #Ahora pienso hacer verificaciones:

    try:
        if not is_valid_order(args.order):
            raise ValueError(
                "Invalid order option. Allowed values are: name, mtime, ctime, embedded."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if not is_valid_prefix(args.prefix):
            raise ValueError(
                "Invalid prefix: contains forbidden characters, is empty, "
            "or uses a reserved system name."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if not is_valid_separator(args.separator):
            raise ValueError(
                "Invalid separator: must be one of the allowed characters ('_', '-', or '.')."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if not is_valid_start_index(args.start):
            raise ValueError(
                "Invalid start index: value must be a positive integer greater than zero."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if not is_valid_padding(args.padding):
            raise ValueError(
                "Invalid padding: value must be a non-negative integer."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if not is_valid_case(args.case):
            raise ValueError(
                "Invalid case option: must be one of 'lower', 'upper', or 'title'."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if is_invalid_keep_no_number_combination(args.keep, args.no_number):
            raise ValueError(
                "Invalid option combination: '--keep' cannot be used together with '--no-number'."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


    other_arguments = False

    if (args.prefix != "") or (args.separator != "_") or (args.start != 1) or (args.padding != 0) or (args.case != "lower") or args.keep or args.no_number or args.dry_run: other_arguments = True

    try:
        if is_invalid_run_reverse_with_extra_option(args.reverse_run, other_arguments):
            raise ValueError(
                "Invalid reverse-run usage: --reverse-run must be invoked alone "
            "and cannot be combined with other renaming options."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        if is_invalid_dry_run_reverse_run_combination(args.dry_run, args.reverse_run):
            raise ValueError(
                "Invalid option combination: --dry-run and --reverse-run cannot be used together."
            )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    plan_renamer = buil_rename_plan(
        args.folder, 
        order=args.order, 
        prefix=args.prefix, 
        separator=args.separator, 
        start=args.start, padding=args.padding, 
        case=args.case, 
        keep=args.keep, 
        no_number=args.no_number)

    path_folder_backup = get_backup_folder()
    path_json_backup = path_folder_backup / "rename_plan_backup.json"
    
    if args.dry_run:
        dry_run_cli(plan_renamer)
    else:

        if args.reverse_run:

            with open(path_json_backup, "r") as f:
                data = json.load(f)

            plan_backup = {Path(old): Path(new) for old, new in data.items()}

            plan_backup_anterior = {Path(new): Path(old) for old, new in data.items()}


            reverse_rename_run(plan_backup)
            save_rename_plan_json(plan_backup_anterior, path_json_backup)
        else:
            rename_run(plan_renamer)
            save_rename_plan_json(plan_renamer, path_json_backup)
        

#Punto de entrada del programa:

if __name__ == "__main__":
    cli_run()





#COSAS A TERMINAR:



#Empaquetarlo y probarlo