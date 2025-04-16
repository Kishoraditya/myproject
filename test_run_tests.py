"""
Tests for the run_tests.py script.
"""
import importlib.util
import os  # noqa: F401 - used in patch decorator
import sys  # noqa: F401 - used in patch decorator

# Keep unittest for unittest.main()
import unittest

# Only keep what's actually used in the mock decorators
from unittest.mock import patch

# We need pytest for type hints but we're not using it directly in the code
# Add a # noqa comment to suppress the linter warning


# Import the module directly
spec = importlib.util.spec_from_file_location("run_tests", "run_tests.py")
run_tests_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_tests_module)


class TestRunTests:
    @patch("pytest.main")
    @patch("sys.exit")
    def test_main_function(self, mock_exit, mock_pytest_main):
        """Test that main function calls pytest.main with correct arguments."""
        mock_pytest_main.return_value = 42

        # Call the main function
        run_tests_module.main()

        # Check that pytest.main was called with expected arguments
        mock_pytest_main.assert_called_once()
        args = mock_pytest_main.call_args[0][0]
        assert "--ds=myproject.settings.test" in args
        assert "-v" in args
        assert "--no-migrations" in args

        # Check that sys.exit was called with the return value of pytest.main
        mock_exit.assert_called_once_with(42)

    @patch("os.path.abspath")
    @patch("os.chdir")
    @patch("pytest.main")
    @patch("sys.exit")
    def test_directory_change(
        self, mock_exit, mock_pytest_main, mock_chdir, mock_abspath
    ):
        """Test that script changes working directory to correct path."""
        mock_abspath.return_value = "/path/to/project"
        mock_pytest_main.return_value = 0

        # Call the main function with the script_dir parameter
        # This avoids the need to mock os.path.dirname(__file__)
        run_tests_module.main(script_dir="/path/to/project")

        # Check that chdir was called with expected directory
        mock_chdir.assert_called_once_with("/path/to/project")
        mock_exit.assert_called_once_with(0)

    @patch(
        "sys.argv",
        ["run_tests.py", "-v", "test_file.py::test_function", "-k", "test_pattern"],
    )
    @patch("pytest.main")
    @patch("sys.exit")
    def test_command_line_args(self, mock_exit, mock_pytest_main):
        """Test that command line arguments are correctly passed to pytest.main."""
        mock_pytest_main.return_value = 0

        # Call the main function
        run_tests_module.main()

        # Check that pytest.main was called with expected arguments
        mock_pytest_main.assert_called_once()
        args = mock_pytest_main.call_args[0][0]
        assert "--ds=myproject.settings.test" in args
        assert "-v" in args
        assert "test_file.py::test_function" in args
        assert "-k" in args
        assert "test_pattern" in args
        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
