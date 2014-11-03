from setuptools import setup

setup(
    name='simple-observers',
    version='0.1.1',
    description='Twisted logging without decorations',
    long_description='Observers for twisted logging that produces log messages without decorations',
    url='https://github.com/wrapp/simple-observers',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    keywords='twisted logging',
    install_requires=['twisted'],
    py_modules=['simple_observers']
)
