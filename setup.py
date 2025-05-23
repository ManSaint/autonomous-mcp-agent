from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='autonomous-mcp-agent',
    version='0.1.0',
    author='MCP Innovations',
    description='Autonomous MCP tool orchestration system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ManSaint/autonomous-mcp-agent',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    install_requires=[
        'aiohttp>=3.8.0',
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
        'spacy>=3.0.0',
        'asyncio>=3.4.3',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.18.0',
            'black>=22.0',
            'flake8>=4.0',
        ]
    }
)