from setuptools import setup, find_packages

setup(
    name='wasmai',
    version='0.1.0',
    description='Python dataclasses for representing WASM modules with WASM 2.0, GC, threads, and tail call support',
    author='wasmai',
    packages=find_packages(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
