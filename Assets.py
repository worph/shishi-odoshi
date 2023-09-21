import os
import sys


def getAssetPath(relative_path: str) -> str:
    """
    Gets the correct asset path for bundled applications or scripts.

    Args:
        relative_path (str): The relative path to the asset.

    Returns:
        str: The correct path to the asset.
    """

    # Determine if running as a script or bundled executable
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle/compiled .exe, this will be True
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)

    return os.path.join(basedir, relative_path)
