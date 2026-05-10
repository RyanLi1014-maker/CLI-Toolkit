"""Unit tests for the project root utility."""

# Import the project root utility to test
import src.util.project_root


class TestProjectRoot:
    """Unit tests for the project root utility."""

    def test_project_root(self):
        """Test that the project root is determined correctly."""
        # Get the project root from the utility
        project_root = src.util.project_root.PROJECT_ROOT

        # Check that the project root is a Path object
        assert isinstance(project_root, src.util.project_root.Path)

        # Check that the project root is correct by checking for a known file
        assert (project_root / "pyproject.toml").exists()
