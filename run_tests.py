#!/usr/bin/env python
"""
Run tests for the Shoshin project with proper Django initialization.
This script ensures that Django settings are properly configured before tests run.
"""
import os
import sys

import pytest


def main(script_dir=None):
    """Run tests with Django settings properly configured."""
    # Default arguments
    args = [
        "--ds=myproject.settings.test",  # Use the test settings
        "-v",  # Verbose output
        "--no-migrations",  # Skip migrations to speed up tests
    ]

    # Add any additional arguments from command line
    args.extend(sys.argv[1:])

    # Make sure we're in the project directory
    if script_dir is None:
        project_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        project_dir = script_dir

    if os.getcwd() != project_dir:
        os.chdir(project_dir)

    # Run pytest with the configured arguments
    result = pytest.main(args)

    # Return the exit code from pytest
    sys.exit(result)


if __name__ == "__main__":
    main()
