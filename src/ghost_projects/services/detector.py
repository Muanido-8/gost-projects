import logging
from pathlib import Path
from typing import Set

from ghost_projects.schemas.project import ProjectInfo

logger = logging.getLogger(__name__)

class ProjectDetector:
    """
    Responsible for identifying likely programming languages, frameworks, 
    and technologies based on project structure and configuration files.
    """

    # Mapping of filenames to the technologies they strongly indicate
    # Format: { filename: (language, technology) }
    STRONG_INDICATORS = {
        "pyproject.toml": ("Python", "Pyproject"),
        "requirements.txt": ("Python", "Pip"),
        "setup.py": ("Python", "Setuptools"),
        "package.json": ("JavaScript/TypeScript", "npm/yarn"),
        "tsconfig.json": ("TypeScript", "TypeScript"),
        "pom.xml": ("Java", "Maven"),
        "build.gradle": ("Java/Kotlin", "Gradle"),
        "Cargo.toml": ("Rust", "Cargo"),
        "go.mod": ("Go", "Go Modules"),
        "composer.json": ("PHP", "Composer"),
        "Gemfile": ("Ruby", "Bundler"),
        "*.csproj": ("C#", ".NET"),
    }

    def __init__(self):
        pass

    def detect(self, root: Path, files: list[Path]) -> ProjectInfo:
        """
        Detects languages and technologies based on the provided list of files.
        
        Args:
            root: The project root path.
            files: A list of all discovered files in the project.
            
        Returns:
            A ProjectInfo object containing the detected information.
        """
        detected_languages: Set[str] = set()
        detected_technologies: Set[str] = set()
        
        # Convert files to a set of names for faster lookup
        file_names = {f.name for f in files}
        
        for indicator, (lang, tech) in self.STRONG_INDICATORS.items():
            # Handle glob patterns like *.csproj
            if indicator.startswith("*."):
                ext = indicator[1:]
                if any(f.name.endswith(ext) for f in files):
                    detected_languages.add(lang)
                    detected_technologies.add(tech)
            elif indicator in file_names:
                detected_languages.add(lang)
                detected_technologies.add(tech)

        # Refine detection by inspecting content of key files if they exist
        # Example: check package.json for "dependencies" to see if it's React, Vue, etc.
        for f in files:
            if f.name == "package.json":
                self._refine_js_tech(f, detected_technologies)
            elif f.name == "pyproject.toml":
                self._refine_python_tech(f, detected_technologies)

        return ProjectInfo(
            name=root.name,
            root_path=root,
            detected_languages=list(detected_languages),
            detected_technologies=list(detected_technologies),
            has_git=(root / ".git").exists()
        )

    def _refine_js_tech(self, path: Path, technologies: Set[str]):
        """Inspects package.json for common JS frameworks."""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            frameworks = {
                "react": "React",
                "vue": "Vue.js",
                "angular": "Angular",
                "next": "Next.js",
                "express": "Express",
                "svelte": "Svelte"
            }
            for key, val in frameworks.items():
                if f'"{key}"' in content:
                    technologies.add(val)
        except Exception as e:
            logger.warning(f"Could not refine JS tech from {path}: {e}")

    def _refine_python_tech(self, path: Path, technologies: Set[str]):
        """Inspects pyproject.toml for common Python frameworks."""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            frameworks = {
                "django": "Django",
                "flask": "Flask",
                "fastapi": "FastAPI",
                "pandas": "Pandas",
                "numpy": "NumPy",
                "pytorch": "PyTorch",
                "tensorflow": "TensorFlow"
            }
            for key, val in frameworks.items():
                if key in content.lower():
                    technologies.add(val)
        except Exception as e:
            logger.warning(f"Could not refine Python tech from {path}: {e}")