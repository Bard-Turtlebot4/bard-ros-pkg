from setuptools import find_packages, setup

package_name = 'bsripkg_talkative'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan',
    maintainer_email='juanjuo37@gmail.com',
    description='CLI to print text to display and generate TTS',
    license='Apache2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtlebot4_ttscli_node = bsripkg_talkative.turtlebot4_ttscli_node:main'
        ],
    },
)
