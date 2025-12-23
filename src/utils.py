from typing import List, Dict
from pathlib import Path
import re
import json
import os


#Funciones de verificacion:

def is_valid_separator(character: str) -> bool:

    """
    Determines whether a given character is a valid file name separator.

    A valid separator is one of the characters typically used to separate
    elements in file names, such as prefixes, indices, or base names.
    This function helps ensure that generated file names conform to expected
    formatting rules.

    Args:
        character (str): A single character to evaluate as a potential separator.

    Returns:
        bool: True if the character is one of the allowed separators ("_", "-", "."),
              False otherwise.

    Raises:
        TypeError: If the input is not a string of length 1.

    Examples:
        >>> is_valid_separator("_")
        True
        >>> is_valid_separator("-")
        True
        >>> is_valid_separator(".")
        True
        >>> is_valid_separator(" ")
        False
        >>> is_valid_separator("a")
        False
    """

    return character in ["_", "-", "."]

def is_valid_start_index(number_initial: int) -> bool:
    
    """
    Checks if the provided start index for file numbering is valid.

    A valid start index must be a positive integer greater than zero.
    This ensures that numbered sequences in file renaming start from a logical,
    non-zero value.

    Args:
        number_initial (int): The initial number to validate.

    Returns:
        bool: True if the number is greater than 0, False otherwise.

    Raises:
        TypeError: If the input is not an integer.

    Examples:
        >>> is_valid_start_index(1)
        True
        >>> is_valid_start_index(5)
        True
        >>> is_valid_start_index(0)
        False
        >>> is_valid_start_index(-3)
        False
    """

    return number_initial > 0

def is_valid_padding(number_padding: int) -> bool:
    
    """
    Checks if the provided padding value for numbering is valid.

    Padding determines the number of leading zeros in file numbering.
    A valid padding is zero or any positive integer.

    Args:
        number_padding (int): The padding value to validate.

    Returns:
        bool: True if the padding is zero or positive, False otherwise.

    Raises:
        TypeError: If the input is not an integer.

    Examples:
        >>> is_valid_padding(0)
        True
        >>> is_valid_padding(3)
        True
        >>> is_valid_padding(-1)
        False
    """

    return number_padding >= 0

def is_valid_case(str_case: str) -> bool:

    """
    Checks whether a given string represents a valid case option for file renaming.

    Valid case options are:
        - "lower"  : convert file names to lowercase
        - "upper"  : convert file names to uppercase
        - "title"  : capitalize the first letter of each word in file names

    Args:
        str_case (str): The case option to validate.

    Returns:
        bool: True if the case option is valid, False otherwise.

    Raises:
        TypeError: If the input is not a string.

    Examples:
        >>> is_valid_case("lower")
        True
        >>> is_valid_case("upper")
        True
        >>> is_valid_case("title")
        True
        >>> is_valid_case("original")
        False
        >>> is_valid_case("")
        False
    """

    return str_case in ["lower", "upper", "title"]

def is_invalid_keep_no_number_combination(keep: bool, no_number: bool) -> bool:

    """
    Determines if a combination of flags 'keep' and 'no_number' is logically invalid
    for file renaming.

    The combination is considered invalid if 'keep' is False and 'no_number' is True,
    because this would result in removing all numbering but not keeping the original name,
    leaving no valid naming for files.

    Args:
        keep (bool): Flag indicating whether to keep the original file name.
        no_number (bool): Flag indicating whether numbering should be removed.

    Returns:
        bool: True if the combination is invalid, False otherwise.

    Raises:
        TypeError: If either input is not a boolean.

    Examples:
        >>> is_invalid_keep_no_number_combination(False, True)
        True
        >>> is_invalid_keep_no_number_combination(True, True)
        False
        >>> is_invalid_keep_no_number_combination(False, False)
        False
        >>> is_invalid_keep_no_number_combination(True, False)
        False
    """

    return (not keep) and (no_number)


#Funciones para el ordenamiento:

def extract_embedded_number(path: Path) -> int:

    """
    Extracts the first embedded number from a file name (without extension).

    This function searches for the first sequence of digits in the file stem
    (i.e., the file name without its extension) and returns it as an integer.
    If no number is found, it returns -1.

    Args:
        path (Path): The Path object representing the file.

    Returns:
        int: The first embedded number found in the file name, or -1 if none exists.

    Raises:
        TypeError: If the input is not a Path object.

    Examples:
        >>> extract_embedded_number(Path("file123.txt"))
        123
        >>> extract_embedded_number(Path("image_45_test.png"))
        45
        >>> extract_embedded_number(Path("no_numbers_here.txt"))
        -1
    """

    result = -1
    match = re.search(r"\d+", path.stem)
    if match: result = int(match.group())
    return result

#Esta justo tambien verifica:
def sort_files(list_files: List[Path], order: str) -> List[Path]:

    """
    Sorts a list of files according to the specified order criteria.

    Supported order criteria:
        - "name"      : Alphabetical order based on the full file name.
        - "mtime"     : Modification time (oldest to newest).
        - "ctime"     : Creation time (oldest to newest).
        - "embedded"  : Order based on the first embedded number in the file name.

    Args:
        list_files (List[Path]): A list of Path objects representing files to sort.
        order (str): The sorting criterion ("name", "mtime", "ctime", "embedded").

    Returns:
        List[Path]: A new list of Path objects sorted according to the specified order.

    Raises:
        TypeError: If list_files is not a list of Path objects or order is not a string.
        ValueError: If the order criterion is unsupported.

    Examples:
        >>> sort_files([Path("file2.txt"), Path("file1.txt")], "name")
        [Path("file1.txt"), Path("file2.txt")]
        
        >>> sort_files([Path("file3.txt"), Path("file1.txt")], "embedded")
        [Path("file1.txt"), Path("file3.txt")]
    """

    match(order):
        case "name": ordered_list = sorted(list_files, key=lambda p: p.name)
        case "mtime": ordered_list = sorted(list_files, key=lambda p: p.stat().st_mtime)
        case "ctime": ordered_list = sorted(list_files, key=lambda p: p.stat().st_ctime)
        case "embedded": ordered_list = sorted(list_files, key=extract_embedded_number)
        case _: raise ValueError(f"Unsupported order: {order}")

    return ordered_list

#Funciones para majerar el salvado en el json:

def get_backup_folder() -> Path:

    """
    Returns the default backup folder path for storing rename plans.

    On Windows, the backup folder is located under the LOCALAPPDATA directory.
    On Linux or MacOS, it is created as a hidden folder in the user's home directory.
    The function ensures the folder exists by creating it if necessary.

    Returns:
        Path: The Path object representing the backup folder.

    Raises:
        OSError: If the folder cannot be created due to filesystem permissions.

    Examples:
        >>> backup_folder = get_backup_folder()
        >>> backup_folder.exists()
        True
        >>> str(backup_folder)
        'C:\\Users\\User\\AppData\\Local\\FilesRenamer'  # on Windows
        >>> str(backup_folder)
        '/home/user/.files_renamer'  # on Linux/MacOS
    """

    if os.name == "nt": #Windows
        folder = Path(f"{os.getenv("LOCALAPPDATA")}") / "FilesRenamer"
    else: #Linux o MacOs
        folder = Path.home() / ".files_renamer"

    folder.mkdir(parents=True, exist_ok=True)

    return folder


def save_rename_plan_json(rename_plan: Dict[Path, Path], backup_files: Path) -> None:

    """
    Saves a rename plan to a JSON file for backup or recovery purposes.

    The function converts Path objects to strings and writes the mapping of
    original file paths to new file paths into a JSON file with indentation
    for readability. The parent directory is created if it does not exist.

    Args:
        rename_plan (Dict[Path, Path]): Dictionary mapping original files to
                                        their new names.
        backup_file (Path): Path to the JSON file where the rename plan will be saved.

    Returns:
        None

    Raises:
        TypeError: If rename_plan is not a dictionary of Path to Path.
        OSError: If the file cannot be written due to filesystem permissions.

    Examples:
        >>> from pathlib import Path
        >>> plan = {Path("file1.txt"): Path("file_1.txt")}
        >>> backup_path = Path("backup/rename_plan.json")
        >>> save_rename_plan_json(plan, backup_path)
        >>> backup_path.exists()
        True
    """

    backup_files.parent.mkdir(parents=True, exist_ok=True)
    with open(backup_files, "w") as f:
        json.dump({str(k): str(v) for k, v in rename_plan.items()}, f, indent=2)