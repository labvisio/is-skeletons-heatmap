from setuptools import setup, find_packages

setup(
    name='is_skeletons_heatmap',
    version='0.0.1',
    description='',
    url='http://github.com/labviros/is-skeletons-heatmap',
    author='labviros',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'is-skeletons-heatmap=is_skeletons_heatmap.service:main',
        ],
    },
    zip_safe=False,
    install_requires=[
        'is-wire==1.1.2',
        'is-msgs==1.1.7',
        'opencv-python==3.4.*',
        'numpy==1.14.3',
        'scipy==1.1.0',
        'matplotlib==2.2.2',
    ],
)
