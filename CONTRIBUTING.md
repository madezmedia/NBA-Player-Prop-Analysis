# Contributing to Basketball AI Performance Analyst

## Welcome!

We're thrilled that you're interested in contributing to the Basketball AI Performance Analyst project. This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others. Harassment, discrimination, and offensive behavior are not tolerated.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template provided
3. Provide clear, detailed information about the issue
4. Include steps to reproduce, expected behavior, and actual behavior

### Suggesting Enhancements

1. Open an issue with a clear title and description
2. Explain the enhancement in detail
3. Provide context on why this enhancement would be valuable

## Development Process

### Prerequisites

- Python 3.8+
- Poetry or pip
- Git

### Setup

1. Fork the repository
2. Clone your fork
```bash
git clone https://github.com/your-username/basketball-ai-analyst.git
cd basketball-ai-analyst
```

3. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

4. Install dependencies
```bash
pip install -r requirements.txt
pip install -e .[dev]
```

### Making Changes

1. Create a new branch
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
   - Follow PEP 8 style guidelines
   - Write clear, concise code
   - Add/update tests
   - Update documentation

3. Run tests and linters
```bash
pytest
flake8
black .
mypy .
```

### Commit Messages

- Use conventional commits
- Format: `<type>(<scope>): <description>`
- Types: 
  - `feat`: New feature
  - `fix`: Bug fix
  - `docs`: Documentation changes
  - `style`: Formatting, missing semicolons
  - `refactor`: Code restructuring
  - `test`: Adding or modifying tests
  - `chore`: Maintenance tasks

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add a clear description of changes
4. Reference related issues

## Code Review Process

- All submissions require review
- Maintainers will provide feedback
- Be open to constructive criticism
- Discussions should be professional and objective

## Development Workflow

### Branching Strategy

- `main`: Stable release branch
- `develop`: Integration branch for features
- Feature branches: `feature/description`
- Hotfix branches: `hotfix/description`

### Code Quality Checks

We use:
- Black for formatting
- Flake8 for linting
- MyPy for type checking
- Pytest for testing
- Pre-commit hooks for automated checks

## Performance and AI Considerations

- Optimize AI model performance
- Minimize computational complexity
- Consider ethical AI practices
- Protect user privacy

## Reporting Security Issues

- Do not open public issues for security vulnerabilities
- Email security concerns to [your-security-email]
- Provide detailed information securely

## Recognition

Contributors will be acknowledged in:
- README.md
- CONTRIBUTORS.md
- Release notes

## Questions?

Open an issue or contact the maintainers directly.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
