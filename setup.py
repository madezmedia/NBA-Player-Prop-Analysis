from setuptools import setup, find_packages

setup(
    name='basketball-ai-analyst',
    version='0.1.0',
    description='Advanced Basketball Performance Analysis AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/basketball-ai-analyst',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'requests',
        'python-dotenv',
        'pillow',
        'opencv-python-headless',
        'pytesseract',
        'groq',
        'crewai',
        'rapidapi-python',
        'matplotlib',
        'scikit-learn',
        'pytest',
        'flake8',
        'coverage',
        'openai',
        'anthropic',
        'transformers',
        'scikit-image',
        'cachetools',
        'joblib',
        'structlog',
        'sentry-sdk',
        'scipy',
        'seaborn'
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'coverage',
            'black',
            'mypy'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Sports Enthusiasts',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Sports/Fitness :: Analytics'
    ],
    keywords='basketball ai analytics machine-learning sports-data',
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'basketball-ai=app:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/basketball-ai-analyst/issues',
        'Source': 'https://github.com/yourusername/basketball-ai-analyst',
    },
)
