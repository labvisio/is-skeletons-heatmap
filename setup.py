from setuptools import setup

setup(
    name='is_skeletons_heatmap',
    version='0.0.2',
    description='',
    url='http://github.com/labvisio/is-skeletons-heatmap',
    author='labvisio',
    license='MIT',
    packages=["is_skeletons_heatmap", "is_skeletons_heatmap.conf"],
    package_dir={'': '.'},
    entry_points={
        'console_scripts': [
            'is-skeletons-heatmap=is_skeletons_heatmap.service:main',
        ],
    },
    zip_safe=False,
    install_requires=[
        'is-wire==1.2.1',
        'is-msgs==1.1.18',
        'opencensus-ext-zipkin==0.2.1',
        'opencv-python==4.8.0.76',
        'numpy==1.26.0',
        'scipy==1.11.2',
        'matplotlib==3.8.0',
    ],
)
