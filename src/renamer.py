from pathlib import Path
from typing import Dict, List
from src.utils import (
    sort_files, 
    is_valid_separator, 
    is_valid_start_index, 
    is_valid_padding, 
    is_valid_case, 
    is_invalid_keep_no_number_combination
    )







def buil_rename_plan(
        src: Path, 
        *, 
        order: str, 
        prefix: str, 
        separator: str, 
        start: int, 
        padding: int, 
        case: str,
        keep: bool, 
        no_number: bool
) -> Dict[Path, Path]:
    
    """
    Builds a rename plan for all files in a source directory based on the specified parameters.

    The function generates a dictionary mapping each original file Path to its
    intended new Path, applying ordering, prefixes, numbering, padding, case formatting,
    and options to keep the original name or remove numbering. This plan can later be
    used to safely perform the renaming.

    Args:
        src (Path): Source directory containing files to rename.
        order (str): Sorting criterion for files. Supported values: 
                     "name", "mtime", "ctime", "embedded".
        prefix (str): Text to prepend to each new file name.
        separator (str): Character used to separate prefix, numbering, and base name.
        start (int): Starting number for file numbering (must be > 0).
        padding (int): Number of digits for zero-padding the numbering (>= 0).
        case (str): Case formatting for the new name. Allowed values: "lower", "upper", "title".
        keep (bool): Whether to keep the original file name as part of the new name.
        no_number (bool): Whether to omit numbering in the new name.

    Returns:
        Dict[Path, Path]: Dictionary mapping each original file Path to its planned new Path.

    Raises:
        ValueError: If src does not exist or is not a directory.
        ValueError: If start is not greater than 0.
        ValueError: If padding is negative.
        ValueError: If separator is invalid (not "_", "-", or ".").
        ValueError: If case is invalid (not "lower", "upper", or "title").
        ValueError: If the combination of keep=False and no_number=True is used.

    Examples:
        >>> from pathlib import Path
        >>> plan = buil_rename_plan(
        ...     Path("my_files"),
        ...     order="name",
        ...     prefix="IMG",
        ...     separator="_",
        ...     start=1,
        ...     padding=3,
        ...     case="upper",
        ...     keep=True,
        ...     no_number=False
        ... )
        >>> list(plan.keys())
        [Path("file1.txt"), Path("file2.txt")]
        >>> list(plan.values())
        [Path("IMG_FILE1_001"), Path("IMG_FILE2_002")]
    """
    
    if not src.exists() or not src.is_dir():
        raise ValueError("Completame el codigo en ingles del error")
    
    if not is_valid_start_index(start): raise ValueError("Start index must be greater than 0")

    if not is_valid_padding(padding): raise ValueError("Padding must be zero or a positive integer")

    if not is_valid_separator(separator): raise ValueError(f"Invalid separator: '{separator}'. Allowed characters are '_', '-', or '.'")

    if not is_valid_case(case): raise ValueError(f"Invalid case: '{case}'. Allowed values are 'lower', 'upper', or 'title'")

    if is_invalid_keep_no_number_combination(keep, no_number): raise ValueError("Cannot combine keep and no_number")

    #Creo una lista auxiliar para recorrer de manera correcta, ya que el sistema me recorre como se le canta:
    files: List[Path] = [p for p in Path.iterdir(src) if p.is_file()]

    ordered_files: List[Path] = sort_files(files, order)

    rename_plan: Dict[Path, Path] = {}

    index = start

    for item in ordered_files:

        parts = []

        if prefix != "": parts.append(prefix)
        if keep: parts.append(item.stem)
        if not no_number: parts.append(str(index).zfill(padding))

        match(case):
            case "upper": parts = [element.upper() for element in parts]
            case "title": parts = [element.title() for element in parts]
            case _: parts = [element.lower() for element in parts]

        new_name = separator.join(parts)

        index += 1

        #rename_plan[item] = src / f"{new_name}{item.suffix}"

        #Para probar:
        rename_plan[Path(item.stem)] = Path(new_name)

    for k, v in rename_plan.items():
        print(f"{k} -> {v}")
    

    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
 
    return rename_plan